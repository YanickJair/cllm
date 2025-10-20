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
            "data structures", "algorithms", "computational complexity", "operating systems",
            "virtual memory", "concurrency", "multithreading", "parallel computing",
            "distributed systems", "load balancing", "event-driven architecture",
            "ip", "udp", "icmp", "ssh", "ftp", "smtp", "snmp", "websockets", "vpn",
            "cdn", "proxy servers", "firewalls", "nat", "bgp",
            "relational databases", "document databases", "graph databases", "time-series databases",
            "indexing", "query optimization", "acid", "event sourcing", "data warehousing",
            "etl", "data lakes", "caching", "redis", "elasticsearch",
            "object-oriented programming", "functional programming", "test-driven development",
            "design patterns", "dependency injection", "continuous integration",
            "continuous deployment", "version control", "git", "monolith", "microfrontends",
            "domain-driven design", "clean architecture",
            "infrastructure as code", "terraform", "ansible", "jenkins", "cicd pipelines",
            "monitoring", "observability", "logging", "prometheus", "grafana",
            "load testing", "chaos engineering",
            "reinforcement learning", "computer vision", "natural language processing",
            "generative ai", "transformers", "autoencoders", "feature engineering",
            "data preprocessing", "model deployment", "mlops", "vector databases",
            "encryption", "hashing", "ssl", "tls", "oauth", "jwt", "zero trust architecture",
            "penetration testing", "vulnerability scanning", "access control", "iam",
            "next.js", "svelte", "astro", "webassembly", "typescript", "tailwind css",
            "progressive web apps", "responsive design", "web performance optimization",
            "grpc", "openapi", "soap", "rate limiting", "api gateway", "message queues",
            "rabbitmq", "kafka", "event-driven systems", "background jobs", "webhooks",
            "ecs", "eks", "lambda", "cloud run", "app engine", "cloudflare workers",
            "service mesh", "istio", "helm", "container orchestration",
            "edge computing", "fog computing", "5g", "iot", "ar", "vr", "xr",
            "federated learning", "quantum encryption", "digital twins", "neuromorphic computing",
            "go", "rust", "swift", "kotlin", "scala", "r", "bash", "c", "c++", "java",
            "ruby", "php", "dart", "flutter", "swiftui",
            "big data", "hadoop", "spark", "kafka streams", "flink", "databricks",
            "data pipelines", "real-time analytics", "business intelligence", "power bi", "tableau"
        ]
        self.cx_technical_concepts = [
            "customer experience", "customer journey", "customer satisfaction",
            "customer retention", "customer loyalty", "customer lifetime value",
            "net promoter score", "nps", "csat", "ces", "customer effort score",
            "churn rate", "voice of the customer", "voc",
            "ticketing system", "helpdesk software", "sla", "first response time",
            "average handle time", "aht", "first call resolution", "fcr",
            "resolution time", "queue management", "escalation management",
            "after call work", "acw", "wrap-up codes", "call disposition",
            "call scripts", "knowledge base", "faq automation", "self-service portal",
            "omnichannel support", "multichannel support", "call handling",
            "inbound calls", "outbound calls", "call queue", "warm transfer",
            "cold transfer", "call escalation", "ticket creation",
            "voice support", "email support", "chat support", "live chat",
            "social media support", "whatsapp support", "sms support",
            "video support", "blended agents", "channel switching",
            "co-browsing", "screen sharing",
            "crm", "agent workspace", "unified agent desktop",
            "zendesk", "freshdesk", "intercom", "salesforce service cloud",
            "hubspot service hub", "helpscout", "genesys", "genesys cloud",
            "twilio flex", "nice incontact", "five9", "avaya", "amazon connect",
            "ccaas", "frontapp", "aircall", "qualtrics", "medallia",
            "chatbots", "voicebots", "virtual assistants", "conversational ai",
            "natural language processing", "nlp routing", "sentiment analysis",
            "intent detection", "speech analytics", "voice recognition",
            "predictive analytics", "ai routing", "automated responses",
            "co-pilot ai", "agent assist ai", "automated workflows",
            "rpa", "bot handoff", "queue prioritization", "call routing",
            "skill-based routing", "emotion detection", "next best action",
            "customer data platform", "cdp", "crm integration", "data integration",
            "real-time analytics", "dashboards", "reporting automation",
            "cohort analysis", "text analytics", "journey analytics",
            "feedback analytics", "customer segmentation",
            "agent performance dashboard", "leaderboards", "kpi tracking",
            "api integration", "webhooks", "bi tools integration", "single sign-on",
            "sso", "oauth", "rest api", "graphql api", "workflow automation",
            "ifttt", "zapier", "data synchronization", "real-time data fetch",
            "user experience", "user interface", "ux design", "ui design",
            "personalization", "customer onboarding", "journey mapping",
            "heatmaps", "a/b testing", "conversion optimization",
            "behavioral analytics", "user feedback loops", "context-aware responses",
            "contact center as a service", "ivr", "interactive voice response",
            "auto dialer", "predictive dialer", "automatic call distributor",
            "acd", "call recording", "screen recording", "call monitoring",
            "live coaching", "speech-to-text", "cloud telephony", "call routing",
            "ivr menu design", "real-time monitoring", "agent dashboards",
            "softphone", "headset integration", "voip", "vpn connection",
            "latency monitoring", "system uptime", "network quality metrics",
            "call latency", "packet loss", "webrtc", "browser-based contact center",
            "thin client environments",
            "gdpr", "ccpa", "data privacy", "pii masking", "data redaction",
            "pci compliance", "security compliance", "access control",
            "encryption", "audit logs", "role-based permissions",
            "secure payment capture", "identity verification",
            "call authentication", "voice biometrics", "knowledge-based authentication",
            "session recording consent", "two-factor authentication",
            "e-learning modules", "microlearning", "gamification", "coaching sessions",
            "agent onboarding", "call simulations", "ai feedback", "training analytics",
            "knowledge suggestions", "contextual knowledge surfacing",
            "real-time assist prompts", "virtual training environments",
            "customer profile", "interaction history", "case notes",
            "customer sentiment", "customer intent", "journey orchestration",
            "proactive support", "predictive support", "hyper-personalization",
            "contextual engagement", "customer digital twin", "emotion ai",
            "real-time translation", "voice biometrics", "augmented reality support",
            "self-healing systems", "recommendation engine", "agent sentiment tracking",
            "real-time transcription", "automated note taking", "proactive engagement prompts"
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

        # PRIORITY 6: Fallback system
        if not targets:
            fallback = self._get_fallback_target(text, doc, detected_req_tokens)
            if fallback:
                targets.append(fallback)

        return self._add_domain_attributes(targets, text)

    @staticmethod
    def _detect_imperative_target(text: str, req_tokens: list[str] = None) -> Optional[Target]:
        """
        Detect targets for imperative commands at sentence start

        Handles:
        - "List X" → ITEMS
        - "Name X" → ITEMS
        - "Calculate X" → RESULT
        - "Generate X" → depends on X and REQ context
        - "Create X" → depends on X and REQ context
        - CX domain targets: TICKET, TRANSCRIPT, EMAIL, COMPLAINT, etc.

        Args:
            text: Prompt text
            req_tokens: Already detected REQ tokens (helps determine target)

        Returns:
            Target object with appropriate token and attributes, or None
        """
        text_lower = text.lower().strip()
        req_tokens = req_tokens or []

        req_actions = [req.split(':')[0] if ':' in req else req for req in req_tokens]

        cx_keywords = {
            'ticket': ('TICKET', ['support', 'issue', 'ticket', 'case', 'incident']),
            'transcript': ('TRANSCRIPT', ['transcript', 'conversation', 'chat', 'dialogue', 'call', 'interaction']),
            'email': ('EMAIL', ['email', 'message', 'correspondence']),
            'complaint': ('COMPLAINT', ['complaint', 'escalation', 'grievance']),
            'feedback': ('FEEDBACK', ['feedback', 'review', 'rating', 'survey']),
            'query': ('QUERY', ['query', 'question', 'inquiry', 'request']),
        }

        for target_type, (target_token, keywords) in cx_keywords.items():
            if any(kw in text_lower[:100] for kw in keywords):
                attributes = {}

                if any(word in text_lower for word in ['support', 'customer service', 'helpdesk']):
                    attributes['DOMAIN'] = 'SUPPORT'
                elif any(word in text_lower for word in ['sales', 'billing', 'payment']):
                    attributes['DOMAIN'] = 'SALES'
                elif any(word in text_lower for word in ['technical', 'tech', 'bug']):
                    attributes['DOMAIN'] = 'TECHNICAL'

                if any(word in text_lower for word in ['urgent', 'critical', 'asap', 'emergency']):
                    attributes['PRIORITY'] = 'HIGH'
                elif any(word in text_lower for word in ['low priority', 'minor', 'eventual']):
                    attributes['PRIORITY'] = 'LOW'

                return Target(token=target_token, attributes=attributes)

        if re.match(r'^(generate|create|write|draft|compose)\s+', text_lower):
            if any(word in text_lower[:80] for word in ['response', 'reply', 'answer', 'customer', 'client']):
                attributes = {}

                if any(word in text_lower for word in ['professional', 'formal']):
                    attributes['TONE'] = 'PROFESSIONAL'
                elif any(word in text_lower for word in ['empathetic', 'apologetic', 'sorry']):
                    attributes['TONE'] = 'EMPATHETIC'
                elif any(word in text_lower for word in ['casual', 'friendly']):
                    attributes['TONE'] = 'CASUAL'

                return Target(token='RESPONSE', attributes=attributes)

        if re.match(r'^(list|name|enumerate|itemize)\s+', text_lower):
            if any(word in text_lower[:50] for word in
                   ["benefits", "examples", "types", "reasons", "ways", "methods", "steps", "items"]):
                attributes = {}

                # Detect if ordered list is implied
                if any(word in text_lower for word in ['steps', 'process', 'sequence', 'order']):
                    attributes['TYPE'] = 'ORDERED'
                else:
                    attributes['TYPE'] = 'LIST'

                return Target(token="ITEMS", attributes=attributes)
            return Target(token="ITEMS", attributes={})

        if re.match(r'^(calculate|compute|determine|find\s+the)\s+', text_lower):
            calc_match = re.search(r'^(?:calculate|compute|determine|find\s+the)\s+([\w\s]+?)(?:\.|$|\n|of)',
                                   text_lower)
            attributes = {}
            if calc_match:
                calc_type = calc_match.group(1).strip()
                attributes['TYPE'] = calc_type.upper().replace(' ', '_')

            return Target(token="RESULT", attributes=attributes)

        if re.match(r'^(extract|identify|find)\s+', text_lower):
            if 'EXTRACT' in req_actions:
                extract_targets = {
                    'issue': 'TICKET',
                    'problem': 'TICKET',
                    'sentiment': 'TRANSCRIPT',
                    'intent': 'MESSAGE',
                    'entities': 'DOCUMENT',
                    'data': 'DATA',
                    'information': 'DOCUMENT'
                }

                for keyword, target in extract_targets.items():
                    if keyword in text_lower[:50]:
                        return Target(token=target, attributes={})

            return Target(token="DATA", attributes={})

        if re.match(r'^(analyze|review|examine|evaluate|assess)\s+', text_lower):
            analysis_targets = {
                'code': ('CODE', {}),
                'script': ('CODE', {}),
                'function': ('CODE', {}),
                'conversation': ('TRANSCRIPT', {'DOMAIN': 'SUPPORT'}),
                'transcript': ('TRANSCRIPT', {}),
                'ticket': ('TICKET', {}),
                'email': ('EMAIL', {}),
                'document': ('DOCUMENT', {}),
                'data': ('DATA', {}),
                'sentiment': ('TRANSCRIPT', {}),
            }

            for keyword, (target, attrs) in analysis_targets.items():
                if keyword in text_lower[:60]:
                    return Target(token=target, attributes=attrs)
            return Target(token="DOCUMENT", attributes={})

        if re.match(r'^(generate|create|write|draft|compose)\s+', text_lower):
            content_types = {
                "response": ("RESPONSE", {}),
                "reply": ("RESPONSE", {}),
                "answer": ("RESPONSE", {}),
                "email": ("EMAIL", {}),
                "message": ("MESSAGE", {}),
                "report": ("REPORT", {}),
                "summary": ("SUMMARY", {}),
                "documentation": ("DOCUMENT", {}),
                "article": ("ARTICLE", {}),
                "story": ("CONTENT", {'TYPE': 'NARRATIVE'}),
                "essay": ("CONTENT", {'TYPE': 'ESSAY'}),
                "blog": ("CONTENT", {'TYPE': 'BLOG'}),
                "code": ("CODE", {}),
                "script": ("CODE", {}),
                "function": ("CODE", {}),
                "api": ("CODE", {'TYPE': 'API'}),
                "list": ("ITEMS", {}),
                "table": ("DATA", {'FORMAT': 'TABLE'}),
                "json": ("DATA", {'FORMAT': 'JSON'}),
                "description": ("DESCRIPTION", {}),
                "explanation": ("EXPLANATION", {}),
            }

            for content_type, (target, attrs) in content_types.items():
                if content_type in text_lower[:60]:
                    if 'GENERATE' in req_actions and target == 'CODE':
                        langs = ['python', 'javascript', 'java', 'c++', 'ruby', 'go', 'rust']
                        for lang in langs:
                            if lang in text_lower[:80]:
                                attrs['LANG'] = lang.upper()
                                break

                    return Target(token=target, attributes=attrs)

            if 'GENERATE' in req_actions:
                return Target(token="CONTENT", attributes={})

        if re.match(r'^(compare|rank|order|sort)\s+', text_lower):
            return Target(token="ITEMS", attributes={'TYPE': 'COMPARISON'})

        if re.match(r'^(summarize|condense|brief)\s+', text_lower):
            if any(word in text_lower[:50] for word in ['conversation', 'transcript', 'chat']):
                return Target(token="TRANSCRIPT", attributes={})
            elif any(word in text_lower[:50] for word in ['document', 'article', 'report']):
                return Target(token="DOCUMENT", attributes={})
            else:
                return Target(token="SUMMARY", attributes={})

        if re.match(r'^(transform|convert|translate|rewrite)\s+', text_lower):
            attributes = {}
            formats = ['json', 'xml', 'csv', 'markdown', 'html', 'yaml']
            for fmt in formats:
                if fmt in text_lower[:80]:
                    attributes['FORMAT'] = fmt.upper()
                    break

            return Target(token="RESULT", attributes=attributes)

        return None

    @staticmethod
    def _detect_question_target(text: str, doc: Doc) -> Optional[Target]:
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

        if text_lower.startswith(("what is", "what are", "what's")):
            match = re.search(r'what\s+(?:is|are|\'s)\s+(.+?)(?:\?|$)', text_lower)
            if match:
                subject = match.group(1).strip()
                subject = re.sub(r'^(the|a|an)\s+', '', subject)

                return Target(
                    token="CONCEPT",
                    attributes={"TOPIC": subject.upper().replace(" ", "_"), "TYPE": "DEFINITION"}
                )
            return Target(token="CONCEPT", attributes={"TYPE": "DEFINITION"})

        if text_lower.startswith(("how to", "how do i", "how can i", "how do you")):
            match = re.search(r'how\s+(?:to|do\s+(?:i|you)|can\s+i)\s+(.+?)(?:\?|$)', text_lower)
            if match:
                action = match.group(1).strip()
                return Target(
                    token="PROCEDURE",
                    attributes={"ACTION": action.upper().replace(" ", "_")}
                )
            return Target(token="PROCEDURE", attributes={})

        if re.match(r'how\s+(?:does|do)\s+', text_lower):
            match = re.search(r'how\s+(?:does|do)\s+(.+?)(?:\s+work|\?|$)', text_lower)
            if match:
                subject = match.group(1).strip()
                return Target(
                    token="CONCEPT",
                    attributes={"TOPIC": subject.upper().replace(" ", "_"), "TYPE": "MECHANISM"}
                )
            return Target(token="CONCEPT", attributes={"TYPE": "MECHANISM"})

        if text_lower.startswith("why"):
            return Target(token="EXPLANATION", attributes={})

        if text_lower.startswith(("when", "where")):
            return Target(token="FACT", attributes={})

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

    @staticmethod
    def _get_fallback_target(text: str, doc: Doc, req_tokens: list[str] = None) -> Optional[Target]:
        """
        Intelligent fallback when no target detected

        Uses REQ tokens + text patterns to infer appropriate target

        Args:
            text: Prompt text
            doc: spaCy doc
            req_tokens: List of detected REQ tokens
        """
        text_lower = text.lower()
        req_tokens = req_tokens or []

        if "GENERATE" in req_tokens or "LIST" in req_tokens:
            creative_indicators = ["story", "poem", "essay", "narrative", "creative", "fiction"]
            if any(ind in text_lower for ind in creative_indicators):
                return Target(token="CONTENT", attributes={})

            list_indicators = ["list", "benefits", "examples", "reasons", "ways", "types", "methods"]
            if any(ind in text_lower[:30] for ind in list_indicators):
                return Target(token="ITEMS", attributes={})

            return Target(token="CONTENT", attributes={})

        if "CALCULATE" in req_tokens:
            return Target(token="RESULT", attributes={})

        if "ANALYZE" in req_tokens or "EVALUATE" in req_tokens:
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

            return Target(token="CONTENT", attributes={})

        if "EXPLAIN" in req_tokens or "DESCRIBE" in req_tokens:
            return Target(token="CONCEPT", attributes={})

        if "COMPARE" in req_tokens:
            return Target(token="OPTIONS", attributes={})

        if "EXTRACT" in req_tokens:
            return Target(token="DATA", attributes={})

        if "TRANSFORM" in req_tokens:
            return Target(token="CONTENT", attributes={})

        if "CLASSIFY" in req_tokens:
            return Target(token="ITEMS", attributes={"ACTION": "CLASSIFY"})

        if any(word in text_lower[:20] for word in ["list", "name", "enumerate"]):
            return Target(token="ITEMS", attributes={})

        if any(word in text_lower[:20] for word in ["explain", "describe", "tell"]):
            return Target(token="CONCEPT", attributes={})

        if any(word in text_lower[:20] for word in ["create", "write", "generate"]):
            return Target(token="CONTENT", attributes={})

        if text.strip().endswith("?"):
            if text_lower.startswith("what"):
                return Target(token="CONCEPT", attributes={})
            if text_lower.startswith("how"):
                return Target(token="PROCEDURE", attributes={})
            return Target(token="ANSWER", attributes={})

        word_count = len(text.split())
        if word_count < 10:
            return Target(token="ANSWER", attributes={})

        return Target(token="CONTENT", attributes={})

    @staticmethod
    def _add_domain_attributes(targets: list[Target], text: str) -> list[Target]:
        """Add domain-specific attributes to targets"""
        text_lower = text.lower()

        domain_keywords = {
            "SUPPORT": ["customer support", "customer service", "support ticket"],
            "TECHNICAL": ["technical", "engineering", "development", "code review", "fix bug"],
            "BUSINESS": ["business", "corporate", "enterprise"],
            "MEDICAL": ["medical", "healthcare", "clinical"],
        }

        for target in targets:
            for domain, keywords in domain_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    target.domain = domain
                    break

            if target.token == "CODE":
                languages = ["python", "javascript", "java", "c++", "ruby", "go", "rust", "typescript"]
                for lang in languages:
                    if lang in text_lower:
                        target.attributes["LANG"] = lang.upper()
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
        """
        text_lower = text.lower()

        explanation_verbs = ["explain", "describe", "clarify", "elucidate", "tell"]

        for token in doc:
            if token.lemma_ in explanation_verbs:
                for child in token.children:
                    if child.dep_ in ["dobj", "attr", "pobj"]:
                        concept_text = self._extract_noun_phrase(child)
                        if concept_text:
                            return Target(
                                token="CONCEPT",
                                attributes={"TOPIC": concept_text.upper().replace(" ", "_")}
                            )

        how_works_pattern = r"how\s+([a-zA-Z\s]+?)\s+works?"
        match = re.search(how_works_pattern, text_lower)
        if match:
            concept = match.group(1).strip()
            return Target(
                token="CONCEPT",
                attributes={"TOPIC": concept.upper().replace(" ", "_")}
            )

        for term in self.technical_concepts:
            if term in text_lower:
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
                for chunk in doc.noun_chunks:
                    if chunk.start > i:
                        noun = chunk.root.text.lower()
                        target_token = self.vocab.get_target_token(noun)
                        if target_token:
                            return Target(token=target_token, attributes={})
                        break

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