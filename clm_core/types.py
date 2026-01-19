from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, computed_field

from clm_core.components.sys_prompt import (
    PromptTemplate, BoundPromptValidator, ValidationLevel, ConfigurationPromptMinimizer, PromptMode
)


type ORIGINAL_INPUT = str | dict | list


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

    @computed_field
    @property
    def compression_ratio(self) -> float:
        """Compression ratio of the input"""
        return round((1 - len(self.compressed) / len(self.original)) * 100, 1)

    def bind(self, **runtime_values) -> str:
        """
        compose CL + NL
        Parameters
        ----------
        runtime_values

        Returns
        -------

        """
        if self.metadata.get("prompt_mode") != "CONFIGURATION":
            return self.compressed

        template = PromptTemplate(
            raw_template=self.original,
            placeholders=self.metadata["placeholders"],
            role=self.metadata.get("role"),
            rules=self.metadata.get("rules", {}),
            priority=self.metadata.get("priority"),
            compressed=self.compressed,
        )

        bound_nl = template.bind(**runtime_values)

        issues = BoundPromptValidator().validate(bound_nl)
        errors = [i for i in issues if i.level == ValidationLevel.ERROR]
        if errors:
            raise RuntimeError(f"Bound prompt invalid: {errors}")

        if self.metadata["prompt_mode"] == PromptMode.CONFIGURATION:
            bound_nl = ConfigurationPromptMinimizer.minimize(bound_nl, cl_metadata=self.metadata)
        return f"{self.compressed}\n\n{bound_nl}"


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
            "title",
            "name",
            "type",
            "article_id",
            "product_id",
        ],
        description="Fields to simplify",
    )
    default_fields_order: list[str] = Field(
        default_factory=lambda: [
            "id",
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
        default_factory=lambda: {
            "id": FieldImportance.CRITICAL,
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
