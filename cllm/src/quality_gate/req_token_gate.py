from cllm.src.core._schemas import CompressionResult
from cllm.src.quality_gate.base import _QualityGate
from cllm.src.quality_gate.schemas import GateResult, GateSeverity, GateStatus


class REQPresenceGate(_QualityGate):
    def __init__(self):
        self.name = "REQ_PRESENCE"
        self.severity = GateSeverity.CRITICAL
    
    def validate(self, input: str, output: CompressionResult) -> GateResult:
        req_tokens = output.intents
        
        if len(req_tokens) == 0:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                severity=self.severity,
                score=0.0,
                message="No REQ token found - unclear intent",
                metadata={
                    "input_length": len(input.split()),
                    "detected_verbs": output.metadata.get("verbs", [])
                },
                failures=["NO_REQ_TOKEN"]
            )
        
        # Multiple REQ tokens is acceptable for multi-step prompts
        if len(req_tokens) > 3:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.DEGRADED,
                severity=GateSeverity.WARNING,
                score=0.7,
                message=f"Unusually high REQ count: {len(req_tokens)}",
                metadata={"req_tokens": req_tokens},
                failures=["EXCESSIVE_REQ_COUNT"]
            )
        
        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=1.0,
            message=f"Found {len(req_tokens)} REQ token(s)",
            metadata={"req_tokens": req_tokens},
            failures=[]
        )
    
class REQValidityGate(_QualityGate):
    def __init__(self, vocabulary: dict):
        self.name = "REQ_VALIDITY"
        self.severity = GateSeverity.CRITICAL
        self.valid_reqs = set(vocabulary["REQ"]["tokens"].keys())
    
    def validate(self, input: str, output: CompressionResult) -> GateResult:
        req_tokens = output.intents
        invalid_tokens = []
        
        for token in req_tokens:
            # Parse [REQ:ANALYZE:DEEP] -> ANALYZE
            action = token.split(":")[1]
            if action not in self.valid_reqs:
                invalid_tokens.append(action)
        
        if invalid_tokens:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                severity=self.severity,
                score=0.0,
                message=f"Invalid REQ tokens: {invalid_tokens}",
                metadata={"invalid": invalid_tokens, "valid": list(self.valid_reqs)},
                failures=[f"INVALID_REQ_{token}" for token in invalid_tokens]
            )
        
        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=1.0,
            message="All REQ tokens valid",
            metadata={"req_tokens": req_tokens},
            failures=[]
        )

class IntentMatchQualityGate(_QualityGate):
    def __init__(self, min_coverage: float = 0.7):
        self.name = "INTENT_MATCH_QUALITY"
        self.severity = GateSeverity.WARNING
        self.min_coverage = min_coverage
    
    def validate(self, input: str, output: CompressionResult) -> GateResult:
        """Check if detected verbs were successfully mapped to REQ tokens"""
        detected_verbs = output.metadata.get("verbs", [])
        req_tokens = output.intents
        
        if not detected_verbs:
            # No verbs to match - might be implicit intent
            return GateResult(
                gate_name=self.name,
                status=GateStatus.DEGRADED,
                severity=self.severity,
                score=0.5,
                message="No verbs detected in input",
                metadata={"input_sample": input[:100]},
                failures=["NO_VERBS_DETECTED"]
            )
        
        if not req_tokens:
            # Verbs present but no REQ tokens matched
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                severity=GateSeverity.CRITICAL,
                score=0.0,
                message=f"Failed to map {len(detected_verbs)} verb(s) to REQ tokens",
                metadata={
                    "detected_verbs": detected_verbs,
                    "input_sample": input[:100]
                },
                failures=["VERB_MAPPING_FAILED"]
            )
        
        # Calculate coverage: how many verbs got mapped
        # Simple heuristic: if we have REQ tokens, assume good coverage
        # Better: track which verbs mapped to which REQ tokens
        verb_to_req_ratio = len(req_tokens) / len(detected_verbs)
        
        # Too many REQ tokens might indicate over-matching
        if verb_to_req_ratio > 1.5:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.DEGRADED,
                severity=GateSeverity.WARNING,
                score=0.7,
                message=f"Possible over-matching: {len(req_tokens)} REQ from {len(detected_verbs)} verbs",
                metadata={
                    "verbs": detected_verbs,
                    "req_tokens": req_tokens,
                    "ratio": verb_to_req_ratio
                },
                failures=["POSSIBLE_OVERMATCHING"]
            )
        
        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=1.0,
            message=f"Successfully mapped {len(detected_verbs)} verb(s) to {len(req_tokens)} REQ token(s)",
            metadata={
                "verbs": detected_verbs,
                "req_tokens": req_tokens
            },
            failures=[]
        )
    def __init__(self, min_coverage: float = 0.7):
        self.name = "INTENT_MATCH_QUALITY"
        self.severity = GateSeverity.WARNING
        self.min_coverage = min_coverage
    
    def validate(self, input: str, output: CompressionResult) -> GateResult:
        """Check if detected verbs were successfully mapped to REQ tokens"""
        detected_verbs = output.metadata.get("verbs", [])
        req_tokens = output.intents
        
        if not detected_verbs:
            # No verbs to match - might be implicit intent
            return GateResult(
                gate_name=self.name,
                status=GateStatus.DEGRADED,
                severity=self.severity,
                score=0.5,
                message="No verbs detected in input",
                metadata={"input_sample": input[:100]},
                failures=["NO_VERBS_DETECTED"]
            )
        
        if not req_tokens:
            # Verbs present but no REQ tokens matched
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                severity=GateSeverity.CRITICAL,
                score=0.0,
                message=f"Failed to map {len(detected_verbs)} verb(s) to REQ tokens",
                metadata={
                    "detected_verbs": detected_verbs,
                    "input_sample": input[:100]
                },
                failures=["VERB_MAPPING_FAILED"]
            )
        
        # Calculate coverage: how many verbs got mapped
        # Simple heuristic: if we have REQ tokens, assume good coverage
        # Better: track which verbs mapped to which REQ tokens
        verb_to_req_ratio = len(req_tokens) / len(detected_verbs)
        
        # Too many REQ tokens might indicate over-matching
        if verb_to_req_ratio > 1.5:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.DEGRADED,
                severity=GateSeverity.WARNING,
                score=0.7,
                message=f"Possible over-matching: {len(req_tokens)} REQ from {len(detected_verbs)} verbs",
                metadata={
                    "verbs": detected_verbs,
                    "req_tokens": req_tokens,
                    "ratio": verb_to_req_ratio
                },
                failures=["POSSIBLE_OVERMATCHING"]
            )
        
        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=1.0,
            message=f"Successfully mapped {len(detected_verbs)} verb(s) to {len(req_tokens)} REQ token(s)",
            metadata={
                "verbs": detected_verbs,
                "req_tokens": req_tokens
            },
            failures=[]
        )