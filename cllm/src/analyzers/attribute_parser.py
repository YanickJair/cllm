# Extract CTX/OUT attributes
from typing import Optional
from spacy import Language

from src.core.vocabulary import Vocabulary
from src.core import ExtractionField, Context, OutputFormat


class AttributeParser:
    """Parses extraction fields, context, and output format"""
    def __init__(self, nlp: Language) -> None:
        self.nlp = nlp
        self.vocab = Vocabulary()

    def parse_extraction_fields(self, text: str) -> Optional[ExtractionField]:
        """Extract fields mentioned in the prompt"""
        text_lower = text.lower()
        found_fields = []

        # Look for extraction keywords
        extraction_indicators = [
            "extract", "identify", "find", "get", "pull out", "check this", "look at this",
            "tell me what you think", "return", "retrieve", "pick out", "locate"
        ]
        has_extraction = any(indicator in text_lower for indicator in extraction_indicators)

        if not has_extraction:
            return None
        
        # Check for common extraction fields
        for field in self.vocab.EXTRACT_FIELDS:
            field_lower = field.lower()
            # Look for the field name or variations
            if field_lower in text_lower or field_lower.replace('_', ' ') in text_lower:
                found_fields.append(field)
        
        if found_fields:
            return ExtractionField(fields=found_fields)

        return None
    
    def parse_contexts(self, text: str) -> list[Context]:
        """Parse context constraints from text"""
        contexts = []
        text_lower = text.lower()

        # Tone detection
        tone_keywords = {
            "PROFESSIONAL": ["professional", "formal", "business"],
            "CASUAL": ["casual", "informal", "friendly"],
            "EMPATHETIC": ["empathetic", "understanding", "compassionate"],
            "TECHNICAL": ["technical", "detailed", "in-depth"]
        }

        for tone, keywords in tone_keywords.items():
            if any(kw in text_lower for kw in keywords):
                contexts.append(Context(aspect="TONE", value=tone))
                break
        
        # Style detection
        if "simple" in text_lower or "easy" in text_lower:
            contexts.append(Context(aspect="STYLE", value="SIMPLE"))
        elif "detailed" in text_lower or "comprehensive" in text_lower:
            contexts.append(Context(aspect="STYLE", value="DETAILED"))

        # Length detection
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
