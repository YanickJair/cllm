from typing import Optional

from src.analyzers.base import BaseAnalyzer
from spacy import Language

from src.core import ExtractionField, Context, OutputFormat


class AttributeParser(BaseAnalyzer):
    """Parses extraction fields, context, and output format"""
    def __init__(self, nlp: Language) -> None:
        super().__init__(nlp=nlp)

        self._extraction_indicators = [
            "extract", "identify", "find", "get", "pull out", "check this", "look at this",
            "tell me what you think", "return", "retrieve", "pick out", "locate"
        ]
        self._tone_keywords = {
            "PROFESSIONAL": ["professional", "formal", "business"],
            "CASUAL": ["casual", "informal", "friendly"],
            "EMPATHETIC": ["empathetic", "understanding", "compassionate"],
            "TECHNICAL": ["technical", "detailed", "in-depth"]
        }

    def parse_extraction_fields(self, text: str) -> Optional[ExtractionField]:
        """Identify fields that represent 'query' or information retrieve

        Usually there is only one extraction token represented.
        - Example: Analyze this file and return X, Y, and Z
        """
        text_lower = text.lower()
        found_fields = []

        has_extraction = any(
            indicator in text_lower for indicator in self._extraction_indicators
        )
        if not has_extraction:
            return None

        for field in self.vocab.EXTRACT_FIELDS:
            field_lower = field.lower()
            if field_lower in text_lower or field_lower.replace("_") in text_lower:
                found_fields.append(field)

        if found_fields:
            return ExtractionField(fields=found_fields)
        return None

    def parse_context(self, text: str) -> list[Context]:
        """Parse contexts from input prompts
        Understands the tone of the prompt, style, and expected output
        """
        contexts = []
        text_lower = text.lower()

        for tone, keywords in self._tone_keywords.items():
            if any(kw in text_lower for kw in keywords):
                contexts.append(Context(aspect="TONE", value=tone))
                break


        if "simple" in text_lower or "easy" in text_lower:
            contexts.append(Context(aspect="STYLE", value="SIMPLE"))
        elif "detailed" in text_lower or "comprehensive" in text_lower:
            contexts.append(Context(aspect="STYLE", value="DETAILED"))

        if "brief" in text_lower or "short" in text_lower:
            contexts.append(Context(aspect="LENGTH", value="BRIEF"))
        elif "long" in text_lower or "detailed" in text_lower:
            contexts.append(Context(aspect="LENGTH", value="DETAILED"))
        return contexts

    def parse_output_format(self, text: str) -> Optional[OutputFormat]:
        """Parse desired output format"""
        format_type = self.vocab.get_output_format(text)
        if format_type:
            return OutputFormat(format_type=format_type)
        return None
