from typing import Optional, Annotated
from pydantic import BaseModel, Field


class Intent(BaseModel):
    """Represents a detected intent (REQ token)"""

    token: str  # e.g., "ANALYZE"
    confidence: float  # 0.0 to 1.0
    trigger_word: str  # Word that triggered detection
    modifier: Optional[str] = None  # e.g., "DEEP", "SURFACE"
    unmatched_verbs: list[str] = Field(
        default_factory=list
    )  # Verbs that didn't map to REQ


class Target(BaseModel):
    """Represents a target object (TARGET token)"""

    token: str  # e.g., "CODE"
    domain: Optional[str] = None  # e.g., "SUPPORT", "TECHNICAL"
    attributes: dict[str, str] | None = None  # e.g., {"LANG": "PYTHON"}
    unmatched_nouns: list[str] = Field(default_factory=list)

    def __post_init__(self) -> None:
        if self.attributes is None:
            self.attributes = {}

class ExtractionField(BaseModel):
    """Represents fields to extract"""

    fields: list[str]  # e.g., ["ISSUE", "SENTIMENT", "ACTIONS"]
    attributes: dict[str, str] | None = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

    def build_token(self) -> str | None:
        """
        Format the extraction field as a semantic token.
        Examples:
        - [EXTRACT:NAMES,DATES]
        - [EXTRACT:VERIFICATION,POLICY:DOMAIN=QA]
        """
        if not self.fields:
            return None

        result = f"[EXTRACT:{','.join(self.fields)}"

        if self.attributes:
            attr_parts = [f"{k}={v}" for k, v in self.attributes.items()]
            result += f":{','.join(attr_parts)}"

        result += "]"
        return result


class Context(BaseModel):
    """Represents context constraints (CTX token)"""

    aspect: str  # e.g., "TONE", "STYLE", "AUDIENCE"
    value: str  # e.g., "PROFESSIONAL", "SIMPLE"


class OutputFormat(BaseModel):
    """Represents output format (OUT token)"""

    format_type: str  # e.g., "JSON", "MARKDOWN", "TABLE"
    attributes: dict[str, str] | None = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

class OutputField(BaseModel):
    """Represents a single field in output schema"""
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    required: bool = True
    nested: Optional[list['OutputField']] = None



class OutputSchema(BaseModel):
    """Extracted schema from NL or structured definition"""
    format_type: str
    fields: list[OutputField]
    attributes: dict[str, str]
    raw_schema: Optional[dict | str] = None
    format_hint: Optional[str] = None

    def build_token(self) -> str:
        """
        Build token in the canonical format:

            [OUT_<FORMAT> : <SCHEMA> : key=value : key=value]

        - SCHEMA always comes first.
        - Other attributes (SCORE_MAP, SPECS, KEYS, etc.) follow.
        - Order of attributes is stable: SCHEMA → KEYS → SCORE_MAP → SPECS → others.
        """
        fmt = (self.format_hint or self.format_type or "STRUCTURED").upper()
        schema = self.attributes.get("schema", "")
        parts = [f"OUT_{fmt}", f"{schema}"]
        ordered_keys = []

        if "KEYS" in self.attributes:
            ordered_keys.append("KEYS")
        if "SCORE_MAP" in self.attributes:
            ordered_keys.append("SCORE_MAP")
        if "SPECS" in self.attributes:
            ordered_keys.append("SPECS")

        for k in sorted(self.attributes.keys()):
            if k not in ["schema", "KEYS", "SCORE_MAP", "SPECS"]:
                ordered_keys.append(k)

        for k in ordered_keys:
            parts.append(f"{k}={self.attributes[k]}")

        return "[" + ":".join(parts) + "]"


class CompressionResult(BaseModel):
    """Complete compression result"""

    original: str
    compressed: str
    intents: list[Intent]
    target: Target
    extractions: Optional[ExtractionField]
    contexts: list[Context]
    output_format: Optional[OutputSchema]
    compression_ratio: float
    metadata: dict

class DetectedField(BaseModel):
    name: str
    span: tuple[int, int]
    source: str
    confidence: float


class SysPromptConfig(BaseModel):
    lang: str = Field(default="en", description="Language of the prompt")
    infer_types: Annotated[bool, Field(default=False, description="Infer types for output fields")]
    add_examples: Annotated[bool, Field(default=False, description="Add examples based on extracted ones from input if exist")]
    add_attrs: Annotated[bool, Field(default=True, description="Add extra attributes from input prompt")]
