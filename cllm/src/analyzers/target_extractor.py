# Indentify TARGET tokens
from spacy import Language

from src.core.vocabulary import Vocabulary
from src.core._schemas import Target


class TargetExtractor:
    """Extracts target objects (TARGET tokens) from text"""
    
    def __init__(self, nlp: Language) -> None:
        self.nlp = nlp
        self.vocab = Vocabulary()

    def extract(self, text: str) -> list[Target]:
        """
        Extract target objects from text
        
        Args:
            text: Input prompt text
            
        Returns:
            List of detected Target objects
        """
        doc = self.nlp(text)
        targets: list[Target] = []

        # Strategy 1: Look for direct noun matches
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"]:
                target_token = self.vocab.get_target_token(token.text)
                if target_token:
                    targets.append(Target(
                        token=target_token,
                        attributes={}
                    ))
        
        # Strategy 2: Look for noun phrases
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            target_token = self.vocab.get_target_token(chunk_text)
            if target_token:
                # Check if not already added
                if not any(t.token == target_token for t in targets):
                    targets.append(Target(
                        token=target_token,
                        attributes={}
                    ))

        # Strategy 3: Extract domain attributes
        return self._add_domain_attributes(targets, text)
    
    def _add_domain_attributes(self, targets: list[Target], text: str) -> list[Target]:
        """Add domain-specific attributes to targets"""
        text_lower = text.lower()

        domain_keywords = {
            "SUPPORT": ["customer support", "customer service", "support ticket"],
            "TECHNICAL": ["technical", "engineering", "development", "code review", "fix bug"],
            "BUSINESS": ["business", "corporate", "enterprise"],
            "MEDICAL": ["medical", "healthcare", "clinical"],
        }

        for target in targets:
            # Add domain if found
            for domain, keywords in domain_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    target.domain = domain
                    break
            
            # Add language attribute for CODE targets
            if target.token == "CODE":
                languages = ["python", "javascript", "java", "c++", "ruby", "go"]
                for lang in languages:
                    if lang in text_lower:
                        target.attributes["LANG"] = lang
                        break
        
        return targets