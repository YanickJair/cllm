from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


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


class CompressionConfig(BaseModel):
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
        description="Order for default fields. IDs take precedence over other fields. If a field is not in this list, it will be placed at the end.",
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
