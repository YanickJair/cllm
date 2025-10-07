# Improved target_extractor.py
import re
from typing import Optional
from spacy import Language
from spacy.tokens import Doc, Token

from src.core import Target
from src.core.vocabulary import Vocabulary


class TargetExtractor:
    """
    Extracts target objects (TARGET tokens) from text

    IMPROVEMENTS:
    - Fallback TARGET system for when nothing detected
    - Better question pattern detection
    - Imperative command handling
    - Math/calculation default targets
    - Priority-based extraction strategy
    """

    def __init__(self, nlp: Language) -> None:
        self.nlp = nlp
        self.vocab = Vocabulary()

        self.technical_concepts = [
            "quantum computing", "machine learning", "deep learning", "neural networks",
            "blockchain", "cryptocurrency", "artificial intelligence", "ai",
            "dns", "tcp", "http", "https", "api", "rest", "graphql",
            "docker", "kubernetes", "microservices", "serverless",
            "react", "vue", "angular", "node.js", "python", "javascript",
            "sql", "nosql", "database", "cloud computing", "aws", "azure", "gcp"
        ]

    def extract(self, text: str, detected_req_tokens: list[str] = None) -> list[Target]:
        """
        Extract target objects from text with fallback system

        Args:
            text: Input prompt text
            detected_req_tokens: Optional list of REQ tokens already detected (helps with fallback)

        Returns:
            List of detected Target objects (always at least 1 if fallback enabled)
        """
        doc = self.nlp(text)
        targets: list[Target] = []

        # PRIORITY 1: Explicit pattern matching (highest confidence)
        # These take precedence over everything else
        imperative_target = self._detect_imperative_target(text, detected_req_tokens)
        if imperative_target:
            return [imperative_target]

        question_target = self._detect_question_target(text, doc)
        if question_target:
            return [question_target]

        # PRIORITY 2: Direct noun matches
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"]:
                target_token = self.vocab.get_target_token(token.text)
                if target_token:
                    targets.append(Target(
                        token=target_token,
                        attributes={}
                    ))

        # PRIORITY 3: Noun phrases
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            target_token = self.vocab.get_target_token(chunk_text)
            if target_token:
                if not any(t.token == target_token for t in targets):
                    targets.append(Target(
                        token=target_token,
                        attributes={}
                    ))

        # PRIORITY 4: Compound phrases (multi-word matching)
        compound_targets = self._detect_compound_phrases(text)
        for target in compound_targets:
            if not any(t.token == target.token for t in targets):
                targets.append(target)

        # PRIORITY 5: Pattern-based detection
        this_target = self._detect_this_pattern(doc)
        if this_target:
            if not any(t.token == this_target.token for t in targets):
                targets.append(this_target)

        for_target = self._detect_for_pattern(text)
        if for_target:
            if not any(t.token == for_target.token for t in targets):
                targets.append(for_target)

        concept_target = self._detect_concept_target(text, doc)
        if concept_target:
            if not any(t.token == "CONCEPT" for t in targets):
                targets.append(concept_target)

        # PRIORITY 6: Fallback system (NEW!)
        # If NO targets found, provide intelligent fallback based on context
        if not targets:
            fallback = self._get_fallback_target(text, doc, detected_req_tokens)
            if fallback:
                targets.append(fallback)

        # Add domain attributes
        return self._add_domain_attributes(targets, text)

    def _detect_imperative_target(self, text: str, req_tokens: list[str] = None) -> Optional[Target]:
        """
        NEW: Detect targets for imperative commands at sentence start

        Handles:
        - "List X" → ITEMS
        - "Name X" → ITEMS
        - "Calculate X" → RESULT
        - "Generate X" → depends on X
        - "Create X" → depends on X

        Args:
            text: Prompt text
            req_tokens: Already detected REQ tokens (helps determine target)
        """
        text_lower = text.lower().strip()

        # Pattern 1: List/Name/Enumerate → ITEMS
        if re.match(r'^(list|name|enumerate|itemize)\s+', text_lower):
            # Check if it's listing specific things vs generating content
            if any(word in text_lower[:50] for word in
                   ["benefits", "examples", "types", "reasons", "ways", "methods", "steps"]):
                return Target(token="ITEMS", attributes={"TYPE": "LIST"})
            return Target(token="ITEMS", attributes={})

        # Pattern 2: Calculate/Compute → RESULT
        if re.match(r'^(calculate|compute|determine|find\s+the)\s+', text_lower):
            # Extract what's being calculated
            calc_match = re.search(r'^(?:calculate|compute|determine|find\s+the)\s+([\w\s]+?)(?:\.|$|\n|of)',
                                   text_lower)
            if calc_match:
                calc_type = calc_match.group(1).strip()
                return Target(token="RESULT", attributes={"TYPE": calc_type.upper()})
            return Target(token="RESULT", attributes={})

        # Pattern 3: Generate/Create/Write → context-dependent
        if re.match(r'^(generate|create|write|draft|compose)\s+', text_lower):
            # Look for specific content types
            content_types = {
                "story": "CONTENT",
                "essay": "CONTENT",
                "article": "CONTENT",
                "email": "EMAIL",
                "report": "REPORT",
                "summary": "SUMMARY",
                "list": "ITEMS",
                "code": "CODE",
                "script": "CODE",
                "function": "CODE",
                "description": "DESCRIPTION"
            }

            for content_type, target in content_types.items():
                if content_type in text_lower[:50]:
                    return Target(token=target, attributes={})

            # Default for creative generation
            return Target(token="CONTENT", attributes={})

        return None

    def _detect_question_target(self, text: str, doc: Doc) -> Optional[Target]:
        """
        IMPROVED: Better question pattern detection with fallbacks

        Patterns:
        - "What is X?" → CONCEPT or DEFINITION
        - "How to X?" → PROCEDURE
        - "How does X work?" → CONCEPT
        - "Why X?" → EXPLANATION
        - "When/Where X?" → FACT
        - "Who is X?" → PERSON (maps to CONCEPT with TYPE=PERSON)
        """
        text_lower = text.lower().strip()

        # Pattern 1: "What is/are X?"
        if text_lower.startswith(("what is", "what are", "what's")):
            # Try to extract the subject
            match = re.search(r'what\s+(?:is|are|\'s)\s+(.+?)(?:\?|$)', text_lower)
            if match:
                subject = match.group(1).strip()
                # Remove common filler words
                subject = re.sub(r'^(the|a|an)\s+', '', subject)

                return Target(
                    token="CONCEPT",
                    attributes={"TOPIC": subject.upper().replace(" ", "_"), "TYPE": "DEFINITION"}
                )
            return Target(token="CONCEPT", attributes={"TYPE": "DEFINITION"})

        # Pattern 2: "How to X?" or "How do I X?"
        if text_lower.startswith(("how to", "how do i", "how can i", "how do you")):
            match = re.search(r'how\s+(?:to|do\s+(?:i|you)|can\s+i)\s+(.+?)(?:\?|$)', text_lower)
            if match:
                action = match.group(1).strip()
                return Target(
                    token="PROCEDURE",
                    attributes={"ACTION": action.upper().replace(" ", "_")}
                )
            return Target(token="PROCEDURE", attributes={})

        # Pattern 3: "How does X work?"
        if re.match(r'how\s+(?:does|do)\s+', text_lower):
            match = re.search(r'how\s+(?:does|do)\s+(.+?)(?:\s+work|\?|$)', text_lower)
            if match:
                subject = match.group(1).strip()
                return Target(
                    token="CONCEPT",
                    attributes={"TOPIC": subject.upper().replace(" ", "_"), "TYPE": "MECHANISM"}
                )
            return Target(token="CONCEPT", attributes={"TYPE": "MECHANISM"})

        # Pattern 4: "Why X?"
        if text_lower.startswith("why"):
            return Target(token="EXPLANATION", attributes={})

        # Pattern 5: "When X?" or "Where X?"
        if text_lower.startswith(("when", "where")):
            return Target(token="FACT", attributes={})

        # Pattern 6: "Who is X?"
        if text_lower.startswith(("who is", "who are", "who was", "who were")):
            match = re.search(r'who\s+(?:is|are|was|were)\s+(.+?)(?:\?|$)', text_lower)
            if match:
                person = match.group(1).strip()
                return Target(
                    token="CONCEPT",
                    attributes={"TOPIC": person.upper().replace(" ", "_"), "TYPE": "PERSON"}
                )
            return Target(token="CONCEPT", attributes={"TYPE": "PERSON"})

        return None

    def _get_fallback_target(self, text: str, doc: Doc, req_tokens: list[str] = None) -> Optional[Target]:
        """
        NEW: Intelligent fallback when no target detected

        Uses REQ tokens + text patterns to infer appropriate target

        Args:
            text: Prompt text
            doc: spaCy doc
            req_tokens: List of detected REQ tokens
        """
        text_lower = text.lower()
        req_tokens = req_tokens or []

        # Strategy 1: Match by REQ token type
        if "GENERATE" in req_tokens or "LIST" in req_tokens:
            # Check if it's creative vs factual content
            creative_indicators = ["story", "poem", "essay", "narrative", "creative", "fiction"]
            if any(ind in text_lower for ind in creative_indicators):
                return Target(token="CONTENT", attributes={})

            # Check for list generation
            list_indicators = ["list", "benefits", "examples", "reasons", "ways", "types", "methods"]
            if any(ind in text_lower[:30] for ind in list_indicators):
                return Target(token="ITEMS", attributes={})

            return Target(token="CONTENT", attributes={})

        if "CALCULATE" in req_tokens:
            return Target(token="RESULT", attributes={})

        if "ANALYZE" in req_tokens or "EVALUATE" in req_tokens:
            # Look for what's being analyzed
            analysis_targets = {
                "code": "CODE",
                "data": "DATA",
                "document": "DOCUMENT",
                "text": "DOCUMENT",
                "performance": "METRICS",
                "strategy": "STRATEGY"
            }
            for keyword, target in analysis_targets.items():
                if keyword in text_lower:
                    return Target(token=target, attributes={})

            # Default: analyzing some content
            return Target(token="CONTENT", attributes={})

        if "EXPLAIN" in req_tokens or "DESCRIBE" in req_tokens:
            return Target(token="CONCEPT", attributes={})

        if "COMPARE" in req_tokens:
            return Target(token="OPTIONS", attributes={})

        if "EXTRACT" in req_tokens:
            # Extracting information from something
            return Target(token="DATA", attributes={})

        if "TRANSFORM" in req_tokens:
            # Transforming some content
            return Target(token="CONTENT", attributes={})

        if "CLASSIFY" in req_tokens:
            return Target(token="ITEMS", attributes={"ACTION": "CLASSIFY"})

        # Strategy 2: Pattern-based fallback
        # Simple sentence structure: check for common patterns
        if any(word in text_lower[:20] for word in ["list", "name", "enumerate"]):
            return Target(token="ITEMS", attributes={})

        if any(word in text_lower[:20] for word in ["explain", "describe", "tell"]):
            return Target(token="CONCEPT", attributes={})

        if any(word in text_lower[:20] for word in ["create", "write", "generate"]):
            return Target(token="CONTENT", attributes={})

        # Strategy 3: Question detection (if missed by question detector)
        if text.strip().endswith("?"):
            if text_lower.startswith("what"):
                return Target(token="CONCEPT", attributes={})
            if text_lower.startswith("how"):
                return Target(token="PROCEDURE", attributes={})
            # Generic question
            return Target(token="ANSWER", attributes={})

        # Strategy 4: Last resort - generic target based on text length
        # Short prompts (< 10 words) are often simple questions/commands
        word_count = len(text.split())
        if word_count < 10:
            return Target(token="ANSWER", attributes={})

        # Longer prompts - assume they're about some content
        return Target(token="CONTENT", attributes={})

    def _add_domain_attributes(self, targets: list[Target], text: str) -> list[Target]:
        """Add domain-specific attributes to targets"""
        text_lower = text.lower()

        domain_keywords = {
            "SUPPORT": ["customer support", "customer service", "support ticket"],
            "TECHNICAL": ["technical", "engineering", "development", "code review", "fix bug"],
            "BUSINESS": ["business", "corporate", "enterprise"],
            "MEDICAL": ["medical", "healthcare", "clinical"],
        }

        for target in targets:
            # Add domain if found
            for domain, keywords in domain_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    target.domain = domain
                    break

            # Add language attribute for CODE targets
            if target.token == "CODE":
                languages = ["python", "javascript", "java", "c++", "ruby", "go", "rust", "typescript"]
                for lang in languages:
                    if lang in text_lower:
                        target.attributes["LANG"] = lang.upper()
                        break

            # Add type attribute for TRANSCRIPT targets
            if target.token == "TRANSCRIPT":
                types = ["meeting", "call", "chat", "interview"]
                for ttype in types:
                    if ttype in text_lower:
                        target.attributes["TYPE"] = ttype.upper()
                        break

        return targets

    def _detect_concept_target(self, text: str, doc: Doc) -> Optional[Target]:
        """
        Detect abstract concepts that need explanation

        Patterns detected:
        1. "Explain X" or "Describe X" where X is the concept
        2. Known technical terms in the text
        3. "How X works" patterns
        """
        text_lower = text.lower()

        # Pattern 1: "Explain/Describe [CONCEPT]"
        explanation_verbs = ["explain", "describe", "clarify", "elucidate", "tell"]

        for token in doc:
            if token.lemma_ in explanation_verbs:
                # Find the object of explanation (direct object)
                for child in token.children:
                    if child.dep_ in ["dobj", "attr", "pobj"]:
                        # Get the full noun phrase
                        concept_text = self._extract_noun_phrase(child)
                        if concept_text:
                            return Target(
                                token="CONCEPT",
                                attributes={"TOPIC": concept_text.upper().replace(" ", "_")}
                            )

        # Pattern 2: "How [CONCEPT] works"
        how_works_pattern = r"how\s+([a-zA-Z\s]+?)\s+works?"
        match = re.search(how_works_pattern, text_lower)
        if match:
            concept = match.group(1).strip()
            return Target(
                token="CONCEPT",
                attributes={"TOPIC": concept.upper().replace(" ", "_")}
            )

        # Pattern 3: Known technical terms
        for term in self.technical_concepts:
            if term in text_lower:
                # Only trigger if it's the main subject
                if any(verb in text_lower for verb in ["explain", "describe", "what is", "how does"]):
                    return Target(
                        token="CONCEPT",
                        attributes={"TOPIC": term.upper().replace(" ", "_")}
                    )

        return None

    def _extract_noun_phrase(self, token: Token) -> Optional[str]:
        """Extract full noun phrase from a token"""
        phrase_tokens: list[Token] = []

        def collect_tokens(tok: Token):
            phrase_tokens.append(tok)
            for child in tok.children:
                if child.dep_ in ["compound", "amod", "nmod", "det"]:
                    collect_tokens(child)

        collect_tokens(token)
        phrase_tokens.sort(key=lambda t: t.i)
        phrase = " ".join([t.text for t in phrase_tokens])
        phrase = phrase.strip()

        # Filter generic words
        generic_words = ["this", "that", "the", "a", "an", "it"]
        if phrase.lower() in generic_words:
            return None

        return phrase if phrase else None

    def _detect_this_pattern(self, doc: Doc) -> Optional[Target]:
        """
        Detect "this X" patterns where X should be a target
        Example: "Check this API endpoint" → TARGET:ENDPOINT
        """
        for i, token in enumerate(doc):
            if token.text.lower() == "this" and i + 1 < len(doc):
                # Look for the noun chunk after "this"
                for chunk in doc.noun_chunks:
                    if chunk.start > i:
                        noun = chunk.root.text.lower()
                        target_token = self.vocab.get_target_token(noun)
                        if target_token:
                            return Target(token=target_token, attributes={})
                        break

                # Fallback: check the next token if it's a noun
                next_token = doc[i + 1]
                if next_token.pos_ in ["NOUN", "PROPN"]:
                    target_token = self.vocab.get_target_token(next_token.text.lower())
                    if target_token:
                        return Target(token=target_token, attributes={})

        return None

    def _detect_for_pattern(self, text: str) -> Optional[Target]:
        """
        Detect "for X" patterns
        Examples:
        - "...for an eco-friendly water bottle" → DESCRIPTION
        - "...for this business plan" → PLAN
        """
        text_lower = text.lower()

        pattern = r'for\s+(?:a|an|the|this)?\s*(?:\w+\s+)*?(\w+)'
        matches = re.finditer(pattern, text_lower)

        for match in matches:
            noun = match.group(1).strip()
            target_token = self.vocab.get_target_token(noun)
            if target_token:
                return Target(token=target_token, attributes={})

        return None

    def _detect_compound_phrases(self, text: str) -> list[Target]:
        """
        Detect multi-word compound phrases that should be targets
        Examples: "support tickets", "caching strategies", "customer conversations"
        """
        targets = []
        text_lower = text.lower()

        for target_type, synonyms in self.vocab.TARGET_TOKENS.items():
            for synonym in synonyms:
                pattern = r'\b' + re.escape(synonym) + r'\b'
                if re.search(pattern, text_lower):
                    targets.append(Target(token=target_type, attributes={}))
                    break

        return targets