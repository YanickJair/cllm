import re
from typing import Optional
from spacy import Language

from src.components.sys_prompt._schemas import DetectedField, ExtractionField
from src.utils.parser_rules import Rules


class FieldExtractor:
    """
    Detects extraction fields (ISSUE, BUG, NAMES, DATES, etc.)
    Now only returns fields when extraction intent is explicit,
    EXCEPT for comparison fields (DIFFERENCES, PROS_CONS, etc.)
    which are always allowed implicitly.
    """

    def __init__(self, nlp: Language):
        self.nlp = nlp
        self.rules = Rules

    def extract(self, text: str) -> list[DetectedField]:
        clean = text.strip()
        text_lower = clean.lower()
        doc = self.nlp(clean)

        detected: list[DetectedField] = []
        comparison_found = False

        for pattern, mapped in self.rules.COMPILED["comparison"]:
            for match in pattern.finditer(text_lower):
                comparison_found = True
                detected.append(
                    DetectedField(
                        name=mapped.upper(),
                        span=match.span(),
                        source="comparison_keyword",
                        confidence=1.0,
                    )
                )

        qa_found = False
        qa_fields: list[DetectedField] = []
        for pattern, mapped in self.rules.COMPILED["qa_criteria"]:
            for match in pattern.finditer(text_lower):
                qa_found = True
                qa_fields.append(
                    DetectedField(
                        name=mapped.upper(),
                        span=match.span(),
                        source="qa_criteria",
                        confidence=0.95,
                    )
                )

        std_fields: list[DetectedField] = []
        for pattern, mapped in self.rules.COMPILED["standard"]:
            for match in pattern.finditer(text_lower):
                canonical = mapped.upper()
                std_fields.append(
                    DetectedField(
                        name=canonical,
                        span=match.span(),
                        source="keyword",
                        confidence=0.9,
                    )
                )

        has_extraction_intent = False

        if any(p.search(text_lower) for p in self.rules.COMPILED["extraction_indicators"]):
            has_extraction_intent = True

        if any(p.search(text_lower) for p in self.rules.COMPILED["qa_indicators"]):
            has_extraction_intent = True
            qa_found = True

        verb_lemmas = {tok.lemma_.lower() for tok in doc if tok.pos_ == "VERB"}
        if {"extract", "identify", "find", "list"}.intersection(verb_lemmas):
            has_extraction_intent = True

        if not has_extraction_intent and not comparison_found:
            return []

        if has_extraction_intent:
            detected.extend(std_fields)

        if qa_found:
            detected.extend(qa_fields)

        if has_extraction_intent and not detected:
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.lower()
                for pattern, mapped in self.rules.COMPILED["standard"]:
                    if pattern.search(chunk_text):
                        detected.append(
                            DetectedField(
                                name=mapped.upper(),
                                span=(chunk.start_char, chunk.end_char),
                                source="inferred_noun",
                                confidence=0.65,
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
            "qa": ["verification", "policy", "soft_skills", "accuracy", "compliance", "disclosures"],
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

        detected_sorted = sorted(detected, key=lambda d: d.span[0])

        # Deduplicate fields while preserving order of first appearance
        seen = set()
        fields_unique = []
        for d in detected_sorted:
            field_name = d.name.upper()
            if field_name not in seen:
                seen.add(field_name)
                fields_unique.append(field_name)

        attrs = self.attr_extractor.extract(text, detected_sorted)

        return ExtractionField(fields=fields_unique, attributes=attrs)