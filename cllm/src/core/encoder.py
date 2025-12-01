from typing import Any

import spacy

from ..components.ds_compression import DSEncoder
from ..components.sys_prompt.encoder import SysPromptEncoder
from ..components.transcript.encoder import TranscriptEncoder
from .text_classifier import DataClassifier, DataTypes
from ..utils.schemas import CLMConfig


class CLLMEncoder:
    """Main CLLM encode - orchestrates compression pipeline"""

    def __init__(self, *, cfg: CLMConfig):
        """
        Initialize encode

        Args:
            model: spaCy model to use (en_core_web_sm, en_core_web_md, en_core_web_lg)
        """
        print(f"Loading spaCy model here: {cfg.lang}...")

        self._cfg = cfg
        self._nlp: spacy.Language = spacy.load("en_core_web_sm")
        self._ds_encoder = DSEncoder(config=self._cfg.ds_config)
        self._ts_encoder = TranscriptEncoder(self._nlp)
        self._sys_prompt_encoder = SysPromptEncoder(
            nlp=self._nlp,
            config=self._cfg.sys_prompt_config,
            vocab=self._cfg.vocab,
            rules=self._cfg.rules,
        )
        self._classifier = DataClassifier()

    def encode(self, input_: Any, verbose: bool = False) -> Any:
        class_ = self._classifier.classifier(input_=input_)

        if verbose:
            print(f"Data Type Classified as - {class_}")

        if class_ == DataTypes.UNK:
            print("Unknown Data Type. Can't compress")
            return None

        if class_ == DataTypes.STRUCTURED_DATA:
            return self._ds_encoder.encode(input_)

        if class_ == DataTypes.TRANSCRIPT:
            pass
        return self._sys_prompt_encoder.compress(input_, verbose)
