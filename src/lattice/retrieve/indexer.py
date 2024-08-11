import os
import json
import configparser
from typing import Tuple, Union

import pandas as pd
from dotenv import load_dotenv
from together import Together
from openai import OpenAI

from src.lattice.llm.together import get_together_chat_response, get_together_embedding
from src.lattice.retrieve.example_data_1 import ENTITY, RELATIONSHIP
from paths import ROOT_PROJECT_PATH


def index(
        entity: pd.DataFrame,
        relationship: pd.DataFrame,
        description_extraction_prompt_template: str,
        keyword_extraction_prompt_template: str,
        together_llm_client: Union[Together],
        together_llm_model_name: str,
        together_embedding_client: Union[OpenAI],
        together_embedding_model_name: str,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # processing entity rows
    for idx, row in entity.iterrows():
        function_name = row['function_name']
        definition = row['definition']

        # embedding function_name
        function_name_emb = get_together_embedding(text=function_name,
                                                   together_embedding_client=together_embedding_client,
                                                   together_model_name=together_embedding_model_name,
                                                   normalize_embedding=True)
        entity.loc[idx, "function_name_embedding"] = str(function_name_emb)
        # embedding definition
        definition_emb = get_together_embedding(text=definition,
                                                together_embedding_client=together_embedding_client,
                                                together_model_name=together_embedding_model_name,
                                                normalize_embedding=True)
        entity.loc[idx, "definition_embedding"] = str(definition_emb)

        # extracting description for current row of entity
        description_extraction_prompt = description_extraction_prompt_template.format(definition=definition)

        llm_response = get_together_chat_response(prompt=description_extraction_prompt,
                                                  together_llm_client=together_llm_client,
                                                  together_llm_model_name=together_llm_model_name)
        description = json.loads(llm_response)['description']
        entity.loc[idx, "description"] = description

        # embedding description
        description_emb = get_together_embedding(text=description,
                                                 together_embedding_client=together_embedding_client,
                                                 together_model_name=together_embedding_model_name,
                                                 normalize_embedding=True)
        entity.loc[idx, "description_embedding"] = str(description_emb)

        # extracting keywords for the current row of entity
        keyword_extraction_prompt = keyword_extraction_prompt_template.format(description=description,
                                                                              code=definition)
        llm_response = get_together_chat_response(prompt=keyword_extraction_prompt,
                                                  together_llm_client=together_llm_client,
                                                  together_llm_model_name=together_llm_model_name)
        keywords = json.loads(llm_response)
        keywords = keywords['description_keywords']

        # embedding keywords
        keywords_columns = []
        keywords_embedding_columns = []
        for keyword_idx, keyword in enumerate(keywords):
            keyword_emb = get_together_embedding(text=keyword,
                                                 together_embedding_client=together_embedding_client,
                                                 together_model_name=together_embedding_model_name,
                                                 normalize_embedding=True)

            entity.loc[idx, f"keyword_{keyword_idx}"] = keyword
            entity.loc[idx, f"keyword_{keyword_idx}_embedding"] = str(keyword_emb)
            keywords_columns.append(f"keyword_{keyword_idx}")
            keywords_embedding_columns.append(f"keyword_{keyword_idx}_embedding")

        # reordering columns of entity
        entity = entity[
            ['id', 'function_name', 'namespace', 'definition', 'description'] +
            keywords_columns +
            ["definition_embedding", "function_name_embedding", "description_embedding"] +
            keywords_embedding_columns
        ]
    return entity, relationship


def main():
    # configurations
    load_dotenv()
    together_api_key = os.getenv('TOGETHER_API_KEY')
    together_llm_client = Together(api_key=together_api_key)
    together_embedding_client = OpenAI(api_key=together_api_key, base_url="https://api.together.xyz/v1")
    together_llm_model_name = "meta-llama/Llama-3-70b-chat-hf"
    together_embedding_model_name = "togethercomputer/m2-bert-80M-32k-retrieval"

    # reading prompt templates
    config = configparser.ConfigParser()
    config.read(os.path.join(ROOT_PROJECT_PATH, 'src', 'lattice', 'retrieve', 'prompt.ini'))
    keyword_extraction_prompt_template = config['prompts']['keyword_extraction']
    description_extraction_prompt_template = config['prompts']['description_extraction']

    # reading raw data and creating dataframes
    entity = pd.DataFrame.from_dict(data=ENTITY)
    relationship = pd.DataFrame.from_dict(data=RELATIONSHIP)

    # indexing the entity and relationship dataframes
    entity, relationship = index(entity=entity,
                                 relationship=relationship,
                                 description_extraction_prompt_template=description_extraction_prompt_template,
                                 keyword_extraction_prompt_template=keyword_extraction_prompt_template,
                                 together_llm_client=together_llm_client,
                                 together_llm_model_name=together_llm_model_name,
                                 together_embedding_client=together_embedding_client,
                                 together_embedding_model_name=together_embedding_model_name)

    # saving processed dataframes
    entity.to_csv("entity.csv", index=False)
    relationship.to_csv("relationship.csv", index=False)


if __name__ == "__main__":
    main()
