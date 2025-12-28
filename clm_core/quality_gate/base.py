from abc import ABC

from core import CompressionResult
from quality_gate.schemas import GateSeverity


class _QualityGate(ABC):
    def __init__(self):
        self.name = "REQ_PRESENCE"
        self.severity: GateSeverity | None = None

    def validate(self, input: str, output: CompressionResult):
        """
        Validate the compressed prompt

        Gate 1: Intent Detection
        - Assert: At least 1 REQ token found
        - Assert: REQ token is valid vocabulary entry
        - Confidence: ≥ 0.7 match score

        Gate 2: Target Extraction
        - Assert: At least 1 TARGET token found
        - Assert: TARGET domain is valid
        - Coverage: Noun chunks → TARGET mapping ≥ 50%

        Gate 3: Attribute Parsing
        - Assert: EXTRACT fields are valid
        - Assert: CTX values match schema
        - Completeness: No orphaned attributes

        Gate 4: Token Assembly
        - Assert: Follows grammar (Section 3.4)
        - Assert: No duplicate token types (except allowed)
        - Syntax: Valid brackets, colons, equals

        Gate 5: Semantic Preservation
        - Reversibility: Can reconstruct original semantics
        - Loss check: Manual sample or learned classifier
        - Compression: Ratio within expected bounds (40-90%)

        Args:
            text: Input prompt text

        Returns:
            List of detected Target objects
        """
        raise NotImplementedError
