from typing import Annotated, Literal
from pydantic import BaseModel, Field, computed_field, ConfigDict

from cllm.utils.parser_rules import BaseRules
from cllm.utils.vocabulary import BaseVocabulary
from cllm.components.ds_compression import CompressionConfig
from cllm.components.sys_prompt import SysPromptConfig
from cllm.dictionary import rules_map, vocab_map

type LANG = Literal["en", "fr", "de", "es", "it", "pt", "ru", "ja", "zh", "ko"]
type ORIGINAL_INPUT = str | dict | list


class CLMConfig(BaseModel):
    lang: Annotated[LANG, Field(default="en", description="Language of the model")]
    ds_config: CompressionConfig = Field(
        default_factory=lambda: CompressionConfig(),
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
    def rules(self) -> BaseRules:
        return rules_map[self.lang]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class CLMOutput(BaseModel):
    original: ORIGINAL_INPUT = Field(
        ..., description="A generic original input. It can be a str, list, or dict"
    )
    component: str = Field(..., description="Component's name (i.e. Transcript, SD, System Prompt)")
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
