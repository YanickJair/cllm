from typing import Optional
from dataclasses import dataclass, field


@dataclass
class Intent:
    """ Represents a detected intent (REQ token) """
    token: str # e.g., "ANALYZE"
    confidence: float # 0.0 to 1.0
    trigger_word: str # Word that triggered detection
    modifier: Optional[str] = None # e.g., "DEEP", "SURFACE"
    unmatched_verbs: list[str] = field(default_factory=list)      # Verbs that didn't map to REQ


@dataclass
class Target:
    """ Represents a target object (TARGET token) """
    token: str # e.g., "CODE"
    domain: Optional[str] = None # e.g., "SUPPORT", "TECHNICAL"
    attributes: dict[str, str] | None = None  # e.g., {"LANG": "PYTHON"}
    unmatched_nouns: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.attributes is None:
            self.attributes = {}

@dataclass
class ExtractionField:
    """Represents fields to extract"""
    fields: list[str]  # e.g., ["ISSUE", "SENTIMENT", "ACTIONS"]
    attributes: dict[str, str] | None = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

@dataclass
class Context:
    """Represents context constraints (CTX token)"""
    aspect: str  # e.g., "TONE", "STYLE", "AUDIENCE"
    value: str  # e.g., "PROFESSIONAL", "SIMPLE"


@dataclass
class OutputFormat:
    """Represents output format (OUT token)"""
    format_type: str  # e.g., "JSON", "MARKDOWN", "TABLE"
    attributes: dict[str, str] | None = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


@dataclass
class CompressionResult:
    """Complete compression result"""
    original: str
    compressed: str
    intents: list[Intent]
    targets: list[Target]
    extractions: Optional[ExtractionField]
    contexts: list[Context]
    output_format: Optional[OutputFormat]
    compression_ratio: float
    metadata: dict
