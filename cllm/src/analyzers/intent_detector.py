from typing import Optional
from spacy import Language

from src.analyzers.base import BaseAnalyzer
from src.core import Intent
from src.core.vocabulary import Vocabulary


class IntentDetector(BaseAnalyzer):
    """
    Detects REQ (request/action) tokens from text
    """

    def __init__(self, nlp: Language) -> None:
        super().__init__(nlp=nlp)

        self._modifiers = {
            'SUMMARIZE': {
                'BRIEF': ['brief', 'short', 'quick', 'concise'],
                'DETAILED': ['detailed', 'comprehensive', 'thorough'],
            },
            'EXPLAIN': {
                'SIMPLE': ['simple', 'basic', 'easy'],
                'TECHNICAL': ['technical', 'detailed', 'in-depth'],
                'DEEP': ['deep', 'thorough', 'comprehensive'],
            },
            'ANALYZE': {
                'DEEP': ['deep', 'thorough', 'comprehensive', 'detailed'],
                'QUICK': ['quick', 'brief', 'rapid', 'fast'],
                'SURFACE': ['surface', 'high-level', 'overview'],
            },
            'GENERATE': {
                'CREATIVE': ['creative', 'original', 'unique'],
                'FORMAL': ['formal', 'professional'],
            },
        }

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
        seen = set()

        imperative_result = self.vocab.detect_imperative_pattern(text)
        if imperative_result:
            req_token, _ = imperative_result
            intents.append(Intent(
                token=req_token,
                confidence=1.0,
                trigger_word=text.split()[0].lower()
            ))
            seen.add(req_token)

        for token in doc:
            if token.pos_ == "VERB":
                req_token = self.vocab.get_req_token(
                    token.lemma_,
                    context=context,
                )
                if req_token and req_token not in seen:
                    intents.append(Intent(
                        token=req_token,
                        confidence=0.95,
                        trigger_word=token.text
                    ))
                    seen.add(req_token)

        text_lower = text.lower()
        for token, synonyms in self.vocab.REQ_TOKENS.items():
            for synonym in synonyms:
                if len(synonym.split()) > 1 and synonym in text_lower:
                    if token not in seen:
                        intents.append(Intent(
                            token=token,
                            confidence=0.90,
                            trigger_word=synonym
                        ))
                        seen.add(token)

        if not intents:
            question_req = self.vocab.get_question_req(text)
            if question_req:
                intents.append(Intent(
                    token=question_req,
                    confidence=0.85,
                    trigger_word="question_pattern"
                ))
                seen.add(question_req)

        unique_intents: dict[str, Intent] = {}
        for intent in intents:
            if intent.token not in unique_intents or intent.confidence > unique_intents[intent.token].confidence:
                intent.modifier = self._detect_req_modifier(text=text, req_token=intent.token)
                unique_intents[intent.token] = intent

        return sorted(unique_intents.values(), key=lambda i: i.confidence, reverse=True)

    @staticmethod
    def get_primary_intent(intents: list[Intent]) -> Optional[Intent]:
        """
        Get the primary (most confident) intent
        """
        if not intents:
            return None
        return intents[0]

    def _detect_req_modifier(self, text: str, req_token: str) -> Optional[str]:
        """
        Detect modifiers for REQ tokens

        Examples:
            "Write a brief summary" + SUMMARIZE → BRIEF
            "Explain in detail" + EXPLAIN → DETAILED
            "Quick analysis" + ANALYZE → QUICK

        Returns:
            Modifier string or None
        """
        text_lower = text.lower()
        if req_token in self._modifiers.items():
            for modifier, kws in self._modifiers:
                if any(kw_ in text_lower for kw_ in kws):
                    return modifier
        return None