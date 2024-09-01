from typing import Iterator

import os
import json
import configparser
from typing import Tuple, Union
import uuid

import pandas as pd
from dotenv import load_dotenv
from together import Together
from openai import OpenAI

from src.lattice.llm.together import get_together_chat_response, get_together_embedding
from src.lattice.compiler.types import Function
from src.lattice.logger import logger
from paths import ROOT_PROJECT_PATH


def index(
    entity: pd.DataFrame,
    description_extraction_prompt_template: str,
    keyword_extraction_prompt_template: str,
    together_llm_client: Union[Together],
    together_llm_model_name: str,
    together_embedding_client: Union[OpenAI],
    together_embedding_model_name: str,
) -> pd.DataFrame:
    # processing entity rows
    for idx, row in entity.iterrows():
        function_name = row["function_name"]
        definition = row["definition"]

        logger.debug(f"embedding {function_name} name")
        # embedding function_name
        function_name_emb = get_together_embedding(
            text=function_name,
            together_embedding_client=together_embedding_client,
            together_model_name=together_embedding_model_name,
            normalize_embedding=True,
        )
        entity.loc[idx, "function_name_embedding"] = str(function_name_emb)
        logger.debug(f"embedding {function_name} definition")
        # embedding definition
        definition_emb = get_together_embedding(
            text=definition,
            together_embedding_client=together_embedding_client,
            together_model_name=together_embedding_model_name,
            normalize_embedding=True,
        )
        entity.loc[idx, "definition_embedding"] = str(definition_emb)

        logger.debug(f"extracting {function_name} description")
        # extracting description for current row of entity
        description_extraction_prompt = description_extraction_prompt_template.format(
            definition=definition
        )

        llm_response = get_together_chat_response(
            prompt=description_extraction_prompt,
            together_llm_client=together_llm_client,
            together_llm_model_name=together_llm_model_name,
        )
        description = json.loads(llm_response)["description"]
        entity.loc[idx, "description"] = description

        logger.debug(f"embedding {function_name} description")
        # embedding description
        description_emb = get_together_embedding(
            text=description,
            together_embedding_client=together_embedding_client,
            together_model_name=together_embedding_model_name,
            normalize_embedding=True,
        )
        entity.loc[idx, "description_embedding"] = str(description_emb)

        logger.debug(f"generating {function_name} keywords")
        # extracting keywords for the current row of entity
        keyword_extraction_prompt = keyword_extraction_prompt_template.format(
            description=description, code=definition
        )
        llm_response = get_together_chat_response(
            prompt=keyword_extraction_prompt,
            together_llm_client=together_llm_client,
            together_llm_model_name=together_llm_model_name,
        )
        keywords = json.loads(llm_response)
        keywords = keywords["description_keywords"]

        logger.debug(f"embedding {function_name} keywords")
        # embedding keywords
        keywords_columns = []
        keywords_embedding_columns = []
        for keyword_idx, keyword in enumerate(keywords):
            keyword_emb = get_together_embedding(
                text=keyword,
                together_embedding_client=together_embedding_client,
                together_model_name=together_embedding_model_name,
                normalize_embedding=True,
            )

            entity.loc[idx, f"keyword_{keyword_idx}"] = keyword
            entity.loc[idx, f"keyword_{keyword_idx}_embedding"] = str(keyword_emb)
            keywords_columns.append(f"keyword_{keyword_idx}")
            keywords_embedding_columns.append(f"keyword_{keyword_idx}_embedding")

        # reordering columns of entity
        entity = entity[
            ["id", "function_name", "namespace", "definition", "description"]
            + keywords_columns
            + [
                "definition_embedding",
                "function_name_embedding",
                "description_embedding",
            ]
            + keywords_embedding_columns
        ]
    return entity


def index_project(
    compiler_iter: Iterator[Function], project_path: str, clients: dict
) -> None:
    together_llm_client = clients["llm"]["client"]
    together_embedding_client = clients["embedding"]["client"]
    together_llm_model_name = clients["llm"]["model"]
    together_embedding_model_name = clients["embedding"]["model"]

    # reading prompt templates
    config = configparser.ConfigParser()
    config.read(
        os.path.join(ROOT_PROJECT_PATH, "src", "lattice", "config", "prompt.ini")
    )
    keyword_extraction_prompt_template = config["prompts"]["keyword_extraction"]
    description_extraction_prompt_template = config["prompts"]["description_extraction"]

    # reading raw data and creating dataframes
    entity_dict = {
        "id": [],
        "function_name": [],
        "namespace": [],
        "definition": [],
    }
    for item in compiler_iter:
        logger.debug(f"reading {item.name}")
        entity_dict["id"].append(uuid.uuid4())
        entity_dict["function_name"].append(item.name)
        entity_dict["namespace"].append("project.default")
        entity_dict["definition"].append(item.definition)
    entity = pd.DataFrame.from_dict(data=entity_dict)

    # indexing the entity and relationship dataframes
    entity = index(
        entity=entity,
        description_extraction_prompt_template=description_extraction_prompt_template,
        keyword_extraction_prompt_template=keyword_extraction_prompt_template,
        together_llm_client=together_llm_client,
        together_llm_model_name=together_llm_model_name,
        together_embedding_client=together_embedding_client,
        together_embedding_model_name=together_embedding_model_name,
    )

    # Create the directory (and any necessary parent directories)
    directory_path = os.path.join(project_path, ".lattice")
    os.makedirs(directory_path, exist_ok=True)

    # saving processed dataframes
    entity.to_csv(os.path.join(directory_path, "entity.csv"), index=False)
