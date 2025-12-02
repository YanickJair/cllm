import re
import spacy
from src.dictionary.en.patterns import NER_DOMAIN_PATTERNS

class EntityExtractor:
    """EntityExtractor is a class that extracts named entities from text using spaCy.
    If spaCy fails to extract entities, it will fall back to using regular expressions.

    Attributes:
        _nlp (spacy.Language): The spaCy language model used for entity extraction.
        _ruler (spacy.pipeline.EntityRuler): The entity ruler used for custom entity recognition.
    """
    def __init__(self, model: str = "en_core_web_sm"):
        self._nlp = spacy.load(model, disable=["parser", "textcat"])
        self._nlp.add_pipe("sentencizer")

        if "entity_ruler" not in self._nlp.pipe_names:
            self._ruler = self._nlp.add_pipe("entity_ruler", before="ner")
        else:
            self._ruler = self._nlp.get_pipe("entity_ruler")

        ruler_patterns = []
        for label, patterns in NER_DOMAIN_PATTERNS.items():
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
        }

    def extract(self, text: str) -> dict:
        """
        Extract named entities from the given text.

        Args:
            text (str): The text to extract entities from.

        Returns:
            dict: A dictionary containing extracted entities.
        Examples:
            >>> named_entity_extractor = NamedEntityExtractor()
            >>> text = "John Doe is a CEO of Google Inc."
            >>> named_entity_extractor.extract(text)
            {'persons': ['John Doe'], 'organizations': ['Google Inc.'], 'locations': [], 'dates': []}
        """
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
            ):
                key = label.lower() + "s"
                entities[key].append(ent.text)

        entities = self._map_regex_fallback(entities, text)
        for k in entities:
            entities[k] = sorted(set(self._normalize(entities[k])))

        return entities

    def _map_regex_fallback(self, entities: dict[str, list], text: str) -> dict[str, list]:
        """Map regex patterns to entities.

        Args:
            entities: Dictionary of entities.
            text: Text to map regex patterns to.

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
    def _normalize(values: list[str]) -> list[str]:
        """Standardize spacing and casing.

        Args:
            values: List of strings to normalize.

        Returns:
            List of normalized strings.

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

    def extract_batch(self, texts: list[str]) -> list[dict]:
        """Fast batch extraction"""
        results = []
        for doc in self._nlp.pipe(texts, batch_size=10):
            results.append(self.extract(doc.text))
        return results
