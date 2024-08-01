import os
import json

import pandas as pd
from dotenv import load_dotenv
from together import Together
from openai import OpenAI

from src.lattice.llm.together import get_together_chat_response, get_together_embedding

ENTITY = {
    "id": [
        "87385df0-d775-4400-a07e-fdf811903c1b",
        "6e7750e7-e87f-4e87-93df-c5e33ac7b7a1",
        "1d4acc99-a798-49aa-8ea0-2820af559f4c",
        "878b9f17-ddf1-495a-bffc-28b039460460",
        "71166b7b-1443-4dd7-a1bc-8139c23aa44c",
        "89af578c-f0fa-4600-bb21-b862e127132a",
        "ab9b9d3f-4f2f-4501-854b-827d0ca93365",
        "f9019878-be11-4772-a83d-68b0db6223cc",
        "064d179b-4940-4c11-acfc-3afff005591d"
    ],
    "function_name": [
        "main",
        "analyze_text_reviews",
        "extract_words",
        "categorize_words",
        "analyze_numerical_ratings",
        "calculate_average",
        "rating_distribution",
        "visualize_word_counts",
        "visualize_rating_distribution"
    ],
    "namespace": [
        "src.lattice.retrieve.example_scenario_1",
        "src.lattice.retrieve.example_scenario_1",
        "src.lattice.retrieve.example_scenario_1",
        "src.lattice.retrieve.example_scenario_1",
        "src.lattice.retrieve.example_scenario_1",
        "src.lattice.retrieve.example_scenario_1",
        "src.lattice.retrieve.example_scenario_1",
        "src.lattice.retrieve.example_scenario_1",
        "src.lattice.retrieve.example_scenario_1",
    ],
    "definition": [
        """
        def main():
            # Sample data
            text_reviews = [
                "The product is fantastic and works great!",
                "Terrible experience, it broke in two days.",
                "Excellent service and wonderful quality.",
                "Not worth the price, very disappointed."
            ]
        
            ratings = [5, 1, 4, 2, 3, 5, 4, 1]
        
            # Analyze text reviews
            positive, negative = analyze_text_reviews(text_reviews)
        
            # Analyze numerical ratings
            average, distribution = analyze_numerical_ratings(ratings)
        
            # Print the results
            print("Positive words:", positive)
            print("Negative words:", negative)
            print(f"Average rating: {average:.2f}")
            print("Rating distribution:", distribution)
        
            # Visualize the results
            fig1 = visualize_word_counts(positive, negative)
            fig2 = visualize_rating_distribution(distribution)
            plt.show()
        """,
        """
        def analyze_text_reviews(texts: List[str]) -> Tuple[List[str], List[str]]:
            \"\"\"
            Analyze the text reviews to extract and categorize words.
        
            Parameters
            ----------
            texts : List[str]
                A list of customer text reviews.
        
            Returns
            -------
            Tuple[List[str], List[str]]
                A tuple containing two lists: positive and negative words.
            \"\"\"
            words = extract_words(texts)
            positive, negative = categorize_words(words)
            return positive, negative
        """,
        """
        def extract_words(texts: List[str]) -> List[str]:
            \"\"\"
            Extract words from a list of text reviews.
        
            Parameters
            ----------
            texts : List[str]
                A list of customer text reviews.
        
            Returns
            -------
            List[str]
                A list of extracted words in lowercase.
            \"\"\"
            words = []
            for text in texts:
                words.extend(text.lower().split())
            return words
        """,
        """
        def categorize_words(words: List[str]) -> Tuple[List[str], List[str]]:
            \"\"\"
            Categorize words into positive and negative categories.
        
            Parameters
            ----------
            words : List[str]
                A list of words to categorize.
        
            Returns
            -------
            Tuple[List[str], List[str]]
                Two lists containing positive and negative words.
            \"\"\"
            # Sample positive and negative word lists
            positive_words = {"fantastic", "great", "excellent", "wonderful"}
            negative_words = {"terrible", "broke", "disappointed"}
        
            positive = []
            negative = []
        
            for word in words:
                if word in positive_words:
                    positive.append(word)
                elif word in negative_words:
                    negative.append(word)
        
            return positive, negative
        """,
        """
        def analyze_numerical_ratings(ratings: List[int]) -> Tuple[float, Dict[str, int]]:
            \"\"\"
            Analyze the numerical ratings to compute average and distribution.
        
            Parameters
            ----------
            ratings : List[int]
                A list of numerical ratings.
        
            Returns
            -------
            Tuple[float, Dict[str, int]]
                The average rating and a dictionary with the rating distribution.
            \"\"\"
            average = calculate_average(ratings)
            distribution = rating_distribution(ratings)
            return average, distribution
        """,
        """
        def calculate_average(ratings: List[int]) -> float:
            \"\"\"
            Calculate the average of the ratings.
        
            Parameters
            ----------
            ratings : List[int]
                A list of numerical ratings.
        
            Returns
            -------
            float
                The average rating.
            \"\"\"
            return sum(ratings) / len(ratings)
        """,
        """
        def rating_distribution(ratings: List[int]) -> Dict[str, int]:
            \"\"\"
            Determine the distribution of ratings in defined bins.
        
            Parameters
            ----------
            ratings : List[int]
                A list of numerical ratings.
        
            Returns
            -------
            Dict[str, int]
                A dictionary with the count of ratings in each bin.
            \"\"\"
            distribution = {
                '1-2': 0,
                '3-4': 0,
                '5': 0
            }
            for rating in ratings:
                if 1 <= rating <= 2:
                    distribution['1-2'] += 1
                elif 3 <= rating <= 4:
                    distribution['3-4'] += 1
                elif rating == 5:
                    distribution['5'] += 1
            return distribution
        """,
        """
        def visualize_word_counts(positive: List[str], negative: List[str]) -> plt.Figure:
            \"\"\"
            Visualize the count of positive and negative words.
        
            Parameters
            ----------
            positive : List[str]
                List of positive words.
            negative : List[str]
                List of negative words.
        
            Returns
            -------
            plt.Figure
                The matplotlib figure object with the visualization.
            \"\"\"
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(['Positive', 'Negative'], [len(positive), len(negative)], color=['green', 'red'])
            ax.set_title('Count of Positive and Negative Words')
            ax.set_ylabel('Count')
            plt.tight_layout()
            return fig
        """,
        """
        def visualize_rating_distribution(distribution: Dict[str, int]) -> plt.Figure:
            \"\"\"
            Visualize the normalized histogram of rating distribution.
        
            Parameters
            ----------
            distribution : Dict[str, int]
                Dictionary with the rating distribution.
        
            Returns
            -------
            plt.Figure
                The matplotlib figure object with the visualization.
            \"\"\"
            fig, ax = plt.subplots(figsize=(6, 4))
            total_ratings = sum(distribution.values())
            normalized_distribution = {key: value / total_ratings for key, value in distribution.items()}
            ax.bar(normalized_distribution.keys(), normalized_distribution.values(), color='blue')
            ax.set_title('Normalized Rating Distribution')
            ax.set_ylabel('Proportion')
            plt.tight_layout()
            return fig
        """
    ]
}
RELATIONSHIP = {
    "id": [
        "669e8e19-ff87-4d1f-8623-bb8d43bd5544",
        "9d66576c-1dc7-4a88-9cc6-92b462bc1825",
        "bb93ff74-32a5-4b76-af78-efb869a2e723",
        "b5800ca1-f089-4b0e-b0db-59fda6a5ee9a",
        "facdebf8-c48d-4dcb-b18d-2f9363091cd6",
        "f9e0dec1-7f98-49a8-bcf8-e6d1118d1ebd",
        "3817de3b-3eba-4aa3-a62b-061b746558c5"

    ],
    "source_id": [
        "87385df0-d775-4400-a07e-fdf811903c1b",
        "6e7750e7-e87f-4e87-93df-c5e33ac7b7a1",
        "87385df0-d775-4400-a07e-fdf811903c1b",
        "71166b7b-1443-4dd7-a1bc-8139c23aa44c",
        "71166b7b-1443-4dd7-a1bc-8139c23aa44c",
        "87385df0-d775-4400-a07e-fdf811903c1b",
        "87385df0-d775-4400-a07e-fdf811903c1b"
    ],
    "target_id": [
        "6e7750e7-e87f-4e87-93df-c5e33ac7b7a1",
        "1d4acc99-a798-49aa-8ea0-2820af559f4c",
        "71166b7b-1443-4dd7-a1bc-8139c23aa44c",
        "89af578c-f0fa-4600-bb21-b862e127132a",
        "ab9b9d3f-4f2f-4501-854b-827d0ca93365",
        "f9019878-be11-4772-a83d-68b0db6223cc",
        "064d179b-4940-4c11-acfc-3afff005591d"
    ],
    "line_number": [
        237,
        57,
        240,
        126,
        127,
        249,
        250
    ],
    "arguments": [
        "texts: List[str]",
        "texts: List[str]",
        "ratings: List[int]",
        "ratings: List[int]",
        "ratings: List[int]",
        "positive: List[str], negative: List[str]",
        "distribution: Dict[str, int]"
    ],
    "returns": [
        "Tuple[List[str], List[str]]",
        "List[str]",
        "Tuple[float, Dict[str, int]]",
        "float",
        "Dict[str, int]",
        "plt.Figure",
        "plt.Figure"
    ]
}


def main():
    load_dotenv()
    together_api_key = os.getenv('TOGETHER_API_KEY')
    together_llm_client = Together(api_key=together_api_key)
    embedding_client = OpenAI(api_key=together_api_key, base_url="https://api.together.xyz/v1")
    together_llm_model_name = "meta-llama/Llama-3-70b-chat-hf"
    together_embedding_model_name = "togethercomputer/m2-bert-80M-32k-retrieval"

    entity = pd.DataFrame.from_dict(data=ENTITY)
    relationship = pd.DataFrame.from_dict(data=RELATIONSHIP)

    for idx, row in entity.iterrows():
        function_name = row['function_name']
        definition = row['definition']

        prompt = f"""
        You are and expert software engineering having deep knowledge about all parts of software development.
        I want you to read this code and give a thorough explanation of what it does.
        I want to use these explanations to index the code in a RAG system to retrieve this code if user asks anything that might 
        be solved with this piece of code. 
        Please provide your answer in a Python Dict format like below:
        {{
            "description": <THOROUGH EXPLANATION OF THE CODE THAT IS USED IN A RAG SYSTEM>
        }}
        I don't want any further explanation. ONLY RETURN THE PYTHON DICT ANSWER.
        CODE:
        {definition}
        """
        llm_response = get_together_chat_response(prompt=prompt,
                                                  together_llm_client=together_llm_client,
                                                  together_llm_model_name=together_llm_model_name)
        description = json.loads(llm_response)['description']

        # embed definition
        definition_emb = get_together_embedding(text=definition,
                                                together_embedding_client=embedding_client,
                                                together_model_name=together_embedding_model_name)

        # embed description
        description_emb = get_together_embedding(text=description,
                                                 together_embedding_client=embedding_client,
                                                 together_model_name=together_embedding_model_name)
        # embed function_name
        function_name_emb = get_together_embedding(text=function_name,
                                                   together_embedding_client=embedding_client,
                                                   together_model_name=together_embedding_model_name)

        entity.loc[idx, "description"] = description
        entity.loc[idx, "definition_embedding"] = str(definition_emb)
        entity.loc[idx, "function_name_embedding"] = str(function_name_emb)
        entity.loc[idx, "description_embedding"] = str(description_emb)

    entity.to_csv("entity.csv", index=False)
    relationship.to_csv("relationship.csv", index=False)


if __name__ == "__main__":
    main()
