from abc import ABC, abstractmethod
from typing import Annotated

from annotated_doc import Doc

from clm_core.types import CLMOutput


class BasePromptEncoder(ABC):
    @abstractmethod
    def compress(
        self,
        prompt: Annotated[str, Doc("Natural language prompt to compress.")],
        verbose: Annotated[
            bool, Doc("When True, print detailed compression steps.")
        ] = False,
    ) -> CLMOutput:
        raise NotImplementedError

    @abstractmethod
    def compress_batch(
        self,
        prompts: Annotated[
            list[str], Doc("List of natural language prompts to compress.")
        ],
        verbose: Annotated[
            bool, Doc("When True, print detailed compression steps for each prompt.")
        ] = False,
    ) -> list[CLMOutput]:
        raise NotImplementedError
