from typing import Annotated, Literal
from pydantic import BaseModel, Field, computed_field, ConfigDict

from clm_core.utils.parser_rules import BaseRules
from clm_core.utils.vocabulary import BaseVocabulary
from clm_core.types import SDCompressionConfig
from clm_core.components.sys_prompt import SysPromptConfig
from clm_core.dictionary import rules_map, vocab_map

type LANG = Literal["en", "fr", "es", "pt"]


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
    def rules(self) -> BaseRules:
        return rules_map[self.lang]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

