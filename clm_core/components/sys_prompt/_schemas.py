from typing import Optional, Annotated
from pydantic import BaseModel, Field, computed_field

DEFAULT_DOMAIN_MAP = {
    "CALL": "SUPPORT",
    "TICKET": "SUPPORT",
}


class Intent(BaseModel):
    """Represents a detected intent (REQ token)"""

    token: Annotated[str, Field(..., description="Main action ANALYZE")]
    confidence: Annotated[float, Field(default=0.0, description="Confidence score")]
    trigger_word: Annotated[str, Field(default="", description="Trigger word")]
    modifier: Annotated[
        Optional[str],
        Field(default=None, description="Modifier (optional) DEEP,SURFACE"),
    ]
    unmatched_verbs: list[str] = Field(
        default_factory=list, description="Verbs that didn't map to REQ"
    )


class Target(BaseModel):
    token: str
    domain: Optional[str] = None
    attributes: dict[str, str] | None = None
    unmatched_nouns: list[str] = Field(default_factory=list)

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

    def build_token(self) -> str:
        """
        Produces clean CLLM TARGET token:
        [TARGET:<TOKEN>:DOMAIN=...:ATTR=...]
        """

        token = str(self.token).upper()
        parts = [f"TARGET:{token}"]

        domain = None
        if self.domain:
            domain = self.domain.upper()

        attrs = dict(self.attributes or {})
        if "DOMAIN" in attrs:
            if domain is None:
                domain = str(attrs["DOMAIN"])
            attrs.pop("DOMAIN")

        if domain:
            parts.append(f"DOMAIN={domain}")

        clean_attrs = {}
        for k, v in attrs.items():
            ck = str(k)
            cv = str(v)
            clean_attrs[ck] = cv

        for k in sorted(clean_attrs.keys()):
            parts.append(f"{k}={clean_attrs[k]}")

        return "[" + ":".join(parts) + "]"


class ExtractionField(BaseModel):
    """Represents fields to extract"""

    fields: list[str] = Field(
        ...,
        description="Fields that represent what to extract from the input (i.e. ISSUE, SENTIMENT, ACTIONS)",
    )
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

    aspect: str = Field(
        ...,
        description="Some aspect presented in prompt for context aware (e.g., TONE, STYLE, AUDIENCE)",
    )
    value: str = Field(
        ...,
        description="Value of the aspect presented in prompt for context aware (PROFESSIONAL, SIMPLE)",
    )


class OutputFormat(BaseModel):
    """Represents output format (OUT token)"""

    format_type: str
    attributes: dict[str, str] | None = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


class OutputField(BaseModel):
    """Represents a single field in output schema"""

    name: str = Field(..., description="Name of the field")
    type: Optional[str] = Field(None, description="Type of the field")
    description: Optional[str] = Field(None, description="Description of the field")
    required: bool = Field(True, description="Whether the field is required")
    nested: Optional[list["OutputField"]] = Field(None, description="Nested fields")


class OutputSchema(BaseModel):
    """Extracted schema from NL or structured definition"""

    format_type: str = Field(..., description="Format type of the schema")
    fields: list[OutputField] = Field(..., description="Fields of the schema")
    attributes: dict[str, str] = Field(..., description="Attributes of the schema")
    raw_schema: Optional[dict | str] = Field(None, description="Raw schema")
    format_hint: Optional[str] = Field(None, description="Format hint")

    def build_token(self) -> str:
        """
        Build token in the canonical format:

            [OUT_<FORMAT> : <SCHEMA> : key=value : key=value]

        - SCHEMA always comes first.
        - Other attributes (ENUMS, SPECS, KEYS, etc.) follow.
        - Order of attributes is stable: SCHEMA → KEYS → ENUMS → SPECS → others.
        """
        fmt = (self.format_hint or self.format_type or "STRUCTURED").upper()
        schema = self.attributes.get("schema", "")
        parts = [f"OUT_{fmt}", f"{schema}"]
        ordered_keys = []

        if "KEYS" in self.attributes:
            ordered_keys.append("KEYS")
        if "ENUMS" in self.attributes:
            ordered_keys.append("ENUMS")
        if "SPECS" in self.attributes:
            ordered_keys.append("SPECS")

        for k in sorted(self.attributes.keys()):
            if k not in ["schema", "KEYS", "ENUMS", "SPECS"]:
                ordered_keys.append(k)

        for k in ordered_keys:
            parts.append(f"{k}={self.attributes[k]}")

        return "[" + ":".join(parts) + "]"


class CompressionResult(BaseModel):
    """Complete compression result"""

    original: str = Field(..., description="Original prompt")
    compressed: str = Field(..., description="Compressed prompt")
    intents: list[Intent] = Field(..., description="Intents extracted from the prompt")
    target: Target = Field(..., description="Target of the prompt")
    extractions: Optional[ExtractionField] = Field(
        ..., description="Extractions from the prompt"
    )
    contexts: list[Context] = Field(
        ..., description="Contexts extracted from the prompt"
    )
    output_format: Optional[OutputSchema] = Field(
        ..., description="Output format of the prompt"
    )
    compression_ratio: float = Field(..., description="Compression ratio of the prompt")
    metadata: dict = Field(..., description="Metadata of the prompt")


class DetectedField(BaseModel):
    name: str = Field(..., description="Name of the detected field")
    span: tuple[int, int] = Field(..., description="Span of the detected field")
    source: str = Field(..., description="Source of the detected field")
    confidence: float = Field(..., description="Confidence of the detected field")


class SysPromptConfig(BaseModel):
    lang: str = Field(default="en", description="Language of the prompt")
    infer_types: Optional[bool] = Field(
        default=False, description="Infer types for output fields"
    )
    add_examples: Optional[bool] = Field(
        default=False,
        description="Add examples based on extracted ones from input if exist",
    )
    add_attrs: Optional[bool] = Field(
        default=True, description="Add extra attributes from input prompt"
    )
