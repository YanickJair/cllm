# Extract CTX/OUT attributes
import re
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
        """
        Enhanced extraction field detection
        
        V3.0 Improvements:
        - Detects "differences", "similarities", "pros/cons"
        - Detects comparison fields
        - Better keyword matching
        """
        text_lower = text.lower()
        found_fields = []
        
        # Check if extraction is implied
        extraction_indicators = [
            "extract", "identify", "find", "get", "pull out",
            "highlight", "show", "return", "retrieve",
            "compare", "contrast",
        ]
        
        has_extraction = any(indicator in text_lower for indicator in extraction_indicators)
        
        comparison_fields = {
            'differences': 'DIFFERENCES',
            'difference': 'DIFFERENCES',
            'distinguish': 'DIFFERENCES',
            'contrast': 'DIFFERENCES',
            'similarities': 'SIMILARITIES',
            'similarity': 'SIMILARITIES',
            'common': 'SIMILARITIES',
            'pros and cons': 'PROS_CONS',
            'advantages and disadvantages': 'PROS_CONS',
            'benefits and drawbacks': 'PROS_CONS',
            'tradeoffs': 'TRADEOFFS',
            'trade-offs': 'TRADEOFFS',
        }
        
        for keyword, field in comparison_fields.items():
            if keyword in text_lower:
                found_fields.append(field)
                has_extraction = True
        
        if found_fields:
            return ExtractionField(fields=found_fields)
        
        if not has_extraction:
            return None
        
        # Standard extraction fields from vocabulary
        standard_fields = {
            'issue': 'ISSUE',
            'problem': 'PROBLEM',
            'error': 'ERROR',
            'bug': 'BUG',
            'names': 'NAMES',
            'dates': 'DATES',
            'amounts': 'AMOUNTS',
            'emails': 'EMAILS',
            'phones': 'PHONES',
            'addresses': 'ADDRESSES',
            'sentiment': 'SENTIMENT',
            'urgency': 'URGENCY',
            'priority': 'PRIORITY',
            'category': 'CATEGORY',
            'actions': 'ACTIONS',
            'next steps': 'NEXT_STEPS',
            'action items': 'ACTIONS',
            'deadlines': 'DEADLINES',
            'bugs': 'BUGS',
            'security': 'SECURITY',
            'performance': 'PERFORMANCE',
        }
        
        for keyword, field in standard_fields.items():
            if keyword in text_lower and field not in found_fields:
                found_fields.append(field)
        
        if found_fields:
            unique_fields = []
            seen = set()
            for field in found_fields:
                if field not in seen:
                    unique_fields.append(field)
                    seen.add(field)
            return ExtractionField(fields=unique_fields)
        
        return None

    def parse_contexts(self, text: str) -> list[Context]:
        """
        Parse context constraints with smart consolidation
        
        V3.0 Improvements:
        - Consolidates redundant CTX (BRIEF = CONCISE, etc.)
        - Prefers LENGTH over STYLE for simplicity
        - Removes duplicate semantic meanings
        """
        contexts = []
        text_lower = text.lower()
        
        added_aspects = set()
        
        if any(pattern in text_lower for pattern in [
            'non-technical', 'nontechnical', 'non technical'
        ]):
            contexts.append(Context(aspect="AUDIENCE", value="NON_TECHNICAL"))
            added_aspects.add("AUDIENCE")
        
        elif any(pattern in text_lower for pattern in [
            'beginner', 'child', 'kid', '5-year-old', '10-year-old',
            'simple', 'layman', 'general audience'
        ]):
            contexts.append(Context(aspect="AUDIENCE", value="BEGINNER"))
            added_aspects.add("AUDIENCE")
        
        elif any(pattern in text_lower for pattern in [
            'expert', 'advanced', 'specialist'
        ]):
            contexts.append(Context(aspect="AUDIENCE", value="EXPERT"))
            added_aspects.add("AUDIENCE")
        
        elif 'technical' in text_lower and 'non' not in text_lower:
            contexts.append(Context(aspect="AUDIENCE", value="TECHNICAL"))
            added_aspects.add("AUDIENCE")
        
        elif any(pattern in text_lower for pattern in [
            'business', 'executives', 'management'
        ]):
            contexts.append(Context(aspect="AUDIENCE", value="BUSINESS"))
            added_aspects.add("AUDIENCE")
        
        # ===== LENGTH (consolidate with STYLE) =====
        # Priority: Use LENGTH, skip redundant STYLE
        
        # BRIEF indicators (consolidate: brief = short = concise)
        if any(pattern in text_lower for pattern in [
            'brief', 'short', 'concise', 'quick', 'summary'
        ]):
            contexts.append(Context(aspect="LENGTH", value="BRIEF"))
            added_aspects.add("LENGTH")
            added_aspects.add("STYLE")  # Mark STYLE as handled
        
        # DETAILED indicators (consolidate: detailed = comprehensive = thorough)
        elif any(pattern in text_lower for pattern in [
            'detailed', 'comprehensive', 'thorough', 'in-depth', 'complete'
        ]):
            contexts.append(Context(aspect="LENGTH", value="DETAILED"))
            added_aspects.add("LENGTH")
            added_aspects.add("STYLE")  # Mark STYLE as handled
        
        # ===== STYLE (only if LENGTH not set) =====
        if "STYLE" not in added_aspects:
            if any(pattern in text_lower for pattern in ['simple', 'easy', 'straightforward']):
                contexts.append(Context(aspect="STYLE", value="SIMPLE"))
                added_aspects.add("STYLE")
        
        # ===== TONE (keep as-is) =====
        tone_keywords = {
            "PROFESSIONAL": ["professional", "formal", "business-like"],
            "CASUAL": ["casual", "informal", "friendly"],
            "EMPATHETIC": ["empathetic", "compassionate", "understanding"],
        }
        
        for tone, keywords in tone_keywords.items():
            if any(kw in text_lower for kw in keywords):
                contexts.append(Context(aspect="TONE", value=tone))
                added_aspects.add("TONE")
                break
        
        return contexts

    def extract_quantifier(self, text: str) -> Optional[tuple[str, int]]:
        """
        Extract quantifiers from text (numbers/amounts)

        Returns:
            Tuple of (token, value) or None
            Example: "three tips" → ("THREE", 3)
        """
        # Number word to value mapping
        NUMBER_WORDS = {
            'one': 1, 'a': 1, 'an': 1, 'single': 1,
            'two': 2, 'couple': 2, 'pair': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10,
            'few': -1,  # Special: indicates small number
            'several': -2,  # Special: indicates medium number
            'many': -3,  # Special: indicates large number
        }

        text_lower = text.lower()

        # Check for number words
        for word, value in NUMBER_WORDS.items():
            # Use word boundary regex to avoid partial matches
            pattern = r'\b' + word + r'\b'
            if re.search(pattern, text_lower):
                return (word.upper(), value)

        # Check for digits
        digit_match = re.search(r'\b(\d+)\s*(tips?|items?|examples?|steps?|ways?|methods?)', text_lower)
        if digit_match:
            num = int(digit_match.group(1))
            return (f"NUM_{num}", num)

        return None
    
    def parse_output_format(self, text: str) -> Optional[OutputFormat]:
        """Parse desired output format"""
        format_type = self.vocab.get_output_format(text)
        if format_type:
            return OutputFormat(format_type=format_type)
        return None

    def extract_specifications(self, text: str) -> Optional[dict]:
        """
        Extract numeric specifications from text

        FIXES:
        - "10 lines" → LINES=10
        - "three tips" → COUNT=3
        - "5 examples" → COUNT=5
        """
        text_lower = text.lower()
        specs = {}

        # Pattern 1: Digit + unit
        patterns = [
            (r'(\d+)\s*lines?', 'LINES'),
            (r'(\d+)\s*words?', 'WORDS'),
            (r'(\d+)\s*(?:items?|things?|elements?)', 'ITEMS'),
            (r'(\d+)\s*(?:tips?|suggestions?)', 'COUNT'),
            (r'(\d+)\s*(?:examples?|instances?)', 'COUNT'),
            (r'(\d+)\s*(?:steps?|stages?)', 'STEPS'),
            (r'(\d+)\s*(?:ways?|methods?)', 'COUNT'),
        ]

        for pattern, spec_type in patterns:
            match = re.search(pattern, text_lower)
            if match:
                specs[spec_type] = int(match.group(1))

        # Pattern 2: Word numbers
        NUMBER_WORDS = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }

        for word, num in NUMBER_WORDS.items():
            # Check for "three tips", "five examples", etc.
            pattern = r'\b' + word + r'\s+(\w+)'
            match = re.search(pattern, text_lower)
            if match:
                following_word = match.group(1)
                if following_word in ['tips', 'examples', 'items', 'ways', 'methods', 'steps']:
                    if 'COUNT' not in specs:  # Don't override if already set
                        specs['COUNT'] = num

        return specs if specs else None