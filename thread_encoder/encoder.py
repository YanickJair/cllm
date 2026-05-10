from typing import Any, Optional, Annotated

import spacy

from annotated_doc import Doc
from thread_encoder.components.ds_compression import SDEncoderV2
from thread_encoder.components.sys_prompt.encoder import SysPromptEncoder
from thread_encoder.components.thread_encoder.encoder import ThreadEncoder
from thread_encoder.text_classifier import DataClassifier, DataTypes
from thread_encoder import CLMConfig
from thread_encoder.types import CLMOutput


class CLMEncoder:
    def __init__(
        self,
        *,
        cfg: Annotated[
            CLMConfig,
            Doc(
                "The CLM configuration object that controls language, compression settings, and component options."
            ),
        ],
    ):
        """Initialize the encoder with the given configuration."""
        self._cfg = cfg
        self._ds_encoder = SDEncoderV2(config=self._cfg.ds_config)
        self._classifier = DataClassifier()
        self._lazy_nlp: Optional[spacy.Language] = None
        self._lazy_ts_encoder: Optional[ThreadEncoder] = None
        self._lazy_sys_prompt_encoder: Optional[SysPromptEncoder] = None

    @property
    def _nlp(self) -> spacy.Language:
        if self._lazy_nlp is None:
            self._lazy_nlp = self._cfg.nlp_model
        print("NLP Model Loaded", self._cfg.nlp_model)
        return self._lazy_nlp

    @property
    def _ts_encoder(self) -> ThreadEncoder:
        if self._lazy_ts_encoder is None:
            self._lazy_ts_encoder = ThreadEncoder(
                nlp=self._nlp,
                vocab=self._cfg.vocab,
                rules=self._cfg.rules,
                patterns=self._cfg.patterns,
                lang=self._cfg.lang,
                config=self._cfg.thread_config,
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
        self,
        input_: Annotated[
            Any,
            Doc(
                "The input data to encode. May be a string (transcript or system prompt), dict, or list of dicts (structured data)."
            ),
        ],
        verbose: Annotated[
            bool,
            Doc("When True, prints classification and compression details to stdout."),
        ] = False,
        data_type: Annotated[
            Optional[DataTypes],
            Doc("The data type of the input. If None, the type will be inferred."),
        ] = None,
        metadata: Annotated[
            Optional[dict],
            Doc(
                "Optional metadata dict to attach to the output (passed through to the thread encoder)."
            ),
        ] = None,
    ) -> CLMOutput:
        if data_type is None:
            data_type = self._classifier.classifier(input_=input_)

        if verbose:
            print(f"Data Type Classified as - {data_type}")

        if data_type == DataTypes.UNK:
            print("Unknown Data Type. Can't compress")
            return None

        if data_type == DataTypes.STRUCTURED_DATA:
            return self._ds_encoder.encode(input_)

        if data_type == DataTypes.TRANSCRIPT or data_type == DataTypes.FREE_FORM:
            return self._ts_encoder.encode(
                thread=input_, verbose=verbose, metadata=metadata
            )
        return self._sys_prompt_encoder.compress(input_, verbose)

    def bind(
        self,
        out: Annotated[
            CLMOutput,
            Doc(
                "The CLMOutput produced by a prior encode() call for a CONFIGURATION-mode system prompt."
            ),
        ],
        **kwargs,
    ):
        """Called during runtime to bind values for configuration prompt placeholders."""
        return self._sys_prompt_encoder.bind(out=out, **kwargs)
