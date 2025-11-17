from .extractors import (
    ImperativeExtractor,
    QuestionExtractor,
    NounExtractor,
    CompoundExtractor,
    PatternExtractor,
    FallbackExtractor
)
from .attributes import AttributeEnhancer
from .validators import TargetValidator
from src.utils.vocabulary import Vocabulary
from ... import Target


class TargetExtractor:
    """
    Main target extraction orchestrator

    Coordinates multiple extraction strategies in priority order
    """

    def __init__(self, nlp):
        self.nlp = nlp
        self.vocab = Vocabulary()

        # Initialize extractors
        self.imperative_extractor = ImperativeExtractor(nlp, self.vocab)
        self.question_extractor = QuestionExtractor(nlp, self.vocab)
        self.noun_extractor = NounExtractor(nlp, self.vocab)
        self.compound_extractor = CompoundExtractor(nlp, self.vocab)
        self.pattern_extractor = PatternExtractor(nlp, self.vocab)
        self.fallback_extractor = FallbackExtractor(nlp, self.vocab)

        # Initialize enhancers
        self.attribute_enhancer = AttributeEnhancer(nlp)
        self.validator = TargetValidator()

    def extract(self, text: str, detected_req_tokens: list[str] | None = None) -> list[Target]:
        """
        Main extraction pipeline

        Priority order:
        1. Imperative patterns (highest confidence)
        2. Question patterns
        3. Noun matches
        4. Compound phrases
        5. Pattern detection
        6. Fallback
        """
        doc = self.nlp(text)

        # PRIORITY 1: Imperative patterns
        target = self.imperative_extractor.extract(text, detected_req_tokens, doc)
        if target:
            return [target]

        # PRIORITY 2: Question patterns
        target = self.question_extractor.extract(text, doc)
        if target:
            return [target]

        # PRIORITY 3-5: Collect multiple targets
        targets = []

        targets.extend(self.noun_extractor.extract(text, doc))
        targets.extend(self.compound_extractor.extract(text, doc))
        targets.extend(self.pattern_extractor.extract(text, doc))

        # PRIORITY 6: Fallback if nothing found
        if not targets:
            target = self.fallback_extractor.extract(text, detected_req_tokens, doc)
            if target:
                targets.append(target)

        # Validate and return (max 1-2 targets)
        return self.validator.deduplicate(targets)

__all__ = ['TargetExtractor']