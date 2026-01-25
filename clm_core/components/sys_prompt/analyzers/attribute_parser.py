import re

from typing import Optional, Any
from spacy import Language
from spacy.tokens import Doc

from clm_core.utils.vocabulary import BaseVocabulary
from clm_core.utils.parser_rules import BaseRules
from clm_core.components.sys_prompt.analyzers.extraction_field import (
    ExtractionFieldParser,
)
from clm_core.components.sys_prompt.analyzers.output_format import SysPromptOutputFormat
from .context_parser import ContextParser
from clm_core import SysPromptConfig
from .._schemas import ExtractionField, Context, OutputSchema


class AttributeParser:
    def __init__(
        self,
        *,
        nlp: Language,
        config: SysPromptConfig,
        vocab: BaseVocabulary,
        rules: BaseRules,
    ) -> None:
        self.nlp = nlp
        self.vocab = vocab
        self.rules = rules
        self._config = config

    def _doc(self, text: str) -> Doc:
        return self.nlp(text)

    @staticmethod
    def _normalize_whitespace(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    @staticmethod
    def _matches_any(
        text: str, compiled_list: list[tuple[re.Pattern, Any]]
    ) -> list[tuple[str, tuple[int, int], Any]]:
        """Return list of (matched_text, span, mapped_value)"""
        matches = []
        for pattern, mapped in compiled_list:
            for m in pattern.finditer(text):
                matches.append((m.group(0), (m.start(), m.end()), mapped))
        return matches

    def parse_extraction_fields(self, text: str) -> Optional[ExtractionField]:
        extraction_field = ExtractionFieldParser(
            nlp=self.nlp, vocab=self.vocab, rules=self.rules
        )
        return extraction_field.parse_extraction_fields(text)

    def parse_contexts(self, text: str) -> list[Context]:
        """
        Independent pipelines for AUDIENCE, LENGTH, STYLE, TONE.
        Returns list[Context] (unchanged external schema).
        """
        parser = ContextParser(nlp=self.nlp, rules=self.rules)
        return parser.parse(text)

    def extract_quantifier(self, text: str) -> Optional[tuple[str, int]]:
        """
        Returns (token, numeric_value) or None.
        Captures:
         - digit forms (e.g. "5 tips")
         - word forms (e.g. "three tips")
         - special words (few/several/many) as negative sentinel values
        """
        clean = self._normalize_whitespace(text).lower()
        digit_match = re.search(
            r"\b(\d+)\s*(tips?|items?|examples?|steps?|ways?|methods?)\b", clean
        )
        if digit_match:
            num = int(digit_match.group(1))
            return (f"NUM_{num}", num)

        for word, val in self.rules.NUMBER_WORDS.items():
            if re.search(
                rf"\b{re.escape(word)}\s+(tips|items|examples|steps|ways|methods|examples?)\b",
                clean,
            ):
                return (word.upper(), val)

        for word, val in self.rules.NUMBER_WORDS.items():
            if re.search(rf"\b{re.escape(word)}\b", clean):
                return (word.upper(), val)

        doc = self._doc(text)
        for ent in doc.ents:
            if ent.label_ in {"CARDINAL", "QUANTITY"}:
                try:
                    n = int(ent.text)
                    return (f"NUM_{n}", n)
                except ValueError:
                    pass

        return None

    def parse_output_format(self, text: str) -> Optional[OutputSchema]:
        """Use vocabulary helper to determine output format (keeps compatibility)."""
        parser = SysPromptOutputFormat(config=self._config)
        return parser.compress(text)

    def extract_specifications(self, text: str) -> Optional[dict[str, int]]:
        """
        Extract numeric specifications such as:
         - '10 lines' -> {"LINES": 10}
         - 'three tips' -> {"COUNT": 3}
         - '5 examples' -> {"COUNT": 5}
        Uses unified SPEC_PATTERNS and NUMBER_WORDS.
        """
        clean = self._normalize_whitespace(text)
        specs: dict[str, int] = {}

        for pattern, spec_name in self.rules.COMPILED["specs"]:
            m = pattern.search(clean)
            if m:
                try:
                    specs[spec_name] = int(m.group(1))
                except (ValueError, TypeError):
                    continue

        for word, num in self.rules.NUMBER_WORDS.items():
            m = re.search(
                rf"\b{re.escape(word)}\s+(tips|examples|items|ways|methods|steps)\b",
                clean,
                re.I,
            )
            if m:
                if "COUNT" not in specs:
                    specs["COUNT"] = num

        doc = self._doc(clean)
        for ent in doc.ents:
            if ent.label_ in {"CARDINAL", "QUANTITY"}:
                end_idx = ent.end
                if end_idx < len(doc):
                    next_token = doc[end_idx].lemma_.lower()
                    if next_token in {"line", "lines"} and "LINES" not in specs:
                        try:
                            specs["LINES"] = int(ent.text)
                        except ValueError:
                            pass
                    if next_token in {
                        "example",
                        "examples",
                        "tip",
                        "tips",
                        "item",
                        "items",
                        "way",
                        "ways",
                        "step",
                        "steps",
                    }:
                        if "COUNT" not in specs:
                            try:
                                specs["COUNT"] = int(ent.text)
                            except ValueError:
                                pass
        return specs if specs else None
