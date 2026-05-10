import re
from typing import Optional, Annotated

from annotated_doc import Doc as _Doc
from spacy import Language
from spacy.tokens import Doc

from thread_encoder.components._target.domain import DomainDetector
from thread_encoder.utils.vocabulary import BaseVocabulary

from thread_encoder.utils.parser_rules import BaseRules


class AttributeEnhancer:
    """
    Enhances targets with rich attributes

    Extracts:
    - TOPIC (for CONCEPT, PROCEDURE)
    - SUBJECT (for CONTENT, ITEMS)
    - TYPE, DURATION, CONTEXT (for specific targets)
    - DOMAIN, LANG (technical metadata)
    """

    def __init__(
        self,
        *,
        nlp: Annotated[
            Language,
            _Doc("spaCy language model used for domain and language detection."),
        ],
        vocab: Annotated[
            BaseVocabulary, _Doc("Vocabulary instance for the target language.")
        ],
        rules: Annotated[BaseRules, _Doc("Language-specific parsing rules.")],
    ) -> None:
        self.nlp = nlp
        self._vocab = vocab
        self.rules = rules

        self.topic_extractor = TopicExtractor(nlp=nlp, vocab=vocab, rules=rules)
        self.subject_detector = SubjectDetector(rules=rules)
        self.rich_extractor = RichAttributeExtractor(rules=rules)
        self.domain_detector = DomainDetector(nlp=nlp, vocab=vocab, rules=rules)
        self.language_detector = LanguageDetector(vocab=vocab, rules=rules)

    def enhance(
        self,
        target_token: Annotated[
            str,
            _Doc(
                "Canonical target token string (e.g. 'CONCEPT', 'CODE') that determines which attribute types to extract."
            ),
        ],
        text: Annotated[
            str, _Doc("Original input text used for attribute and domain detection.")
        ],
        doc: Annotated[
            Doc, _Doc("Pre-computed spaCy Doc for domain and language detection.")
        ],
    ) -> dict[str, str]:
        attributes = {}

        if target_token in ["CONCEPT", "PROCEDURE", "ANSWER", "FACT"]:
            topic = self.topic_extractor.extract(text, target_token, doc)
            if topic:
                attributes["TOPIC"] = topic

        if target_token in ["CONTENT", "ITEMS", "ANSWER", "DOCUMENT"]:
            subject = self.subject_detector.detect(text)
            if subject:
                attributes["SUBJECT"] = subject

        if target_token == "RESULT":
            type_match = re.search(
                r"(?:calculate|compute|find) (?:the )?([\w\s]+)", text.lower()
            )
            if type_match:
                result_type = type_match.group(1).strip()
                attributes["TYPE"] = result_type.replace(" ", "_").upper()

        attributes.update(self.rich_extractor.extract(text, target_token))

        domain, _ = self.domain_detector.detect(text, doc=doc)
        if domain:
            attributes["DOMAIN"] = domain

        lang = self.language_detector.detect(text)
        if lang:
            attributes["LANG"] = lang

        return attributes


class TopicExtractor:
    """Extracts TOPIC attribute using centralized rules."""

    def __init__(
        self,
        nlp: Annotated[
            Language, _Doc("spaCy language model for noun chunk iteration.")
        ],
        vocab: Annotated[
            BaseVocabulary,
            _Doc(
                "Vocabulary instance providing STOPWORDS, DEMONSTRATIVES, PRONOUNS, MODALS, and ACTION_VERBS."
            ),
        ],
        rules: Annotated[
            BaseRules,
            _Doc(
                "Language-specific rules for question/explain/concept/procedure pattern matching."
            ),
        ],
    ):
        self.nlp = nlp
        self._vocab = vocab
        self._rules = rules

    def extract(
        self,
        text: Annotated[str, _Doc("Input text to extract a TOPIC value from.")],
        target: Annotated[
            str,
            _Doc(
                "The target token type (e.g. 'CONCEPT', 'PROCEDURE') providing context for topic extraction."
            ),
        ],
        doc: Annotated[
            Doc,
            _Doc(
                "Pre-computed spaCy Doc providing noun chunks for fallback topic detection."
            ),
        ],
    ) -> Optional[str]:
        text_lower = text.lower()

        if m := self._rules.extract_question_subject(text_lower):
            topic = self._clean_topic(m)
            if topic:
                return self._format_topic(topic)

        if m := self._rules.extract_explain_subject(text_lower):
            topic = self._clean_topic(m)
            if topic:
                return self._format_topic(topic)

        concept = self._rules.extract_concept(text_lower)
        if concept:
            topic = self._clean_topic(concept)
            if topic:
                return self._format_topic(topic)

        procedure = self._rules.extract_procedure(text_lower)
        if procedure:
            topic = self._clean_topic(procedure)
            if topic:
                return self._format_topic(topic)

        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower().strip()

            if chunk_text in self._vocab.STOPWORDS:
                continue

            for prefix in self._vocab.DEMONSTRATIVES:
                if chunk_text.startswith(prefix + " "):
                    chunk_text = chunk_text[len(prefix) :].strip()

            if not chunk_text or chunk_text in self._vocab.STOPWORDS:
                continue

            if len(chunk_text) > 3:
                cleaned = self._clean_topic(chunk_text)
                if cleaned:
                    formatted = self._format_topic(cleaned)
                    valid = self._validate_topic(formatted)
                    if valid:
                        return valid
        return None

    def _format_topic(
        self,
        topic: Annotated[
            str, _Doc("Raw topic string to uppercase and underscore-delimit.")
        ],
    ) -> str:
        return topic.replace(" ", "_").replace("'", "").upper()

    def _validate_topic(
        self,
        topic: Annotated[
            str,
            _Doc(
                "Formatted topic string to validate; rejected if too short or purely non-alphabetic."
            ),
        ],
    ) -> Optional[str]:
        if not topic or len(topic) < 2:
            return None
        if re.match(r"^[\d\W_]+$", topic):
            return None
        return topic

    def _clean_topic(
        self,
        topic: Annotated[
            str,
            _Doc(
                "Raw topic string to strip of pronouns, demonstratives, modals, articles, and trailing action verbs."
            ),
        ],
    ) -> Optional[str]:
        if not topic:
            return None

        t = topic.strip()
        for p in self._vocab.PRONOUNS:
            t = re.sub(rf"^{p}\s+", "", t, flags=re.I)

        for d in self._vocab.DEMONSTRATIVES:
            t = re.sub(rf"^{d}\s+", "", t, flags=re.I)

        for m in self._vocab.MODALS:
            t = re.sub(rf"^{m}\s+", "", t, flags=re.I)

        t = re.sub(r"^(the|a|an)\s+", "", t, flags=re.I)
        for verb in self._vocab.ACTION_VERBS:
            t = re.sub(rf"\b{verb}\b", "", t, flags=re.I)

        t = self._rules.cleanup_tail(t)
        t = re.sub(r"\s+", " ", t).strip()
        return t if t else None


class SubjectDetector:
    """Detect SUBJECT attribute using Rules.SUBJECT_PATTERNS."""

    def __init__(
        self,
        rules: Annotated[
            BaseRules,
            _Doc(
                "Language-specific rules providing compiled SUBJECT_PATTERNS for matching."
            ),
        ],
    ) -> None:
        self._rules = rules

    def detect(
        self,
        text: Annotated[str, _Doc("Input text to match against subject patterns.")],
    ) -> Optional[str]:
        text_lower = text.lower()
        if label := self._rules.match_subject_pattern(text_lower):
            return label

        return None


class RichAttributeExtractor:
    """Extracts TYPE, CONTEXT, ISSUE, DURATION etc. using centralized rules."""

    def __init__(
        self,
        rules: Annotated[
            BaseRules,
            _Doc(
                "Language-specific rules providing DURATION_PATTERNS, TYPE_MAP, CONTEXT_MAP, and issue pattern matching."
            ),
        ],
    ):
        self.rules = rules

    def extract(
        self,
        text: Annotated[str, _Doc("Input text to extract rich attributes from.")],
        target_type: Annotated[
            str,
            _Doc(
                "The target token type (e.g. 'TRANSCRIPT', 'TICKET') that determines which attribute types are extracted."
            ),
        ],
    ) -> dict[str, str]:
        attrs = {}
        text_lower = text.lower()

        if target_type in ["TRANSCRIPT", "CALL", "MEETING"]:
            for pattern in self.rules.DURATION_PATTERNS:
                m = re.search(pattern, text_lower)
                if m:
                    minutes = int(m.group(1))
                    if "hour" in pattern or "hr" in pattern:
                        minutes *= 60
                    attrs["DURATION"] = str(minutes)

        if target_type in ["TRANSCRIPT", "DOCUMENT"]:
            for k, v in self.rules.TYPE_MAP.items():
                if k in text_lower:
                    attrs["TYPE"] = v

        for keyword, v in self.rules.CONTEXT_MAP.items():
            if keyword in text_lower:
                attrs["CONTEXT"] = v
                break

        if target_type in ["COMPLAINT", "TICKET"]:
            if m := self.rules.extract_issue_context(text):
                attrs["ISSUE"] = m.replace(" ", "_").upper()
        return attrs


class LanguageDetector:
    """Detects programming language using centralized Rules."""

    def __init__(
        self,
        *,
        vocab: Annotated[
            BaseVocabulary,
            _Doc(
                "Vocabulary providing CODE_INDICATORS to gate programming language detection."
            ),
        ],
        rules: Annotated[
            BaseRules,
            _Doc(
                "Language-specific rules with compiled PROGRAMMING_LANGUAGE_PATTERN entries."
            ),
        ],
    ):
        self._vocab = vocab
        self._rules = rules

    def detect(
        self,
        text: Annotated[
            str, _Doc("Input text to scan for programming language indicators.")
        ],
    ) -> Optional[str]:
        text_lower = text.lower()

        if not any(ind in text_lower for ind in self._vocab.CODE_INDICATORS):
            return None

        if lang := self._rules.match_programming_language(text_lower):
            return lang.upper()
        return None
