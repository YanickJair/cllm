import json
import re
from enum import Enum
from typing import Optional, Self, Literal, Annotated, TypeAlias, Union

import spacy
from annotated_doc import Doc
from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    computed_field,
    ConfigDict,
    field_validator,
    model_validator,
)

from clm_core.utils.parser_rules import BaseRules
from clm_core.utils.vocabulary import BaseVocabulary
from clm_core.dictionary import rules_map, vocab_map, patterns_map

ORIGINAL_INPUT: TypeAlias = Union[str, dict, list]
LANG: TypeAlias = Literal["en", "fr", "es", "pt"]


class CLMOutput(BaseModel):
    original: ORIGINAL_INPUT = Field(
        ..., description="A generic original input. It can be a str, list, or dict"
    )
    component: str = Field(
        ..., description="Component's name (i.e. Transcript, SD, System Prompt)"
    )
    compressed: str = Field(..., description="Compressed output.")
    metadata: dict = Field(
        ...,
        description="Metadata of the compressing input. It can include specific things from each component",
    )

    @model_validator(mode="after")
    def validate_compression_ratio(self) -> Self:
        """If compression ratio is negative (expanded), use original instead."""
        if self.c_tokens > self.n_tokens:
            original = self.original
            if isinstance(original, str):
                self.compressed = original
            else:
                self.compressed = json.dumps(original, ensure_ascii=False)
            self.metadata["description"] = (
                "CL Tokens greater than NL token. Keeping NL input"
            )
        return self

    @field_validator("compressed", mode="before")
    @classmethod
    def validate_compressed(
        cls,
        c: Annotated[
            str, Doc("Raw compressed string value to normalize before assignment.")
        ],
    ) -> str:
        """Normalize whitespace: collapse all whitespace (tabs, newlines, spaces) to single spaces."""
        return re.sub(r"\s+", " ", c).strip()

    @staticmethod
    def _estimate_tokens(
        data: Annotated[
            str | dict | list,
            Doc(
                "Input data (string, dict, or list) whose token count is to be estimated at ~4 chars per token."
            ),
        ],
    ) -> int:
        """Estimate token count (~4 chars per token)."""
        if isinstance(data, str):
            text = data
        else:
            text = json.dumps(data, ensure_ascii=False)
        return max(1, len(text) // 4)

    @computed_field
    @property
    def n_tokens(self) -> int:
        """Estimated input token count."""
        return self._estimate_tokens(self.original)

    @computed_field
    @property
    def c_tokens(self) -> int:
        """Estimated compressed token count."""
        return self._estimate_tokens(self.compressed)

    @computed_field
    @property
    def compression_ratio(self) -> float:
        """Compression ratio based on token reduction."""
        if self.n_tokens == 0:
            return 0.0
        return round((1 - self.c_tokens / self.n_tokens) * 100, 1)

    def to_dict(self) -> dict:
        raise NotImplementedError


class FieldImportance(Enum):
    """Field importance levels

    CRITICAL: Always include (id, name)
    HIGH: Usually include (description, category)
    MEDIUM: Sometimes include (tags, metadata)
    LOW: Rarely include (timestamps, internal codes)
    NEVER: Never include (passwords, secrets)
    """

    CRITICAL = 1.0
    HIGH = 0.8
    MEDIUM = 0.5
    LOW = 0.2
    NEVER = 0.0


class SDCompressionConfig(BaseModel):
    required_fields: Optional[list[str]] = Field(
        default=None, description="Always include these"
    )
    auto_detect: Optional[bool] = Field(
        default=True,
        description="Auto-detect field importance based on name patterns and value heuristics",
    )
    drop_non_required_fields: Optional[bool] = Field(
        default=True, description="Whether or not to drop no required fields"
    )
    importance_threshold: Optional[float] = Field(
        default=0.5, description="Include fields above this threshold"
    )
    field_importance: Optional[dict[str, float]] = Field(
        default=None,
        description="Custom importance scores. Overrides default thresholds.",
    )
    excluded_fields: Optional[list[str]] = Field(
        default=None, description="Never include these"
    )
    max_truncation_length: Optional[int] = Field(
        default=200,
        description="Truncate long text. If max config truncation mapping not defined, will use this for all",
    )
    max_truncation_mapping: Optional[dict[str, int]] = Field(
        default=None,
        description="Per-field truncation lengths. Overrides max_truncation_length for each specified field.",
    )
    preserve_structure: Optional[bool] = Field(
        default=True, description="Keep nested dicts/lists"
    )

    @computed_field
    @property
    def default_fields_importance(self) -> dict[str, FieldImportance]:
        return {
            "id": FieldImportance.CRITICAL,
            "uuid": FieldImportance.CRITICAL,
            "external_id": FieldImportance.CRITICAL,
            "name": FieldImportance.HIGH,
            "title": FieldImportance.HIGH,
            "type": FieldImportance.HIGH,
            "category": FieldImportance.HIGH,
            "subcategory": FieldImportance.MEDIUM,
            "tags": FieldImportance.HIGH,
            "description": FieldImportance.HIGH,
            "details": FieldImportance.MEDIUM,
            "notes": FieldImportance.LOW,
            "status": FieldImportance.CRITICAL,
            "priority": FieldImportance.HIGH,
            "severity": FieldImportance.HIGH,
            "resolution": FieldImportance.HIGH,
            "owner": FieldImportance.HIGH,
            "assignee": FieldImportance.MEDIUM,
            "department": FieldImportance.MEDIUM,
            "channel": FieldImportance.HIGH,
            "language": FieldImportance.MEDIUM,
            "source": FieldImportance.LOW,
            "metadata": FieldImportance.LOW,
            "created_at": FieldImportance.LOW,
            "updated_at": FieldImportance.LOW,
            "version": FieldImportance.LOW,
        }

    @computed_field
    @property
    def simple_fields(self) -> tuple[str, ...]:
        """Default fields that are mapped if no field is configured"""
        return (
            "id",
            "uuid",
            "title",
            "name",
            "type",
            "priority",
            "email",
            "article_id",
            "product_id",
        )

    @computed_field
    @property
    def default_fields_order(self) -> tuple[str, ...]:
        """
        Order for default fields. IDs take precedence over other fields. "
        "If a field is not in this list, it will be placed at the end.
        """
        return (
            "id",
            "uuid",
            "priority",
            "article_id",
            "product_id",
            "title",
            "name",
            "type",
        )


class SysPromptConfig(BaseModel):
    lang: str = Field(default="en", description="Language of the prompt")
    infer_types: Optional[bool] = Field(
        default=False, description="Infer types for output fields"
    )
    use_structured_output_abstraction: Optional[bool] = Field(
        default=True,
        description="If to compress output structure define with CL or keep it as-is",
    )
    add_examples: Optional[bool] = Field(
        default=False,
        description="Add examples based on extracted ones from input if exist",
    )
    add_attrs: Optional[bool] = Field(
        default=True,
        description="Add extra attributes from input prompt. "
        "This can be specifications found in prompt, enums/constraints values defined",
    )


class ThreadConfig(BaseModel):
    detect_lang: Annotated[
        bool,
        Doc("""
        This flag tells CLM if Thread language should be detected or not. If so, it will include it in the
        compressed output.
        """),
    ] = Field(default=True, description="Detects CLM language")
    include_ctx_values: Annotated[
        Optional[bool],
        Doc("""
        Contexts can be NER extract from original. By default CLM only flags
        the entities recognized but does not returns them.
        By enabling this flag, this information will also be included in the
        compressed output.
        
        **Examples**
        [CONTEXT:EMAIL_PROVIDED:doe@mail.com]
        """),
    ] = Field(default=False)
    estimate_thread_duration: Annotated[
        bool,
        Doc("""
        Duration can be included in the metadata or CLM can estimate.
        If this flag is set to True, it will override the duration of metadata.
        """),
    ] = Field(default=False)
    include_summary: Annotated[
        bool,
        Doc("""
        CLM can create a summary of the original Thread based on the compressed version.
        
        This feature can remove the dependency of LLMs for basic tasks such as this.
        A template can also be configured and CLM will update the placeholders with the extracted
        information.
        """),
    ] = Field(default=False)
    summary_template: Annotated[
        str | None,
        Doc("""
        Custom summary template for CLM.
        """),
    ] = Field(default=None)
    redaction_pattern: str = Field(
        default=r"\[\*+REDACTED\*+\]|\*{3,}|\[REDACTED\]|<redacted>|XXX+|\[PII\]",
        description="Regex pattern to detect redacted fields in thread input",
    )

    @computed_field
    def default_summary_template(self) -> str:
        return """
        Customer contacted {{ DOMAIN | lower }} support via {{ CHANNEL | lower }} regarding {{ CUSTOMER_INTENT | lower }} affecting their {{ SERVICE | lower }}.

        {% if AGENT_ACTIONS %}
        Actions performed:
        {% for action in AGENT_ACTIONS %}
        • {{ action }}
        {% endfor %}
        {% endif %}
        
        {% if SYSTEM_ACTIONS %}
        System detections:
        {% for action in SYSTEM_ACTIONS %}
        • {{ action }}
        {% endfor %}
        {% endfor %}
        {% endif %}
        
        Outcome: {{ RESOLUTION | replace("_", " ") | lower }} ({{ STATE | replace("_", " ") | lower }})
        {% if COMMITMENT %}
        Commitment: {{ COMMITMENT | replace("_", " ") | lower }}
        {% endif %}
        {% if ARTIFACT %}
        Reference: {{ ARTIFACT }}
        {% endif %}
        
        {% if SENTIMENT_START and SENTIMENT_END %}
        Sentiment: {{ SENTIMENT_START | lower }} → {{ SENTIMENT_END | lower }}
        {% endif %}
        """


class CLMConfig(BaseModel):
    lang: Annotated[LANG, Field(default="en", description="Language of the model")]
    ds_config: SDCompressionConfig = Field(
        default_factory=lambda: SDCompressionConfig(),
        description="Configuration for data Structure Data compression",
    )
    sys_prompt_config: SysPromptConfig = Field(
        default_factory=lambda: SysPromptConfig(),
        description="Configuration for system prompt",
    )

    _nlp_cache: Optional[spacy.Language] = PrivateAttr(default=None)

    @computed_field
    @property
    def vocab(self) -> BaseVocabulary:
        return vocab_map[self.lang]

    @computed_field
    @property
    def nlp_model(self) -> spacy.Language:
        """
        Load spaCy model for the configured language.
        Cached at instance level to avoid repeated loading.
        """
        if self._nlp_cache is not None:
            return self._nlp_cache
        model_map = {
            "en": "en_core_web_sm",
            "es": "es_core_news_sm",
            "pt": "pt_core_news_sm",
            "fr": "fr_core_news_sm",
        }
        model_name = model_map.get(self.lang)
        if model_name is None:
            raise NotImplementedError(
                f"Model for language {self.lang} not supported yet"
            )
        self._nlp_cache = spacy.load(model_name)
        return self._nlp_cache

    @computed_field
    @property
    def rules(self) -> BaseRules:
        return rules_map[self.lang]

    @computed_field(return_type=object)
    @property
    def patterns(self):
        return patterns_map[self.lang]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
