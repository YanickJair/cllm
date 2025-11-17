from typing import Any

import spacy

from src.components.ds_compression import DSEncoder, CompressionConfig
from src.components.sys_prompt.encoder import SysPromptEncoder
from src.components.transcript.encoder import TranscriptEncoder
from .text_classifier import DataClassifier, DataTypes


class CLLMEncoder:
    """Main CLLM encode - orchestrates compression pipeline"""

    def __init__(self, model: str = "en_core_web_sm"):
        """
        Initialize encode

        Args:
            model: spaCy model to use (en_core_web_sm, en_core_web_md, en_core_web_lg)
        """
        print(f"Loading spaCy model: {model}...")

        self._nlp: spacy.Language = spacy.load(model)
        self._ds_config = CompressionConfig(
            required_fields=["id", "title", "description", "category"], auto_detect=False
        )
        self._ds_encoder = DSEncoder(
            config=self._ds_config
        )
        self._ts_encoder = TranscriptEncoder(self._nlp)
        self._sys_prompt_encoder = SysPromptEncoder(self._nlp)

        self._classifier = DataClassifier()

    @property
    def ds_config(self) -> CompressionConfig:
        return self._ds_config

    @ds_config.setter
    def ds_config(self, cfg: CompressionConfig) -> None:
        self._ds_config = cfg

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
