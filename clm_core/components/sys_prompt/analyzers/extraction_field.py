import re
from typing import Optional, Annotated

from annotated_doc import Doc
from spacy import Language
from clm_core.utils.vocabulary import BaseVocabulary

from clm_core.components.sys_prompt._schemas import DetectedField, ExtractionField
from clm_core.utils.parser_rules import BaseRules


class FieldExtractor:
    """
    Detects extraction fields (ISSUE, BUG, NAMES, DATES, etc.)
    Now only returns fields when extraction intent is explicit,
    EXCEPT for comparison fields (DIFFERENCES, PROS_CONS, etc.)
    which are always allowed implicitly.
    """

    def __init__(
        self,
        nlp: Annotated[
            Language, Doc("spaCy language model for tokenization and lemma extraction.")
        ],
        rules: Annotated[
            BaseRules,
            Doc(
                "Language-specific rules with compiled patterns for comparison, QA criteria, and extraction indicators."
            ),
        ],
    ):
        self.nlp = nlp
        self.rules = rules

    def extract(
        self,
        text: Annotated[str, Doc("The input text to detect extraction fields from.")],
    ) -> list[DetectedField]:
        """
        Extracts fields from the given text.

        Args:
            text (str): The text to extract fields from.

        Returns:
            list[DetectedField]: A list of detected fields.

        Examples:
            >>> extractor = FieldExtractor(nlp)
            >>> extractor.extract("What are the differences between the two products?")
            [DetectedField(name='DIFFERENCES', span=(18, 35))]
        """
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

        if any(
            p.search(text_lower) for p in self.rules.COMPILED["extraction_indicators"]
        ):
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

    def __init__(
        self,
        vocab: Annotated[
            BaseVocabulary,
            Doc(
                "Vocabulary instance used for list-indicator and domain-candidate lookups."
            ),
        ],
    ):
        self._vocab = vocab
        self._list_indicators = set()
        if "LIST" in self._vocab.REQ_TOKENS:
            self._list_indicators.update(
                s.lower() for s in self._vocab.REQ_TOKENS["LIST"]
            )
        if "ITEMS" in self._vocab.TARGET_TOKENS:
            self._list_indicators.update(
                s.lower() for s in self._vocab.TARGET_TOKENS["ITEMS"]
            )
        self._list_pattern = (
            re.compile(
                r"\b(?:" + "|".join(re.escape(i) for i in self._list_indicators) + r")\b"
            )
            if self._list_indicators
            else None
        )

    def extract(
        self,
        text: Annotated[str, Doc("The input text to extract attributes from.")],
        detected_fields: Annotated[
            list[DetectedField],
            Doc("Previously detected fields used to infer domain and type attributes."),
        ],
    ) -> dict[str, str] | None:
        """
        Extract optional attributes (TYPE=list|single, DOMAIN=document|code|support, etc.)
        Only returns attributes when they can be detected.

        Args:
            text (str): The input text to extract attributes from.
            detected_fields (list[DetectedField]): The detected fields in the text.

        Returns:
            dict[str, str] | None: The extracted attributes or None if no attributes are found.

        Examples:
            >>> extract("Extract all items", [])
            {'TYPE': 'LIST'}
            >>> extract("Extract items from document", [DetectedField("document", 0, 10)])
            {'TYPE': 'LIST', 'DOMAIN': 'DOCUMENT'}
        """
        text_lower = text.lower()
        attrs = {}

        if self._list_pattern and self._list_pattern.search(text_lower):
            attrs["TYPE"] = "LIST"

        found = {f.name for f in detected_fields}
        for domain, keywords in self._vocab.domain_candidates.items():
            if any(k.upper() in found for k in keywords):
                attrs["DOMAIN"] = domain.upper()

        return attrs or None


class ExtractionFieldParser:
    def __init__(
        self,
        nlp: Annotated[
            Language, Doc("spaCy language model for tokenization and lemma extraction.")
        ],
        vocab: Annotated[
            BaseVocabulary,
            Doc("Vocabulary instance for list-indicator and domain-candidate lookups."),
        ],
        rules: Annotated[
            BaseRules,
            Doc("Language-specific rules with compiled extraction and QA patterns."),
        ],
    ):
        self.field_extractor = FieldExtractor(nlp, rules)
        self.attr_extractor = AttributeExtractor(vocab=vocab)
        self._vocab = vocab

    def parse_extraction_fields(
        self,
        text: Annotated[str, Doc("The input text to parse extraction fields from.")],
        schema_field_names: Annotated[
            Optional[set[str]],
            Doc(
                "Uppercased field names from an already-parsed output schema. When "
                "given and the detected fields overlap with it, detected fields "
                "outside the schema (keyword noise not part of the actual output "
                "shape) are dropped."
            ),
        ] = None,
    ) -> Optional[ExtractionField]:
        """Parse extraction fields from a given text.

        Args:
            text (str): The input text to parse.
            schema_field_names (Optional[set[str]]): Uppercased output schema field
                names used to prune keyword noise from the detected fields.

        Returns:
            Optional[ExtractionField]: The parsed extraction fields, or None if no fields are found.

        Examples:
            >>> parser = ExtractionFieldParser(nlp)
            >>> text = "Extract bug and error fields from the document."
            >>> parser.parse_extraction_fields(text)
            ExtractionField(fields=['BUG', 'ERROR'], attributes={})
        """
        detected = self.field_extractor.extract(text)

        if not detected:
            return None

        detected_sorted = sorted(detected, key=lambda d: d.span[0])

        seen = set()
        fields_unique = []
        for d in detected_sorted:
            field_name = d.name.upper()
            if field_name not in seen:
                seen.add(field_name)
                fields_unique.append(field_name)

        if schema_field_names:
            overlap = [f for f in fields_unique if f in schema_field_names]
            if overlap:
                fields_unique = overlap
                detected_sorted = [
                    d for d in detected_sorted if d.name.upper() in schema_field_names
                ]

        attrs = self.attr_extractor.extract(text, detected_sorted)

        return ExtractionField(fields=fields_unique, attributes=attrs)
