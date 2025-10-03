# Detect REQ tokens
from typing import Optional
from spacy import Language

from src.core.vocabulary import Vocabulary
from src.core._schemas import Intent

class IntentDetector:
    def __init__(self, nlp: Language) -> None:
        self.nlp = nlp
        self.vocab = Vocabulary()

    def detect(self, text: str) -> list[Intent]:
        """
        Detect all intents in the text
        
        Args:
            text: Input prompt text
            
        Returns:
            List of detected Intent objects
        """
        doc = self.nlp(text)
        intents: list[Intent] = []

        # Strategy 1: Look for verbs that match REQ vocabulary
        for token in doc:
            if token.pos_ == "VERB":
                # Get REQ token
                req_token = self.vocab.get_req_token(token.lemma_)
                if req_token:
                    intents.append(Intent(
                        token=req_token,
                        confidence=1.0,
                        trigger_word=token.text
                    ))
        
        # Strategy 2: Check first word as imperative
        first_token = doc[0] if len(doc) > 0 else None
        if first_token:
            req_token = self.vocab.get_req_token(first_token.text.lower())
            if req_token:
                # Only add if not already detected
                if not any(i.token == req_token for i in intents):
                    intents.append(Intent(
                        token=req_token,
                        confidence=0.95,
                        trigger_word=first_token.text
                    ))

        # Strategy 3: Look for multi-word expressions
        text_lower = text.lower()
        for token, synomyms in self.vocab.REQ_TOKENS.items():
            for synomym in synomyms:
                if len(synomym.split()) > 1 and synomym in text_lower:
                    # Check if not already detected
                    if not any(i.token == token for i in intents):
                        intents.append(Intent(
                            token=token,
                            confidence=0.9,
                            trigger_word=synomym
                        ))
        
        # Remove duplicates, keep highest confidence
        unique_intents: dict[Intent] = {}
        for intent in intents:
            if intent.token not in unique_intents or intent.confidence > unique_intents[intent.token].confidence:
                unique_intents[intent.token] = intent
        
        return list(unique_intents.values())
    
    def get_primary_intent(self, intents: list[Intent]) -> Optional[Intent]:
        """Get the primary (most confident) intent"""
        if not intents:
            return None
        return max(intents, key=lambda i: i.confidence)