from enum import Enum
from typing import Any


class DataTypes(Enum):
    """Data types to start the CLM encoding process"""

    SYSTEM_PROMPT = 0
    TRANSCRIPT = 1
    STRUCTURED_DATA = 2
    UNK = -1


class DataClassifier:
    """
    Classifies input data into CLM-compatible types.

    Expected inputs:
    - System Prompt: str (instruction text)
    - Transcript: str (conversation with speakers)
    - Structured Data: list[dict] or dict (catalog items)
    """

    def __init__(self) -> None:
        self._system_prompt_patterns: list[str] = [
            "your task is",
            "you are a",
            "your goal is to",
            "you must",
            "you should",
            "your role is",
            "instructions:",    
            "please analyze",
            "please extract",
            "the following",  # Often in system prompts
        ]

        self._transcript_patterns: list[str] = [
            "agent:",
            "customer:",
            "user:",
            "assistant:",
            "caller:",
            "representative:",
        ]

    def classifier(self, *, input_: Any) -> DataTypes:
        """
        Classify input data type.

        Args:
            input_: Any input data to classify

        Returns:
            DataTypes enum indicating the classified type

        Examples:
            >>> classifier.classify(input_="Your task is to analyze...")
            DataTypes.SYSTEM_PROMPT

            >>> classifier.classify(input_="Agent: Hello\\nCustomer: Hi")
            DataTypes.TRANSCRIPT

            >>> classifier.classify(input_=[{"id": "NBA-001", ...}, ...])
            DataTypes.STRUCTURED_DATA
        """
        if input_ is None or (isinstance(input_, str) and not input_.strip()):
            return DataTypes.UNK

        if self._is_structured_data(input_):
            return DataTypes.STRUCTURED_DATA

        if not isinstance(input_, str):
            return DataTypes.UNK

        normalized = input_.lower().strip()

        if self._is_transcript(normalized):
            return DataTypes.TRANSCRIPT

        if self._is_system_prompt(normalized):
            return DataTypes.SYSTEM_PROMPT

        return DataTypes.UNK

    @staticmethod
    def _is_structured_data(input_: Any) -> bool:
        """
        Check if input is structured data (catalog).

        Structured data is:
        - list of dicts (catalog items)
        - dict with known catalog structure

        NOT:
        - strings (even though they're iterable!)
        - empty collections
        """

        if isinstance(input_, str):
            return False

        if isinstance(input_, list):
            if not input_:
                return False
            return isinstance(input_[0], dict)

        if isinstance(input_, dict):
            return True

        return False

    def _is_transcript(self, normalized_text: str) -> bool:
        """
        Check if text is a transcript (conversation).

        Transcripts have:
        - Speaker labels (Agent:, Customer:, etc.)
        - Multiple exchanges (at least 2 speaker occurrences)
        """
        # Check for speaker patterns
        speaker_count = sum(
            normalized_text.count(pattern) for pattern in self._transcript_patterns
        )

        # Need at least 2 speaker occurrences for a conversation
        return speaker_count >= 2

    def _is_system_prompt(self, normalized_text: str) -> bool:
        """
        Check if text is a system prompt (instructions).

        System prompts typically:
        - Give instructions or define tasks
        - Are longer than a single sentence
        - Contain imperative language
        """
        # Check for system prompt patterns
        has_prompt_pattern = any(
            pattern in normalized_text for pattern in self._system_prompt_patterns
        )

        return has_prompt_pattern
