import os
import ast
from typing import Tuple, Union

from dotenv import load_dotenv
import numpy as np
import pandas as pd
from together import Together
from openai import OpenAI

from src.lattice.llm.together import get_together_chat_response, get_together_embedding
from paths import ROOT_PROJECT_PATH


def get_db_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    entity_path = os.path.join(ROOT_PROJECT_PATH, "src", "lattice", "retrieve", "entity.csv")
    relationship_path = os.path.join(ROOT_PROJECT_PATH, "src", "lattice", "retrieve", "relationship.csv")
    entity = pd.read_csv(entity_path)
    relationship = pd.read_csv(relationship_path)
    return entity, relationship


def normalize_embeddings(x: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    normalized_embeddings = x / norms
    return normalized_embeddings


def retrieve(
        query: str,
        llm_client: Union[Together],
        together_llm_model_name: str,
        embedding_client: Union[OpenAI],
        together_embedding_model_name: str,
        score_type: str = "normalized_inner_product_score",

):
    assert score_type in ["normalized_inner_product_score", "normalized_l2_score"], \
        "The argument score_type must be either 'normalized_inner_product_score' or 'normalized_l2_score'."

    # loading data
    entity, relationship = get_db_data()

    # processing the embeddings
    function_name_embeddings = np.stack(entity["function_name_embedding"].apply(ast.literal_eval))
    function_name_embeddings = normalize_embeddings(x=function_name_embeddings)
    definition_embeddings = np.stack(entity["definition_embedding"].apply(ast.literal_eval))
    definition_embeddings = normalize_embeddings(x=definition_embeddings)
    description_embeddings = np.stack(entity["description_embedding"].apply(ast.literal_eval))
    description_embeddings = normalize_embeddings(x=description_embeddings)

    # preparing the query
    info_extraction_prompt_1 = f"""
    You are knowledgeable in retrieving Python function based on natural language queries of user.
    I will give you the users query. I will also give you function names and their description. 
    Tell which 2 functions are most relevant or similar to user's query.
    
    QUERY:
    {query}
    
    FUNCTIONS NAME:
    {entity["function_name"].values.tolist()}
    
    FUNCTION DESCRIPTIONS:
    {entity["description"].values.tolist()}
    """
    num_keywords = 20
    info_extraction_prompt_2 = f"""
    You are knowledgeable in retrieving Python function based on natural language queries of user.
    I will give you the users query. 
    I want you to grasp the query entirely, and output {num_keywords} keywords that reflect the essence of the query.
    These {num_keywords} keywords can be keywords in the query, or synonyms of the key concepts in the query.
    I want to embed these {num_keywords} keywords and use the embeddings to compute similarities in a RAG system.
    Output the {num_keywords} keywords in a Python list.
    DO NOT OUTPUT EXTRA EXPLANATIONS OTHER THAN THE PYTHON LIST.
    
    QUERY:
    {query}
    
    PYTHON LIST:
    """
    response = get_together_chat_response(prompt=info_extraction_prompt_2,
                                          together_llm_client=llm_client,
                                          together_llm_model_name=together_llm_model_name)
    query_keywords = ast.literal_eval(response)
    query_keywords_embeddings = []
    for keyword in query_keywords:
        keyword_embedding = get_together_embedding(text=keyword,
                                                   together_embedding_client=embedding_client,
                                                   together_model_name=together_embedding_model_name)
        keyword_embedding = np.expand_dims(np.array(keyword_embedding), axis=0)
        keyword_embedding = normalize_embeddings(x=keyword_embedding)
        query_keywords_embeddings.append(keyword_embedding.squeeze().tolist())
    query_keywords_embeddings = np.array(query_keywords_embeddings)

    keywords_results = entity.copy()
    score_cols = []
    for keyword_idx in range(len(query_keywords)):
        emb = query_keywords_embeddings[keyword_idx, :]
        if score_type == 'normalized_inner_product_score':
            function_name_scores = (function_name_embeddings @ emb.T).squeeze()
            definition_scores = (definition_embeddings @ emb.T).squeeze()
            description_scores = (description_embeddings @ emb.T).squeeze()
        elif score_type == 'normalized_l2_score':
            function_name_scores = 2 - np.linalg.norm(function_name_embeddings - emb, axis=1)
            definition_scores = 2 - np.linalg.norm(definition_embeddings - emb, axis=1)
            description_scores = 2 - np.linalg.norm(description_embeddings - emb, axis=1)
        else:
            raise ValueError
        keywords_results[f"function_name_scores@{query_keywords[keyword_idx]}"] = function_name_scores
        keywords_results[f"definition_scores@{query_keywords[keyword_idx]}"] = definition_scores
        keywords_results[f"description_scores@{query_keywords[keyword_idx]}"] = description_scores
        score_cols.append(f"function_name_scores@{query_keywords[keyword_idx]}")
        score_cols.append(f"definition_scores@{query_keywords[keyword_idx]}")
        score_cols.append(f"description_scores@{query_keywords[keyword_idx]}")

    pass

    # processing the query
    # embedding the query
    query_embedding = get_together_embedding(text=query,
                                             together_embedding_client=embedding_client,
                                             together_model_name=together_embedding_model_name)
    query_embedding = np.expand_dims(np.array(query_embedding), axis=0)
    query_embedding = normalize_embeddings(x=query_embedding)

    if score_type == 'normalized_inner_product_score':
        function_name_scores = (function_name_embeddings @ query_embedding.T).squeeze()
        definition_scores = (definition_embeddings @ query_embedding.T).squeeze()
        description_scores = (description_embeddings @ query_embedding.T).squeeze()
    elif score_type == 'normalized_l2_score':
        function_name_scores = 2 - np.linalg.norm(function_name_embeddings - query_embedding, axis=1)
        definition_scores = 2 - np.linalg.norm(definition_embeddings - query_embedding, axis=1)
        description_scores = 2 - np.linalg.norm(description_embeddings - query_embedding, axis=1)
    else:
        raise ValueError

    results = entity.copy()
    results["function_name_scores"] = function_name_scores
    results["definition_scores"] = definition_scores
    results["description_scores"] = description_scores
    pass


def main():
    load_dotenv()
    together_api_key = os.getenv('TOGETHER_API_KEY')
    together_llm_client = Together(api_key=together_api_key)
    embedding_client = OpenAI(api_key=together_api_key, base_url="https://api.together.xyz/v1")
    together_llm_model_name = "meta-llama/Llama-3-70b-chat-hf"
    together_embedding_model_name = "togethercomputer/m2-bert-80M-32k-retrieval"

    query = "I want a function that visualizes a histogram."
    retrieve(query=query,
             llm_client=together_llm_client,
             together_llm_model_name=together_llm_model_name,
             embedding_client=embedding_client,
             together_embedding_model_name=together_embedding_model_name,
             score_type="normalized_l2_score")
    pass


if __name__ == "__main__":
    main()
