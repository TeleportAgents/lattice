from typing import List, Tuple


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
