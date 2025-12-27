from components.sys_prompt._schemas import CompressionResult
from quality_gate.base import _QualityGate
from quality_gate.schemas import GateResult, GateSeverity, GateStatus


class PatternMatchGate(_QualityGate):
    def __init__(self, pattern_db, min_confidence: float = 0.8):
        self.name = "PATTERN_MATCH"
        self.severity = GateSeverity.WARNING
        self.pattern_db = pattern_db
        self.min_confidence = min_confidence

    def validate(self, input: str, output: CompressionResult) -> GateResult:
        # After statistical compression with REF tokens
        ref_tokens = None  # TODO: extract REF when available

        if not ref_tokens:
            # No patterns used - not necessarily bad
            return GateResult(
                gate_name=self.name,
                status=GateStatus.PASS,
                severity=GateSeverity.INFO,
                score=1.0,
                message="No pattern matching applied",
                metadata={},
                failures=[],
            )

        low_confidence_refs = []
        for ref_token in ref_tokens:
            # Parse [REF:TMPL_001:v1] -> TMPL_001
            ref_id = ref_token.split(":")[1]
            pattern_info = self.pattern_db.get(ref_id)

            if not pattern_info:
                low_confidence_refs.append({"ref": ref_id, "issue": "UNKNOWN_REF"})
                continue

            # Check match confidence from metadata
            confidence = output.metadata.get(f"ref_confidence_{ref_id}", 0.0)
            if confidence < self.min_confidence:
                low_confidence_refs.append(
                    {"ref": ref_id, "confidence": confidence, "issue": "LOW_CONFIDENCE"}
                )

        if low_confidence_refs:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.DEGRADED,
                severity=self.severity,
                score=self.min_confidence,
                message=f"Low confidence pattern matches: {len(low_confidence_refs)}",
                metadata={"low_confidence": low_confidence_refs},
                failures=["LOW_PATTERN_CONFIDENCE"],
            )

        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=1.0,
            message=f"Pattern matching confident ({len(ref_tokens)} refs)",
            metadata={"ref_tokens": ref_tokens},
            failures=[],
        )
