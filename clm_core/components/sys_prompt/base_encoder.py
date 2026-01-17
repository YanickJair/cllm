from abc import ABC, abstractmethod

from clm_core import CLMOutput


class BasePromptEncoder(ABC):
    @abstractmethod
    def compress(self, prompt: str, verbose: bool = False) -> CLMOutput:
        raise NotImplementedError

    @abstractmethod
    def compress_batch(self, prompts: list[str], verbose: bool = False) -> list[CLMOutput]:
        raise NotImplementedError
