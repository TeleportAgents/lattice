from typing import List, Tuple

from example_child import extract_words
from example_child.example_deep_script import categorize_words


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
