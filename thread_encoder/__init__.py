from thread_encoder.types import (
    CLMOutput,
    SDCompressionConfig,
    SysPromptConfig,
    CLMConfig,
    FieldImportance,
    ThreadConfig
)
from thread_encoder.text_classifier import DataTypes
from thread_encoder.components.sys_prompt import PromptMode, PromptTemplate
from thread_encoder.components.ds_compression import SDEncoderV2, SDEncoder
from thread_encoder.components.sys_prompt.encoder import SysPromptEncoder
from thread_encoder.components.thread_encoder.encoder import ThreadEncoder
from thread_encoder.components.thread_encoder import (
    TranscriptCompressionResult,
    TranscriptAnalysis,
)
from thread_encoder.encoder import CLMEncoder
from thread_encoder.quality_gate import (
    KolmogorovModel,
    PerplexityResult,
    ConditionalEntropyResult,
    KolmogorovAnalyzer,
    PerplexityAnalyzer,
    CompressionQualityReport,
    CompressionQualityGate,
)

from thread_encoder.__version__ import __description__, __title__, __version__

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
    "PromptTemplate",
    "TranscriptCompressionResult",
    "TranscriptAnalysis",
    "SDEncoderV2",
    "SDEncoder",
    "ThreadEncoder",
    "SysPromptEncoder",
    "KolmogorovModel",
    "PerplexityResult",
    "ConditionalEntropyResult",
    "CompressionQualityReport",
    "KolmogorovAnalyzer",
    "PerplexityAnalyzer",
    "CompressionQualityGate",
]

__locals = locals()
for __name in __all__:
    if not __name.startswith("__"):
        setattr(__locals[__name], "__module__", "thread_encoder")
