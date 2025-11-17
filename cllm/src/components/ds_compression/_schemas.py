from enum import Enum
from typing import Annotated, Optional
from pydantic import BaseModel, Field


class FieldImportance(Enum):
    CRITICAL = 1.0  # Always include (id, name)
    HIGH = 0.8  # Usually include (description, category)
    MEDIUM = 0.5  # Sometimes include (tags, metadata)
    LOW = 0.2  # Rarely include (timestamps, internal codes)
    NEVER = 0.0  # Never include (passwords, secrets)


class CompressionConfig(BaseModel):
    """
    Configuration for how to compress a catalog

    This is the "domain config" that makes compression universal
    """

    required_fields: Annotated[
        list[str] | None, Field(default=None, description="Always include these")
    ]

    auto_detect: Annotated[
        Optional[bool], Field(default=True, description="Approach 2: Auto-detect rule")
    ]
    importance_threshold: Annotated[
        Optional[float],
        Field(default=0.5, description="Include fields above this threshold"),
    ]

    # Hybrid: Overrides
    field_importance: Annotated[
        Optional[dict[str, float]],
        Field(default=None, description="Custom importance scores"),
    ]
    excluded_fields: Annotated[
        Optional[list[str]], Field(default=None, description="Never include these")
    ]

    max_description_length: Annotated[
        Optional[int], Field(default=200, description="Truncate long text")
    ]
    preserve_structure: Annotated[
        Optional[bool], Field(default=True, description="Keep nested dicts/lists")
    ]
