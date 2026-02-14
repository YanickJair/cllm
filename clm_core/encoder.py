from typing import Any, Optional

import spacy

from clm_core.components.ds_compression import SDEncoder, SDEncoderV2
from clm_core.components.sys_prompt.encoder import SysPromptEncoder
from clm_core.components.transcript.encoder import TranscriptEncoder
from clm_core.core.text_classifier import DataClassifier, DataTypes
from clm_core import CLMConfig
from clm_core.types import CLMOutput


class CLMEncoder:
    def __init__(self, *, cfg: CLMConfig):
        """
        Initialize encode
        """
        self._cfg = cfg
        self._ds_encoder = SDEncoderV2(config=self._cfg.ds_config)
        self._classifier = DataClassifier()
        self._lazy_nlp: Optional[spacy.Language] = None
        self._lazy_ts_encoder: Optional[TranscriptEncoder] = None
        self._lazy_sys_prompt_encoder: Optional[SysPromptEncoder] = None

    @property
    def _nlp(self) -> spacy.Language:
        if self._lazy_nlp is None:
            self._lazy_nlp = self._cfg.nlp_model
        print("NLP Model Loaded", self._cfg.nlp_model)
        return self._lazy_nlp

    @property
    def _ts_encoder(self) -> TranscriptEncoder:
        if self._lazy_ts_encoder is None:
            self._lazy_ts_encoder = TranscriptEncoder(
                nlp=self._nlp,
                vocab=self._cfg.vocab,
                rules=self._cfg.rules,
                patterns=self._cfg.patterns,
                lang=self._cfg.lang,
            )
        return self._lazy_ts_encoder

    @property
    def _sys_prompt_encoder(self) -> SysPromptEncoder:
        if self._lazy_sys_prompt_encoder is None:
            self._lazy_sys_prompt_encoder = SysPromptEncoder(
                nlp=self._nlp,
                config=self._cfg.sys_prompt_config,
                vocab=self._cfg.vocab,
                rules=self._cfg.rules,
            )
        return self._lazy_sys_prompt_encoder

    def encode(
        self, input_: Any, verbose: bool = False, metadata: Optional[dict] = None
    ) -> CLMOutput:
        class_ = self._classifier.classifier(input_=input_)

        if verbose:
            print(f"Data Type Classified as - {class_}")

        if class_ == DataTypes.UNK:
            print("Unknown Data Type. Can't compress")
            return None

        if class_ == DataTypes.STRUCTURED_DATA:
            return self._ds_encoder.encode(input_)

        if class_ == DataTypes.TRANSCRIPT:
            return self._ts_encoder.encode(
                transcript=input_, verbose=verbose, metadata=metadata
            )
        return self._sys_prompt_encoder.compress(input_, verbose)

    def bind(self, out: CLMOutput, **kwargs):
        """Called during runtime to bind values for configuration prompt placeholders"""
        return self._sys_prompt_encoder.bind(out=out, **kwargs)
