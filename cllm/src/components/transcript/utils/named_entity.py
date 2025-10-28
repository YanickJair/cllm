import re

import spacy


class EntityExtractor:
    """Extract entities with better patterns"""

    def __init__(self, nlp: spacy.Language):
        self.nlp = nlp

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
            'accounts': [],
            'addresses': [],
            'plans': [],
            'products': [],
            'dates': [],
            'times': [],
            'money': [],
            'product_models': [],
            'tracking_numbers': [],
            'claim_numbers': [],
        }

        money_patterns = [
            r'\$(\d+(?:\.\d{2})?)',  # $14.99, $12
            r'(\d+(?:\.\d{2})?)\s*(?:USD|dollars?)',  # 50.00 USD
        ]

        for pattern in money_patterns:
            matches = re.findall(pattern, text)
            entities['money'].extend([f"${m}" for m in matches])

        model_patterns = [
            r'\b([A-Z]{2,4}-\d{3,4}[A-Z]?)\b',  # HP-300A, TL-5000
            r'\bmodel\s+([A-Z0-9-]+)\b',  # model XYZ-456
            r'\b([A-Z]{3}\d{3})\b',  # ABC123
        ]

        for pattern in model_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['product_models'].extend(matches)

        tracking_patterns = [
            r'\b([A-Z]{2}-\d{7,10})\b',  # PL-7294008
            r'\b(TRK\d{9,12})\b',  # TRK123456789
        ]

        for pattern in tracking_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['tracking_numbers'].extend(matches)

        claim_patterns = [
            r'\b([A-Z]{2}-CLA-\d{5})\b',  # SS-CLA-89210
            r'\b(CLM-\d{5,8})\b',  # CLM-12345
        ]

        for pattern in claim_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['claim_numbers'].extend(matches)

        # Account numbers
        # Patterns: 847-392-1045, 123-456-7890, ACCT123456
        account_patterns = [
            r'\b\d{3}-\d{3}-\d{4}\b',  # 847-392-1045
            r'\b[A-Z]{2,4}\d{6,}\b',  # ACCT123456
        ]
        for pattern in account_patterns:
            matches = re.findall(pattern, text)
            entities['accounts'].extend(matches)

        # Addresses
        # Pattern: "123 Main Street", "456 Oak Ave"
        address_pattern = r'\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b'
        matches = re.findall(address_pattern, text)
        entities['addresses'].extend(matches)

        # Service plans
        # Pattern: "Premium Internet 500", "Basic Plan", "Enterprise Support"
        plan_keywords = ['premium', 'basic', 'enterprise', 'standard', 'pro', 'plus']
        plan_pattern = r'\b(' + '|'.join(plan_keywords) + r')\s+[\w\s]+\d*\b'
        matches = re.findall(plan_pattern, text, re.IGNORECASE)
        entities['plans'].extend(matches)

        # Use spaCy for additional entities
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == 'DATE':
                entities['dates'].append(ent.text)
            elif ent.label_ == 'TIME':
                entities['times'].append(ent.text)

        # Deduplicate
        for key in entities:
            entities[key] = list(set(entities[key]))

        return entities