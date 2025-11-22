import dictionary
from utils.vocabulary import BaseVocabulary


class Vocabulary(object):
    """
    Vocabulary class for managing a collection of words and their frequencies.

    Attributes:
        words (dict): A dictionary mapping words to their frequencies.
    """
    def __init__(self, lang: str) -> None:
        """
        Initialize the Vocabulary object with a language.
        Right now it supports English, Spanish, Portuguese, and French.

        :param lang: The language of the vocabulary.
        """
        self._vocab: BaseVocabulary = dictionary.vocab_map[lang]()
