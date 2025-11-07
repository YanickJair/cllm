import re

import spacy


class EntityExtractor:
    """Extract entities with better patterns"""

    def __init__(self, nlp: spacy.Language):
        self.nlp = nlp

        # Domain-specific regex patterns
        self.domain_patterns = {
            "account_numbers": [
                r"\b\d{3}-\d{3}-\d{4}\b",  # 847-392-1045
                r"\b[A-Z]{2,4}\d{6,10}\b",  # ACCT123456
                r"\baccount[:\s]+([A-Z0-9-]+)\b",  # "account: ABC123"
            ],
            "tracking_numbers": [
                r"\b([A-Z]{2}-\d{7,10})\b",  # PL-7294008
                r"\b(TRK\d{9,12})\b",  # TRK123456789
                r"\btracking[:\s#]+([A-Z0-9-]+)\b",  # "tracking #ABC123"
            ],
            "product_models": [
                r"\b([A-Z]{2,4}-\d{3,4}[A-Z]?)\b",  # HP-300A, TL-5000
                r"\bmodel[:\s]+([A-Z0-9-]+)\b",  # "model XYZ-456"
                r"\b([A-Z]{3}\d{3,4})\b",  # ABC1234
            ],
            "claim_numbers": [
                r"\b([A-Z]{2,3}-CLA-\d{5,8})\b",  # SS-CLA-89210
                r"\b(CLM-?\d{5,8})\b",  # CLM-12345
                r"\bclaim[:\s#]+([A-Z0-9-]+)\b",  # "claim #ABC123"
            ],
            "ticket_numbers": [
                r"\b(TK-?\d{5,8})\b",  # TK-12345
                r"\bticket[:\s#]+([A-Z0-9-]+)\b",  # "ticket #123456"
            ],
            "case_numbers": [
                r"\b(CASE-?\d{5,8})\b",  # CASE-12345
                r"\bcase[:\s#]+([A-Z0-9-]+)\b",  # "case #123456"
            ],
        }

    def extract(self, text: str) -> dict:
        """
        Extract all entities

        Returns:
            {
                'accounts': [...],
                'addresses': [...],
                'plans': [...],
                'products': [...],
                'dates': [...],
                'times': [...]
            }
        """
        entities = {
            # SpaCy NER
            "persons": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "times": [],
            "money": [],
            # Regex patterns
            "account_numbers": [],
            "tracking_numbers": [],
            "product_models": [],
            "claim_numbers": [],
            "ticket_numbers": [],
            "case_numbers": [],
            "order_numbers": [],
            # Hybrid/Regex only
            "addresses": [],
            "emails": [],
            "phone_numbers": [],
            "urls": [],
        }

        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["persons"].append(ent.text)

            elif ent.label_ == "ORG":
                entities["organizations"].append(ent.text)

            elif ent.label_ == "GPE":
                entities["locations"].append(ent.text)

            elif ent.label_ == "DATE":
                entities["dates"].append(ent.text)

            elif ent.label_ == "TIME":
                entities["times"].append(ent.text)

            elif ent.label_ == "MONEY":
                money_text = ent.text.replace(" ", "")
                if (
                    "$" not in money_text
                    and money_text.replace(".", "").replace(",", "").isdigit()
                ):
                    money_text = f"${money_text}"
                entities["money"].append(money_text)

            elif ent.label_ in ["FAC", "LOC"]:
                entities["addresses"].append(ent.text)

        entities["account_numbers"].extend(self.extract_account_numbers(text))
        entities["tracking_numbers"].extend(self.extract_tracking_numbers(text))
        entities["product_models"].extend(self.extract_product_models(text))
        entities["claim_numbers"].extend(self.extract_claim_numbers(text))
        entities["ticket_numbers"].extend(self.extract_ticket_numbers(text))
        entities["case_numbers"].extend(self.extract_case_numbers(text))
        entities["order_numbers"].extend(self.extract_order_numbers(text))

        address_patterns = [
            r"\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Court|Ct|Place|Pl)\b",
            r"\b\d+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln)\b",  # Two-word streets
        ]

        for pattern in address_patterns:
            matches = re.findall(pattern, text)
            entities["addresses"].extend(matches)

        # Email addresses (regex only - SpaCy doesn't catch these well)
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        entities["emails"].extend(emails)

        # Phone numbers (regex only)
        phone_patterns = [
            r"\b\d{3}-\d{3}-\d{4}\b",
            r"\b\(\d{3}\)\s*\d{3}-\d{4}\b",
            r"\b\d{10}\b",
        ]

        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            entities["phone_numbers"].extend(matches)

        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        entities["urls"].extend(urls)

        for key in entities:
            entities[key] = list(dict.fromkeys(entities[key]))

        # Clean up entities
        entities = self._clean_entities(entities)

        # Validate entities
        entities = self._validate_entities(entities)

        return entities

    @staticmethod
    def extract_account_numbers(text: str) -> list[str]:
        """
        Extract account numbers

        Patterns:
        - 847-392-1045 (phone-like format)
        - ACCT123456 (alphanumeric)
        - MW-55983 (company prefix)
        """
        accounts = []

        pattern1 = r"\b(\d{3}-\d{3}-\d{4})\b"
        matches = re.findall(pattern1, text)
        accounts.extend(matches)

        pattern2 = r"\b([A-Z]{2,3}-\d{5,6})\b"
        matches = re.findall(pattern2, text)

        for match in matches:
            if not re.match(r"[A-Z]{2}-\d{7,}", match) and "CLA" not in match:
                accounts.append(match)

        # Pattern 3: ACCT followed by digits
        pattern3 = r"\b(ACCT\d{6,10})\b"
        matches = re.findall(pattern3, text, re.IGNORECASE)
        accounts.extend(matches)

        # Pattern 4: Plain 6-digit numbers when context suggests account
        if "account" in text.lower():
            pattern4 = r"\baccount[:\s]+(\d{6,8})\b"
            matches = re.findall(pattern4, text, re.IGNORECASE)
            accounts.extend(matches)

        return list(set(accounts))

    @staticmethod
    def extract_tracking_numbers(text: str) -> list[str]:
        """
        Extract tracking numbers

        Patterns:
        - PL-7294008 (2 letters + dash + 7+ digits)
        - TRK123456789 (TRK prefix)
        """
        tracking = []

        # Pattern 1: XX-NNNNNNN (2 letters, dash, 7-10 digits)
        pattern1 = r"\b([A-Z]{2}-\d{7,10})\b"
        matches = re.findall(pattern1, text)
        tracking.extend(matches)

        # Pattern 2: TRK followed by 9-12 digits
        pattern2 = r"\b(TRK\d{9,12})\b"
        matches = re.findall(pattern2, text, re.IGNORECASE)
        tracking.extend([m.upper() for m in matches])

        # Pattern 3: Only if explicitly mentioned with "tracking"
        if "tracking" in text.lower():
            # Look for the FIRST alphanumeric sequence after "tracking"
            pattern3 = r"tracking[:\s#]+([A-Z0-9]{10,15})\b"
            matches = re.findall(pattern3, text, re.IGNORECASE)
            tracking.extend([m.upper() for m in matches])

        return list(set(tracking))

    @staticmethod
    def extract_product_models(text: str) -> list[str]:
        """
        Extract product models

        Patterns:
        - HP-300A
        - Model XYZ-123
        """
        models = []

        # Pattern 1: XX-NNNA (2-4 letters, dash, 3-4 digits, optional letter)
        pattern1 = r"\b([A-Z]{2,4}-\d{3,4}[A-Z]?)\b"
        matches = re.findall(pattern1, text)
        # Filter out patterns that look like tracking numbers (7+ digits)
        for match in matches:
            # Count digits
            digits = re.findall(r"\d+", match)
            if digits and len(digits[0]) <= 4:  # Product models have ≤4 digits
                models.append(match)

        # Pattern 2: "model" followed by alphanumeric
        if "model" in text.lower():
            # Look for the FIRST valid pattern after "model"
            pattern2 = r"model\s+(?:number\s+)?([A-Z]{2,4}-\d{3,4}[A-Z]?)\b"
            matches = re.findall(pattern2, text, re.IGNORECASE)
            models.extend([m.upper() for m in matches])

        # Pattern 3: XXXNNN (3 letters + 3 digits, no dash)
        pattern3 = r"\b([A-Z]{3}\d{3,4})\b"
        matches = re.findall(pattern3, text)
        models.extend(matches)

        return list(set(models))

    @staticmethod
    def extract_claim_numbers(text: str) -> list[str]:
        """
        Extract claim numbers

        Patterns:
        - SS-CLA-89210 (prefix-CLA-digits)
        - CLM-12345 (CLM prefix)
        """
        claims = []

        # Pattern 1: XX-CLA-NNNNN (prefix-CLA-digits)
        # SS-CLA-89210, INS-CLA-12345
        pattern1 = r"\b([A-Z]{2,3}-CLA-\d{5,8})\b"
        matches = re.findall(pattern1, text)
        claims.extend(matches)

        # Pattern 2: CLM-NNNNN (CLM prefix with dash)
        pattern2 = r"\b(CLM-\d{5,8})\b"
        matches = re.findall(pattern2, text, re.IGNORECASE)
        claims.extend([m.upper() for m in matches])

        # Pattern 3: CLMNNNNN (CLM prefix without dash)
        pattern3 = r"\b(CLM\d{5,8})\b"
        matches = re.findall(pattern3, text, re.IGNORECASE)
        claims.extend([m.upper() for m in matches])

        # Pattern 4: Only if explicitly mentioned with "claim"
        # "claim number SS-CLA-89210" or "claim: SS-CLA-89210"
        # Look for the FIRST valid pattern after "claim"
        if "claim" in text.lower():
            pattern4 = r"claim\s+(?:number\s+)?([A-Z]{2,3}-CLA-\d{5,8})\b"
            matches = re.findall(pattern4, text, re.IGNORECASE)
            claims.extend([m.upper() for m in matches])

        return list(set(claims))

    @staticmethod
    def extract_ticket_numbers(text: str) -> list[str]:
        """Extract ticket numbers: TK-12345, TICKET-98765"""
        tickets = []

        # Pattern 1: TK-NNNNN
        pattern1 = r"\b(TK-\d{5,8})\b"
        matches = re.findall(pattern1, text, re.IGNORECASE)
        tickets.extend([m.upper() for m in matches])

        # Pattern 2: TICKET-NNNNN
        pattern2 = r"\b(TICKET-\d{5,8})\b"
        matches = re.findall(pattern2, text, re.IGNORECASE)
        tickets.extend([m.upper() for m in matches])

        return list(set(tickets))

    @staticmethod
    def extract_case_numbers(text: str) -> list[str]:
        """Extract case numbers: CASE-12345"""
        cases = []

        # Pattern: CASE-NNNNN
        pattern = r"\b(CASE-?\d{5,8})\b"
        matches = re.findall(pattern, text, re.IGNORECASE)
        cases.extend([m.upper() for m in matches])

        return list(set(cases))

    @staticmethod
    def extract_order_numbers(text: str) -> list[str]:
        """Extract order numbers: SE-90211, ORD-12345"""
        orders = []

        # Pattern 1: XX-NNNNN (but not tracking/claim patterns)
        if "order" in text.lower():
            pattern = r"order\s+(?:number\s+)?([A-Z]{2,3}-\d{5,6})\b"
            matches = re.findall(pattern, text, re.IGNORECASE)
            orders.extend([m.upper() for m in matches])

        # Pattern 2: ORD-NNNNN
        pattern2 = r"\b(ORD-\d{5,8})\b"
        matches = re.findall(pattern2, text, re.IGNORECASE)
        orders.extend([m.upper() for m in matches])

        return list(set(orders))

    @staticmethod
    def _clean_entities(entities: dict[str, list[str]]) -> dict[str, list[str]]:
        """Clean up extracted entities"""

        # Clean person names (remove titles, etc.)
        cleaned_persons = []
        for person in entities["persons"]:
            # Remove common titles
            person = re.sub(
                r"\b(Mr|Mrs|Ms|Dr|Prof)\.?\s*", "", person, flags=re.IGNORECASE
            )
            person = person.strip()
            if person and len(person) > 1:  # At least 2 chars
                cleaned_persons.append(person)
        entities["persons"] = cleaned_persons

        # Clean money amounts (standardize format)
        cleaned_money = []
        for amount in entities["money"]:
            # Ensure it starts with $
            if not amount.startswith("$"):
                amount = f"${amount}"
            # Remove spaces
            amount = amount.replace(" ", "")
            # Ensure decimal format
            if "." not in amount:
                amount = amount + ".00"
            cleaned_money.append(amount)
        entities["money"] = cleaned_money

        # Clean addresses (capitalize properly)
        cleaned_addresses = []
        for address in entities["addresses"]:
            # Title case
            address = address.title()
            cleaned_addresses.append(address)
        entities["addresses"] = cleaned_addresses

        return entities

    @staticmethod
    def _validate_entities(entities: dict[str, list[str]]) -> dict[str, list[str]]:
        """Validate extracted entities"""

        validated = {}

        for key, values in entities.items():
            validated_values = []

            for value in values:
                if not value or len(value) < 2:
                    continue

                if key == "persons" and len(value) < 2 or value.isdigit():
                    continue

                if key == "organizations" and len(value) < 3:
                    continue

                if key == "money" and not re.match(r"\$\d+(\.\d{2})?", value):
                    continue

                validated_values.append(value)

            validated[key] = validated_values

        return validated

    def extract_for_transcript(self, text: str) -> dict[str, list[str]]:
        """
        Convenience method for transcript compression
        Returns simplified dict with commonly needed entities
        """
        all_entities = self.extract(text)

        # Map to transcript compression format
        return {
            "accounts": all_entities["account_numbers"],
            "tracking_numbers": all_entities["tracking_numbers"],
            "claim_numbers": all_entities["claim_numbers"],
            "ticket_numbers": all_entities["ticket_numbers"],
            "product_models": all_entities["product_models"],
            "money": all_entities["money"],
            "addresses": all_entities["addresses"],
            "organizations": all_entities["organizations"],
            "locations": all_entities["locations"],
            "dates": all_entities["dates"],
            "times": all_entities["times"],
            "emails": all_entities["emails"],
            "phone_numbers": all_entities["phone_numbers"],
        }
