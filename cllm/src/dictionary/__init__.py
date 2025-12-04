from src.utils.vocabulary import BaseVocabulary
from .en.vocabulary import ENVocabulary
from .en.rules import ENRules
from .es.vocabulary import ESVocabulary
from .es.rules import ESRules
from .pt.vocabulary import PTVocabulary
from .pt.rules import PTRules
from .fr.vocabulary import FRVocabulary
from .fr.rules import FRRules
from src.utils.parser_rules import BaseRules

vocab_map: dict[str, BaseVocabulary] = {
    "en": ENVocabulary(),
    "es": ESVocabulary(),
    "pt": PTVocabulary(),
    "fr": FRVocabulary(),
}

rules_map: dict[str, BaseRules] = {
    "en": ENRules(),
    # "es": ESRules(),
    # "pt": PTRules(),
    # "fr": FRRules()
}

__all__ = ["vocab_map", "rules_map"]
