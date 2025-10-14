# Detect REQ tokens
from typing import Optional
from spacy import Language

from src.core import Intent
from src.core.vocabulary import Vocabulary


class IntentDetector:
    """
    Detects REQ (request/action) tokens from text
    """

    def __init__(self, nlp: Language) -> None:
        self.nlp = nlp
        self.vocab = Vocabulary()

    def detect(self, text: str, context: str = "") -> list[Intent]:
        """
        Detect all intents in the text using multiple strategies

        Strategies (in priority order):
        0. Imperative patterns (HIGHEST) - "List X", "Give Y", "Suggest Z"
        1. Verb matching - spaCy POS tagging
        2. Multi-word expressions - "pull out", "turn into"
        3. Question fallback - "What is X?" when no verbs found

        Args:
            text: Input prompt text
            context: Context parameter for context-aware filtering

        Returns:
            List of detected Intent objects sorted by confidence
        """
        doc = self.nlp(text)
        intents: list[Intent] = []
        seen = set()  # Prevent duplicates

        # This catches "List X", "Give Y", "Suggest Z" patterns
        # These are high-confidence and should override verb matching
        imperative_result = self.vocab.detect_imperative_pattern(text)
        if imperative_result:
            req_token, _ = imperative_result  # We only need REQ here, target handled elsewhere
            intents.append(Intent(
                token=req_token,
                confidence=1.0,  # Highest confidence
                trigger_word=text.split()[0].lower()  # First word is the trigger
            ))
            seen.add(req_token)

            # IMPORTANT: For imperative patterns, often this is THE intent
            # Return early to avoid over-detecting
            # But still check for secondary intents (e.g., "List and sort")

        # Strategy 1: Look for verbs that match REQ vocabulary
        for token in doc:
            if token.pos_ == "VERB":
                # Get REQ token with context-aware filtering
                req_token = self.vocab.get_req_token(
                    token.lemma_,
                    context=context,
                )
                if req_token and req_token not in seen:
                    intents.append(Intent(
                        token=req_token,
                        confidence=0.95,  # High confidence for verb matches
                        trigger_word=token.text
                    ))
                    seen.add(req_token)

        # Strategy 2: Look for multi-word expressions
        text_lower = text.lower()
        for token, synonyms in self.vocab.REQ_TOKENS.items():
            for synonym in synonyms:
                # Only check multi-word phrases (2+ words)
                if len(synonym.split()) > 1 and synonym in text_lower:
                    # Check if not already detected
                    if token not in seen:
                        intents.append(Intent(
                            token=token,
                            confidence=0.90,  # Medium-high confidence
                            trigger_word=synonym
                        ))
                        seen.add(token)

        # If NO intents detected so far, check if it's a question
        # This handles prompts like "What is X?" with no verbs
        if not intents:
            question_req = self.vocab.get_question_req(text)
            if question_req:
                intents.append(Intent(
                    token=question_req,
                    confidence=0.85,  # Medium confidence (fallback)
                    trigger_word="question_pattern"
                ))
                seen.add(question_req)

        # Remove duplicates, keep the highest confidence
        unique_intents: dict[str, Intent] = {}
        for intent in intents:
            if intent.token not in unique_intents or intent.confidence > unique_intents[intent.token].confidence:
                unique_intents[intent.token] = intent

        # Return sorted by confidence (highest first)
        return sorted(unique_intents.values(), key=lambda i: i.confidence, reverse=True)

    @staticmethod
    def get_primary_intent(intents: list[Intent]) -> Optional[Intent]:
        """
        Get the primary (most confident) intent

        With v2.1 improvements, the first intent in the list
        is always the highest confidence due to sorting.
        """
        if not intents:
            return None
        return intents[0]
