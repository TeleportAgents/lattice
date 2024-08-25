import uuid
import click
import configparser
import os
import logging
import json
from together import Together
from openai import OpenAI
from dotenv import load_dotenv
from src.lattice.compiler.digest import iterate_over_functions_project
from src.lattice.indexer.local import index_project
from src.lattice.logger import logger
from src.lattice.retrieve import get_db_data, retrieve
from paths import ROOT_PROJECT_PATH

@click.group()
def lattice():
    """Lattice CLI tool."""
    pass

@click.command(name='search')
@click.argument('path', required=True, type=click.Path(exists=True))
@click.argument('query', required=True)
@click.option('--verbose', is_flag=True, help='Print info.')
def search(path, query, verbose):
    """Search for code using human language queries."""
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    clients = get_ai_clients()

    together_llm_client = clients['llm']['client']
    together_embedding_client = clients['embedding']['client']
    together_llm_model_name = clients['llm']['model']
    together_embedding_model_name = clients['embedding']['model']

    entity_path = os.path.join(path, ".lattice", "entity.csv")
    relationship_path = os.path.join(path, ".lattice", "relationship.csv")

    entity, _ = get_db_data(entity_path)

    # reading prompt templates
    config = configparser.ConfigParser()
    config.read(os.path.join(ROOT_PROJECT_PATH, 'src', 'lattice', 'config', 'prompt.ini'))
    keyword_extraction_prompt_template = config['prompts']['keyword_extraction']

    num_keywords = 10
    result = retrieve(
        entity=entity,
        query=query,
        num_keywords=num_keywords,
        keyword_extraction_prompt_template=keyword_extraction_prompt_template,
        together_llm_client=together_llm_client,
        together_llm_model_name=together_llm_model_name,
        together_embedding_client=together_embedding_client,
        together_embedding_model_name=together_embedding_model_name,
        score_type="normalized_l2_score"
    )

    click.echo(json.dumps(result, indent=4))
    

def read_prompt(config_path):
    # reading prompt templates
    config = configparser.ConfigParser()
    config.read(os.path.join(config_path,'prompt.ini'))
    return {
        "keyword": config['prompts']['keyword_extraction'],
        "description":config['prompts']['description_extraction']
    }

def read_config(config_path):
    config = configparser.ConfigParser()
    config.read(os.path.join(config_path, 'config.ini'))
    return {
        "db_url": config['database']['url']
    }

    
def get_ai_clients():
    together_api_key = os.getenv('TOGETHER_API_KEY')
    return {
        "llm":{
            "client":Together(api_key=together_api_key),
            "model":"meta-llama/Llama-3-70b-chat-hf"
        },
        "embedding":{
            "client":OpenAI(api_key=together_api_key, base_url="https://api.together.xyz/v1"),
            "model":"togethercomputer/m2-bert-80M-32k-retrieval"
        }
    }



@click.command(name='index')
@click.argument('path', required=True, type=click.Path(exists=True))
@click.option('--exclude', required=False, help='Exclude Path from the project directory.')
@click.option('--verbose', is_flag=True, help='Print info.')
def index(path, exclude, verbose):
    """Index a project."""
    if exclude is None:
        exclude = [".venv", ".env", "venv", "env"]

    if verbose:
        logger.setLevel(logging.DEBUG)

    # call compiler
    compiler_iter = iterate_over_functions_project(path, exclude=exclude)
    clients = get_ai_clients()
    
    index_project(compiler_iter, path, clients)


# Add the index command to the lattice group
lattice.add_command(index)
lattice.add_command(search)


if __name__ == '__main__':
    load_dotenv()
    lattice()