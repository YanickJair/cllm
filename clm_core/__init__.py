from clm_core.__version__ import __description__, __title__, __version__
from clm_core.components.sys_prompt import OutputMode, PromptMode, PromptTemplate
from clm_core.components.sys_prompt.encoder import SysPromptEncoder
from clm_core.components.thread_encoder import (
    TranscriptAnalysis,
    TranscriptCompressionResult,
)
from clm_core.components.thread_encoder.turn_classifier.classifier import TurnClassifier
from clm_core.encoder import CLMEncoder
from clm_core.quality_gate import (
    CompressionQualityGate,
    CompressionQualityReport,
    ConditionalEntropyResult,
    KolmogorovAnalyzer,
    KolmogorovModel,
    PerplexityAnalyzer,
    PerplexityResult,
)
from clm_core.text_classifier import DataTypes
from clm_core.types import (
    CLMConfig,
    CLMOutput,
    FieldImportance,
    SDCompressionConfig,
    SysPromptConfig,
    ThreadConfig,
    TurnType,
)

from .components.thread_encoder import ThreadEncoder

__all__ = [
    "__version__",
    "__title__",
    "__description__",
    "CLMEncoder",
    "CLMConfig",
    "CLMOutput",
    "SysPromptConfig",
    "ThreadConfig",
    "DataTypes",
    "SDCompressionConfig",
    "FieldImportance",
    "PromptMode",
    "OutputMode",
    "PromptTemplate",
    "TranscriptCompressionResult",
    "TranscriptAnalysis",
    "ThreadEncoder",
    "SysPromptEncoder",
    "KolmogorovModel",
    "PerplexityResult",
    "ConditionalEntropyResult",
    "CompressionQualityReport",
    "KolmogorovAnalyzer",
    "PerplexityAnalyzer",
    "CompressionQualityGate",
    "TurnClassifier",
    "TurnType",
]

__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "clm_core")
