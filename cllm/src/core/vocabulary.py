from typing import Optional

# Token vocabulary definitions
class Vocabulary:
    """CLLM token vocabulary with synonyms and patterns"""
    
    # REQ tokens with trigger words
    REQ_TOKENS = {
        "ANALYZE": ["analyze", "review", "examine", "evaluate", "assess", "inspect", "check out"],
        "EXTRACT": ["extract", "pull out", "identify", "find", "locate", "get", "retrieve"],
        "GENERATE": ["generate", "create", "write", "draft", "compose", "produce", "build"],
        "SUMMARIZE": ["summarize", "condense", "brief", "synopsis", "sum up"],
        "TRANSFORM": ["convert", "transform", "change", "rewrite", "translate", "turn into"],
        "EXPLAIN": ["explain", "describe", "clarify", "elaborate", "tell me about"],
        "COMPARE": ["compare", "contrast", "versus", "vs", "difference between"],
        "CLASSIFY": ["classify", "categorize", "sort", "group", "label", "organize"],
        "DEBUG": ["debug", "fix", "troubleshoot", "diagnose", "solve"],
        "OPTIMIZE": ["optimize", "improve", "enhance", "refactor", "speed up"],
        "VALIDATE": ["validate", "verify", "check", "confirm", "test"],
        "SEARCH": ["search", "query", "lookup", "find", "look for"],
        "RANK": ["rank", "prioritize", "order", "sort by"],
        "PREDICT": ["predict", "forecast", "estimate", "project"],
        "FORMAT": ["format", "structure", "organize"],
    }
    
    # TARGET tokens with trigger words
    TARGET_TOKENS = {
        "CODE": ["code", "script", "function", "program", "algorithm"],
        "TRANSCRIPT": ["transcript", "conversation log", "chat log", "dialogue"],
        "EMAIL": ["email", "e-mail", "message"],
        "DOCUMENT": ["document", "text", "article", "paper", "file", "proposal", "documentation"],
        "DATA": ["data", "dataset", "csv", "spreadsheet", "table"],
        "TICKET": ["ticket", "issue", "request"],
        "COMPLAINT": ["complaint", "grievance"],
        "QUERY": ["query", "sql", "search query"],
        "FEEDBACK": ["feedback", "review", "rating"],
        "REPORT": ["report", "analysis", "findings"],
        "CONVERSATION": ["conversation", "chat", "discussion"],
        "SPECIFICATION": ["specification", "spec", "requirements"],
        "CONCEPT": ["concept", "idea", "theory"],
        "TEST": ["test", "unit test", "testing"],
        "FRAMEWORK": ["framework", "frameworks", "library", "platform", "tool", "libraries", "library", "platform", "platforms"]
    }
    
    # Common extraction fields
    EXTRACT_FIELDS = [
        "ISSUE", "SENTIMENT", "ACTIONS", "NEXT_STEPS", "URGENCY", "PRIORITY",
        "NAMES", "DATES", "AMOUNTS", "EMAILS", "PHONES", "ADDRESSES",
        "BUGS", "SECURITY", "PERFORMANCE", "STYLE", "ERRORS", "WARNINGS",
        "KEYWORDS", "TOPICS", "ENTITIES", "FACTS", "DECISIONS", "DEADLINES"
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
    def get_req_token(cls, word: str) -> Optional[str]:
        """Find REQ token for a given word"""
        word_lower = word.lower()
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
    