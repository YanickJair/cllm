"""
Target attribute enhancement
Extracts and enriches attributes for targets
"""

import re
from typing import Optional
from spacy import Language
from spacy.tokens import Doc

from src.components.sys_prompt.analyzers.target.domain import DomainDetector


class AttributeEnhancer:
    """
    Enhances targets with rich attributes

    Extracts:
    - TOPIC (for CONCEPT, PROCEDURE)
    - SUBJECT (for CONTENT, ITEMS)
    - TYPE, DURATION, CONTEXT (for specific targets)
    - DOMAIN, LANG (technical metadata)
    """

    def __init__(self, nlp: Language):
        self.nlp = nlp
        self.topic_extractor = TopicExtractor(nlp)
        self.subject_detector = SubjectDetector()
        self.rich_extractor = RichAttributeExtractor()
        self.domain_detector = DomainDetector(nlp)
        self.language_detector = LanguageDetector()

    def enhance(self, target_token: str, text: str, doc: Doc) -> dict[str, str]:
        """
        Extract all applicable attributes for a target

        Returns dict of attributes
        """
        attributes = {}

        # Add TOPIC for concepts
        if target_token in ['CONCEPT', 'PROCEDURE', 'ANSWER', 'FACT']:
            topic = self.topic_extractor.extract(text, target_token, doc)
            if topic:
                attributes['TOPIC'] = topic

        # Add SUBJECT for content
        if target_token in ['CONTENT', 'ITEMS', 'ANSWER', 'DOCUMENT']:
            subject = self.subject_detector.detect(text)
            if subject:
                attributes['SUBJECT'] = subject

        if target_token == 'RESULT':
            type_match = re.search(r'(?:calculate|compute|find) (?:the )?([\w\s]+)',
                                   text.lower())
            if type_match:
                result_type = type_match.group(1).strip()
                attributes['TYPE'] = result_type.replace(' ', '_').upper()

        # Add rich attributes (TYPE, DURATION, CONTEXT, etc.)
        rich_attrs = self.rich_extractor.extract(text, target_token)
        attributes.update(rich_attrs)

        # Add DOMAIN
        domain, _ = self.domain_detector.detect(text)
        if domain:
            attributes['DOMAIN'] = domain

        # Add LANG
        lang = self.language_detector.detect(text)
        if lang:
            attributes['LANG'] = lang

        return attributes


class TopicExtractor:
    """Extracts TOPIC attribute"""

    def __init__(self, nlp):
        self.nlp = nlp

    def extract(self, text: str, target_type: str, doc: Doc) -> Optional[str]:
        """Extract TOPIC from text"""
        text_lower = text.lower()

        # Strategy 1: Question patterns - extract ONLY the noun/subject
        question_patterns = [
            # "What is X?" - capture only X
            (r'what (?:is|are|\'s) (?:the |an? )?([\w\s]+?)(?:\?|$)', 1),
            # "How does X work?" - capture only X, not "how X works"
            (r'how (?:does|do|can|is|are) ([\w\s]+?)(?: work| function| operate|\?|$)', 1),
            # "Why is X?" - capture only X
            (r'why (?:is|are|does|do) ([\w\s]+?)(?:\?|$)', 1),
            # "Where is X?" - capture only X
            (r'where (?:is|are|can) ([\w\s]+?)(?:\?|$)', 1),
            # "When did X?" - capture only X
            (r'when (?:is|are|was|were|did) ([\w\s]+?)(?:\?|$)', 1),
            # "Who is X?" - capture only X
            (r'who (?:is|are|was|were) (?:the )?([\w\s]+?)(?:\?|$)', 1),
        ]

        for pattern, group in question_patterns:
            match = re.search(pattern, text_lower)
            if match:
                topic = match.group(group).strip()
                topic = self._clean_topic(topic)
                if topic:
                    return topic.replace(' ', '_').replace("'", '').upper()

        # Strategy 2: "Explain/Describe X" patterns - extract ONLY the core noun
        explain_patterns = [
            (r'(?:explain|describe) how ([\w\s]+?)(?: works?| functions?| operates?|$)', 1),
            # "Explain the X" → "X"
            (r'(?:explain|describe|clarify|detail) (?:the |an? )?([\w\s]+?)(?:\s+in\s+|\s+with\s+|\s+for\s+|\.|\?|$)',
             1),
            # "Tell me about X" → "X"
            (r'tell me about ([\w\s]+?)(?:\s+in\s+|\s+with\s+|\.|\?|$)', 1),
        ]

        for pattern, group in explain_patterns:
            match = re.search(pattern, text_lower)
            if match:
                topic = match.group(group).strip()
                topic = self._clean_topic(topic)
                if topic:
                    return topic.replace(' ', '_').replace("'", '').upper()

        # Strategy 3: "X of Y" patterns for concepts
        if target_type == 'CONCEPT':
            of_pattern = r'(?:concept|idea|notion|principle|theory) of ([\w\s]+?)(?:\s+in\s+|\.|\?|$)'
            match = re.search(of_pattern, text_lower)
            if match:
                topic = match.group(1).strip()
                topic = self._clean_topic(topic)
                if topic:
                    return topic.replace(' ', '_').replace("'", '').upper()

        # Strategy 4: For procedures, extract the action/process
        if target_type == 'PROCEDURE':
            how_pattern = r'how (?:to|can I|do I) ([\w\s]+?)(?:\s+in\s+|\s+with\s+|\.|\?|$)'
            match = re.search(how_pattern, text_lower)
            if match:
                topic = match.group(1).strip()
                topic = self._clean_topic(topic)
                if topic:
                    return topic.replace(' ', '_').replace("'", '').upper()

        # Strategy 5: Extract main noun from first meaningful noun chunk
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()

            skip_words = [
                'it', 'this', 'that', 'these', 'those',
                'the following', 'a', 'an', 'the',
                'something', 'anything', 'everything',
                'someone', 'anyone', 'everyone',
            ]

            # Skip if chunk is just a demonstrative/article
            if chunk_text in skip_words:
                continue

            # Skip if chunk starts with demonstrative
            if chunk_text.startswith(('this ', 'that ', 'these ', 'those ')):
                chunk_text = re.sub(r'^(this|that|these|those)\s+', '', chunk_text)
                if not chunk_text or chunk_text in skip_words:
                    continue

            # Only proceed if we have substantial content
            if len(chunk_text) > 3:
                topic = self._clean_topic(chunk_text)
                if topic:
                    topic_formatted = topic.replace(' ', '_').replace("'", '').upper()
                    validated = self._validate_topic(topic_formatted)
                    if validated:
                        return validated
        return None

    def _validate_topic(self, topic: str) -> Optional[str]:
        """
        Final validation to ensure TOPIC quality

        Reject topics that are:
        - Just demonstratives (THIS, THAT)
        - Too short (< 2 chars)
        - Still have "THIS_" prefix
        - Just numbers or punctuation

        Returns:
            Validated topic or None if invalid
        """
        if not topic:
            return None

        topic_upper = topic.upper()

        # Reject if it's just a demonstrative
        if topic_upper in ['THIS', 'THAT', 'THESE', 'THOSE', 'IT', 'THE', 'A', 'AN']:
            return None

        # Reject if it still starts with "THIS_"
        if topic_upper.startswith('THIS_'):
            # Try to salvage by removing prefix
            topic = re.sub(r'^THIS_', '', topic, flags=re.IGNORECASE)
            if not topic or len(topic) < 2:
                return None

        # Reject if too short
        if len(topic) < 2:
            return None

        # Reject if just numbers or punctuation
        if re.match(r'^[\d\W_]+$', topic):
            return None
        return topic

    def _clean_topic(self, topic: str) -> Optional[str]:
        """
        Clean up extracted topic by removing pronouns, verbs, and filler words

        Examples:
            "this support ticket" → "support ticket"
            "we reduce air pollution" → "air pollution"
            "how dns works in technical detail" → "dns"

        Returns:
            Cleaned topic string or None if nothing remains
        """
        if not topic:
            return None

        # CRITICAL FIX: Remove "this/that/these/those" ANYWHERE in topic
        topic = re.sub(r'\bthis\b', '', topic, flags=re.IGNORECASE)
        topic = re.sub(r'\bthat\b', '', topic, flags=re.IGNORECASE)
        topic = re.sub(r'\bthese\b', '', topic, flags=re.IGNORECASE)
        topic = re.sub(r'\bthose\b', '', topic, flags=re.IGNORECASE)

        # Remove articles at start
        topic = re.sub(r'^(the|a|an)\s+', '', topic, flags=re.IGNORECASE)

        # Remove common pronouns at start
        topic = re.sub(r'^(i|we|you|they|he|she|it|us|our|your|their)\s+', '', topic, flags=re.IGNORECASE)

        # Remove auxiliary/modal verbs at start
        topic = re.sub(r'^(can|could|should|would|will|shall|may|might|must|do|does|did)\s+', '', topic,
                       flags=re.IGNORECASE)

        # Remove question words at start
        topic = re.sub(r'^(how|what|why|when|where|who|which)\s+', '', topic, flags=re.IGNORECASE)

        # Remove common action verbs that are redundant with REQ tokens
        action_verbs = [
            'reduce', 'increase', 'improve', 'optimize', 'enhance',
            'fix', 'solve', 'resolve', 'debug', 'repair',
            'create', 'generate', 'build', 'make', 'produce',
            'analyze', 'examine', 'review', 'evaluate', 'assess',
            'explain', 'describe', 'clarify', 'define',
            'calculate', 'compute', 'determine', 'find',
            'compare', 'contrast', 'differentiate',
            'classify', 'categorize', 'sort', 'organize',
            'highlight', 'identify', 'show', 'demonstrate',
        ]

        for verb in action_verbs:
            # Remove verb anywhere in string
            topic = re.sub(rf'\b{verb}\b', '', topic, flags=re.IGNORECASE)

        # Remove trailing/leading prepositions and modifiers
        topic = re.sub(r'\s+(of|in|for|with|about|from|to|at|on|by|detail|details|technical|specific)$', '', topic,
                       flags=re.IGNORECASE)

        # Clean up multiple spaces
        topic = re.sub(r'\s+', ' ', topic).strip()

        # Return None if nothing meaningful remains
        return topic if topic and len(topic) > 1 else None


class SubjectDetector:
    """Detects SUBJECT attribute"""

    def detect(self, text: str) -> Optional[str]:
        """Detect SUBJECT from text"""
        text_lower = text.lower()

        # Subject patterns (order matters - specific before general)
        SUBJECT_PATTERNS = [
            (r'\bverb[s]?\b', 'VERB'),
            (r'\bnoun[s]?\b', 'NOUN'),
            (r'\badjective[s]?\b', 'ADJECTIVE'),
            (r'\badverb[s]?\b', 'ADVERB'),
            (r'\bpronoun[s]?\b', 'PRONOUN'),
            (r'\bpreposition[s]?\b', 'PREPOSITION'),
            (r'\bconjunction[s]?\b', 'CONJUNCTION'),
            (r'\btip[s]?\b', 'TIP'),
            (r'\b(?:suggestion|recommendation)[s]?\b', 'TIP'),
            (r'\bmethod[s]?\b', 'METHOD'),
            (r'\btechnique[s]?\b', 'TECHNIQUE'),
            (r'\bstrateg(?:y|ies)\b', 'STRATEGY'),
            (r'\bapproach(?:es)?\b', 'APPROACH'),
            (r'\bpractice[s]?\b', 'PRACTICE'),
            (r'\balgorithm[s]?\b', 'ALGORITHM'),
            (r'\bfunction[s]?\b', 'FUNCTION'),
            (r'\bformula[s]?\b', 'FORMULA'),
            (r'\bequation[s]?\b', 'EQUATION'),
            (r'\btheorem[s]?\b', 'THEOREM'),
            (r'\bproof[s]?\b', 'PROOF'),
            (r'\bexample[s]?\b', 'EXAMPLE'),
            (r'\bidea[s]?\b', 'IDEA'),
            (r'\bway[s]?\b', 'METHOD'),
            (r'\bstep[s]?\b', 'STEP'),
            (r'\bfactor[s]?\b', 'FACTOR'),
            (r'\breason[s]?\b', 'REASON'),
            (r'\bbenefit[s]?\b', 'BENEFIT'),
            (r'\badvantage[s]?\b', 'ADVANTAGE'),
            (r'\bdisadvantage[s]?\b', 'DISADVANTAGE'),
            (r'\bfeature[s]?\b', 'FEATURE'),
            (r'\bcharacteristic[s]?\b', 'CHARACTERISTIC'),
            (r'\bmetric[s]?\b', 'METRIC'),
            (r'\bindicator[s]?\b', 'INDICATOR'),
            (r'\binsight[s]?\b', 'INSIGHT'),
            (r'\bfinding[s]?\b', 'FINDING'),
        ]

        for pattern, subject in SUBJECT_PATTERNS:
            if re.search(pattern, text_lower):
                return subject
        return None

class RichAttributeExtractor:
    """
    Extracts rich attributes like TYPE, DURATION, CONTEXT, etc.

    This is the NEW functionality we discussed
    """

    def extract(self, text: str, target_token: str) -> dict[str, str]:
        """Extract rich attributes"""
        attributes = {}
        text_lower = text.lower()

        # Extract DURATION
        if target_token in ['TRANSCRIPT', 'CALL', 'MEETING']:
            duration = self._extract_duration(text_lower)
            if duration:
                attributes['DURATION'] = duration

        # Extract TYPE
        if target_token in ['TRANSCRIPT', 'DOCUMENT']:
            type_value = self._extract_type(text_lower)
            if type_value:
                attributes['TYPE'] = type_value

        # Extract CONTEXT
        context = self._extract_context(text_lower)
        if context:
            attributes['CONTEXT'] = context

        # Extract ISSUE (for COMPLAINT, TICKET)
        if target_token in ['COMPLAINT', 'TICKET']:
            issue = self._extract_issue(text_lower)
            if issue:
                attributes['ISSUE'] = issue

        return attributes

    def _extract_duration(self, text_lower: str) -> Optional[str]:
        """Extract duration in minutes"""
        patterns = [
            r'(\d+)[\s-]*(?:minute|min)s?',
            r'(\d+)[\s-]*(?:hour|hr)s?',
        ]

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                num = int(match.group(1))
                if 'hour' in pattern or 'hr' in pattern:
                    return str(num * 60)
                return str(num)

        return None

    def _extract_type(self, text_lower: str) -> Optional[str]:
        """Extract content TYPE"""
        type_map = {
            'call': 'CALL',
            'phone call': 'CALL',
            'meeting': 'MEETING',
            'chat': 'CHAT',
            'conversation': 'CONVERSATION',
            'report': 'REPORT',
            'article': 'ARTICLE',
        }

        for keyword, type_value in type_map.items():
            if keyword in text_lower:
                return type_value

        return None

    def _extract_context(self, text_lower: str) -> Optional[str]:
        """Extract CONTEXT (customer, support, sales, etc.)"""
        context_map = {
            'customer': 'CUSTOMER',
            'support': 'SUPPORT',
            'sales': 'SALES',
            'technical': 'TECHNICAL',
        }

        for keyword, context_value in context_map.items():
            if keyword in text_lower:
                return context_value

        return None

    def _extract_issue(self, text_lower: str) -> Optional[str]:
        """Extract ISSUE from complaint/ticket"""
        patterns = [
            r'about\s+([\w\s]+?)(?:\s+and|$)',
            r'regarding\s+([\w\s]+?)(?:\s+and|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                issue = match.group(1).strip()
                return issue.upper().replace(' ', '_')
        return None

class LanguageDetector:
    """Detects programming LANG"""

    def detect(self, text: str) -> Optional[str]:
        """Detect programming language"""
        text_lower = text.lower()

        # CRITICAL: Only detect language if there's code-related context
        code_indicators = [
            'code', 'script', 'function', 'program', 'algorithm',
            'snippet', 'file', 'implementation', 'syntax', 'debug',
            'compile', 'runtime', 'library', 'framework', 'api',
        ]

        # If no code context, don't detect language
        if not any(indicator in text_lower for indicator in code_indicators):
            return None

        # Language patterns with word boundaries to avoid false matches
        language_patterns = [
            (r'\bpython\b', 'PYTHON'),
            (r'\bdjango\b', 'PYTHON'),
            (r'\bflask\b', 'PYTHON'),
            (r'\bpandas\b', 'PYTHON'),
            (r'\b\.py\b', 'PYTHON'),
            (r'\bjavascript\b', 'JAVASCRIPT'),
            (r'\bnode\.?js\b', 'JAVASCRIPT'),
            (r'\breact\b', 'JAVASCRIPT'),
            (r'\bvue\b', 'JAVASCRIPT'),
            (r'\bangular\b', 'JAVASCRIPT'),
            (r'\b\.js\b', 'JAVASCRIPT'),
            (r'\bjava\b(?!script)', 'JAVA'),
            (r'\bspring\b', 'JAVA'),
            (r'\bmaven\b', 'JAVA'),
            (r'\bc\+\+\b', 'CPP'),
            (r'\bcpp\b', 'CPP'),
            (r'\bgolang\b', 'GO'),
            (r'\bgo\s+(?:code|lang|program|script)', 'GO'),
            (r'\brust\b', 'RUST'),
            (r'\btypescript\b', 'TYPESCRIPT'),
            (r'\b\.ts\b', 'TYPESCRIPT'),
        ]

        for pattern, lang in language_patterns:
            if re.search(pattern, text_lower):
                return lang

        return None