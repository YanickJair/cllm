from components.sys_prompt._schemas import CompressionResult
from utils.vocabulary import Vocabulary
from quality_gate.base import _QualityGate
from quality_gate.schemas import GateResult, GateSeverity, GateStatus


class TARGETPresenceGate(_QualityGate):
    def __init__(self):
        self.name = "TARGET_PRESENCE"
        self.severity = GateSeverity.CRITICAL

    def validate(self, input: str, output: CompressionResult) -> GateResult:
        target_tokens = output.targets
        noun_chunks = output.metadata.get("noun_chunks", [])

        if len(target_tokens) == 0:
            # Check if input actually has nouns to extract
            if len(noun_chunks) > 0:
                return GateResult(
                    gate_name=self.name,
                    status=GateStatus.FAIL,
                    severity=self.severity,
                    score=0.0,
                    message="No TARGET token despite noun chunks present",
                    metadata={"noun_chunks": noun_chunks, "input_snippet": input[:100]},
                    failures=["MISSING_TARGET_WITH_NOUNS"],
                )
            else:
                # Might be a prompt with implicit target
                return GateResult(
                    gate_name=self.name,
                    status=GateStatus.DEGRADED,
                    severity=GateSeverity.WARNING,
                    score=0.3,
                    message="No TARGET token (no nouns detected)",
                    metadata={"input": input},
                    failures=["NO_TARGET_NO_NOUNS"],
                )

        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=1.0,
            message=f"Found {len(target_tokens)} TARGET token(s)",
            metadata={"target_tokens": target_tokens},
            failures=[],
        )


class TARGETCoverageGate(_QualityGate):
    def __init__(self, min_coverage: float = 0.5):
        self.name = "TARGET_COVERAGE"
        self.severity = GateSeverity.WARNING
        self.min_coverage = min_coverage

    def validate(self, input: str, output: CompressionResult) -> GateResult:
        noun_chunks = output.metadata.get("noun_chunks", [])
        target_tokens = output.targets

        if not noun_chunks:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.PASS,
                severity=self.severity,
                score=1.0,
                message="No noun chunks to cover",
                metadata={},
                failures=[],
            )

        # Calculate coverage: how many noun chunks are represented in TARGET tokens
        covered_chunks = []
        for chunk in noun_chunks:
            for target in target_tokens:
                # Simple string matching (could be more sophisticated)
                if any(word in target.lower() for word in chunk.lower().split()):
                    covered_chunks.append(chunk)
                    break

        coverage_ratio = len(covered_chunks) / len(noun_chunks)

        if coverage_ratio < self.min_coverage:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.DEGRADED,
                severity=self.severity,
                score=coverage_ratio,
                message=f"Low TARGET coverage: {coverage_ratio:.1%}",
                metadata={
                    "total_chunks": len(noun_chunks),
                    "covered_chunks": len(covered_chunks),
                    "uncovered": list(set(noun_chunks) - set(covered_chunks)),
                },
                failures=["LOW_COVERAGE"],
            )

        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=coverage_ratio,
            message=f"Good TARGET coverage: {coverage_ratio:.1%}",
            metadata={"coverage": coverage_ratio, "covered": covered_chunks},
            failures=[],
        )


class AttributeValidityGate(_QualityGate):
    def __init__(self):
        self.name = "ATTRIBUTE_VALIDITY"
        self.severity = GateSeverity.CRITICAL
        self.schemas = Vocabulary.TARGET_TOKENS

    def validate(self, input: str, output: CompressionResult) -> GateResult:
        target_tokens = output.targets
        invalid_attributes = []

        for token in target_tokens:
            # Parse [TARGET:CODE:LANG=PYTHON:FILE_TYPE=MODULE]
            parts = token.split(":")
            target_type = parts[1] if len(parts) > 1 else None
            attributes = parts[2:] if len(parts) > 2 else []

            if target_type not in self.schemas:
                invalid_attributes.append(
                    {
                        "token": token,
                        "issue": "UNKNOWN_TARGET_TYPE",
                        "value": target_type,
                    }
                )
                continue

            # Validate each attribute
            valid_attrs = self.schemas[target_type].get("attributes", {})
            for attr in attributes:
                if "=" in attr:
                    key, value = attr.split("=", 1)
                    if key not in valid_attrs:
                        invalid_attributes.append(
                            {
                                "token": token,
                                "issue": "UNKNOWN_ATTRIBUTE",
                                "key": key,
                                "valid_keys": list(valid_attrs.keys()),
                            }
                        )
                    # Could also validate value is in allowed set

        if invalid_attributes:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                severity=self.severity,
                score=0.0,
                message=f"Found {len(invalid_attributes)} invalid attributes",
                metadata={"invalid": invalid_attributes},
                failures=["INVALID_ATTRIBUTES"],
            )

        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=1.0,
            message="All attributes valid",
            metadata={"target_tokens": target_tokens},
            failures=[],
        )
