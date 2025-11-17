import re
from typing import Optional
from spacy import Language

from src.components.sys_prompt._schemas import DetectedField, ExtractionField
from src.utils.parser_rules import Rules


class FieldExtractor:
    """
    Detects extraction fields (ISSUE, BUG, NAMES, DATES, ...).
    Preserves original order of detection.
    """

    def __init__(self, nlp: Language):
        self.nlp = nlp
        self.rules = Rules

    def extract(self, text: str) -> list[DetectedField]:
        clean = text.strip()
        text_lower = clean.lower()
        doc = self.nlp(clean)

        detected = []

        for pattern, mapped in self.rules.COMPILED["comparison"]:
            for match in pattern.finditer(text_lower):
                detected.append(
                    DetectedField(
                        name=mapped.upper(),
                        span=match.span(),
                        source="comparison_keyword",
                        confidence=1.0
                    )
                )


        for pattern, mapped in self.rules.COMPILED["standard"]:
            for match in pattern.finditer(text_lower):
                canonical = mapped.upper()
                if not any(d.name == canonical for d in detected):
                    detected.append(
                        DetectedField(
                            name=canonical,
                            span=match.span(),
                            source="keyword",
                            confidence=0.9
                        )
                    )

        has_extraction_indicator = any(
            p.search(text_lower) for p in self.rules.COMPILED["extraction_indicators"]
        )


        verb_lemmas = {tok.lemma_.lower() for tok in doc if tok.pos_ == "VERB"}
        if "compare" in verb_lemmas or "contrast" in verb_lemmas:
            if not any(d.name == "DIFFERENCES" for d in detected):
                detected.append(
                    DetectedField(
                        name="DIFFERENCES",
                        span=(0, 0),
                        source="nlp_lemma",
                        confidence=0.95
                    )
                )
            has_extraction_indicator = True

        if any(v in verb_lemmas for v in ("extract", "identify", "list", "find")):
            has_extraction_indicator = True

        if has_extraction_indicator and not detected:
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower()
                for pattern, mapped in self.rules.COMPILED["standard"]:
                    if pattern.search(chunk_text):
                        detected.append(
                            DetectedField(
                                name=mapped.upper(),
                                span=(chunk.start_char, chunk.end_char),
                                source="inferred_noun",
                                confidence=0.65
                            )
                        )

        return detected


class AttributeExtractor:
    """
    Extract optional attributes (TYPE=list|single, DOMAIN=document|code|support, etc.)
    Only returns attributes when they can be detected.
    """
    @staticmethod
    def extract(text: str, detected_fields: list[DetectedField]) -> dict[str, str] | None:
        text_lower = text.lower()
        attrs = {}

        if any(word in text_lower for word in ["list", "all", "items", "extract all"]):
            attrs["TYPE"] = "LIST"

        domain_candidates = {
            "support": ["issue", "sentiment", "actions", "urgency", "priority"],
            "code": ["bug", "error", "security", "performance"],
            "document": ["names", "dates", "amounts", "addresses", "emails", "phones"],
        }

        found = set(f.name for f in detected_fields)

        for domain, keywords in domain_candidates.items():
            if any(k.upper() in found for k in keywords):
                attrs["DOMAIN"] = domain.upper()

        return attrs or None


class ExtractionFieldParser:
    def __init__(self, nlp: Language):
        self.field_extractor = FieldExtractor(nlp)
        self.attr_extractor = AttributeExtractor()

    def parse_extraction_fields(self, text: str) -> Optional[ExtractionField]:
        detected = self.field_extractor.extract(text)

        if not detected:
            return None

        # preserve original textual order by sorting by span start
        detected_sorted = sorted(detected, key=lambda d: d.span[0])
        fields_in_order = [d.name.upper() for d in detected_sorted]

        # extract attributes
        attrs = self.attr_extractor.extract(text, detected_sorted)

        return ExtractionField(fields=fields_in_order, attributes=attrs)
