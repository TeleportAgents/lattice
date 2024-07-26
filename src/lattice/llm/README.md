
# Together and OpenAI Integration Functions

This repository provides two Python functions for interacting with the Together API to obtain chat responses and text embeddings using their language models. Follow the instructions below to set up and use these functions.

## Prerequisites

- **API Keys**: A valid API key for the Together platform is required.
- **Python Environment**: Ensure you have Python installed along with the required libraries.

## Installation

Install the necessary packages using pip:

```bash
pip install together openai python-dotenv
```

## Setup

### Environment Variables

Create a `.env` file in the root directory of your project to store your Together API key:

```plaintext
TOGETHER_API_KEY=<your together api key>
```

Load the environment variables in your script:

```python
import os
from dotenv import load_dotenv

load_dotenv()
together_api_key = os.getenv('TOGETHER_API_KEY')
```

## Usage

### 1. Get Together Chat Response

Fetch a response from a language model using a prompt.

#### Function

```python
from together import Together

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
```

#### Example

```python
together_llm_client = Together(api_key=together_api_key)
together_llm_model_name = "meta-llama/Llama-3-70b-chat-hf"
prompt = "Hello! How can I assist you today?"

response = get_together_chat_response(prompt, together_llm_client, together_llm_model_name)
print(response)
```

### 2. Get Together Embedding

Generate text embeddings using Together's models.

#### Function

```python
from openai import OpenAI
from typing import List

def get_together_embedding(text: str,
                           together_embedding_client: OpenAI,
                           together_model_name: str) -> List[float]:
    text = text.replace("
", " ")
    return together_embedding_client.embeddings.create(input=[text],
                                                       model=together_model_name).data[0].embedding
```

#### Example

```python
embedding_client = OpenAI(api_key=together_api_key, base_url="https://api.together.xyz/v1")
together_embedding_model_name = "togethercomputer/m2-bert-80M-32k-retrieval"
text = "Example text for embedding."

embedding = get_together_embedding(text, embedding_client, together_embedding_model_name)
print(embedding)
```

## Conclusion

This repository provides a simple interface for integrating with Together's API for language models and embeddings. Make sure to replace placeholder API keys and model names with your own. For more detailed options and configurations, refer to the official documentation of the Together and OpenAI libraries.
