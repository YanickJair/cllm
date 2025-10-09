from typing import Optional


# Token vocabulary definitions
class Vocabulary:
    """CLLM token vocabulary with synonyms and patterns"""

    # REQ tokens with trigger words
    REQ_TOKENS = {
        # Core analysis actions
        "ANALYZE": [
            "analyze", "review", "examine", "evaluate", "assess", "inspect",
            "check out", "audit", "investigate"
        ],

        # Information extraction
        "EXTRACT": [
            "extract", "pull out", "identify", "find", "locate", "get",
            "retrieve", "return", "include", "select", "pick out"
        ],

        # Content generation
        "GENERATE": [
            "generate", "create", "write", "draft", "compose", "produce",
            "build", "develop", "design", "craft", "author", "make up",
            "name", "suggest", "formulate", "form", "construct"
        ],

        # Summaries and condensing
        "SUMMARIZE": [
            "summarize", "condense", "brief", "synopsis", "sum up",
            "digest", "recap"
        ],

        # Content transformation
        "TRANSFORM": [
            "convert", "transform", "change", "rewrite", "translate", "complete",
            "turn into", "modify", "adapt", "adjust", "rephrase", "rework", "rearrange",
            "edit", "add", "paraphrase", "fill", "remove", "replace", "reverse",
        ],

        # Explanations and descriptions
        "EXPLAIN": [
            "explain", "describe", "clarify", "elaborate", "tell me about",
            "detail", "expound", "illustrate", "express", "tell", "discuss", "define"
        ],

        # Comparisons
        "COMPARE": [
            "compare", "contrast", "versus", "vs", "difference between",
            "differentiate", "distinguish"
        ],

        # Classification and organization
        "CLASSIFY": [
            "classify", "categorize", "sort", "group", "label", "organize",
            "arrange", "order by", "segment"
        ],

        # Debugging and fixing
        "DEBUG": [
            "debug", "fix", "troubleshoot", "diagnose", "solve", "repair",
            "resolve", "correct"
        ],

        # Optimization and improvement
        "OPTIMIZE": [
            "optimize", "improve", "enhance", "refactor", "speed up",
            "streamline", "maximize", "minimize",
            # NEW: Specific improvement verbs (65+ occurrences)
            "reduce",  # "Reduce air pollution"
            "increase",  # "Increase efficiency"
        ],

        # Validation and verification
        "VALIDATE": [
            "validate", "verify", "check", "confirm", "test", "ensure",
            "certify", "authenticate"
        ],

        # Search operations
        "SEARCH": [
            "search", "query", "lookup", "find", "look for", "seek",
            "hunt for", "discover"
        ],

        # Ranking and prioritization
        "RANK": [
            "rank", "prioritize", "order", "sort by", "rate", "score"
        ],

        # Predictions and forecasting
        "PREDICT": [
            "predict", "forecast", "estimate", "project", "anticipate",
            "foresee", "extrapolate"
        ],

        # Formatting
        "FORMAT": [
            "format", "structure", "organize", "layout", "arrange"
        ],

        # Detection
        "DETECT": [
            "detect", "spot", "discover", "uncover", "identify", "notice",
            "recognize"
        ],

        # Mathematical operations
        "CALCULATE": [
            "calculate", "compute", "figure out", "determine mathematically",
            "quantify", "measure", "count", "tally"
        ],

        # Aggregation
        "AGGREGATE": [
            "aggregate", "group", "combine", "consolidate", "roll up",
            "merge", "compile", "collect"
        ],

        # Decision making
        "DETERMINE": [
            "determine", "decide", "assess", "evaluate", "figure out",
            "conclude", "establish", "choose"
        ],

        # Routing and assignment
        "ROUTE": [
            "route", "assign", "direct", "forward", "send to", "delegate",
            "allocate"
        ],

        # NEW: Action execution (376 occurrences - HIGHEST PRIORITY)
        "EXECUTE": [
            "use",  # "Use X to do Y"
            "apply",  # "Apply this method"
            "implement",  # "Implement this solution"
            "run",  # "Run this script"
            "perform",  # "Perform this action"
            "employ",  # "Employ this technique"
            "utilize"  # "Utilize these resources"
        ],

        # NEW: List generation (117+ occurrences with 72.6% fail rate)
        "LIST": [
            "list",  # "List 5 benefits"
            "enumerate",  # "Enumerate the steps"
            "itemize",  # "Itemize the costs"
            "outline"  # "Outline the main points"
        ],
    }

    # Verbs to EXCLUDE from intent detection (noise words)
    # These appear as verbs in parsing but are not actionable intents
    NOISE_VERBS = {
        # Auxiliary/modal verbs
        "be", "have", "do", "can", "could", "should", "would", "may",
        "might", "must", "will", "shall",

        # Generic motion/state verbs (non-specific actions)
        "go", "come", "take", "get", "make", "work", "live", "stay",

        # Descriptive/relational verbs (not actions)
        "follow", "base", "relate", "need", "want", "start", "begin",
        "become", "seem", "appear", "remain",

        # Context-dependent verbs (too ambiguous)
        "show", "see", "know", "think", "feel", "say", "call",
    }

    # Context patterns to filter out (verb used non-actionably)
    CONTEXT_FILTERS = {
        "give": ["given", "give me", "giving"],  # "the given text" is not an action
        "follow": ["following", "as follows"],  # "the following items" is not an action
        "base": ["based on", "base it on"],  # "based on X" is descriptive
        "use": ["useful", "used to", "uses"],  # Sometimes descriptive
    }

    # TARGET tokens with trigger words
    TARGET_TOKENS = {
        # Technical artifacts
        "CODE": ["code", "script", "program", "function", "method", "class", "snippet"],
        "DATA": ["data", "dataset", "database", "spreadsheet", "table", "csv"],
        "QUERY": ["query", "sql", "sql query", "database query"],
        "ENDPOINT": ["endpoint", "api", "api endpoint", "rest endpoint"],
        "COMPONENT": ["component", "module", "package", "library"],
        "SYSTEM": ["system", "application", "app", "software", "platform"],
        "TEST": ["test", "unit test", "test case", "test suite"],
        "LOG": ["log", "logs", "log file", "error log", "system log"],
        "RECORD": ["record", "entry", "row", "item"],
        "STRATEGY": ["strategy", "approach", "plan", "methodology"],

        # Documents and content
        "DOCUMENT": ["document", "doc", "file", "report", "paper"],
        "EMAIL": ["email", "message", "correspondence"],
        "REPORT": ["report", "analysis", "findings", "summary report"],
        "TICKET": ["ticket", "support ticket", "issue", "case"],
        "TRANSCRIPT": ["transcript", "conversation", "dialogue", "chat log"],
        "FEEDBACK": ["feedback", "comment", "review", "critique"],
        "COMMENT": ["comment", "remark", "note", "observation"],

        # Customer service
        "COMPLAINT": ["complaint", "issue", "problem", "grievance"],
        "REQUEST": ["request", "customer request", "service request"],
        "INQUIRY": ["inquiry", "question", "query"],
        "INTERACTION": ["interaction", "support interaction", "customer interaction"],
        "CALL": ["call", "phone call", "support call", "customer call"],

        # Business content
        "EMAIL": ["email", "message", "correspondence"],
        "DESCRIPTION": ["description", "product description"],
        "SUMMARY": ["summary", "executive summary", "brief summary"],
        "PLAN": ["plan", "business plan", "project plan"],
        "POST": ["post", "linkedin post", "social media post", "blog post"],
        "PRESS_RELEASE": ["press release", "release", "announcement"],
        "INTRODUCTION": ["introduction", "intro"],
        "CAPTION": ["caption", "captions", "social media caption"],
        "QUESTIONS": ["questions", "interview questions", "quiz questions", "faq"],
        "RESPONSE": ["response", "reply", "answer", "template response"],

        # Analysis targets
        "LOGS": ["logs", "log files", "traffic logs", "system logs", "access logs"],
        "CORRELATION": ["correlation", "correlations", "relationship", "relationships"],
        "TRADEOFF": ["trade-off", "tradeoffs", "tradeoff", "trade-offs"],
        "PARADIGM": ["paradigm", "paradigms", "methodology", "approach"],
        "PAIN_POINTS": ["pain points", "pain point", "issues", "problems"],
        "PATTERN": ["pattern", "patterns", "trend", "trends"],
        "CHURN": ["churn", "customer churn", "attrition"],
        "FEATURES": ["features", "feature", "functionality", "capabilities"],

        # Abstract/metrics
        "METRICS": ["revenue", "metrics", "statistics", "numbers", "data points"],
        "REGIONS": ["regions", "areas", "locations", "territories"],

        # NEW: Fallback targets for common patterns
        "ITEMS": ["items", "things", "elements", "list", "options", "choices"],
        "CONCEPT": ["concept", "idea", "notion", "principle", "theory"],
        "PROCEDURE": ["procedure", "process", "steps", "method", "technique"],
        "FACT": ["fact", "facts", "information", "details", "truth"],
        "ANSWER": ["answer", "solution", "response"],
    }

    # Common extraction fields
    EXTRACT_FIELDS = [
        "ISSUE", "SENTIMENT", "ACTIONS", "NEXT_STEPS", "URGENCY", "PRIORITY",
        "NAMES", "DATES", "AMOUNTS", "EMAILS", "PHONES", "ADDRESSES",
        "BUGS", "SECURITY", "PERFORMANCE", "STYLE", "ERRORS", "WARNINGS",
        "KEYWORDS", "TOPICS", "ENTITIES", "FACTS", "DECISIONS", "DEADLINES",
        "REQUIREMENTS", "FEATURES", "PROBLEMS", "SOLUTIONS", "RISKS",
        "METRICS", "KPI", "SCORES", "RATINGS", "FEEDBACK", "COMPLAINTS",
        "OWNERS", "ASSIGNEES", "STAKEHOLDERS", "PARTICIPANTS",
        "TIMESTAMPS", "DURATIONS", "FREQUENCIES", "QUANTITIES",
        "CATEGORIES", "TAGS", "LABELS", "STATUS", "TYPE"
    ]

    # Output formats with trigger words
    OUTPUT_FORMATS = {
        "JSON": ["json", "json format"],
        "MARKDOWN": ["markdown", "md"],
        "TABLE": ["table", "tabular"],
        "LIST": ["list", "bullet points", "bullets"],
        "PLAIN": ["plain text", "text only"],
        "CSV": ["csv", "comma-separated"]
    }

    @classmethod
    def get_req_token(cls, word: str, context: str = "") -> Optional[str]:
        """
        Find REQ token for a given word

        Args:
            word: The verb to match
            context: Surrounding text for context-aware filtering

        Returns:
            REQ token or None if no match or filtered out
        """
        word_lower = word.lower()

        # Filter out noise verbs
        if word_lower in cls.NOISE_VERBS:
            return None

        # Context-aware filtering
        if word_lower in cls.CONTEXT_FILTERS:
            for pattern in cls.CONTEXT_FILTERS[word_lower]:
                if pattern in context.lower():
                    return None

        # Match against vocabulary
        for token, synonyms in cls.REQ_TOKENS.items():
            if word_lower in synonyms:
                return token

        return None

    @classmethod
    def get_target_token(cls, word: str) -> Optional[str]:
        """Find TARGET token for a given word"""
        word_lower = word.lower()
        for token, synonyms in cls.TARGET_TOKENS.items():
            if word_lower in synonyms:
                return token
        return None

    @classmethod
    def get_output_format(cls, text: str) -> Optional[str]:
        """Find output format from text"""
        text_lower = text.lower()
        for format_type, triggers in cls.OUTPUT_FORMATS.items():
            if any(trigger in text_lower for trigger in triggers):
                return format_type
        return None

    @classmethod
    def detect_imperative_pattern(cls, text: str) -> Optional[tuple]:
        """
        Detect common imperative patterns at sentence start
        Returns (REQ_token, TARGET_token) or None
        """
        text_lower = text.lower().strip()

        # Pattern: "List X" / "Name X" / "Give X"
        imperative_patterns = [
            (["list", "enumerate", "itemize"], "LIST", "ITEMS"),
            (["name", "identify"], "GENERATE", "ITEMS"),
            (["give", "provide", "suggest"], "GENERATE", "ITEMS"),
            (["tell", "explain", "describe"], "EXPLAIN", "CONCEPT"),
        ]

        for triggers, req_token, target_token in imperative_patterns:
            for trigger in triggers:
                if text_lower.startswith(trigger + " "):
                    return req_token, target_token

        return None

    @classmethod
    def get_question_req(cls, text: str) -> Optional[str]:
        """
        NEW v2.1: Fallback REQ for question patterns with no verb detected

        Returns QUERY token for questions like:
        - "What is X?"
        - "What are the benefits?"
        - "Who is the president?"

        This handles the 168 prompts with no verbs detected.

        Args:
            text: The full prompt text

        Returns:
            "QUERY" if it's a question pattern, None otherwise

        Examples:
            >>> Vocabulary.get_question_req("What is machine learning?")
            'QUERY'

            >>> Vocabulary.get_question_req("Who invented the telephone?")
            'QUERY'

            >>> Vocabulary.get_question_req("Analyze this code")
            None
        """
        text_lower = text.lower().strip()

        # Check if it's a question (ends with ?)
        if not text.strip().endswith("?"):
            return None

        # Question words that indicate a query
        question_words = ["what", "who", "where", "when", "why", "how", "which"]

        # Check if the question starts with a question word
        if any(text_lower.startswith(word) for word in question_words):
            return "QUERY"

        return None