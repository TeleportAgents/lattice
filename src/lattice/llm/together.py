from typing import List

import numpy as np
from together import Together
from openai import OpenAI

from src.lattice.retrieve.utils import normalize_embeddings


def get_together_chat_response(
        prompt: str,
        together_llm_client: Together,
        together_llm_model_name: str
) -> str:
    response = together_llm_client.chat.completions.create(
        model=together_llm_model_name,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
    llm_response = response.choices[0].message.content
    return llm_response


def get_together_embedding(
        text: str,
        together_embedding_client: OpenAI,
        together_model_name: str,
        normalize_embedding: bool = False
) -> List[float]:
    text = text.replace("\n", " ")
    emb = together_embedding_client.embeddings.create(input=[text],
                                                      model=together_model_name).data[0].embedding
    if normalize_embedding:
        emb = np.array(emb)
        emb = np.expand_dims(emb, axis=0)
        emb = normalize_embeddings(x=emb)
        emb = emb.reshape(-1, ).tolist()
    return emb
