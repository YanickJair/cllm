import json
import re
from enum import Enum
from typing import Optional, Self, Literal, Annotated, TypeAlias, Union

import spacy
from pydantic import (
    BaseModel,
    Field,
    computed_field,
    ConfigDict,
    field_validator,
    field_serializer,
    model_validator,
)

from clm_core.utils.parser_rules import BaseRules
from clm_core.utils.vocabulary import BaseVocabulary
from clm_core.dictionary import rules_map, vocab_map

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
    def validate_compressed(cls, c: str) -> str:
        """Normalize whitespace: collapse all whitespace (tabs, newlines, spaces) to single spaces."""
        return re.sub(r"\s+", " ", c).strip()

    @staticmethod
    def _estimate_tokens(data: str | dict | list) -> int:
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
        default=True, description="Approach 2: Auto-detect rule"
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
    max_description_length: Optional[int] = Field(
        default=200, description="Truncate long text"
    )
    preserve_structure: Optional[bool] = Field(
        default=True, description="Keep nested dicts/lists"
    )
    simple_fields: list[str] = Field(
        default_factory=lambda: [
            "id",
            "uuid",
            "title",
            "name",
            "type",
            "priority",
            "article_id",
            "product_id",
        ],
        description="Fields to simplify",
    )
    default_fields_order: list[str] = Field(
        default_factory=lambda: [
            "id",
            "uuid",
            "priority",
            "article_id",
            "product_id",
            "title",
            "name",
            "type",
        ],
        description="Order for default fields. IDs take precedence over other fields. "
        "If a field is not in this list, it will be placed at the end.",
    )
    default_fields_importance: dict[str, FieldImportance] = Field(
        frozen=True,
        default_factory=lambda: {
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
        },
        description="Importance scores for default fields. Overrides default thresholds.",
    )

    @field_validator("default_fields_importance", mode="before")
    @classmethod
    def convert_float_to_field_importance(cls, v: dict) -> dict[str, FieldImportance]:
        if not isinstance(v, dict):
            return v
        result = {}
        for key, value in v.items():
            if isinstance(value, (int, float)):
                for member in FieldImportance:
                    if member.value == value:
                        result[key] = member
                        break
                else:
                    raise ValueError(f"No FieldImportance enum matches value {value}")
            else:
                result[key] = value
        return result

    @field_serializer("default_fields_importance")
    @classmethod
    def serialize_field_importance(
        cls, v: dict[str, FieldImportance]
    ) -> dict[str, float]:
        return {key: importance.value for key, importance in v.items()}

    model_config = ConfigDict(use_enum_values=False)


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

    @computed_field
    @property
    def vocab(self) -> BaseVocabulary:
        return vocab_map[self.lang]

    @computed_field
    @property
    def nlp_model(self) -> spacy.Language:
        """
        Load spaCy model for the configured language
        Returns
        -------

        """
        match self.lang:
            case "en":
                return spacy.load("en_core_web_sm")
            case _:
                raise NotImplementedError(
                    f"Model for language {self.lang} not supported yet"
                )

    @computed_field
    @property
    def rules(self) -> BaseRules:
        return rules_map[self.lang]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
