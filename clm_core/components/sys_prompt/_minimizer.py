import re
from typing import Optional

try:
    import spacy
    from spacy.matcher import Matcher
    from spacy.language import Language
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None  # type: ignore
    Matcher = None  # type: ignore
    Language = None  # type: ignore


class ConfigurationPromptMinimizer:
    """
    Minimizes configuration prompts by removing redundant instructions,
    priority explanations, and trimming verbose sections.

    Uses spaCy for linguistic analysis when available, falls back to regex.
    """

    # Keywords that indicate a meta-instruction (about following rules)
    META_KEYWORDS = {
        "paramount", "custom instructions", "adapt culturally",
        "basic rules", "custom rules", "enhance naturally",
        "preserve language" # When combined with "adapt" or "enhance"
    }

    # Patterns for sentences that should be dropped
    DROP_PATTERNS = [
        # Priority/conflict explanations (must have both terms)
        (r"follow the basic rules", r"prioritize"),
        (r"if there are conflicts", r"prioritize"),
        (r"conflicts between", r"custom instructions"),

        # Redundant meta-instructions (standalone)
        (r"custom instructions are paramount", None),
    ]

    _nlp: Optional["Language"] = None

    @classmethod
    def _get_nlp(cls) -> Optional["Language"]:
        """Lazy load spaCy model."""
        if not SPACY_AVAILABLE:
            return None

        if cls._nlp is None:
            try:
                cls._nlp = spacy.load("en_core_web_sm")
            except OSError:
                cls._nlp = spacy.blank("en")
                cls._nlp.add_pipe("sentencizer")
        return cls._nlp

    @classmethod
    def minimize(cls, nl_prompt: str, cl_metadata: Optional[dict] = None) -> str:
        """
        Minimize the natural language prompt by removing redundant content.

        Args:
            nl_prompt: The original natural language prompt

        Returns:
            Minimized prompt with redundant content removed
        """
        nlp = cls._get_nlp()
        if nlp is not None:
            out = cls._minimize_with_spacy(nl_prompt, nlp)
        else:
            out = cls._minimize_with_regex(nl_prompt)

        if "<basic_rules>" in out.lower():
            out = cls._trim_basic_rules(out)

        out = cls._clean_general_prompt(out)

        return out.strip()

    @classmethod
    def _minimize_with_spacy(cls, text: str, nlp: "Language") -> str:
        """
        Use spaCy for more robust sentence-level analysis and filtering.

        Args:
            text: Input text
            nlp: spaCy Language model

        Returns:
            Filtered text with droppable sentences removed
        """
        # Parse the text, but skip XML-like blocks for sentence analysis
        blocks = cls._extract_blocks(text)

        result_parts = []

        for block_type, content in blocks:
            if block_type == "xml":
                result_parts.append(content)
            else:
                doc = nlp(content)

                kept_sentences = []
                for sent in doc.sents:
                    if not cls._should_drop_sentence(sent):
                        kept_sentences.append(sent.text)

                if kept_sentences:
                    result_parts.append(" ".join(kept_sentences))

        return "\n".join(result_parts)

    @classmethod
    def _should_drop_sentence(cls, sent) -> bool:
        """
        Determine if a sentence should be dropped based on linguistic patterns.

        This method is conservative - it only drops sentences that are clearly
        meta-instructions about following/prioritizing rules, not actual task
        constraints that happen to use similar vocabulary.

        Args:
            sent: spaCy Span object representing a sentence

        Returns:
            True if the sentence should be dropped
        """
        sent_text_lower = sent.text.lower().strip()

        if "output" in sent_text_lower or "only" in sent_text_lower:
            return False

        for pattern_tuple in cls.DROP_PATTERNS:
            if isinstance(pattern_tuple, tuple):
                pattern1, pattern2 = pattern_tuple
                if re.search(pattern1, sent_text_lower, re.IGNORECASE):
                    if pattern2 is None or re.search(pattern2, sent_text_lower, re.IGNORECASE):
                        return True

        if sent_text_lower.startswith("remember:"):
            return cls._is_meta_instruction(sent_text_lower)

        has_priority = any(word in sent_text_lower for word in ["prioritize", "priority", "paramount"])
        has_conflict = any(word in sent_text_lower for word in ["conflict", "conflicts"])
        if has_priority and has_conflict:
            return True

        if "follow" in sent_text_lower and "rule" in sent_text_lower and "custom" in sent_text_lower:
            return True

        if len(sent_text_lower) < 50 and cls._is_standalone_meta_fragment(sent_text_lower):
            return True

        return False

    @classmethod
    def _is_meta_instruction(cls, text: str) -> bool:
        """
        Determine if text is a meta-instruction about following rules.

        Meta-instructions are statements about how to follow/prioritize rules,
        not actual task constraints.

        Args:
            text: Lowercase sentence text

        Returns:
            True if this is a meta-instruction that should be dropped
        """
        for keyword in cls.META_KEYWORDS:
            if keyword in text:
                return True

        meta_patterns = [
            r"adapt\s+culturally",
            r"preserve\s+language.*enhance",
            r"enhance.*preserve\s+language",
        ]

        for pattern in meta_patterns:
            if re.search(pattern, text):
                return True

        return False

    @classmethod
    def _is_standalone_meta_fragment(cls, text: str) -> bool:
        """
        Determine if a short sentence is a standalone meta-instruction fragment.

        These are typically imperative fragments like:
        - "Adapt culturally."
        - "Preserve language."
        - "Enhance naturally."

        But NOT full sentences with context like:
        - "When translating, adapt culturally to the target audience."

        Args:
            text: Lowercase sentence text

        Returns:
            True if this is a standalone meta-fragment
        """
        # Strip sentence and check length (fragments are typically very short)
        text = text.strip().rstrip(".")

        # If it contains connecting words, it's likely a full sentence, not a fragment
        connecting_words = ["when", "if", "while", "to", "for", "with", "by", "the"]
        if any(word in text.split() for word in connecting_words):
            return False

        # Check for meta-instruction patterns (simple imperative forms)
        fragment_patterns = [
            r"^adapt culturally$",
            r"^preserve language$",
            r"^enhance naturally$",
            r"^follow\s+(the\s+)?(basic\s+)?rules$",
        ]

        for pattern in fragment_patterns:
            if re.match(pattern, text):
                return True

        return False

    @classmethod
    def _extract_blocks(cls, text: str) -> list[tuple[str, str]]:
        """
        Extract XML-like blocks and plain text segments.

        Args:
            text: Input text with XML-like tags

        Returns:
            List of (block_type, content) tuples where block_type is 'xml' or 'text'
        """
        blocks = []
        pattern = r'(<[^>]+>.*?</[^>]+>)'

        parts = re.split(pattern, text, flags=re.DOTALL)

        for part in parts:
            if not part.strip():
                continue

            if re.match(r'<[^>]+>.*?</[^>]+>', part, re.DOTALL):
                blocks.append(("xml", part))
            else:
                blocks.append(("text", part))

        return blocks

    @classmethod
    def _minimize_with_regex(cls, text: str) -> str:
        """
        Fall back to regex-based minimization when spaCy is not available.

        Args:
            text: Input text

        Returns:
            Filtered text
        """
        out = text

        # Remove explicit priority explanations
        out = re.sub(
            r"Follow the basic rules.*?custom instructions.*?\.",
            "",
            out,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Remove "Remember:" statements
        out = re.sub(
            r"Remember:\s*[^.]*\.",
            "",
            out,
            flags=re.IGNORECASE,
        )

        # Remove conflict/priority statements
        out = re.sub(
            r"[^.]*if there are conflicts[^.]*\.",
            "",
            out,
            flags=re.IGNORECASE,
        )

        return out

    @staticmethod
    def _trim_basic_rules(text: str) -> str:
        """
        Replace verbose basic_rules content with a minimized version.

        Args:
            text: Input text containing <basic_rules> block

        Returns:
            Text with trimmed basic_rules
        """
        def replacer(match):
            return """<basic_rules>
            • Detect input language automatically
            • Apply appropriate grammar and style
            • Improve clarity and readability
            • Output only the enhanced text
            </basic_rules>"""

        return re.sub(
            r"<basic_rules>.*?</basic_rules>",
            replacer,
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

    @staticmethod
    def _clean_general_prompt(text: str) -> str:
        """
        Clean the general_prompt block by removing priority/conflict statements.

        Args:
            text: Input text containing <general_prompt> block

        Returns:
            Text with cleaned general_prompt
        """
        def replacer(match):
            content = match.group(1)

            content = re.sub(
                r"\s*Follow the basic rules[^.]*prioritize[^.]*\.",
                "",
                content,
                flags=re.IGNORECASE,
            )

            content = re.sub(
                r"\s*[Ii]f there are conflicts[^.]*\.",
                "",
                content,
                flags=re.IGNORECASE,
            )

            return f"<general_prompt>{content.strip()}</general_prompt>"

        return re.sub(
            r"<general_prompt>(.*?)</general_prompt>",
            replacer,
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
