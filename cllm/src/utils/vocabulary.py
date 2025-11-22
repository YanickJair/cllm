from abc import ABC, abstractmethod
from typing import Optional


class BaseVocabulary(ABC):
    """
    Multilingual CLLM Token Vocabulary
    Supports: English (EN), Portuguese (PT), Spanish (ES), French (FR)

    BaseVocabulary contains all shared logic.
    Language classes define only the data (tokens, triggers, patterns).
    """
    @property
    @abstractmethod
    def REQ_TOKENS(self) -> dict[str, list[str]]:
        # REQ tokens with trigger words
        raise NotImplementedError("Subclasses must implement REQ_TOKENS")

    @property
    @abstractmethod
    def TARGET_TOKENS(self) -> dict:
        """TARGET tokens with trigger words"""
        raise NotImplementedError("Subclasses must implement TARGET_TOKENS")

    @property
    @abstractmethod
    def NOISE_VERBS(self) -> set:
        """Verbs to EXCLUDE from intent detection (noise words)
        These appear as verbs in parsing but are not actionable intents"""
        raise NotImplementedError("Subclasses must implement NOISE_VERBS")

    @property
    @abstractmethod
    def CONTEXT_FILTERS(self) -> dict[str, list[str]]:
        """Context patterns to filter out (verb used non-actionably)
        These appear as verbs in parsing but are not actionable intents"""
        raise NotImplementedError("Subclasses must implement CONTEXT_FILTERS")

    @property
    @abstractmethod
    def EXTRACT_FIELDS(self) -> tuple[str, ...]:
        """Fields to extract from the input text"""
        raise NotImplementedError("Subclasses must implement EXTRACT_FIELDS")

    @property
    @abstractmethod
    def OUTPUT_FORMATS(self) -> dict[str, list[str]]:
        """Output formats supported by the vocabulary"""
        raise NotImplementedError("Subclasses must implement OUTPUT_FORMATS")

    @property
    @abstractmethod
    def IMPERATIVE_PATTERNS(self) -> list[tuple[list[str], str, str]]:
        """
        Patterns for imperative sentences: (triggers, req_token, target_token)
        Example: (["list", "enumerate"], "LIST", "ITEMS")
        """
        pass

    @property
    @abstractmethod
    def QUESTION_WORDS(self) -> list[str]:
        """Question words for the language (what, who, where, etc.)"""
        pass

    def get_req_token(self, word: str, context: str = "") -> Optional[str]:
        """
        Get REQ token for a word, considering context.
        Returns None if word is noise or filtered by context.
        """
        word_lower = word.lower()

        # Filter noise verbs
        if word_lower in self.NOISE_VERBS:
            return None

        # Apply context filters
        if word_lower in self.CONTEXT_FILTERS:
            for pattern in self.CONTEXT_FILTERS[word_lower]:
                if pattern in context.lower():
                    return None

        # Look up token
        for token, synonyms in self.REQ_TOKENS.items():
            if word_lower in synonyms:
                return token

        return None

    def get_target_token(self, word: str) -> Optional[str]:
        """Get TARGET token for a word."""
        word_lower = word.lower()
        for token, synonyms in self.TARGET_TOKENS.items():
            if word_lower in synonyms:
                return token
        return None

    def get_output_format(self, text: str) -> Optional[str]:
        """Detect output format from text."""
        text_lower = text.lower()
        for format_type, triggers in self.OUTPUT_FORMATS.items():
            if any(trigger in text_lower for trigger in triggers):
                return format_type
        return None

    def detect_imperative_pattern(self, text: str) -> Optional[tuple[str, str]]:
        """
        Detect imperative sentence patterns.
        Returns (req_token, target_token) or None.
        """
        text_lower = text.lower().strip()

        for triggers, req_token, target_token in self.IMPERATIVE_PATTERNS:
            for trigger in triggers:
                if text_lower.startswith(trigger + " "):
                    return req_token, target_token
        return None

    def get_question_req(self, text: str) -> Optional[str]:
        """
        Detect if text is a question and return appropriate REQ token.
        Returns "QUERY" for question patterns, None otherwise.
        """
        text_lower = text.lower().strip()

        if not text.strip().endswith("?"):
            return None

        if any(text_lower.startswith(word) for word in self.QUESTION_WORDS):
            return "QUERY"

        return None

    def get_all_req_triggers(self) -> dict[str, str]:
        """Get reverse mapping: trigger -> token for all REQ tokens."""
        result = {}
        for token, triggers in self.REQ_TOKENS.items():
            for trigger in triggers:
                result[trigger] = token
        return result

    def get_all_target_triggers(self) -> dict[str, str]:
        """Get reverse mapping: trigger -> token for all TARGET tokens."""
        result = {}
        for token, triggers in self.TARGET_TOKENS.items():
            for trigger in triggers:
                result[trigger] = token
        return result
