"""
Target extraction strategies
Each extractor handles a specific pattern type
"""

import re
from typing import Optional, List
from spacy.tokens import Doc

from .attributes import AttributeEnhancer
from .domain import DomainDetector
from .patterns import CX_TECHNICAL_CONCEPTS, TECHNICAL_CONCEPTS
from ... import Target


class BaseExtractor:
    """Base class for all extractors"""

    def __init__(self, nlp, vocab):
        self.nlp = nlp
        self.vocab = vocab
        self.attribute_enhancer = AttributeEnhancer(nlp)
        self.domain_parser = DomainDetector(nlp)


class ImperativeExtractor(BaseExtractor):
    """
    Extracts targets from imperative commands

    Examples:
        "Analyze this code" → CODE
        "Summarize this transcript" → TRANSCRIPT
        "Classify this ticket" → TICKET
    """

    def extract(self, text: str, req_tokens: Optional[List[str]], doc: Doc) -> Optional[Target]:
        """Extract target from imperative pattern"""
        text_lower = text.lower().strip()

        # Pattern 1: List/Name/Enumerate
        if re.match(r'^(list|name|enumerate|itemize)\s+', text_lower):
            return self._create_target("ITEMS", text, doc)

        # Pattern 2: Calculate/Compute
        if re.match(r'^(calculate|compute|determine|find\s+the)\s+', text_lower):
            return self._create_target("RESULT", text, doc)

        # Pattern 3: Extract/Identify
        if re.match(r'^(extract|identify|find)\s+', text_lower):
            return self._create_target("DATA", text, doc)

        # Pattern 4: Analyze
        if re.match(r'^(analyze|review|examine|evaluate)\s+', text_lower):
            if 'code' in text_lower[:30]:
                return self._create_target("CODE", text, doc)
            elif 'data' in text_lower[:30]:
                return self._create_target("DATA", text, doc)
            else:
                return self._create_target("DOCUMENT", text, doc)

        # Pattern 5: Generate/Create
        if re.match(r'^(generate|create|write|draft)\s+', text_lower):
            return self._create_target("CONTENT", text, doc)

        # Pattern 6: Classify
        if re.match(r'^classify\s+', text_lower):
            if 'ticket' in text_lower[:30]:
                return self._create_target("TICKET", text, doc)
            elif 'email' in text_lower[:30]:
                return self._create_target("EMAIL", text, doc)
            else:
                return self._create_target("CONTENT", text, doc)

        # Pattern 7: Summarize
        if re.match(r'^summarize\s+', text_lower):
            target_token = self._detect_summarize_target(text_lower)
            return self._create_target(target_token, text, doc)

        # Pattern 8: Optimize
        if re.match(r'^optimize\s+', text_lower):
            if 'query' in text_lower[:30] or 'sql' in text_lower[:30]:
                return self._create_target("QUERY", text, doc)
            else:
                return self._create_target("CODE", text, doc)

        # Pattern 9: Debug
        if re.match(r'^debug\s+', text_lower):
            return self._create_target("CODE", text, doc)

        # Pattern 10: Transform/Convert
        if re.match(r'^(convert|transform|translate|rewrite)\s+', text_lower):
            target_token = self._detect_transform_target(text_lower)
            return self._create_target(target_token, text, doc)

        return None

    def _create_target(self, token: str, text: str, doc: Doc) -> Target:
        """Create target with full attributes"""
        attributes = self.attribute_enhancer.enhance(token, text, doc)
        return Target(token=token, attributes=attributes)

    def _detect_summarize_target(self, text_lower: str) -> str:
        """Detect specific target for summarize commands"""
        if 'transcript' in text_lower:
            return "TRANSCRIPT"
        elif 'call' in text_lower:
            return "CALL"
        elif 'meeting' in text_lower:
            return "MEETING"
        elif 'article' in text_lower or 'report' in text_lower:
            return "DOCUMENT"
        else:
            return "DOCUMENT"

    def _detect_transform_target(self, text_lower: str) -> str:
        """Detect what's being transformed"""
        if 'transcript' in text_lower[:40]:
            return "TRANSCRIPT"
        elif 'document' in text_lower[:40] or 'documentation' in text_lower[:40]:
            return "DOCUMENT"
        elif 'proposal' in text_lower[:40]:
            return "DOCUMENT"
        else:
            return "CONTENT"


class QuestionExtractor(BaseExtractor):
    """Extracts targets from questions"""

    def extract(self, text: str, doc: Doc) -> Optional[Target]:
        """Extract target from question pattern"""
        if not text.strip().endswith('?'):
            return None

        text_lower = text.lower()
        domain, _ = self.domain_parser.detect(text)

        if any(text_lower.startswith(q) for q in ['what', 'who', 'where', 'when', 'why', 'how']):
            attributes = self.attribute_enhancer.enhance("CONCEPT", text, doc)
            return Target(token="CONCEPT", attributes=attributes, domain=domain)

        return None


class NounExtractor(BaseExtractor):
    """Extracts targets from direct noun matches"""

    def extract(self, text: str, doc: Doc) -> List[Target]:
        """Extract targets from nouns"""
        targets = []
        domain, _ = self.domain_parser.detect(text)

        # Direct noun matches
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"]:
                target_token = self.vocab.get_target_token(token.text)
                if target_token:
                    attributes = self.attribute_enhancer.enhance(target_token, text, doc)
                    targets.append(Target(token=target_token, attributes=attributes, domain=domain))

        # Noun phrases
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            target_token = self.vocab.get_target_token(chunk_text)
            if target_token:
                if not any(t.token == target_token for t in targets):
                    attributes = self.attribute_enhancer.enhance(target_token, text, doc)
                    targets.append(Target(token=target_token, attributes=attributes, domain=domain))

        return targets


class CompoundExtractor(BaseExtractor):
    """Extracts compound phrase targets"""

    COMPOUND_PHRASES = {
        "customer support": "TICKET",
        "support ticket": "TICKET",
        "email message": "EMAIL",
        "chat transcript": "TRANSCRIPT",
        "phone call": "CALL",
        "source code": "CODE",
    }

    def extract(self, text: str, doc: Doc) -> List[Target]:
        """Extract compound phrase targets"""
        targets = []
        text_lower = text.lower()
        domain, _ = self.domain_parser.detect(text)

        for phrase, target_token in self.COMPOUND_PHRASES.items():
            if phrase in text_lower:
                attributes = self.attribute_enhancer.enhance(target_token, text, doc)
                targets.append(Target(token=target_token, attributes=attributes, domain=domain))

        return targets


class PatternExtractor(BaseExtractor):
    """Extracts targets from specific patterns"""

    def extract(self, text: str, doc: Doc) -> List[Target]:
        """Extract from patterns like 'this X', 'for X', concepts"""
        targets = []
        domain, _ = self.domain_parser.detect(text)

        # "this X" pattern
        this_target = self._detect_this_pattern(doc, text)
        if this_target:
            this_target.domain = domain
            targets.append(this_target)

        # "for X" pattern
        for_target = self._detect_for_pattern(text, doc)
        if for_target:
            for_target.domain = domain
            targets.append(for_target)

        # Concept detection
        concept_target = self._detect_concept(text, doc)
        if concept_target:
            concept_target.domain = domain
            targets.append(concept_target)

        return targets

    def _detect_this_pattern(self, doc: Doc, text: str) -> Optional[Target]:
        """Detect 'this X' patterns"""
        for i, token in enumerate(doc):
            if token.text.lower() == "this" and i + 1 < len(doc):
                next_token = doc[i + 1]
                if next_token.pos_ in ["NOUN", "PROPN"]:
                    target_token = self.vocab.get_target_token(next_token.text.lower())
                    if target_token:
                        attributes = self.attribute_enhancer.enhance(target_token, text, doc)
                        return Target(token=target_token, attributes=attributes)
        return None

    def _detect_for_pattern(self, text: str, doc: Doc) -> Optional[Target]:
        """Detect 'for X' patterns"""
        text_lower = text.lower()

        for_patterns = {
            r'for\s+(?:a|an|the)?\s*(?:\w+\s+)*?business plan': 'PLAN',
            r'for\s+(?:a|an|the)?\s*(?:\w+\s+)*?product': 'DESCRIPTION',
            r'for\s+(?:a|an|the)?\s*(?:\w+\s+)*?report': 'REPORT',
        }

        for pattern, target_token in for_patterns.items():
            if re.search(pattern, text_lower):
                attributes = self.attribute_enhancer.enhance(target_token, text, doc)
                return Target(token=target_token, attributes=attributes)

        return None

    def _detect_concept(self, text: str, doc: Doc) -> Optional[Target]:
        """Detect concept targets"""
        text_lower = text.lower()

        # Pattern 1: "concept of X"
        if "concept of" in text_lower:
            attributes = self.attribute_enhancer.enhance("CONCEPT", text, doc)
            return Target(token="CONCEPT", attributes=attributes)

        # Pattern 2: Explanation requests
        if any(verb in text_lower for verb in ["explain", "describe", "clarify", "define"]):
            # Check if it's explaining a specific concept
            if not any(target in text_lower for target in ["code", "data", "document"]):
                attributes = self.attribute_enhancer.enhance("CONCEPT", text, doc)
                return Target(token="CONCEPT", attributes=attributes)

        # Pattern 3: Known technical concepts
        concepts = TECHNICAL_CONCEPTS + CX_TECHNICAL_CONCEPTS
        for concept in concepts:
            if concept in text_lower:
                attributes = self.attribute_enhancer.enhance("CONCEPT", text, doc)
                return Target(token="CONCEPT", attributes=attributes)

        return None


class FallbackExtractor(BaseExtractor):
    """Fallback target extraction based on REQ tokens"""

    def extract(self, text: str, req_tokens: Optional[List[str]], doc: Doc) -> Optional[Target]:
        """Fallback extraction"""
        if not req_tokens:
            return Target(token="ANSWER", attributes={})

        text_lower = text.lower()

        if "GENERATE" in req_tokens or "CREATE" in req_tokens:
            if any(word in text_lower for word in ["list", "items", "examples"]):
                return self._create_target("ITEMS", text, doc)
            else:
                return self._create_target("CONTENT", text, doc)

        if "EXPLAIN" in req_tokens or "DESCRIBE" in req_tokens:
            return self._create_target("CONCEPT", text, doc)

        return self._create_target("ANSWER", text, doc)

    def _create_target(self, token: str, text: str, doc: Doc) -> Target:
        """Create target with attributes"""
        attributes = self.attribute_enhancer.enhance(token, text, doc)
        domain, _ = self.domain_parser.detect(text)
        return Target(token=token, attributes=attributes, domain=domain)