from spacy.matcher import Matcher
from spacy.language import Language
from .constants import TURN_PATTERNS
from clm_core.types import TurnType


class TurnClassifier:
    def __init__(self, nlp: Language) -> None:
        self._nlp = nlp
        turns = TURN_PATTERNS.get(nlp.lang or "en", {})
        self._matcher = Matcher(nlp.vocab)
        for turn, patterns in turns.items():
            self._matcher.add(turn, patterns)

    def classify(self, text: str) -> tuple[TurnType, float]:
        """
        Classify a turn/phrase and return a type and a confidence.
        If it was not able to classify, returns NEUTRAL with 0% confidence ratio
        """
        if len(text) < 10:
            return TurnType.NEUTRAL, 0.0

        doc = self._nlp(text)
        matches = self._matcher(doc)

        if not matches:
            return TurnType.NEUTRAL, 0.0

        best = max(matches, key=lambda m: m[2] - m[1])
        matched_id, start, end = best
        coverage = (end - start) / len(doc)
        turn_type = TurnType(self._nlp.vocab.strings[matched_id])

        return turn_type, round(coverage, 2)
