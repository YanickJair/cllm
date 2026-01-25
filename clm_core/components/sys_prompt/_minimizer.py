import re
from typing import Optional, Literal

from spacy import Language

from ._schemas import SysPromptConfig
from clm_core.components.sys_prompt.analyzers.output_format import SysPromptOutputFormat


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
        "preserve language"
    }
    ROLE_BLOCK_PATTERN = [
        r"<general_prompt>.*?</general_prompt>",
        r"<role>.*?</role>",
    ]
    # Pattern to match "You are a..." role sentences (for non-XML prompts)
    ROLE_SENTENCE_PATTERN = re.compile(
        r"(?:^|\n)\s*(?:You are|Your role is)\s+(?:an?\s+)?[^.]+\.\s*",
        re.IGNORECASE
    )
    # Pattern to match SCORING sections with ranges
    SCORING_SECTION_PATTERN = re.compile(
        r"(?:^|\n\n?)(?:SCORING|SCORE RANGES?|RATING):?\s*\n"
        r"(?:[\d.]+\s*[-–]\s*[\d.]+\s*[:=]?\s*[^\n]+\n?)+",
        re.IGNORECASE | re.MULTILINE
    )
    PRIORITY_PATTERNS = [
        r"if there (is|are) (any )?conflicts.*?(prioritize|override).*",
        r"custom instructions.*?(override|take precedence).*",
        r"remember:.*?(priority|override).*",
        r"\bin case of conflicts?\b.*\b(follow|use)\b.*\b(custom|user)\b",
    ]
    RULE_INTENT_PATTERNS = [
        r"the following rules.*",
        r"please adhere to.*rules.*",
        r"these rules (apply|must be followed).*",
        r"\bplease\b.*\b(follow|adhere to|comply with)\b.*\brules?\b",
        r"\bthese rules\b.*\b(should|must|need to)\b.*\b(followed|applied)\b",
        r"\bensure that\b.*\brules?\b.*\b(followed|applied)\b",
    ]

    CL_NL_SUPPRESSION_MAP = {
        "priority": {
            "enabled": True,
            "patterns": [...],
            "scope": "sentence",  # type: Literal["sentence", "block"]
        },
        "rules": {
            "enabled": True,
            "patterns": [...],
            "scope": "sentence",
        },
        "output_format": {
            "enabled": True,
            "patterns": [...],
            "scope": "sentence",
        },
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

    def __init__(
        self,
            *,
        nlp: Language,
        config: SysPromptConfig,
    ):
        self._nlp = nlp
        self._cfg = config
        if "sentencizer" not in self._nlp.pipe_names:
            self._nlp.add_pipe("sentencizer")

    def suppress_with_cl(self, out: str, cl_metadata: dict) -> str:
        if cl_metadata.get("role"):
            out = self.suppress_role(text=out, patterns=self.ROLE_BLOCK_PATTERN)
            # Also remove "You are a..." sentences for non-XML prompts
            out = self.ROLE_SENTENCE_PATTERN.sub("", out)

        if cl_metadata.get("priority"):
            out = self.suppress_sentences(out, self.PRIORITY_PATTERNS)

        if cl_metadata.get("rules"):
            out = self.suppress_sentences(out, self.RULE_INTENT_PATTERNS)

        if cl_metadata.get("output_format"):
            output_analyzer = SysPromptOutputFormat(self._cfg)
            out, _ = output_analyzer.extract_output_block(out)
            out = self.SCORING_SECTION_PATTERN.sub("", out)
        return out.strip()


    @staticmethod
    def suppress_role(text: str, patterns: list[str]) -> str:
        for pattern in patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)
        return text

    @staticmethod
    def suppress_sentences(text: str, patterns: list[str]) -> str:
        """
        Remove sentences matching any of the given regex patterns.
        Operates ONLY on free text, never on blocks, lists, or schemas.
        """
        compiled_patterns = [
            re.compile(pat, re.IGNORECASE)
            for pat in patterns
        ]

        def should_drop(sentence: str) -> bool:
            sent = sentence.strip().lower()

            if not sent:
                return False

            if any(k in sent for k in ("output", "return", "include", "format", "must", "shall")):
                return False

            if sent.startswith(("-", "•")):
                return False
            if re.match(r"\d+\.", sent):
                return False

            if "{" in sent or "}" in sent:
                return False

            for pat in compiled_patterns:
                if pat.search(sent):
                    return True

            return False

        lines = text.splitlines()
        output_lines = []

        buffer = []

        def flush_buffer():
            if not buffer:
                return
            paragraph = " ".join(buffer).strip()
            buffer.clear()

            sentences = re.split(r"(?<=[.!?])\s+", paragraph)

            kept = [
                s for s in sentences
                if not should_drop(s)
            ]

            if kept:
                output_lines.append(" ".join(kept))

        for line in lines:
            stripped = line.strip()

            if not stripped:
                flush_buffer()
                output_lines.append("")
                continue

            if (
                stripped.startswith("<")
                or stripped.endswith(">")
                or stripped.startswith("{")
                or stripped.startswith("}")
            ):
                flush_buffer()
                output_lines.append(line)
                continue

            if stripped.startswith(("-", "•")) or re.match(r"\d+\.", stripped):
                flush_buffer()
                output_lines.append(line)
                continue

            buffer.append(stripped)

        flush_buffer()

        return "\n".join(output_lines).strip()

    def minimize(self, nl_prompt: str, cl_metadata: Optional[dict] = None) -> str:
        """
        Minimize the natural language prompt by removing redundant content.

        Args:
            nl_prompt: The original natural language prompt
            cl_metadata: CL metadata for Prompt compression

        Returns:
            Minimized prompt with redundant content removed
        """
        out = self._minimize_with_spacy(nl_prompt)

        if "<basic_rules>" in out.lower():
            out = self._trim_basic_rules(out)

        if cl_metadata:
            out = self.suppress_with_cl(out=out, cl_metadata=cl_metadata)
        out = self._clean_general_prompt(out)
        return out.strip()

    def _minimize_with_spacy(self, text: str) -> str:
        """
        Use spaCy for more robust sentence-level analysis and filtering.

        Args:
            text: Input text
            nlp: spaCy Language model

        Returns:
            Filtered text with droppable sentences removed
        """
        # Parse the text, but skip XML-like blocks for sentence analysis
        blocks = self._extract_blocks(text)

        result_parts = []

        for block_type, content in blocks:
            if block_type == "xml":
                result_parts.append(content)
            else:
                doc = self._nlp(content)

                kept_sentences = []
                for sent in doc.sents:
                    if not self._should_drop_sentence(sent):
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
            return (
                "<basic_rules>"
                "• Detect input language automatically "
                "• Apply appropriate grammar and style "
                "• Improve clarity and readability "
                "• Output only the enhanced text"
                "</basic_rules>"
            )

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
