from typing import Annotated, Literal
from pydantic import BaseModel, Field, computed_field, ConfigDict

from src.utils.parser_rules import BaseRules
from src.utils.vocabulary import BaseVocabulary
from ..components.ds_compression import CompressionConfig
from ..components.sys_prompt import SysPromptConfig
from src.dictionary import rules_map, vocab_map

type LANG = Literal["en", "fr", "de", "es", "it", "pt", "ru", "ja", "zh", "ko"]


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
