from typing import Annotated
from pydantic import BaseModel, Field

from cllm.src.components.ds_compression._schemas import CompressionConfig
from cllm.src.components.sys_prompt._schemas import SysPromptConfig


class CommpressionRequest(BaseModel):
    text: str = Field(..., description="The text to compress")
    language: str = Field(default="en", description="The language of the text")
    compression_level: int = Field(default=9, description="The compression level")


class CLMConfiguration(BaseModel):
    ds_cfg: Annotated[
        CompressionConfig, Field(description="The configuration for the encoder")
    ]
    sys_prompt_cfg: Annotated[
        SysPromptConfig, Field(description="The configuration for the system prompt")
    ]
    lang: str = Field(default="en", description="The language of the text")
