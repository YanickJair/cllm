import re
import spacy


class EntityExtractor:
    """Improved hybrid extractor using spaCy + EntityRuler"""

    def __init__(self, model: str = "en_core_web_sm"):
        self._nlp = spacy.load(model, disable=["parser", "textcat"])
        self._nlp.add_pipe("sentencizer")

        # === Custom EntityRuler setup ===
        if "entity_ruler" not in self._nlp.pipe_names:
            self._ruler = self._nlp.add_pipe("entity_ruler", before="ner")
        else:
            self._ruler = self._nlp.get_pipe("entity_ruler")

        # Domain patterns (you can load from JSON or define inline)
        domain_patterns = {
            "ACCOUNT_NUMBER": [
                r"\b[A-Z]{2,4}\d{6,10}\b",
                r"\baccount[:\s]+([A-Z0-9-]+)\b",
            ],
            "TRACKING_NUMBER": [
                r"\b([A-Z]{2}-\d{7,10})\b",
                r"\b(TRK\d{9,12})\b",
                r"\btracking[:\s#]+([A-Z0-9-]+)\b",
            ],
            "CLAIM_NUMBER": [
                r"\b([A-Z]{2,3}-CLA-\d{5,8})\b",
                r"\b(CLM-?\d{5,8})\b",
                r"\bclaim[:\s#]+([A-Z0-9-]+)\b",
            ],
            "TICKET_NUMBER": [
                r"\b(TK-?\d{5,8})\b",
                r"\bticket[:\s#]+([A-Z0-9-]+)\b",
            ],
            "CASE_NUMBER": [
                r"\b(CASE-?\d{5,8})\b",
                r"\bcase[:\s#]+([A-Z0-9-]+)\b",
            ],
            "PRODUCT_MODEL": [
                r"\b([A-Z]{2,4}-\d{3,4}[A-Z]?)\b",
                r"\b([A-Z]{3}\d{3,4})\b",
                r"\bmodel[:\s]+([A-Z0-9-]+)\b",
            ],
        }

        # Add regex patterns as token-level rules
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

        # === Regex-only fields (not ideal for EntityRuler) ===
        self.regex_fields = {
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "PHONE": r"\b(?:\(\d{3}\)\s*\d{3}-\d{4}|\d{3}-\d{3}-\d{4}|\d{10})\b",
            "URL": r"https?://[^\s<>'\"{}|\\^`\[\]]+",
        }

    # === Core extraction ===
    def extract(self, text: str) -> dict:
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
            elif label in (
                "ACCOUNT_NUMBER",
                "TRACKING_NUMBER",
                "CLAIM_NUMBER",
                "TICKET_NUMBER",
                "CASE_NUMBER",
                "PRODUCT_MODEL",
            ):
                key = label.lower() + "s"
                entities[key].append(ent.text)

        # Regex-based matches for remaining types
        for key, pattern in self.regex_fields.items():
            matches = re.findall(pattern, text)
            key_name = key.lower() + "s"
            entities[key_name] = matches

        # Deduplicate + clean values
        for k in entities:
            entities[k] = sorted(set(self._normalize(entities[k])))

        return entities

    @staticmethod
    def _normalize(values):
        """Standardize spacing and casing."""
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
