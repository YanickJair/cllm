from spacy.language import Language

from clm_core.utils.parser_rules import BaseRules
from clm_core.utils.vocabulary import BaseVocabulary
from ._configuration_prompt_encoder import ConfigurationPromptEncoder
from clm_core import SysPromptConfig

from ._schemas import PromptMode
from ._task_prompt_encoder import TaskPromptEncoder
from clm_core.types import CLMOutput

COMPONENT = "SYSTEM_PROMPT"


class SysPromptEncoder:
    def __init__(
        self,
        *,
        nlp: Language,
        config: SysPromptConfig = SysPromptConfig(),
        vocab: BaseVocabulary,
        rules: BaseRules,
    ):
        """
        Initialize encode
        """
        self._task_prompt = TaskPromptEncoder(
            nlp=nlp, config=config, rules=rules, vocab=vocab
        )
        self._configuration_prompt = ConfigurationPromptEncoder(
            nlp=nlp, vocab=vocab, rules=rules, config=config
        )

    def bind(self, out: CLMOutput, **kwargs: dict) -> str:
        return self._configuration_prompt.bind(out=out, **kwargs)

    @staticmethod
    def _detect_prompt_mode(text: str) -> PromptMode:
        """Detect which prompt we are dealing with.
        This is intentionally conservative to avoid hallucination
        """
        tl = text[:150].lower()

        if any(
            phrase in tl
            for phrase in (
                "you are an ai",
                "your role",
                "follow the rules",
                "capabilities:",
                "safety boundaries",
                "custom instructions",
                "<basic_rules>",
                "<custom_rules>",
            )
        ):
            return PromptMode.CONFIGURATION
        return PromptMode.TASK

    def compress(self, prompt: str, verbose: bool = False) -> CLMOutput:
        """
        Compress a natural language prompt into CLLM format

        Args:
            prompt: Natural language prompt to compress
            verbose: Print detailed compression steps

        Returns:
            CompressionResult with compressed format and metadata
        """
        mode = self._detect_prompt_mode(prompt)
        if mode == PromptMode.TASK:
            self._task_prompt.compress(prompt=prompt, verbose=verbose)
        return self._configuration_prompt.compress(prompt=prompt)

    def compress_batch(
        self, prompts: list[str], verbose: bool = False
    ) -> list[CLMOutput]:
        """Compress multiple prompts"""
        return [self.compress(prompt=prompt, verbose=verbose) for prompt in prompts]
