from spacy import Language
from src.core.vocabulary import Vocabulary


class BaseAnalyzer:
    def __init__(self, nlp: Language) -> None:
        self.nlp = nlp
        self.vocab = Vocabulary()