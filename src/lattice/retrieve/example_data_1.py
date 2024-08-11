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
