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
            # Core Computer Science
            "data structures", "algorithms", "computational complexity", "operating systems",
            "virtual memory", "concurrency", "multithreading", "parallel computing",
            "distributed systems", "load balancing", "event-driven architecture",

            # Networking & Protocols
            "ip", "udp", "icmp", "ssh", "ftp", "smtp", "snmp", "websockets", "vpn",
            "cdn", "proxy servers", "firewalls", "nat", "bgp",

            # Databases & Storage
            "relational databases", "document databases", "graph databases", "time-series databases",
            "indexing", "query optimization", "acid", "event sourcing", "data warehousing",
            "etl", "data lakes", "caching", "redis", "elasticsearch",

            # Software Development & Architecture
            "object-oriented programming", "functional programming", "test-driven development",
            "design patterns", "dependency injection", "continuous integration",
            "continuous deployment", "version control", "git", "monolith", "microfrontends",
            "domain-driven design", "clean architecture",

            # Cloud & DevOps
            "infrastructure as code", "terraform", "ansible", "jenkins", "cicd pipelines",
            "monitoring", "observability", "logging", "prometheus", "grafana",
            "load testing", "chaos engineering",

            # AI / ML / Data Science
            "reinforcement learning", "computer vision", "natural language processing",
            "generative ai", "transformers", "autoencoders", "feature engineering",
            "data preprocessing", "model deployment", "mlops", "vector databases",

            # Security
            "encryption", "hashing", "ssl", "tls", "oauth", "jwt", "zero trust architecture",
            "penetration testing", "vulnerability scanning", "access control", "iam",

            # Web & Frontend
            "next.js", "svelte", "astro", "webassembly", "typescript", "tailwind css",
            "progressive web apps", "responsive design", "web performance optimization",

            # Backend & APIs
            "grpc", "openapi", "soap", "rate limiting", "api gateway", "message queues",
            "rabbitmq", "kafka", "event-driven systems", "background jobs", "webhooks",

            # Cloud Platforms & Containers
            "ecs", "eks", "lambda", "cloud run", "app engine", "cloudflare workers",
            "service mesh", "istio", "helm", "container orchestration",

            # Emerging & Advanced Tech
            "edge computing", "fog computing", "5g", "iot", "ar", "vr", "xr",
            "federated learning", "quantum encryption", "digital twins", "neuromorphic computing",

            # Programming Languages & Tools
            "go", "rust", "swift", "kotlin", "scala", "r", "bash", "c", "c++", "java",
            "ruby", "php", "dart", "flutter", "swiftui",

            # Analytics & Big Data
            "big data", "hadoop", "spark", "kafka streams", "flink", "databricks",
            "data pipelines", "real-time analytics", "business intelligence", "power bi", "tableau"
        ]
        self.cx_technical_concepts = [
            # Core CX & Support Concepts
            "customer experience", "customer journey", "customer satisfaction",
            "customer retention", "customer loyalty", "customer lifetime value",
            "net promoter score", "nps", "csat", "ces", "customer effort score",
            "churn rate", "voice of the customer", "voc",

            # Support Operations
            "ticketing system", "helpdesk software", "sla", "first response time",
            "average handle time", "aht", "first call resolution", "fcr",
            "resolution time", "queue management", "escalation management",
            "after call work", "acw", "wrap-up codes", "call disposition",
            "call scripts", "knowledge base", "faq automation", "self-service portal",
            "omnichannel support", "multichannel support", "call handling",
            "inbound calls", "outbound calls", "call queue", "warm transfer",
            "cold transfer", "call escalation", "ticket creation",

            # Communication Channels
            "voice support", "email support", "chat support", "live chat",
            "social media support", "whatsapp support", "sms support",
            "video support", "blended agents", "channel switching",
            "co-browsing", "screen sharing",

            # Tools & Platforms
            "crm", "agent workspace", "unified agent desktop",
            "zendesk", "freshdesk", "intercom", "salesforce service cloud",
            "hubspot service hub", "helpscout", "genesys", "genesys cloud",
            "twilio flex", "nice incontact", "five9", "avaya", "amazon connect",
            "ccaas", "frontapp", "aircall", "qualtrics", "medallia",

            # Automation & AI
            "chatbots", "voicebots", "virtual assistants", "conversational ai",
            "natural language processing", "nlp routing", "sentiment analysis",
            "intent detection", "speech analytics", "voice recognition",
            "predictive analytics", "ai routing", "automated responses",
            "co-pilot ai", "agent assist ai", "automated workflows",
            "rpa", "bot handoff", "queue prioritization", "call routing",
            "skill-based routing", "emotion detection", "next best action",

            # Data & Analytics
            "customer data platform", "cdp", "crm integration", "data integration",
            "real-time analytics", "dashboards", "reporting automation",
            "cohort analysis", "text analytics", "journey analytics",
            "feedback analytics", "customer segmentation",
            "agent performance dashboard", "leaderboards", "kpi tracking",

            # System Integration & APIs
            "api integration", "webhooks", "bi tools integration", "single sign-on",
            "sso", "oauth", "rest api", "graphql api", "workflow automation",
            "ifttt", "zapier", "data synchronization", "real-time data fetch",

            # UX / UI & Digital CX
            "user experience", "user interface", "ux design", "ui design",
            "personalization", "customer onboarding", "journey mapping",
            "heatmaps", "a/b testing", "conversion optimization",
            "behavioral analytics", "user feedback loops", "context-aware responses",

            # Contact Center & Infrastructure
            "contact center as a service", "ivr", "interactive voice response",
            "auto dialer", "predictive dialer", "automatic call distributor",
            "acd", "call recording", "screen recording", "call monitoring",
            "live coaching", "speech-to-text", "cloud telephony", "call routing",
            "ivr menu design", "real-time monitoring", "agent dashboards",
            "softphone", "headset integration", "voip", "vpn connection",
            "latency monitoring", "system uptime", "network quality metrics",
            "call latency", "packet loss", "webrtc", "browser-based contact center",
            "thin client environments",

            # Security & Compliance
            "gdpr", "ccpa", "data privacy", "pii masking", "data redaction",
            "pci compliance", "security compliance", "access control",
            "encryption", "audit logs", "role-based permissions",
            "secure payment capture", "identity verification",
            "call authentication", "voice biometrics", "knowledge-based authentication",
            "session recording consent", "two-factor authentication",

            # Agent Enablement & Training
            "e-learning modules", "microlearning", "gamification", "coaching sessions",
            "agent onboarding", "call simulations", "ai feedback", "training analytics",
            "knowledge suggestions", "contextual knowledge surfacing",
            "real-time assist prompts", "virtual training environments",

            # Customer Data & Context
            "customer profile", "interaction history", "case notes",
            "customer sentiment", "customer intent", "journey orchestration",

            # Emerging CX Tech
            "proactive support", "predictive support", "hyper-personalization",
            "contextual engagement", "customer digital twin", "emotion ai",
            "real-time translation", "voice biometrics", "augmented reality support",
            "self-healing systems", "recommendation engine", "agent sentiment tracking",
            "real-time transcription", "automated note taking", "proactive engagement prompts"
        ]

    def extract(self, text: str, detected_req_tokens: list[str] = None) -> list[Target]:
        """
        Main extraction method - extracts TARGET tokens from text
        
        Args:
            text: Input prompt text
            detected_req_tokens: List of REQ tokens already detected
            
        Returns:
            List of Target objects with enhanced attributes
        """
        doc = self.nlp(text)
        targets: list[Target] = []

        # PRIORITY 1: Explicit pattern matching (highest confidence)
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
                    attributes = self._enhance_target_attributes(target_token, text, doc)
                    targets.append(Target(token=target_token, attributes=attributes))

        # PRIORITY 3: Noun phrases
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            target_token = self.vocab.get_target_token(chunk_text)
            if target_token:
                if not any(t.token == target_token for t in targets):
                    attributes = self._enhance_target_attributes(target_token, text, doc)
                    targets.append(Target(token=target_token, attributes=attributes))

        # PRIORITY 4: Compound phrases
        compound_targets = self._detect_compound_phrases(text, doc)
        for target in compound_targets:
            if not any(t.token == target.token for t in targets):
                targets.append(target)

        # PRIORITY 5: Pattern-based detection
        this_target = self._detect_this_pattern(doc, text)
        if this_target:
            if not any(t.token == this_target.token for t in targets):
                targets.append(this_target)

        for_target = self._detect_for_pattern(text, doc)
        if for_target:
            if not any(t.token == for_target.token for t in targets):
                targets.append(for_target)

        concept_target = self._detect_concept_target(text, doc)
        if concept_target:
            if not any(t.token == "CONCEPT" for t in targets):
                targets.append(concept_target)

        # PRIORITY 6: Fallback system
        if not targets:
            fallback = self._get_fallback_target(text, doc, detected_req_tokens or [])
            if fallback:
                targets.append(fallback)

        # Add domain attributes to all targets
        return self._add_domain_attributes(targets, text)

    def extract_topic_attribute(self, text: str, target_type: str, doc: Doc) -> Optional[str]:
        """
        Extract TOPIC attribute with high accuracy
        
        FIXED: No longer greedy, extracts only the core concept
        
        Examples:
            "Describe how DNS works in technical detail" → "DNS"
            "Explain the bubble sort algorithm" → "BUBBLE_SORT"
            "What are the three primary colors?" → "PRIMARY_COLORS"
            "How does photosynthesis work?" → "PHOTOSYNTHESIS"
        
        Returns:
            TOPIC string in UPPER_SNAKE_CASE or None
        """
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
            (r'(?:explain|describe|clarify|detail) (?:the |an? )?([\w\s]+?)(?:\s+in\s+|\s+with\s+|\s+for\s+|\.|\?|$)', 1),
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
                    topic = self._trim_topic(topic)
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
        topic = re.sub(r'^(can|could|should|would|will|shall|may|might|must|do|does|did)\s+', '', topic, flags=re.IGNORECASE)
        
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
        topic = re.sub(r'\s+(of|in|for|with|about|from|to|at|on|by|detail|details|technical|specific)$', '', topic, flags=re.IGNORECASE)
        
        # Clean up multiple spaces
        topic = re.sub(r'\s+', ' ', topic).strip()
        
        # Return None if nothing meaningful remains
        return topic if topic and len(topic) > 1 else None

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

    def detect_subject_attribute(self, text: str) -> Optional[str]:
        """
        Detect SUBJECT attribute for specific content types
        
        Examples:
            "three verbs" → "VERB"
            "five tips" → "TIP"
            "bubble sort algorithm" → "ALGORITHM"
            "examples of recursion" → "EXAMPLE"
        
        Returns:
            SUBJECT string like "VERB", "TIP", etc. or None
        """
        text_lower = text.lower()
        
        # Subject patterns (order matters - specific before general)
        SUBJECT_PATTERNS = [
            # Grammar elements
            (r'\bverb[s]?\b', 'VERB'),
            (r'\bnoun[s]?\b', 'NOUN'),
            (r'\badjective[s]?\b', 'ADJECTIVE'),
            (r'\badverb[s]?\b', 'ADVERB'),
            (r'\bpronoun[s]?\b', 'PRONOUN'),
            (r'\bpreposition[s]?\b', 'PREPOSITION'),
            (r'\bconjunction[s]?\b', 'CONJUNCTION'),
            
            # Content types (specific)
            (r'\btip[s]?\b', 'TIP'),
            (r'\b(?:suggestion|recommendation)[s]?\b', 'TIP'),
            (r'\bmethod[s]?\b', 'METHOD'),
            (r'\btechnique[s]?\b', 'TECHNIQUE'),
            (r'\bstrateg(?:y|ies)\b', 'STRATEGY'),
            (r'\bapproach(?:es)?\b', 'APPROACH'),
            (r'\bpractice[s]?\b', 'PRACTICE'),
            
            # Technical subjects
            (r'\balgorithm[s]?\b', 'ALGORITHM'),
            (r'\bfunction[s]?\b', 'FUNCTION'),
            (r'\bformula[s]?\b', 'FORMULA'),
            (r'\bequation[s]?\b', 'EQUATION'),
            (r'\btheorem[s]?\b', 'THEOREM'),
            (r'\bproof[s]?\b', 'PROOF'),
            
            # Lists and collections
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
            
            # Business/Analysis
            (r'\bmetric[s]?\b', 'METRIC'),
            (r'\bindicator[s]?\b', 'INDICATOR'),
            (r'\binsight[s]?\b', 'INSIGHT'),
            (r'\bfinding[s]?\b', 'FINDING'),
        ]
        
        for pattern, subject in SUBJECT_PATTERNS:
            if re.search(pattern, text_lower):
                return subject
        
        return None

    def _enhance_target_attributes(self, target_token: str, text: str, doc: Doc) -> dict:
        """
        Central method to enhance Target attributes with TOPIC and SUBJECT
        
        Args:
            target_token: The target type (e.g., "CONCEPT", "CONTENT", "ITEMS")
            text: Original prompt text
            doc: spaCy Doc object
            
        Returns:
            Dictionary of attributes including TOPIC, SUBJECT, DOMAIN, LANG
        """
        attributes = {}
        
        # Add TOPIC for applicable targets
        if target_token in ['CONCEPT', 'PROCEDURE', 'ANSWER', 'FACT']:
            topic = self.extract_topic_attribute(text, target_token, doc)
            if topic:
                attributes['TOPIC'] = topic
        
        # Add SUBJECT for applicable targets
        if target_token in ['CONTENT', 'ITEMS', 'ANSWER', 'DOCUMENT']:
            subject = self.detect_subject_attribute(text)
            if subject:
                attributes['SUBJECT'] = subject
        
        # Add TYPE for RESULT targets
        if target_token == 'RESULT':
            type_match = re.search(r'(?:calculate|compute|find) (?:the )?([\w\s]+)', 
                                 text.lower())
            if type_match:
                result_type = type_match.group(1).strip()
                attributes['TYPE'] = result_type.replace(' ', '_').upper()
        
        # Keep existing domain detection
        domain = self._detect_domain(text)
        if domain:
            attributes['DOMAIN'] = domain
        
        # Keep existing language detection
        lang = self._detect_language(text)
        if lang:
            attributes['LANG'] = lang
        
        return attributes

    def _detect_domain(self, text: str) -> Optional[str]:
        """
        Detect domain (SUPPORT, TECHNICAL, SALES) with context awareness
        
        Only triggers when domain keywords appear in relevant contexts
        """
        text_lower = text.lower()
        
        # Domain patterns with context
        # Only match when we have strong indicators
        
        # SUPPORT domain - needs customer service context
        support_patterns = [
            r'\b(?:customer\s+)?support\s+(?:ticket|transcript|call|email|chat)',
            r'\b(?:support|customer\s+service|helpdesk|service\s+desk)',
            r'\bticket\b.*\b(?:customer|support|issue)',
            r'\bcustomer\s+(?:support|service|complaint|inquiry)',
        ]
        
        for pattern in support_patterns:
            if re.search(pattern, text_lower):
                return 'SUPPORT'
        
        # TECHNICAL domain - needs technical context
        technical_patterns = [
            r'\b(?:technical\s+)?(?:bug|debug|error|exception)',
            r'\bcode\s+review\b',
            r'\btechnical\s+(?:issue|problem|documentation)',
            r'\bstack\s+trace\b',
        ]
        
        for pattern in technical_patterns:
            if re.search(pattern, text_lower):
                return 'TECHNICAL'
        
        # SALES domain - needs sales/billing context
        sales_patterns = [
            r'\b(?:sales|billing|payment|invoice|pricing)',
            r'\bpurchase\s+order\b',
            r'\bquote\b.*\b(?:sales|price)',
        ]
        
        for pattern in sales_patterns:
            if re.search(pattern, text_lower):
                return 'SALES'
        
        return None

    def _detect_language(self, text: str) -> Optional[str]:
        """
        Detect programming language ONLY in code-related contexts
        
        Uses strict matching to avoid false positives on common English words
        """
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
        # Format: (regex pattern, language name)
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
            (r'\b\.js\b', 'JAVASCRIPT'),  # ".js" file extension
            
            (r'\bjava\b(?!script)', 'JAVA'),  # "java" but not "javascript"
            (r'\bspring\b', 'JAVA'),
            (r'\bmaven\b', 'JAVA'),
            
            (r'\bc\+\+\b', 'CPP'),
            (r'\bcpp\b', 'CPP'),
            
            (r'\bgolang\b', 'GO'),  # Only "golang", not "go"
            (r'\bgo\s+(?:code|lang|program|script)', 'GO'),  # "go code", "go program"
            
            (r'\brust\b', 'RUST'),
            
            (r'\btypescript\b', 'TYPESCRIPT'),
            (r'\b\.ts\b', 'TYPESCRIPT'),  # ".ts" file extension
        ]
        
        for pattern, lang in language_patterns:
            if re.search(pattern, text_lower):
                return lang
        
        return None

    # ============================================================================
    # DETECTION METHODS (Enhanced with attribute extraction)
    # ============================================================================

    def _detect_question_target(self, text: str, doc: Doc) -> Optional[Target]:
        """Detect target for question patterns with enhanced attributes"""
        if not text.strip().endswith('?'):
            return None
        
        text_lower = text.lower()
        
        # Question word detection
        if any(text_lower.startswith(q) for q in ['what', 'who', 'where', 'when', 'why', 'how']):
            attributes = self._enhance_target_attributes("CONCEPT", text, doc)
            return Target(token="CONCEPT", attributes=attributes)
        
        return None

    def _detect_imperative_target(self, text: str, req_tokens: list[str] = None) -> Optional[Target]:
        """Detect targets for imperative commands with enhanced attributes"""
        text_lower = text.lower().strip()
        req_tokens = req_tokens or []
        req_actions = [req.split(':')[0] if ':' in req else req for req in req_tokens]
        
        doc = self.nlp(text)

        if re.match(r'^compare\s+', text_lower):
            compare_pattern = r'compare\s+([\w\s.]+?)\s+and\s+([\w\s.]+?)(?:\s+frameworks?|\s+libraries?|\s+and|$)'
            match = re.search(compare_pattern, text_lower)
            
            if match:
                item1 = match.group(1).strip()
                item2 = match.group(2).strip()
                
                attributes = {
                    'TYPE': 'COMPARISON',
                    'ITEMS': f"{item1.upper()}+{item2.upper()}".replace(' ', '_').replace('.', '')
                }
                if 'code' in text_lower or 'implementation' in text_lower:
                    lang = self._detect_language(text)
                    if lang:
                        attributes['LANG'] = lang
                
                return Target(token="OPTIONS", attributes=attributes)
    
        
        # Pattern 1: List/Name/Enumerate → ITEMS
        if re.match(r'^(list|name|enumerate|itemize)\s+', text_lower):
            attributes = self._enhance_target_attributes("ITEMS", text, doc)
            return Target(token="ITEMS", attributes=attributes)
        
        # Pattern 2: Calculate/Compute → RESULT
        if re.match(r'^(calculate|compute|determine|find\s+the)\s+', text_lower):
            attributes = self._enhance_target_attributes("RESULT", text, doc)
            return Target(token="RESULT", attributes=attributes)
        
        # Pattern 3: Extract/Identify → DATA
        if re.match(r'^(extract|identify|find)\s+', text_lower):
            attributes = self._enhance_target_attributes("DATA", text, doc)
            return Target(token="DATA", attributes=attributes)
        
        # Pattern 4: Analyze → depends on context
        if re.match(r'^(analyze|review|examine|evaluate)\s+', text_lower):
            # Look for specific targets
            if 'code' in text_lower[:30]:
                attributes = self._enhance_target_attributes("CODE", text, doc)
                return Target(token="CODE", attributes=attributes)
            elif 'data' in text_lower[:30]:
                attributes = self._enhance_target_attributes("DATA", text, doc)
                return Target(token="DATA", attributes=attributes)
            else:
                attributes = self._enhance_target_attributes("DOCUMENT", text, doc)
                return Target(token="DOCUMENT", attributes=attributes)
        
        # Pattern 5: Generate/Create → CONTENT
        if re.match(r'^(generate|create|write|draft)\s+', text_lower):
            attributes = self._enhance_target_attributes("CONTENT", text, doc)
            return Target(token="CONTENT", attributes=attributes)
        
        if re.match(r'^classify\s+', text_lower):
            # Check what's being classified
            if 'ticket' in text_lower[:30]:
                attributes = self._enhance_target_attributes("TICKET", text, doc)
                return Target(token="TICKET", attributes=attributes)
            elif 'email' in text_lower[:30] or 'message' in text_lower[:30]:
                attributes = self._enhance_target_attributes("EMAIL", text, doc)
                return Target(token="EMAIL", attributes=attributes)
            else:
                # Generic classification
                attributes = self._enhance_target_attributes("CONTENT", text, doc)
                return Target(token="CONTENT", attributes=attributes)
    
        # Pattern 7: Summarize → DOCUMENT or specific content type
        if re.match(r'^summarize\s+', text_lower):
            if 'transcript' in text_lower[:30]:
                attributes = self._enhance_target_attributes("TRANSCRIPT", text, doc)
                return Target(token="TRANSCRIPT", attributes=attributes)
            elif 'call' in text_lower[:30]:
                attributes = self._enhance_target_attributes("CALL", text, doc)
                return Target(token="CALL", attributes=attributes)
            elif 'article' in text_lower[:30]:
                attributes = self._enhance_target_attributes("DOCUMENT", text, doc)
                return Target(token="DOCUMENT", attributes=attributes)
            else:
                attributes = self._enhance_target_attributes("DOCUMENT", text, doc)
                return Target(token="DOCUMENT", attributes=attributes)
        
        # Pattern 8: Optimize → QUERY or CODE
        if re.match(r'^optimize\s+', text_lower):
            if 'query' in text_lower[:30] or 'sql' in text_lower[:30]:
                attributes = self._enhance_target_attributes("QUERY", text, doc)
                return Target(token="QUERY", attributes=attributes)
            elif 'code' in text_lower[:30]:
                attributes = self._enhance_target_attributes("CODE", text, doc)
                return Target(token="CODE", attributes=attributes)
            else:
                attributes = self._enhance_target_attributes("CODE", text, doc)
                return Target(token="CODE", attributes=attributes)
        
        # Pattern 9: Debug → CODE
        if re.match(r'^debug\s+', text_lower):
            attributes = self._enhance_target_attributes("CODE", text, doc)
            return Target(token="CODE", attributes=attributes)
        
        # Pattern 10: Review → CODE or DOCUMENT
        if re.match(r'^review\s+', text_lower):
            if 'code' in text_lower[:30]:
                attributes = self._enhance_target_attributes("CODE", text, doc)
                return Target(token="CODE", attributes=attributes)
            else:
                attributes = self._enhance_target_attributes("DOCUMENT", text, doc)
                return Target(token="DOCUMENT", attributes=attributes)
        
        # Pattern 11: Convert/Transform → RESULT with source detection
        if re.match(r'^(convert|transform|translate|rewrite)\s+', text_lower):
            # Try to detect what's being transformed
            if 'transcript' in text_lower[:40]:
                attributes = self._enhance_target_attributes("TRANSCRIPT", text, doc)
                return Target(token="TRANSCRIPT", attributes=attributes)
            elif 'document' in text_lower[:40] or 'documentation' in text_lower[:40]:
                attributes = self._enhance_target_attributes("DOCUMENT", text, doc)
                return Target(token="DOCUMENT", attributes=attributes)
            elif 'proposal' in text_lower[:40]:
                attributes = self._enhance_target_attributes("DOCUMENT", text, doc)
                return Target(token="DOCUMENT", attributes=attributes)
            else:
                attributes = self._enhance_target_attributes("CONTENT", text, doc)
                return Target(token="CONTENT", attributes=attributes)
        
        return None
    
    def _extract_comparison_items(self, text: str) -> Optional[tuple[str, str]]:
        """
        Extract two items being compared
        
        Examples:
            "Difference between X and Y" → ("X", "Y")
        
        Returns:
            Tuple of (item1, item2) or None
        """
        text_lower = text.lower()
        
        patterns = [
            # "Compare X and Y"
            r'compare\s+([\w\s.]+?)\s+and\s+([\w\s.]+?)(?:\s+frameworks?|\s+libraries?|\s+languages?|$)',
            # "Compare X vs Y"
            r'compare\s+([\w\s.]+?)\s+(?:vs|versus)\s+([\w\s.]+?)(?:\s+|$)',
            # "X vs Y"
            r'^([\w\s.]+?)\s+(?:vs|versus)\s+([\w\s.]+?)(?:\s+|$)',
            # "Difference between X and Y"
            r'difference[s]?\s+between\s+([\w\s.]+?)\s+and\s+([\w\s.]+?)(?:\s+|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                item1 = match.group(1).strip()
                item2 = match.group(2).strip()
                
                item1 = re.sub(r'^(the|a|an)\s+', '', item1)
                item2 = re.sub(r'^(the|a|an)\s+', '', item2)
                
                item1 = re.sub(r'\.js$', '', item1)
                item2 = re.sub(r'\.js$', '', item2)
                
                if item1 and item2:
                    return (
                        item1.upper().replace(' ', '_'),
                        item2.upper().replace(' ', '_')
                    )
        
        return None

    def _detect_compound_phrases(self, text: str, doc: Doc) -> list[Target]:
        """Detect compound phrase targets with enhanced attributes"""
        targets = []
        text_lower = text.lower()
        
        # Multi-word target phrases
        compound_phrases = {
            "customer support": "TICKET",
            "support ticket": "TICKET",
            "email message": "EMAIL",
            "chat transcript": "TRANSCRIPT",
            "phone call": "CALL",
            "source code": "CODE",
        }
        
        for phrase, target_token in compound_phrases.items():
            if phrase in text_lower:
                attributes = self._enhance_target_attributes(target_token, text, doc)
                targets.append(Target(token=target_token, attributes=attributes))
        
        return targets

    def _detect_this_pattern(self, doc: Doc, text: str) -> Optional[Target]:
        """Detect 'this X' patterns with enhanced attributes"""
        for i, token in enumerate(doc):
            if token.text.lower() == "this" and i + 1 < len(doc):
                next_token = doc[i + 1]
                if next_token.pos_ in ["NOUN", "PROPN"]:
                    target_token = self.vocab.get_target_token(next_token.text.lower())
                    if target_token:
                        attributes = self._enhance_target_attributes(target_token, text, doc)
                        return Target(token=target_token, attributes=attributes)
        return None

    def _detect_for_pattern(self, text: str, doc: Doc) -> Optional[Target]:
        """Detect 'for X' patterns with enhanced attributes"""
        text_lower = text.lower()
        
        for_patterns = {
            r'for\s+(?:a|an|the)?\s*(?:\w+\s+)*?business plan': 'PLAN',
            r'for\s+(?:a|an|the)?\s*(?:\w+\s+)*?product': 'DESCRIPTION',
            r'for\s+(?:a|an|the)?\s*(?:\w+\s+)*?report': 'REPORT',
        }
        
        for pattern, target_token in for_patterns.items():
            if re.search(pattern, text_lower):
                attributes = self._enhance_target_attributes(target_token, text, doc)
                return Target(token=target_token, attributes=attributes)
        
        return None

    def _detect_concept_target(self, text: str, doc: Doc) -> Optional[Target]:
        """Detect CONCEPT targets with enhanced TOPIC attribute"""
        text_lower = text.lower()
        
        # Pattern 1: "concept of X"
        if "concept of" in text_lower:
            attributes = self._enhance_target_attributes("CONCEPT", text, doc)
            return Target(token="CONCEPT", attributes=attributes)
        
        # Pattern 2: Explanation requests
        if any(verb in text_lower for verb in ["explain", "describe", "clarify", "define"]):
            # Check if it's explaining a specific concept
            if not any(target in text_lower for target in ["code", "data", "document"]):
                attributes = self._enhance_target_attributes("CONCEPT", text, doc)
                return Target(token="CONCEPT", attributes=attributes)
        
        # Pattern 3: Known technical concepts
        for concept in self.technical_concepts:
            if concept in text_lower:
                attributes = self._enhance_target_attributes("CONCEPT", text, doc)
                return Target(token="CONCEPT", attributes=attributes)
        
        return None

    def _get_fallback_target(self, text: str, doc: Doc, req_tokens: list[str]) -> Optional[Target]:
        """Intelligent fallback based on REQ tokens with enhanced attributes"""
        text_lower = text.lower()
        
        if "GENERATE" in req_tokens or "CREATE" in req_tokens:
            # Check what's being generated
            if any(word in text_lower for word in ["list", "items", "examples", "options"]):
                attributes = self._enhance_target_attributes("ITEMS", text, doc)
                return Target(token="ITEMS", attributes=attributes)
            else:
                attributes = self._enhance_target_attributes("CONTENT", text, doc)
                return Target(token="CONTENT", attributes=attributes)
        
        if "EXPLAIN" in req_tokens or "DESCRIBE" in req_tokens:
            attributes = self._enhance_target_attributes("CONCEPT", text, doc)
            return Target(token="CONCEPT", attributes=attributes)
        
        if "ANALYZE" in req_tokens or "EVALUATE" in req_tokens:
            attributes = self._enhance_target_attributes("DOCUMENT", text, doc)
            return Target(token="DOCUMENT", attributes=attributes)
        
        if "EXTRACT" in req_tokens or "IDENTIFY" in req_tokens:
            attributes = self._enhance_target_attributes("DATA", text, doc)
            return Target(token="DATA", attributes=attributes)
        
        if "CALCULATE" in req_tokens or "COMPUTE" in req_tokens:
            attributes = self._enhance_target_attributes("RESULT", text, doc)
            return Target(token="RESULT", attributes=attributes)
        
        if "COMPARE" in req_tokens:
            attributes = self._enhance_target_attributes("ITEMS", text, doc)
            attributes['TYPE'] = 'COMPARISON'
            return Target(token="ITEMS", attributes=attributes)
        
        if "TRANSFORM" in req_tokens or "CONVERT" in req_tokens:
            attributes = self._enhance_target_attributes("RESULT", text, doc)
            return Target(token="RESULT", attributes=attributes)
        
        if "CLASSIFY" in req_tokens or "CATEGORIZE" in req_tokens:
            attributes = self._enhance_target_attributes("CONTENT", text, doc)
            return Target(token="CONTENT", attributes=attributes)
        
        # Ultimate fallback: ANSWER
        attributes = self._enhance_target_attributes("ANSWER", text, doc)
        return Target(token="ANSWER", attributes=attributes)

    def _add_domain_attributes(self, targets: list[Target], text: str) -> list[Target]:
        """Add domain-specific attributes to targets (keep existing logic)"""
        # This method stays the same - just returns targets as-is
        # Domain is already added in _enhance_target_attributes
        return targets
        