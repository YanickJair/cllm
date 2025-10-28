import re

import spacy


class EntityExtractor:
    """Extract entities with better patterns"""

    def __init__(self, nlp: spacy.Language):
        self.nlp = nlp

        # Domain-specific regex patterns
        self.domain_patterns = {
            'account_numbers': [
                r'\b\d{3}-\d{3}-\d{4}\b',           # 847-392-1045
                r'\b[A-Z]{2,4}\d{6,10}\b',          # ACCT123456
                r'\baccount[:\s]+([A-Z0-9-]+)\b',   # "account: ABC123"
            ],
            'tracking_numbers': [
                r'\b([A-Z]{2}-\d{7,10})\b',         # PL-7294008
                r'\b(TRK\d{9,12})\b',               # TRK123456789
                r'\btracking[:\s#]+([A-Z0-9-]+)\b', # "tracking #ABC123"
            ],
            'product_models': [
                r'\b([A-Z]{2,4}-\d{3,4}[A-Z]?)\b',  # HP-300A, TL-5000
                r'\bmodel[:\s]+([A-Z0-9-]+)\b',     # "model XYZ-456"
                r'\b([A-Z]{3}\d{3,4})\b',           # ABC1234
            ],
            'claim_numbers': [
                r'\b([A-Z]{2,3}-CLA-\d{5,8})\b',    # SS-CLA-89210
                r'\b(CLM-?\d{5,8})\b',              # CLM-12345
                r'\bclaim[:\s#]+([A-Z0-9-]+)\b',    # "claim #ABC123"
            ],
            'ticket_numbers': [
                r'\b(TK-?\d{5,8})\b',               # TK-12345
                r'\bticket[:\s#]+([A-Z0-9-]+)\b',   # "ticket #123456"
            ],
            'case_numbers': [
                r'\b(CASE-?\d{5,8})\b',             # CASE-12345
                r'\bcase[:\s#]+([A-Z0-9-]+)\b',     # "case #123456"
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
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'times': [],
            'money': [],
            
            # Regex patterns
            'account_numbers': [],
            'tracking_numbers': [],
            'product_models': [],
            'claim_numbers': [],
            'ticket_numbers': [],
            'case_numbers': [],
            
            # Hybrid/Regex only
            'addresses': [],
            'emails': [],
            'phone_numbers': [],
            'urls': [],
        }

        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                entities['persons'].append(ent.text)
            
            elif ent.label_ == 'ORG':
                entities['organizations'].append(ent.text)
            
            elif ent.label_ == 'GPE':
                entities['locations'].append(ent.text)
            
            elif ent.label_ == 'DATE':
                entities['dates'].append(ent.text)
            
            elif ent.label_ == 'TIME':
                entities['times'].append(ent.text)
            
            elif ent.label_ == 'MONEY':
                money_text = ent.text.replace(' ', '')
                if '$' not in money_text and money_text.replace('.', '').replace(',', '').isdigit():
                    money_text = f"${money_text}"
                entities['money'].append(money_text)
            
            elif ent.label_ in ['FAC', 'LOC']:
                entities['addresses'].append(ent.text)

        for pattern in self.domain_patterns['account_numbers']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['account_numbers'].extend(matches)
        
        # Tracking numbers
        for pattern in self.domain_patterns['tracking_numbers']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['tracking_numbers'].extend(matches)
        
        # Product models
        for pattern in self.domain_patterns['product_models']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['product_models'].extend(matches)
        
        # Claim numbers
        for pattern in self.domain_patterns['claim_numbers']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['claim_numbers'].extend(matches)
        
        # Ticket numbers
        for pattern in self.domain_patterns['ticket_numbers']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['ticket_numbers'].extend(matches)
        
        # Case numbers
        for pattern in self.domain_patterns['case_numbers']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['case_numbers'].extend(matches)

        address_patterns = [
            r'\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Court|Ct|Place|Pl)\b',
            r'\b\d+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln)\b',  # Two-word streets
        ]
        
        for pattern in address_patterns:
            matches = re.findall(pattern, text)
            entities['addresses'].extend(matches)
        
        # Email addresses (regex only - SpaCy doesn't catch these well)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        entities['emails'].extend(emails)
        
        # Phone numbers (regex only)
        phone_patterns = [
            r'\b\d{3}-\d{3}-\d{4}\b',
            r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',
            r'\b\d{10}\b',
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            entities['phone_numbers'].extend(matches)
        
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        entities['urls'].extend(urls)

        for key in entities:
            entities[key] = list(dict.fromkeys(entities[key]))
        
        # Clean up entities
        entities = self._clean_entities(entities)
        
        # Validate entities
        entities = self._validate_entities(entities)
        
        return entities
    
    def _clean_entities(self, entities: dict[str, list[str]]) -> dict[str, list[str]]:
        """Clean up extracted entities"""
        
        # Clean person names (remove titles, etc.)
        cleaned_persons = []
        for person in entities['persons']:
            # Remove common titles
            person = re.sub(r'\b(Mr|Mrs|Ms|Dr|Prof)\.?\s*', '', person, flags=re.IGNORECASE)
            person = person.strip()
            if person and len(person) > 1:  # At least 2 chars
                cleaned_persons.append(person)
        entities['persons'] = cleaned_persons
        
        # Clean money amounts (standardize format)
        cleaned_money = []
        for amount in entities['money']:
            # Ensure it starts with $
            if not amount.startswith('$'):
                amount = f"${amount}"
            # Remove spaces
            amount = amount.replace(' ', '')
            # Ensure decimal format
            if '.' not in amount:
                amount = amount + '.00'
            cleaned_money.append(amount)
        entities['money'] = cleaned_money
        
        # Clean addresses (capitalize properly)
        cleaned_addresses = []
        for address in entities['addresses']:
            # Title case
            address = address.title()
            cleaned_addresses.append(address)
        entities['addresses'] = cleaned_addresses
        
        return entities
    
    def _validate_entities(self, entities: dict[str, list[str]]) -> dict[str, list[str]]:
        """Validate extracted entities"""
        
        validated = {}
        
        for key, values in entities.items():
            validated_values = []
            
            for value in values:
                # Skip empty or too short
                if not value or len(value) < 2:
                    continue
                
                # Skip common false positives
                if key == 'persons':
                    # Skip single letters, numbers only
                    if len(value) < 2 or value.isdigit():
                        continue
                
                if key == 'organizations':
                    # Skip very short org names
                    if len(value) < 3:
                        continue
                
                if key == 'money':
                    # Validate money format
                    if not re.match(r'\$\d+(\.\d{2})?', value):
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
            'accounts': all_entities['account_numbers'],
            'tracking_numbers': all_entities['tracking_numbers'],
            'claim_numbers': all_entities['claim_numbers'],
            'ticket_numbers': all_entities['ticket_numbers'],
            'product_models': all_entities['product_models'],
            'money': all_entities['money'],
            'addresses': all_entities['addresses'],
            'organizations': all_entities['organizations'],
            'locations': all_entities['locations'],
            'dates': all_entities['dates'],
            'times': all_entities['times'],
            'emails': all_entities['emails'],
            'phone_numbers': all_entities['phone_numbers'],
        }