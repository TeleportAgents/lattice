"""
Customer Feedback Analysis and Visualization Tool

This Python script analyzes customer feedback data consisting of text reviews and numerical ratings.
The goal is to extract meaningful insights about customer satisfaction and sentiment.

Modules and Functions:
1. `main()`: The entry point of the application. It handles sample data, calls analysis functions,
   prints results, and displays visualizations.

2. Text Reviews Analysis:
   - `analyze_text_reviews(texts: List[str]) -> Tuple[List[str], List[str]]`: Analyzes the text reviews to extract and
     categorize words into positive and negative categories.
   - `extract_words(texts: List[str]) -> List[str]`: Extracts words from the reviews, converting them to lowercase.
   - `categorize_words(words: List[str]) -> Tuple[List[str], List[str]]`: Categorizes words into positive and negative
     lists based on predefined dictionaries.

3. Numerical Ratings Analysis:
   - `analyze_numerical_ratings(ratings: List[int]) -> Tuple[float, Dict[str, int]]`: Analyzes numerical ratings to
     compute the average and categorize the ratings into bins.
   - `calculate_average(ratings: List[int]) -> float`: Calculates the average of the numerical ratings.
   - `rating_distribution(ratings: List[int]) -> Dict[str, int]`: Determines the distribution of ratings across
     specified bins.

4. Visualization:
   - `visualize_word_counts(positive: List[str], negative: List[str]) -> plt.Figure`: Creates a bar chart visualizing
     the count of positive and negative words.
   - `visualize_rating_distribution(distribution: Dict[str, int]) -> plt.Figure`: Creates a normalized histogram
     of the rating distribution.

Usage:
- Run the script to analyze sample text reviews and ratings, print the results, and display visualizations.

Dependencies:
- Requires the `matplotlib` library for plotting.

"""

from typing import List, Dict, Tuple
import matplotlib.pyplot as plt


def analyze_text_reviews(texts: List[str]) -> Tuple[List[str], List[str]]:
    """
    Analyze the text reviews to extract and categorize words.

    Parameters
    ----------
    texts : List[str]
        A list of customer text reviews.

    Returns
    -------
    Tuple[List[str], List[str]]
        A tuple containing two lists: positive and negative words.
    """
    words = extract_words(texts)
    positive, negative = categorize_words(words)
    return positive, negative


def extract_words(texts: List[str]) -> List[str]:
    """
    Extract words from a list of text reviews.

    Parameters
    ----------
    texts : List[str]
        A list of customer text reviews.

    Returns
    -------
    List[str]
        A list of extracted words in lowercase.
    """
    words = []
    for text in texts:
        words.extend(text.lower().split())
    return words


def categorize_words(words: List[str]) -> Tuple[List[str], List[str]]:
    """
    Categorize words into positive and negative categories.

    Parameters
    ----------
    words : List[str]
        A list of words to categorize.

    Returns
    -------
    Tuple[List[str], List[str]]
        Two lists containing positive and negative words.
    """
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


def analyze_numerical_ratings(ratings: List[int]) -> Tuple[float, Dict[str, int]]:
    """
    Analyze the numerical ratings to compute average and distribution.

    Parameters
    ----------
    ratings : List[int]
        A list of numerical ratings.

    Returns
    -------
    Tuple[float, Dict[str, int]]
        The average rating and a dictionary with the rating distribution.
    """
    average = calculate_average(ratings)
    distribution = rating_distribution(ratings)
    return average, distribution


def calculate_average(ratings: List[int]) -> float:
    """
    Calculate the average of the ratings.

    Parameters
    ----------
    ratings : List[int]
        A list of numerical ratings.

    Returns
    -------
    float
        The average rating.
    """
    return sum(ratings) / len(ratings)


def rating_distribution(ratings: List[int]) -> Dict[str, int]:
    """
    Determine the distribution of ratings in defined bins.

    Parameters
    ----------
    ratings : List[int]
        A list of numerical ratings.

    Returns
    -------
    Dict[str, int]
        A dictionary with the count of ratings in each bin.
    """
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


def visualize_word_counts(positive: List[str], negative: List[str]) -> plt.Figure:
    """
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
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(['Positive', 'Negative'], [len(positive), len(negative)], color=['green', 'red'])
    ax.set_title('Count of Positive and Negative Words')
    ax.set_ylabel('Count')
    plt.tight_layout()
    return fig


def visualize_rating_distribution(distribution: Dict[str, int]) -> plt.Figure:
    """
    Visualize the normalized histogram of rating distribution.

    Parameters
    ----------
    distribution : Dict[str, int]
        Dictionary with the rating distribution.

    Returns
    -------
    plt.Figure
        The matplotlib figure object with the visualization.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    total_ratings = sum(distribution.values())
    normalized_distribution = {key: value / total_ratings for key, value in distribution.items()}
    ax.bar(normalized_distribution.keys(), normalized_distribution.values(), color='blue')
    ax.set_title('Normalized Rating Distribution')
    ax.set_ylabel('Proportion')
    plt.tight_layout()
    return fig


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


if __name__ == "__main__":
    main()
