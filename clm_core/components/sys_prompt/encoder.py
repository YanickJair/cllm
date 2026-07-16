from typing import Annotated

from annotated_doc import Doc
from spacy.language import Language

from clm_core.types import CLMOutput, SysPromptConfig
from clm_core.utils.parser_rules import BaseRules
from clm_core.utils.vocabulary import BaseVocabulary

from ._configuration_prompt_encoder import ConfigurationPromptEncoder
from ._schemas import PromptMode
from ._task_prompt_encoder import TaskPromptEncoder

COMPONENT = "SYSTEM_PROMPT"


class SysPromptEncoder:
    def __init__(
        self,
        *,
        nlp: Annotated[Language, Doc("spaCy language model used for NLP processing.")],
        config: Annotated[
            SysPromptConfig, Doc("Configuration for the system prompt encoder.")
        ] = SysPromptConfig(),
        vocab: Annotated[
            BaseVocabulary, Doc("Vocabulary instance for the target language.")
        ],
        rules: Annotated[BaseRules, Doc("Language-specific parsing rules.")],
    ):
        """Initialize the encoder."""
        self._task_prompt = TaskPromptEncoder(
            nlp=nlp, config=config, rules=rules, vocab=vocab
        )
        self._config = config
        self._configuration_prompt = ConfigurationPromptEncoder(
            nlp=nlp, vocab=vocab, rules=rules, config=config
        )

    def bind(
        self,
        out: Annotated[
            CLMOutput, Doc("The CLMOutput object produced by a prior compress() call.")
        ],
        **kwargs: dict,
    ) -> str:
        return self._configuration_prompt.bind(out=out, **kwargs)

    @staticmethod
    def _detect_prompt_mode(
        text: Annotated[
            str, Doc("The raw prompt text to classify as TASK or CONFIGURATION.")
        ],
    ) -> PromptMode:
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

    def compress(
        self,
        prompt: Annotated[str, Doc("Natural language prompt to compress.")],
        verbose: Annotated[
            bool, Doc("When True, print detailed compression steps.")
        ] = False,
    ) -> CLMOutput:
        """Compress a natural language prompt into CLLM format."""
        mode = (
            self._config.prompt_mode
            if self._config.prompt_mode
            else self._detect_prompt_mode(prompt)
        )
        if mode == PromptMode.TASK:
            return self._task_prompt.compress(prompt=prompt, verbose=verbose)
        return self._configuration_prompt.compress(prompt=prompt)

    def compress_batch(
        self,
        prompts: Annotated[
            list[str], Doc("List of natural language prompts to compress.")
        ],
        verbose: Annotated[
            bool, Doc("When True, print detailed compression steps for each prompt.")
        ] = False,
    ) -> list[CLMOutput]:
        """Compress multiple prompts."""
        return [self.compress(prompt=prompt, verbose=verbose) for prompt in prompts]
