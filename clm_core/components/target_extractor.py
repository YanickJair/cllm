from typing import Annotated

from annotated_doc import Doc as _Doc
from spacy.tokens import Doc
from clm_core.components.sys_prompt import Target

from ._target.target_normalizer import TargetNormalizer
from ._target.extractors import (
    ImperativeExtractor,
    QuestionExtractor,
    NounExtractor,
    CompoundExtractor,
    PatternExtractor,
    FallbackExtractor,
)
from ._target.attributes import AttributeEnhancer
from clm_core.utils.parser_rules import BaseRules
from clm_core.utils.vocabulary import BaseVocabulary


class TargetExtractor:
    """
    Main target extraction orchestrator

    Coordinates multiple extraction strategies in priority order
    """

    def __init__(
        self,
        nlp: Annotated[
            object,
            _Doc(
                "spaCy language model used for NLP processing across all sub-extractors."
            ),
        ],
        vocab: Annotated[
            BaseVocabulary, _Doc("Vocabulary instance for the target language.")
        ],
        rules: Annotated[BaseRules, _Doc("Language-specific parsing rules.")],
    ):
        self.nlp = nlp
        self.vocab = vocab
        self.rules = rules

        self.imperative_extractor = ImperativeExtractor(
            nlp=self.nlp,
            vocab=self.vocab,
            rules=self.rules,
        )
        self.question_extractor = QuestionExtractor(
            nlp=self.nlp,
            vocab=self.vocab,
            rules=self.rules,
        )
        self.noun_extractor = NounExtractor(
            nlp=self.nlp, vocab=self.vocab, rules=self.rules
        )
        self.compound_extractor = CompoundExtractor(
            nlp=self.nlp, vocab=self.vocab, rules=self.rules
        )
        self.pattern_extractor = PatternExtractor(
            nlp=self.nlp, vocab=self.vocab, rules=self.rules
        )
        self.fallback_extractor = FallbackExtractor(
            nlp=self.nlp, vocab=self.vocab, rules=self.rules
        )
        self.attribute_enhancer = AttributeEnhancer(
            nlp=self.nlp, vocab=self.vocab, rules=self.rules
        )
        self.normalizer = TargetNormalizer()

    def extract(
        self,
        text: Annotated[str, _Doc("Input text to extract the primary target from.")],
        detected_req_tokens: Annotated[
            list[str] | None,
            _Doc(
                "Optional list of already-detected REQ token strings used by the fallback extractor."
            ),
        ] = None,
        doc: Annotated[
            Doc,
            _Doc(
                "Optional pre-computed spaCy Doc to reuse, avoiding redundant NLP processing."
            ),
        ] = None,
    ) -> Target:
        """Main extraction pipeline

        Priority order:
        1. Imperative patterns (highest confidence)
        2. Question patterns
        3. Noun matches
        4. Compound phrases
        5. Pattern detection
        6. Fallback

        Args:
            text (str): The input text to extract targets from.
            detected_req_tokens (list[str] | None): Optional list of detected requirement tokens.
            doc (Doc): Optional pre-processed spaCy doc to reuse.

        Returns:
            list[Target]: A list of extracted targets.

        Example:
            >>> extractor = TargetExtractor(nlp, vocab)
            >>> text = "I need a laptop with a 16GB RAM and a 512GB SSD."
            >>> detected_req_tokens = ["laptop", "ram", "ssd"]
            >>> targets = extractor.extract(text, detected_req_tokens)
            >>> targets
            [Target(text='laptop', attributes={'ram': '16GB', 'ssd': '512GB'})]
        """
        if doc is None:
            doc = self.nlp(text)

        target = self.imperative_extractor.extract(text, detected_req_tokens, doc)
        if target:
            return target

        target = self.question_extractor.extract(text, doc)
        if target:
            return target

        targets = []

        targets.extend(self.noun_extractor.extract(text, doc))
        targets.extend(self.compound_extractor.extract(text, doc))
        targets.extend(self.pattern_extractor.extract(text, doc))

        if not targets:
            target = self.fallback_extractor.extract(text, detected_req_tokens, doc)
            if target:
                targets.append(target)

        return self.normalizer.normalize_many(targets)
