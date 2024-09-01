import os
import ast
import hashlib
import configparser
import json
from typing import Tuple, Dict, Union

from dotenv import load_dotenv
import numpy as np
import pandas as pd
from together import Together
from openai import OpenAI
from rank_bm25 import BM25Okapi

from ..llm.together import get_together_chat_response, get_together_embedding


def get_db_data(
    entity_path: str, relationship_path=None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    entity = pd.read_csv(entity_path)
    if relationship_path:
        relationship = pd.read_csv(relationship_path)
    else:
        relationship = None
    return entity, relationship


def get_entity_embeddings(entity: pd.DataFrame, num_keywords: int) -> np.ndarray:
    # loading function_name embeddings
    function_name_embeddings = np.stack(
        entity["function_name_embedding"].apply(ast.literal_eval)
    )
    function_name_embeddings = np.expand_dims(function_name_embeddings, axis=1)

    # loading definition embeddings
    definition_embeddings = np.stack(
        entity["definition_embedding"].apply(ast.literal_eval)
    )
    definition_embeddings = np.expand_dims(definition_embeddings, axis=1)

    # loading description embeddings
    description_embeddings = np.stack(
        entity["description_embedding"].apply(ast.literal_eval)
    )
    description_embeddings = np.expand_dims(description_embeddings, axis=1)

    # loading keyword embeddings
    keyword_embeddings = []
    for idx in range(num_keywords):
        keyword_idx_embeddings = np.stack(
            entity[f"keyword_{idx}_embedding"].apply(ast.literal_eval)
        )
        keyword_idx_embeddings = np.expand_dims(keyword_idx_embeddings, axis=1)
        keyword_embeddings.append(keyword_idx_embeddings)
    keyword_embeddings = np.concat(keyword_embeddings, axis=1)

    # packing all embeddings together
    entity_embeddings = np.concat(
        [
            function_name_embeddings,
            definition_embeddings,
            description_embeddings,
            keyword_embeddings,
        ],
        axis=1,
    )
    return entity_embeddings


def bm25_search(query: str, entity: pd.DataFrame) -> np.ndarray:
    documents = (entity["description"] + "\n" + entity["definition"]).tolist()

    # Convert the document-term matrix to a list of lists (sparse matrix to dense)
    tokenized_docs = [doc.split() for doc in documents]

    # Tokenize the query in the same way
    tokenized_query = query.split()

    # Initialize BM25 with the tokenized documents
    bm25 = BM25Okapi(tokenized_docs)

    # Get the BM25 scores for the query against all documents
    scores = bm25.get_scores(tokenized_query)
    return scores


def retrieve(
    entity: pd.DataFrame,
    query: str,
    num_keywords: int,
    keyword_extraction_prompt_template: str,
    together_llm_client: Union[Together],
    together_llm_model_name: str,
    together_embedding_client: Union[OpenAI],
    together_embedding_model_name: str,
    project_path: str,
    score_type: str = "normalized_inner_product_score",
) -> Dict:
    assert score_type in [
        "normalized_inner_product_score",
        "normalized_l2_score",
    ], "The argument score_type must be either 'normalized_inner_product_score' or 'normalized_l2_score'."

    # loading entity and relation data
    # entity, relationship = get_db_data()

    # Loading the embeddings of data
    entity_embeddings = get_entity_embeddings(entity=entity, num_keywords=num_keywords)

    # query processing
    query_hash_object = hashlib.md5(query.encode())
    query_hash = query_hash_object.hexdigest()
    query_path = os.path.join(project_path, ".lattice", f"query_{query_hash}.csv")
    if os.path.isfile(query_path):
        # loading query embeddings and keywords
        query_data = pd.read_csv(query_path)

    else:
        # extracting keywords of the query
        query_prompt = keyword_extraction_prompt_template.format(
            description=query, code=""
        )
        query_keywords = get_together_chat_response(
            prompt=query_prompt,
            together_llm_client=together_llm_client,
            together_llm_model_name=together_llm_model_name,
        )
        query_keywords = json.loads(query_keywords)
        query_keywords = query_keywords["description_keywords"]

        # embedding keywords of the query
        query_data = {"keyword": [], "embedding": []}
        for query_keyword_idx, query_keyword in enumerate(query_keywords):
            query_keyword_emb = get_together_embedding(
                text=query_keyword,
                together_embedding_client=together_embedding_client,
                together_model_name=together_embedding_model_name,
                normalize_embedding=True,
            )
            query_data["keyword"].append(query_keyword)
            query_data["embedding"].append(str(query_keyword_emb))
        query_data = pd.DataFrame.from_dict(data=query_data)
        query_data.to_csv(query_path, index=False)

    # loading query keyword embeddings
    query_embeddings = np.stack(query_data["embedding"].apply(ast.literal_eval))

    # computing the similarity score between entity embeddings and query embeddings
    emb_scores = entity_embeddings @ query_embeddings.T

    # ============== computing the retrieved entity ==============
    # flattening the score query scores for each entity
    emb_scores = emb_scores.reshape(emb_scores.shape[0], -1)
    # averaging the two highest scores for each entity
    emb_scores = np.sort(emb_scores, axis=1)[:, -2:].mean(1)

    # computing the BM25 search scores
    bm25_scores = bm25_search(query=query, entity=entity)

    # constructing score dataframe
    score = pd.DataFrame.from_dict(
        data={"embedding": emb_scores.tolist(), "bm25": bm25_scores}
    ).reset_index()

    # first getting the top-5 BM25 search scores, then return the top embedding scores among those top-5 scores
    result_idx = int(
        score.sort_values(by="bm25", ascending=False)
        .iloc[:9]
        .sort_values(by="embedding", ascending=False)
        .iloc[0]["index"]
    )
    result = entity.iloc[result_idx][
        ["id", "function_name", "description", "definition"]
    ].to_dict()
    return result


def main():
    # configurations
    load_dotenv()
    together_api_key = os.getenv("TOGETHER_API_KEY")
    together_llm_client = Together(api_key=together_api_key)
    together_embedding_client = OpenAI(
        api_key=together_api_key, base_url="https://api.together.xyz/v1"
    )
    together_llm_model_name = "meta-llama/Llama-3-70b-chat-hf"
    together_embedding_model_name = "togethercomputer/m2-bert-80M-32k-retrieval"

    entity_path = os.path.join(
        ROOT_PROJECT_PATH, "src", "lattice", "retrieve", "entity.csv"
    )
    relationship_path = os.path.join(
        ROOT_PROJECT_PATH, "src", "lattice", "retrieve", "relationship.csv"
    )

    entity, relationship = get_db_data(entity_path, relationship_path)

    # reading prompt templates
    config = configparser.ConfigParser()
    config.read(
        os.path.join(ROOT_PROJECT_PATH, "src", "lattice", "retrieve", "prompt.ini")
    )
    keyword_extraction_prompt_template = config["prompts"]["keyword_extraction"]

    # calling the retrieve function
    query = "I want a function that visualizes a histogram."
    num_keywords = 10
    result = retrieve(
        entity=entity,
        relationship=relationship,
        query=query,
        num_keywords=num_keywords,
        keyword_extraction_prompt_template=keyword_extraction_prompt_template,
        together_llm_client=together_llm_client,
        together_llm_model_name=together_llm_model_name,
        together_embedding_client=together_embedding_client,
        together_embedding_model_name=together_embedding_model_name,
        project_path="./",
        score_type="normalized_l2_score",
    )
    print("Input Query:")
    print(query)
    print("Result:")
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    from paths import ROOT_PROJECT_PATH
    main()
