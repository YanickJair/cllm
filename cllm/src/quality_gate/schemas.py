from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any


class GateSeverity(Enum):
    CRITICAL = "critical"  # Must pass or fail entire compression
    WARNING = "warning"  # Log but allow through
    INFO = "info"  # Collect metrics only


class GateStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    DEGRADED = "degraded"  # Passed but with concerns


@dataclass
class GateResult:
    gate_name: str
    status: GateStatus
    severity: GateSeverity
    score: float = 0.0  # 0.0 to 1.0
    message: str
    metadata: dict[str, Any]
    failures: list[str]  # Specific failure reasons


@dataclass
class CompressionPipeline:
    input: str
    semantic_tokens: Optional[str]
    statistical_tokens: Optional[str]
    entropy_coded: Optional[str]
    gate_results: list[GateResult]
    final_output: Optional[str]
    fallback_used: bool
