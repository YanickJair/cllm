from src.utils.vocabulary import BaseVocabulary
from .en.vocabulary import ENVocabulary
from .es.vocabulary import ESVocabulary
from .pt.vocabulary import PTVocabulary
from .fr.vocabulary import FRVocabulary

vocab_map: dict[str, BaseVocabulary] = {
    "en": ENVocabulary(),
    "es": ESVocabulary(),
    "pt": PTVocabulary(),
    "fr": FRVocabulary()
}

__all__ = [
    "vocab_map"
]
