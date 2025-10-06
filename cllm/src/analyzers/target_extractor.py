# Indentify TARGET tokens
import re
from typing import Optional
from spacy import Language
from spacy.tokens import Doc, Token

from src.core import Target
from src.core.vocabulary import Vocabulary


class TargetExtractor:
    """Extracts target objects (TARGET tokens) from text"""
    
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

    def extract(self, text: str) -> list[Target]:
        """
        Extract target objects from text
        
        Args:
            text: Input prompt text
            
        Returns:
            List of detected Target objects
        """
        doc = self.nlp(text)
        targets: list[Target] = []

        # Strategy 1: Look for direct noun matches
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"]:
                target_token = self.vocab.get_target_token(token.text)
                if target_token:
                    targets.append(Target(
                        token=target_token,
                        attributes={}
                    ))
        
        # Strategy 2: Look for noun phrases
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            target_token = self.vocab.get_target_token(chunk_text)
            if target_token:
                # Check if not already added
                if not any(t.token == target_token for t in targets):
                    targets.append(Target(
                        token=target_token,
                        attributes={}
                    ))

        # Strategy 3: Word-boundary matching (for plurals and compounds)
        compound_targets = self._detect_compound_phrases(text)
        for target in compound_targets:
            if not any(t.token == target.token for t in targets):
                targets.append(target)

        # Strategy 4: "This X" pattern detection (NEW!)
        this_target = self._detect_this_pattern(text, doc)
        if this_target:
            if not any(t.token == this_target.token for t in targets):
                targets.append(this_target)

        # Strategy 5: "For X" pattern detection (NEW!)
        for_target = self._detect_for_pattern(text)
        if for_target:
            if not any(t.token == for_target.token for t in targets):
                targets.append(for_target)

        # Strategy 6: Detect CONCEPT targets (NEW!)
        concept_target = self._detect_concept_target(text, doc)
        if concept_target:
            # Check if not already added
            if not any(t.token == "CONCEPT" for t in targets):
                targets.append(concept_target)

        # Strategy 7: Extract domain attributes
        return self._add_domain_attributes(targets, text)
    
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
                languages = ["python", "javascript", "java", "c++", "ruby", "go"]
                for lang in languages:
                    if lang in text_lower:
                        target.attributes["LANG"] = lang
                        break
            
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
        
        Args:
            text: Original prompt text
            doc: spaCy Doc object
            
        Returns:
            Target object with CONCEPT token, or None
        """
        text_lower = text.lower()
        
        # Pattern 1: "Explain/Describe [CONCEPT]"
        # Look for explain/describe verbs and extract what follows
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
                # Only trigger if it's the main subject, not just mentioned
                # Check if it appears after explain/describe or in question context
                if any(verb in text_lower for verb in ["explain", "describe", "what is", "how does"]):
                    return Target(
                        token="CONCEPT",
                        attributes={"TOPIC": term.upper().replace(" ", "_")}
                    )
                
        # Pattern 4: Question format "What is X?"
        what_is_pattern = r"what\s+(?:is|are)\s+([a-zA-Z\s]+?)(?:\?|$|\s+to)"
        match = re.search(what_is_pattern, text_lower)
        if match:
            concept = match.group(1).strip()
            # Filter out common words
            if len(concept.split()) <= 4 and concept not in ["this", "that", "it", "the"]:
                return Target(
                    token="CONCEPT",
                    attributes={"TOPIC": concept.upper().replace(" ", "_")}
                )
        
        return None
    
    def _extract_noun_phrase(self, token: Token) -> Optional[str]:
        """
        Extract full noun phrase from a token
        
        Args:
            token: spaCy Token object
            
        Returns:
            Full noun phrase as string
        """
        # Get all tokens in the subtree
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
    
    def _detect_this_pattern(self, text: str, doc) -> Optional[Target]:
        """
        Detect "this X" patterns where X should be a target
        
        Example: "Check this API endpoint" → TARGET:ENDPOINT
        """
        # Pattern: "this [adjective]* [noun]"
        text_lower = text.lower()
        patterns = [
            r'this\s+(\w+\s+)?(\w+)',  # "this [adj] noun"
            r'this\s+(\w+)',            # "this noun"
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                # Get the last captured group (the noun)
                words = [g for g in match.groups() if g]
                if not words:
                    continue
                
                # Try each word as potential target
                for match in matches:
                    word = word.strip()
                    target_token = self.vocab.get_target_token(word)
                    if target_token:
                        return Target(token=target_token, attributes={})
        
        return None
    
    def _detect_for_pattern(self, text: str) -> Optional[Target]:
        """
        Detect "for X" patterns
        
        Examples:
        - "...for an eco-friendly water bottle" → DESCRIPTION implied
        - "...for this business plan" → PLAN
        """
        import re
        text_lower = text.lower()
        
        # Pattern: "for [article] [adjective]* [NOUN]"
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
        
        This catches phrases like:
        - "support tickets" → TICKET
        - "caching strategies" → STRATEGY
        - "customer conversations" → CONVERSATION
        """
        targets = []
        text_lower = text.lower()
        
        # For each target type, check ALL its synonyms (including multi-word)
        for target_type, synonyms in self.vocab.TARGET_TOKENS.items():
            for synonym in synonyms:
                # Use word boundary matching
                pattern = r'\b' + re.escape(synonym) + r'\b'
                if re.search(pattern, text_lower):
                    targets.append(Target(token=target_type, attributes={}))
                    break  # Found this target, move to next type
        
        return targets