import re
from typing import Optional, List
from spacy.tokens import Doc
from spacy.language import Language

from clm_core.utils.parser_rules import BaseRules
from clm_core.utils.vocabulary import BaseVocabulary

from .attributes import AttributeEnhancer
from .domain import DomainDetector

# TODO: Implement this for each lang
from clm_core.dictionary.en.patterns import CX_TECHNICAL_CONCEPTS, TECHNICAL_CONCEPTS
from clm_core.components.sys_prompt import Target


class BaseExtractor:
    """Base class for all extractors"""

    def __init__(self, *, nlp: Language, vocab: BaseVocabulary, rules: BaseRules):
        self.nlp = nlp
        self.vocab = vocab
        self.attribute_enhancer = AttributeEnhancer(nlp=nlp, vocab=vocab, rules=rules)
        self.domain_parser = DomainDetector(nlp=nlp, vocab=vocab, rules=rules)

        self._build_pattern_helpers()

    def _build_pattern_helpers(self):
        """Build regex patterns from vocabulary"""

        def make_pattern(synonyms):
            escaped = [re.escape(s) for s in synonyms]
            return "|".join(escaped)

        self.list_pattern = make_pattern(self.vocab.REQ_TOKENS.get("LIST", []))
        self.calculate_pattern = make_pattern(
            self.vocab.REQ_TOKENS.get("CALCULATE", [])
        )
        self.extract_pattern = make_pattern(self.vocab.REQ_TOKENS.get("EXTRACT", []))
        self.analyze_pattern = make_pattern(self.vocab.REQ_TOKENS.get("ANALYZE", []))
        self.generate_pattern = make_pattern(self.vocab.REQ_TOKENS.get("GENERATE", []))
        self.classify_pattern = make_pattern(self.vocab.REQ_TOKENS.get("CLASSIFY", []))
        self.summarize_pattern = make_pattern(
            self.vocab.REQ_TOKENS.get("SUMMARIZE", [])
        )
        self.optimize_pattern = make_pattern(self.vocab.REQ_TOKENS.get("OPTIMIZE", []))
        self.debug_pattern = make_pattern(self.vocab.REQ_TOKENS.get("DEBUG", []))
        self.transform_pattern = make_pattern(
            self.vocab.REQ_TOKENS.get("TRANSFORM", [])
        )
        self.explain_pattern = make_pattern(self.vocab.REQ_TOKENS.get("EXPLAIN", []))

        # Build target detection helpers
        self.code_synonyms = set(
            s.lower() for s in self.vocab.TARGET_TOKENS.get("CODE", [])
        )
        self.data_synonyms = set(
            s.lower() for s in self.vocab.TARGET_TOKENS.get("DATA", [])
        )
        self.document_synonyms = set(
            s.lower() for s in self.vocab.TARGET_TOKENS.get("DOCUMENT", [])
        )
        self.transcript_synonyms = set(
            s.lower() for s in self.vocab.TARGET_TOKENS.get("TRANSCRIPT", [])
        )
        self.ticket_synonyms = set(
            s.lower() for s in self.vocab.TARGET_TOKENS.get("TICKET", [])
        )
        self.email_synonyms = set(
            s.lower() for s in self.vocab.TARGET_TOKENS.get("EMAIL", [])
        )
        self.query_synonyms = set(
            s.lower() for s in self.vocab.TARGET_TOKENS.get("QUERY", [])
        )
        self.call_synonyms = set(
            s.lower() for s in self.vocab.TARGET_TOKENS.get("CALL", [])
        )
        self.meeting_synonyms = set(s.lower() for s in self.vocab.MEETING_WORDS)
        self.proposal_synonyms = set(s.lower() for s in self.vocab.PROPOSAL_WORDS)

        # Build quantifier/list indicators
        self.list_indicators = set(
            s.lower() for s in self.vocab.REQ_TOKENS.get("LIST", [])
        )
        if "ITEMS" in self.vocab.TARGET_TOKENS:
            self.list_indicators.update(
                s.lower() for s in self.vocab.TARGET_TOKENS["ITEMS"]
            )
        # Add quantifiers if vocabulary has them
        if hasattr(self.vocab, "QUANTIFIER_WORDS"):
            self.list_indicators.update(s.lower() for s in self.vocab.QUANTIFIER_WORDS)

    def _contains_any(
        self, text_lower: str, word_set: set[str], window: Optional[int] = None
    ) -> bool:
        """Check if text contains any word from set, optionally within first N chars"""
        check_text = text_lower[:window] if window else text_lower
        return any(word in check_text for word in word_set)


class ImperativeExtractor(BaseExtractor):
    """
    Extracts targets from imperative commands
    Language-agnostic using vocabulary
    """

    def __init__(self, nlp: Language, vocab: BaseVocabulary, rules: BaseRules):
        super().__init__(nlp=nlp, vocab=vocab, rules=rules)

    def extract(
        self, text: str, req_tokens: Optional[List[str]], doc: Doc
    ) -> Optional[Target]:
        """
        Extracts targets from imperative commands

        Args:
            text (str): The text to extract targets from
            req_tokens (Optional[List[str]]): Required tokens for extraction
            doc (Doc): The document to extract targets from

        Returns:
            Optional[Target]: The extracted target or None if no target is found
        """
        text_lower = text.lower().strip()

        if re.match(rf"^({self.list_pattern})\s+", text_lower, re.IGNORECASE):
            return self._create_target("ITEMS", text, doc)

        if re.match(rf"^({self.calculate_pattern})\s+", text_lower, re.IGNORECASE):
            return self._create_target("RESULT", text, doc)

        if re.match(rf"^({self.extract_pattern})\s+", text_lower, re.IGNORECASE):
            return self._create_target("DATA", text, doc)

        if re.match(rf"^({self.analyze_pattern})\s+", text_lower, re.IGNORECASE):
            if self._contains_any(text_lower, self.code_synonyms, window=30):
                return self._create_target("CODE", text, doc)
            elif self._contains_any(text_lower, self.data_synonyms, window=30):
                return self._create_target("DATA", text, doc)
            else:
                return self._create_target("DOCUMENT", text, doc)

        if re.match(rf"^({self.generate_pattern})\s+", text_lower, re.IGNORECASE):
            return self._create_target("CONTENT", text, doc)

        if re.match(rf"^({self.classify_pattern})\s+", text_lower, re.IGNORECASE):
            if self._contains_any(text_lower, self.ticket_synonyms, window=30):
                return self._create_target("TICKET", text, doc)
            elif self._contains_any(text_lower, self.email_synonyms, window=30):
                return self._create_target("EMAIL", text, doc)
            else:
                return self._create_target("CONTENT", text, doc)

        if re.match(rf"^({self.summarize_pattern})\s+", text_lower, re.IGNORECASE):
            target_token = self._detect_summarize_target(text_lower)
            return self._create_target(target_token, text, doc)

        if re.match(rf"^({self.optimize_pattern})\s+", text_lower, re.IGNORECASE):
            if self._contains_any(text_lower, self.query_synonyms, window=30):
                return self._create_target("QUERY", text, doc)
            else:
                return self._create_target("CODE", text, doc)

        if re.match(rf"^({self.debug_pattern})\s+", text_lower, re.IGNORECASE):
            return self._create_target("CODE", text, doc)

        if re.match(rf"^({self.transform_pattern})\s+", text_lower, re.IGNORECASE):
            target_token = self._detect_transform_target(text_lower)
            return self._create_target(target_token, text, doc)

        return None

    def _create_target(self, token: str, text: str, doc: Doc) -> Target:
        """Create target with full attributes"""
        attributes = self.attribute_enhancer.enhance(token, text, doc)
        return Target(token=token, attributes=attributes)

    def _detect_summarize_target(self, text_lower: str) -> str:
        """Detect specific target for summarize commands (language-agnostic)"""

        if self._contains_any(text_lower, self.transcript_synonyms):
            return "TRANSCRIPT"

        elif self._contains_any(text_lower, self.call_synonyms):
            return "CALL"

        elif self._contains_any(text_lower, self.meeting_synonyms):
            return "MEETING"

        elif self._contains_any(text_lower, self.document_synonyms):
            return "DOCUMENT"
        else:
            return "DOCUMENT"

    def _detect_transform_target(self, text_lower: str) -> str:
        """Detect what's being transformed (language-agnostic)"""

        if self._contains_any(text_lower, self.transcript_synonyms, window=40):
            return "TRANSCRIPT"
        elif self._contains_any(text_lower, self.document_synonyms, window=40):
            return "DOCUMENT"

        elif self._contains_any(text_lower[:40], self.proposal_synonyms):
            return "DOCUMENT"
        else:
            return "CONTENT"


class QuestionExtractor(BaseExtractor):
    """Extracts targets from questions (language-agnostic)"""

    def __init__(self, nlp: Language, vocab: BaseVocabulary, rules: BaseRules):
        super().__init__(nlp=nlp, vocab=vocab, rules=rules)

        self.question_words = [q.lower() for q in self.vocab.QUESTION_WORDS]

    def extract(self, text: str, doc: Doc) -> Optional[Target]:
        """Extract target from question pattern"""
        if not text.strip().endswith("?"):
            return None

        text_lower = text.lower()
        domain, _ = self.domain_parser.detect(text)

        if any(text_lower.startswith(qw) for qw in self.question_words):
            attributes = self.attribute_enhancer.enhance("CONCEPT", text, doc)
            return Target(token="CONCEPT", attributes=attributes, domain=domain)

        return None


class NounExtractor(BaseExtractor):
    """Extracts targets from direct noun matches (language-agnostic)"""

    def __init__(self, nlp: Language, vocab: BaseVocabulary, rules: BaseRules):
        super().__init__(nlp=nlp, vocab=vocab, rules=rules)

    def extract(self, text: str, doc: Doc) -> List[Target]:
        """Extract targets from nouns"""
        targets = []
        domain, _ = self.domain_parser.detect(text)

        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"]:
                target_token = self.vocab.get_target_token(token.text)
                if target_token:
                    attributes = self.attribute_enhancer.enhance(
                        target_token, text, doc
                    )
                    targets.append(
                        Target(token=target_token, attributes=attributes, domain=domain)
                    )

        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            target_token = self.vocab.get_target_token(chunk_text)
            if target_token:
                if not any(t.token == target_token for t in targets):
                    attributes = self.attribute_enhancer.enhance(
                        target_token, text, doc
                    )
                    targets.append(
                        Target(token=target_token, attributes=attributes, domain=domain)
                    )

        return targets


class CompoundExtractor(BaseExtractor):
    """Extracts compound phrase targets (language-agnostic)"""

    def __init__(self, nlp: Language, vocab: BaseVocabulary, rules: BaseRules):
        super().__init__(nlp=nlp, vocab=vocab, rules=rules)

        self._build_compound_phrases()

    def _build_compound_phrases(self):
        """Build language-specific compound phrases"""
        self.compound_phrases = {}

        for target_token, synonyms in self.vocab.TARGET_TOKENS.items():
            for syn in synonyms:
                if " " in syn:
                    self.compound_phrases[syn.lower()] = target_token

        if hasattr(self.vocab, "COMPOUND_PHRASES"):
            self.compound_phrases.update(
                {k.lower(): v for k, v in self.vocab.COMPOUND_PHRASES.items()}
            )

    def extract(self, text: str, doc: Doc) -> List[Target]:
        """Extract compound phrase targets"""
        targets = []
        text_lower = text.lower()
        domain, _ = self.domain_parser.detect(text)

        for phrase, target_token in self.compound_phrases.items():
            if phrase in text_lower:
                attributes = self.attribute_enhancer.enhance(target_token, text, doc)
                targets.append(
                    Target(token=target_token, attributes=attributes, domain=domain)
                )

        return targets


class PatternExtractor(BaseExtractor):
    """Extracts targets from specific patterns (language-agnostic)"""

    def __init__(self, nlp: Language, vocab: BaseVocabulary, rules: BaseRules):
        super().__init__(nlp=nlp, vocab=vocab, rules=rules)

        self.demonstratives = self.vocab.DEMONSTRATIVES
        self.demonstratives_lower = [d.lower() for d in self.demonstratives]

    def extract(self, text: str, doc: Doc) -> List[Target]:
        """Extract from patterns like 'this X', 'for X', concepts

        Args:
            text (str): The input text to extract targets from.
            doc (Doc): The spaCy document object representing the input text.

        Returns:
            List[Target]: A list of extracted targets.

        Examples:
            >>> extractor = TargetExtractor(nlp, vocab)
            >>> text = "this is a test"
            >>> doc = nlp(text)
            >>> extractor.extract(text, doc)
            [Target(text='this', domain='general', type='demonstrative')]
        """
        targets = []
        domain, _ = self.domain_parser.detect(text)

        this_target = self._detect_this_pattern(doc, text)
        if this_target:
            this_target.domain = domain
            targets.append(this_target)

        for_target = self._detect_for_pattern(text, doc)
        if for_target:
            for_target.domain = domain
            targets.append(for_target)

        concept_target = self._detect_concept(text, doc)
        if concept_target:
            concept_target.domain = domain
            targets.append(concept_target)

        return targets

    def _detect_this_pattern(self, doc: Doc, text: str) -> Optional[Target]:
        """Detect 'this X' patterns (language-agnostic)"""
        for i, token in enumerate(doc):
            if token.text.lower() in self.demonstratives_lower and i + 1 < len(doc):
                next_token = doc[i + 1]
                if next_token.pos_ in ["NOUN", "PROPN"]:
                    target_token = self.vocab.get_target_token(next_token.text.lower())
                    if target_token:
                        attributes = self.attribute_enhancer.enhance(
                            target_token, text, doc
                        )
                        return Target(token=target_token, attributes=attributes)
        return None

    def _detect_for_pattern(self, text: str, doc: Doc) -> Optional[Target]:
        """
        Detect 'for X' patterns (language-agnostic using vocabulary)

        Args:
            text (str): The text to analyze.
            doc (Doc): The spaCy document object.

        Returns:
            Optional[Target]: The detected target or None if no target is found.

        Example:
            >>> text = "for a cat"
            >>> doc = nlp(text)
            >>> extractor = TargetExtractor()
            >>> extractor._detect_for_pattern(text, doc)
            Target(token=Token(text='cat', pos='NOUN'), attributes={'type': 'animal', 'color': 'unknown'})
        """
        text_lower = text.lower()

        for target_token, synonyms in self.vocab.TARGET_TOKENS.items():
            for syn in synonyms:
                pattern = rf"for\s+(?:a|an|the|um|uma|o|a|un|une|le|la)?\s*(?:\w+\s+)*?{re.escape(syn)}"
                if re.search(pattern, text_lower):
                    attributes = self.attribute_enhancer.enhance(
                        target_token, text, doc
                    )
                    return Target(token=target_token, attributes=attributes)

        return None

    def _detect_concept(self, text: str, doc: Doc) -> Optional[Target]:
        """
        Detect concept targets (language-agnostic)

        Args:
            text (str): The text to analyze.
            doc (Doc): The spaCy document object.

        Returns:
            Optional[Target]: The detected target or None if no target is found.

        Examples:
            >>> _detect_concept("for the concept of", Doc("for the concept of"))
            Target(token='CONCEPT', attributes={'type': 'concept', 'scope': 'global'})
            >>> _detect_concept("for the concept of", Doc("for the concept of"))
            Target(token='CONCEPT', attributes={'type': 'concept', 'scope': 'global'})
        """
        text_lower = text.lower()

        concept_phrases = ["concept of", "conceito de", "concepto de", "concept de"]
        if any(phrase in text_lower for phrase in concept_phrases):
            attributes = self.attribute_enhancer.enhance("CONCEPT", text, doc)
            return Target(token="CONCEPT", attributes=attributes)

        explain_synonyms = set(
            s.lower() for s in self.vocab.REQ_TOKENS.get("EXPLAIN", [])
        )
        if any(verb in text_lower for verb in explain_synonyms):
            if not (
                self._contains_any(text_lower, self.code_synonyms)
                or self._contains_any(text_lower, self.data_synonyms)
                or self._contains_any(text_lower, self.document_synonyms)
            ):
                attributes = self.attribute_enhancer.enhance("CONCEPT", text, doc)
                return Target(token="CONCEPT", attributes=attributes)

        concepts = TECHNICAL_CONCEPTS + CX_TECHNICAL_CONCEPTS
        for concept in concepts:
            if concept in text_lower:
                attributes = self.attribute_enhancer.enhance("CONCEPT", text, doc)
                return Target(token="CONCEPT", attributes=attributes)

        return None


class FallbackExtractor(BaseExtractor):
    def __init__(self, nlp: Language, vocab: BaseVocabulary, rules: BaseRules):
        super().__init__(nlp=nlp, vocab=vocab, rules=rules)

    def extract(
        self, text: str, req_tokens: Optional[List[str]], doc: Doc
    ) -> Optional[Target]:
        """
        Extract target from text

        Args:
            text (str): The text to extract the target from.
            req_tokens (Optional[List[str]]): The required tokens to extract the target.
            doc (Doc): The document to extract the target from.

        Returns:
            Optional[Target]: The extracted target.

        Example:
            >>> extractor = FallbackExtractor(nlp, vocab)
            >>> extractor.extract("What is the capital of France?", ["EXPLAIN"], doc)
            Target(token="CONCEPT", attributes={'text': 'What is the capital of France?', 'doc': <Doc>})
        """
        if not req_tokens:
            return Target(token="ANSWER", attributes={})

        text_lower = text.lower()

        if "GENERATE" in req_tokens or "CREATE" in req_tokens:
            if any(indicator in text_lower for indicator in self.list_indicators):
                return self._create_target("ITEMS", text, doc)
            else:
                return self._create_target("CONTENT", text, doc)

        if "EXPLAIN" in req_tokens or "DESCRIBE" in req_tokens:
            return self._create_target("CONCEPT", text, doc)

        return self._create_target("ANSWER", text, doc)

    def _create_target(self, token: str, text: str, doc: Doc) -> Target:
        """
        Create target with attributes

        Args:
            token (str): The token to create the target for.
            text (str): The text to create the target from.
            doc (Doc): The document to create the target from.

        Returns:
            Target: The created target.

        Examples:
            >>> extractor = FallbackExtractor(nlp, vocab)
            >>> doc = nlp("What is the capital of France?")
            >>> target = extractor._create_target("ANSWER", "Paris", doc)
            >>> target.token
            'ANSWER'
            >>> target.attributes
            {'type': 'ANSWER'}
            >>> target.domain
            'GEOGRAPHY'
        """
        attributes = self.attribute_enhancer.enhance(token, text, doc)
        domain, _ = self.domain_parser.detect(text)
        return Target(token=token, attributes=attributes, domain=domain)
