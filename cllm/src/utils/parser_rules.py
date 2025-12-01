import re
from abc import ABC, abstractmethod


class BaseRules(ABC):
    """
    Abstract base class for language-specific pattern matching rules.
    Contains shared compilation logic while language classes define the patterns.
    """

    def __init__(self):
        """Initialize and compile all patterns on instantiation"""
        self._compile_patterns()

    @property
    @abstractmethod
    def DOMAIN_REGEX(self) -> dict[str, str]:
        raise NotImplementedError("Subclasses must implement DOMAIN_REGEX")

    @property
    @abstractmethod
    def COMPARISON_MAP(self) -> dict[str, str]:
        """Comparison keywords: differences, similarities, pros/cons, tradeoffs"""
        pass

    @property
    @abstractmethod
    def DURATION_PATTERNS(self) -> list[str]:
        """Regex patterns for duration extraction (minutes, hours)"""
        pass

    @property
    @abstractmethod
    def STANDARD_FIELD_KEYWORDS(self) -> dict[str, str]:
        """Standard extraction fields: issue, problem, error, names, dates, etc."""
        pass

    @property
    @abstractmethod
    def AUDIENCE_MAP(self) -> dict[str, str]:
        """Target audience keywords: non-technical, beginner, expert, etc."""
        pass

    @property
    @abstractmethod
    def LENGTH_MAP(self) -> dict[str, str]:
        """Length preferences: brief, short, detailed, comprehensive"""
        pass

    @property
    @abstractmethod
    def STYLE_MAP(self) -> dict[str, str]:
        """Style preferences: simple, formal, professional"""
        pass

    @property
    @abstractmethod
    def TONE_MAP(self) -> dict[str, str]:
        """Tone preferences: professional, casual, empathetic"""
        pass

    @property
    @abstractmethod
    def NUMBER_WORDS(self) -> dict[str, int]:
        """Number words mapping: one->1, two->2, few->-1, etc."""
        pass

    @property
    @abstractmethod
    def SPEC_PATTERNS(self) -> list[tuple[str, str]]:
        """Specification patterns: (pattern, label) for lines, words, items, steps"""
        pass

    @property
    @abstractmethod
    def PROGRAMMING_LANGUAGE_PATTERN(self) -> list[tuple[str, str]]:
        """Programming language detection: (pattern, language)"""
        pass

    @property
    @abstractmethod
    def EXTRACTION_INDICATORS(self) -> list[str]:
        """Verbs indicating extraction intent: extract, identify, find, etc."""
        pass

    @property
    @abstractmethod
    def QA_CRITERIA(self) -> dict[str, str]:
        """QA/compliance criteria: verification, policy, compliance, etc."""
        pass

    @property
    @abstractmethod
    def QA_INDICATORS(self) -> list[str]:
        """QA indicators: score, qa, quality assurance, audit"""
        pass

    @property
    @abstractmethod
    def QUESTION_PATTERNS(self) -> list[tuple[str, int]]:
        """Question patterns: (regex, group_index)"""
        pass

    @property
    @abstractmethod
    def EXPLAIN_PATTERNS(self) -> list[tuple[str, int]]:
        """Explanation patterns: (regex, group_index)"""
        pass

    @property
    @abstractmethod
    def CONCEPT_PATTERN(self) -> tuple[str, int]:
        """Concept pattern: (regex, group_index)"""
        pass

    @property
    @abstractmethod
    def PROCEDURE_PATTERN(self) -> tuple[str, int]:
        """Procedure pattern: (regex, group_index)"""
        pass

    @property
    @abstractmethod
    def CLEANUP_TAIL(self) -> str:
        """Pattern for cleaning up trailing words"""
        pass

    @property
    @abstractmethod
    def SUBJECT_PATTERNS(self) -> list[tuple[str, str]]:
        """Subject type patterns: verb, noun, tip, method, etc."""
        pass

    @property
    @abstractmethod
    def TYPE_MAP(self) -> dict[str, str]:
        """Communication type mapping: call, meeting, chat, etc."""
        pass

    @property
    @abstractmethod
    def CONTEXT_MAP(self) -> dict[str, str]:
        """Context mapping: customer, support, sales, technical"""
        pass

    @property
    @abstractmethod
    def ISSUE_PATTERNS(self) -> list[str]:
        """Issue extraction patterns: about X, regarding X"""
        pass

    def _compile_patterns(self):
        """Compile all regex patterns for efficient matching"""
        self.COMPILED = {
            "comparison": [
                (re.compile(p, re.I), v) for p, v in self.COMPARISON_MAP.items()
            ],
            "standard": [
                (re.compile(p, re.I), v)
                for p, v in self.STANDARD_FIELD_KEYWORDS.items()
            ],
            "audience": [
                (re.compile(p, re.I), v) for p, v in self.AUDIENCE_MAP.items()
            ],
            "length": [(re.compile(p, re.I), v) for p, v in self.LENGTH_MAP.items()],
            "style": [(re.compile(p, re.I), v) for p, v in self.STYLE_MAP.items()],
            "tone": [(re.compile(p, re.I), v) for p, v in self.TONE_MAP.items()],
            "specs": [(re.compile(p, re.I), name) for p, name in self.SPEC_PATTERNS],
            "extraction_indicators": [
                re.compile(p, re.I) for p in self.EXTRACTION_INDICATORS
            ],
            "qa_criteria": [
                (re.compile(p, re.I), v) for p, v in self.QA_CRITERIA.items()
            ],
            "qa_indicators": [re.compile(p, re.I) for p in self.QA_INDICATORS],
            "questions": [
                (re.compile(p, re.I), group) for p, group in self.QUESTION_PATTERNS
            ],
            "explain": [
                (re.compile(p, re.I), group) for p, group in self.EXPLAIN_PATTERNS
            ],
            "concept": re.compile(self.CONCEPT_PATTERN[0], re.I),
            "procedure": re.compile(self.PROCEDURE_PATTERN[0], re.I),
            "subject_patterns": [
                (re.compile(p, re.I), label) for p, label in self.SUBJECT_PATTERNS
            ],
            "issue_patterns": [re.compile(p, re.I) for p in self.ISSUE_PATTERNS],
            "language_patterns": [
                (re.compile(p, re.I), lang)
                for p, lang in self.PROGRAMMING_LANGUAGE_PATTERN
            ],
        }

    @property
    def ctx_patterns(self) -> dict[str, list[tuple[str, str]]]:
        """
        Returns a dictionary of context patterns for different categories.
        Categories:
        - LANGUAGE
        - REGION
        - SLA
        - FORMAT
        - PRIORITY
        """
        return {
            "LANGUAGE": [
                (r"\benglish\b", "ENGLISH"),
                (r"\bspanish\b", "SPANISH"),
                (r"\bfrench\b", "FRENCH"),
                (r"\bgerman\b", "GERMAN"),
                (r"\bchinese\b", "CHINESE"),
                (r"\bjapanese\b", "JAPANESE"),
            ],
            "REGION": [
                (r"\b(us|usa|american)\b", "US"),
                (r"\b(uk|british|england)\b", "UK"),
                (r"\b(europe|eu)\b", "EU"),
                (r"\b(apac|asia pacific)\b", "APAC"),
                (r"\bcanada|ca\b", "CA"),
            ],
            "PRIORITY": [
                (r"\burgent\b", "URGENT"),
                (r"\bpriority\b", "HIGH_PRIORITY"),
                (r"\basap\b", "URGENT"),
                (r"\bimmediately\b", "URGENT"),
            ],
            "SLA": [
                (r"\bwithin\s+(\d+)\s*(hours|hrs|h)\b", "SLA_HOURS"),
                (r"\brespond by\b", "SLA_DEADLINE"),
            ],
            "FORMAT": [
                (r"\bbullet(s)?\b", "BULLET_POINTS"),
                (r"\bnumbered\b", "NUMBERED_LIST"),
                (r"\btable\b", "TABLE"),
                (r"\bparagraph\b", "PARAGRAPH"),
            ],
        }

    def match_comparison(self, text: str) -> str | None:
        """Match comparison type in text"""
        for pattern, value in self.COMPILED["comparison"]:
            if pattern.search(text):
                return value
        return None

    def match_standard_field(self, text: str) -> str | None:
        """Match standard extraction field in text"""
        for pattern, value in self.COMPILED["standard"]:
            if pattern.search(text):
                return value
        return None

    def match_audience(self, text: str) -> str | None:
        """Match target audience in text"""
        for pattern, value in self.COMPILED["audience"]:
            if pattern.search(text):
                return value
        return None

    def match_length(self, text: str) -> str | None:
        """Match length preference in text"""
        for pattern, value in self.COMPILED["length"]:
            if pattern.search(text):
                return value
        return None

    def match_style(self, text: str) -> str | None:
        """Match style preference in text"""
        for pattern, value in self.COMPILED["style"]:
            if pattern.search(text):
                return value
        return None

    def match_tone(self, text: str) -> str | None:
        """Match tone preference in text"""
        for pattern, value in self.COMPILED["tone"]:
            if pattern.search(text):
                return value
        return None

    def match_specs(self, text: str) -> list[tuple[str, int]]:
        """Match specification patterns (lines, words, items, etc.)"""
        results = []
        for pattern, name in self.COMPILED["specs"]:
            match = pattern.search(text)
            if match:
                results.append((name, int(match.group(1))))
        return results

    def match_programming_language(self, text: str) -> str | None:
        """Match programming language in text"""
        for pattern, lang in self.COMPILED["language_patterns"]:
            if pattern.search(text):
                return lang
        return None

    def has_extraction_indicator(self, text: str) -> bool:
        """Check if text has extraction indicators"""
        return any(
            pattern.search(text) for pattern in self.COMPILED["extraction_indicators"]
        )

    def match_qa_criteria(self, text: str) -> list[str]:
        """Match QA criteria in text"""
        results = []
        for pattern, value in self.COMPILED["qa_criteria"]:
            if pattern.search(text):
                results.append(value)
        return results

    def has_qa_indicator(self, text: str) -> bool:
        """Check if text has QA indicators"""
        return any(pattern.search(text) for pattern in self.COMPILED["qa_indicators"])

    def extract_question_subject(self, text: str) -> str | None:
        """Extract subject from question patterns"""
        for pattern, group in self.COMPILED["questions"]:
            match = pattern.search(text)
            if match:
                return match.group(group).strip()
        return None

    def extract_explain_subject(self, text: str) -> str | None:
        """Extract subject from explain patterns"""
        for pattern, group in self.COMPILED["explain"]:
            match = pattern.search(text)
            if match:
                return match.group(group).strip()
        return None

    def extract_concept(self, text: str) -> str | None:
        """Extract concept from text"""
        match = self.COMPILED["concept"].search(text)
        if match:
            return match.group(self.CONCEPT_PATTERN[1]).strip()
        return None

    def extract_procedure(self, text: str) -> str | None:
        """Extract procedure from text"""
        match = self.COMPILED["procedure"].search(text)
        if match:
            return match.group(self.PROCEDURE_PATTERN[1]).strip()
        return None

    def match_subject_pattern(self, text: str) -> str | None:
        """Match subject pattern label"""
        for pattern, label in self.COMPILED["subject_patterns"]:
            if pattern.search(text):
                return label
        return None

    def cleanup_tail(self, text: str) -> str:
        """Remove trailing prepositions and common words"""
        return re.sub(self.CLEANUP_TAIL, "", text, flags=re.I).strip()

    def extract_issue_context(self, text: str) -> str | None:
        """Extract issue context from patterns"""
        for pattern in self.COMPILED["issue_patterns"]:
            match = pattern.search(text)
            if match:
                return match.group(1).strip()
        return None

    def parse_number_word(self, word: str) -> int | None:
        """Parse number word to integer"""
        return self.NUMBER_WORDS.get(word.lower())
