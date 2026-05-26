from typing import Annotated, Any, Optional

import spacy
from annotated_doc import Doc

from clm_core.components.sys_prompt.encoder import SysPromptEncoder
from clm_core.components.thread_encoder.encoder import ThreadEncoder
from clm_core.text_classifier import DataClassifier, DataTypes
from clm_core.types import CLMConfig, CLMOutput

try:
    from sd_encoder import SDCompressionConfig as _SDCompressionConfig
    from sd_encoder import FieldImportance as _SDFieldImportance
except ImportError:  # pragma: no cover - exercised when the extra is missing.
    _SDCompressionConfig = None
    _SDFieldImportance = None


class _SDEncoderV2:
    def __init__(self, *_args, **_kwargs):
        self._missing_message = (
            "Structured data encoding requires the 'sd_encoder' extra. "
            "Install with: pip install \"clm-core[sd_encoder]\""
        )

    def encode(self, *_args, **_kwargs):
        raise ImportError(self._missing_message)

    def encode_validated(self, *_args, **_kwargs):
        raise ImportError(self._missing_message)


class _StructuredDataEncoderAdapter:
    """Thin Python wrapper around the optional structured-data encoder.

    The native `sd_encoder` implementation exposes methods that are awkward to
    monkeypatch in tests. Wrapping it keeps runtime behavior unchanged while
    preserving a patchable Python attribute surface.
    """

    def __init__(self, config):
        self._inner = self._build_inner(config)

    @staticmethod
    def _build_inner(config):
        try:
            from sd_encoder import SDEncoderV2 as NativeSDEncoderV2
            from sd_encoder import SDCompressionConfig as NativeSDCompressionConfig
        except ImportError:
            return _SDEncoderV2(config=config)

        if isinstance(config, NativeSDCompressionConfig):
            native_config = config
        else:
            native_config = NativeSDCompressionConfig(**config)
        return NativeSDEncoderV2(native_config)

    def encode(self, *args, **kwargs):
        return self._inner.encode(*args, **kwargs)

    def encode_validated(self, *args, **kwargs):
        return self._inner.encode_validated(*args, **kwargs)


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
        self._classifier = DataClassifier()
        self._ds_encoder = _StructuredDataEncoderAdapter(self._build_sd_config())
        self._lazy_nlp: Optional[spacy.Language] = None
        self._lazy_ts_encoder: Optional[ThreadEncoder] = None
        self._lazy_sys_prompt_encoder: Optional[SysPromptEncoder] = None

    def _build_sd_config(self):
        """
        Convert the internal Pydantic SD config into the native sd_encoder config.

        The optional dependency uses its own config class, so we must pass a native
        instance rather than the CLM-side Pydantic model.
        """
        if _SDCompressionConfig is None:
            return self._cfg.ds_config

        ds_config = self._cfg.ds_config.model_dump(
            mode="json",
            exclude={
                "default_fields_importance",
                "simple_fields",
                "default_fields_order",
            },
        )
        ds_config["importance_threshold"] = self._to_native_importance(
            ds_config.get("importance_threshold")
        )
        if ds_config.get("field_importance"):
            ds_config["field_importance"] = {
                k: self._to_native_importance(v)
                for k, v in ds_config["field_importance"].items()
            }
        return _SDCompressionConfig(**ds_config)

    @staticmethod
    def _to_native_importance(value):
        if _SDFieldImportance is None or value is None:
            return value

        if isinstance(value, _SDFieldImportance):
            return value

        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return value

        if numeric <= 0.2:
            return _SDFieldImportance.LOW
        if numeric <= 0.5:
            return _SDFieldImportance.MEDIUM
        if numeric <= 0.8:
            return _SDFieldImportance.HIGH
        return _SDFieldImportance.CRITICAL

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
    ) -> CLMOutput | None:
        if data_type is None:
            data_type = self._classifier.classifier(input_=input_)

        if verbose:
            print(f"Data Type Classified as - {data_type}")

        if data_type == DataTypes.UNK:
            print("Unknown Data Type. Can't compress")
            return None

        if data_type == DataTypes.STRUCTURED_DATA:
            result = self._ds_encoder.encode(input_)
            if isinstance(result, CLMOutput):
                return result
            if hasattr(result, "model_dump"):
                return CLMOutput.model_validate(result.model_dump())
            return CLMOutput(
                original=getattr(result, "original"),
                component=getattr(result, "component"),
                compressed=getattr(result, "compressed"),
                metadata=dict(getattr(result, "metadata") or {}),
            )

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
