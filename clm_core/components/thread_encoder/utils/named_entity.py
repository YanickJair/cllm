import re
from typing import Annotated

import spacy
from spacy.language import Language
from annotated_doc import Doc as ParamDoc
from spacy.tokens import Doc


class EntityExtractor:
    """EntityExtractor is a class that extracts named entities from text using spaCy.
    If spaCy fails to extract entities, it will fall back to using regular expressions.

    Attributes:
        _nlp (spacy.Language): The spaCy language model used for entity extraction.
        _ruler (spacy.pipeline.EntityRuler): The entity ruler used for custom entity recognition.
    """

    def __init__(
        self,
        nlp: Annotated[
            Language | None,
            ParamDoc(
                "An existing spaCy Language instance to reuse. If None, a new model is loaded using the model argument."
            ),
        ] = None,
        model: Annotated[
            str,
            ParamDoc(
                "Name of the spaCy model to load when nlp is not provided, e.g. 'en_core_web_sm'."
            ),
        ] = "en_core_web_sm",
        ner_domain_patterns: Annotated[
            dict[str, list] | None,
            ParamDoc(
                "Optional mapping of entity label to list of regex patterns for the entity ruler. If None, no custom patterns are added."
            ),
        ] = None,
    ):
        if nlp is not None:
            self._nlp = nlp
        else:
            self._nlp = spacy.load(model, disable=["parser", "textcat"])
            if "sentencizer" not in self._nlp.pipe_names:
                self._nlp.add_pipe("sentencizer")

        if "entity_ruler" not in self._nlp.pipe_names:
            self._ruler = self._nlp.add_pipe("entity_ruler", before="ner")
        else:
            self._ruler = self._nlp.get_pipe("entity_ruler")

        domain_patterns = ner_domain_patterns or {}
        ruler_patterns = []
        for label, patterns in domain_patterns.items():
            for pat in patterns:
                ruler_patterns.append(
                    {
                        "label": label,
                        "pattern": [{"TEXT": {"REGEX": pat}}],
                    }
                )
        self._ruler.add_patterns(ruler_patterns)

        self.regex_fields = {
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "PHONE": r"\b(?:\(\d{3}\)\s*\d{3}-\d{4}|\d{3}-\d{3}-\d{4}|\d{10})\b",
            "URL": r"https?://[^\s<>'\"{}|\\^`\[\]]+",
            "CASE_NUMBER": [
                r"\bcase\s*(?:number)?\s*(?:is)?\s*(\d{4,})\b",
                r"\bCASE-?\d{5,12}\b",
            ],
            "ESCALATION_ID": [
                r"\bESC-?\d{4,10}\b",
                r"\bTEC-?\d{4,10}\b",
            ],
            "VERIFICATION_CODE": [
                r"\b(?:code|verification)\s*(?:is|:)?\s*(\d{4,8})\b",
            ],
            "ORDER_NUMBER": [
                r"\border\s*(?:number)?\s*(?:is)?\s*(\d{4,})\b",
            ],
        }

    def extract(
        self,
        text: Annotated[
            str, ParamDoc("The raw text from which to extract named entities.")
        ],
        doc: Annotated[
            Doc,
            ParamDoc(
                "Optional pre-processed spaCy Doc to reuse, avoiding redundant NLP processing."
            ),
        ] = None,
    ) -> dict:
        """Extract named entities from the given text.

        Returns:
            dict: A dictionary containing extracted entities.
        Examples:
            >>> named_entity_extractor = NamedEntityExtractor()
            >>> text = "John Doe is a CEO of Google Inc."
            >>> named_entity_extractor.extract(text)
            {'persons': ['John Doe'], 'organizations': ['Google Inc.'], 'locations': [], 'dates': []}
        """
        if doc is None:
            doc = self._nlp(text)

        entities: dict[str, list] = {
            "persons": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "times": [],
            "money": [],
            "account_numbers": [],
            "tracking_numbers": [],
            "claim_numbers": [],
            "ticket_numbers": [],
            "case_numbers": [],
            "product_models": [],
            "emails": [],
            "phone_numbers": [],
            "urls": [],
            "escalation_ids": [],
            "verification_codes": [],
            "order_numbers": [],
        }

        for ent in doc.ents:
            label = ent.label_
            if label == "PERSON":
                entities["persons"].append(ent.text)
            elif label == "ORG":
                entities["organizations"].append(ent.text)
            elif label in ("GPE", "LOC"):
                entities["locations"].append(ent.text)
            elif label == "DATE":
                entities["dates"].append(ent.text)
            elif label == "TIME":
                entities["times"].append(ent.text)
            elif label == "MONEY":
                entities["money"].append(ent.text)
            elif label == "URL":
                entities["urls"].append(ent.text)
            elif label in (
                "ACCOUNT_NUMBER",
                "TRACKING_NUMBER",
                "CLAIM_NUMBER",
                "TICKET_NUMBER",
                "CASE_NUMBER",
                "PRODUCT_MODEL",
                "ORDER_NUMBER",
                "PACKAGE_ID",
                "INVOICE_NUMBER",
                "SUBSCRIPTION_ID",
                "SERIAL_NUMBER",
                "POLICY_NUMBER",
                "MEMBER_ID",
                "DEVICE_ID",
                "EMAIL",
                "PHONE_NUMBER",
                "ESCALATION_ID",
                "VERIFICATION_CODE",
            ):
                key = label.lower() + "s"
                entities.setdefault(key, []).append(ent.text)

        entities = self._map_regex_fallback(entities, text)
        for k in entities:
            entities[k] = sorted(set(self._normalize(entities[k])))

        return entities

    def _map_regex_fallback(
        self,
        entities: Annotated[
            dict[str, list],
            ParamDoc(
                "The partially populated entities dict to augment with regex matches."
            ),
        ],
        text: Annotated[
            str, ParamDoc("The original text to search with regex fallback patterns.")
        ],
    ) -> dict[str, list]:
        """Map regex patterns to entities.

        Returns:
            Dictionary of entities with regex patterns mapped.

        Examples:
            >>> NamedEntity._map_regex_fallback({"POLICY_NUMBER": ["\\d{8}"]}, "12345678")
            {"policy_numbers": ["12345678"]}
        """
        for key, patterns in self.regex_fields.items():
            bucket = key.lower() + "s"

            if bucket not in entities:
                entities[bucket] = []

            if isinstance(patterns, str):
                patterns = [patterns]

            for pattern in patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if isinstance(match, tuple):
                        for m in match:
                            if m:
                                entities[bucket].append(m)
                    else:
                        entities[bucket].append(match)
        return entities

    @staticmethod
    def _normalize(
        values: Annotated[
            list[str], ParamDoc("List of raw entity strings to standardize.")
        ],
    ) -> list[str]:
        """Standardize spacing and casing.

        Returns:
            List of normalized strings. URLs are kept as-is; all other values are uppercased.

        Examples:
            >>> NamedEntity._normalize(["  hello ", "world"])
            ["HELLO", "WORLD"]
        """
        clean = []
        for v in values:
            v = v.strip()
            if v:
                if any(v.startswith(s) for s in ("http", "www")):
                    clean.append(v)
                else:
                    clean.append(v.upper())
        return clean

    def extract_batch(
        self,
        texts: Annotated[
            list[str],
            ParamDoc("List of raw text strings to extract entities from in bulk."),
        ],
    ) -> list[dict]:
        """Fast batch extraction."""
        return [self.extract(doc.text) for doc in self._nlp.pipe(texts, batch_size=10)]
