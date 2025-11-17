from src.components.sys_prompt._schemas import CompressionResult
from cllm.src.quality_gate.base import _QualityGate
from cllm.src.quality_gate.schemas import GateResult, GateSeverity, GateStatus


class TokenSyntaxGate(_QualityGate):
    def __init__(self):
        self.name = "TOKEN_SYNTAX"
        self.severity = GateSeverity.CRITICAL

    def validate(self, input: str, output: CompressionResult) -> GateResult:
        syntax_errors = []

        # Check balanced brackets
        if output.count("[") != output.count("]"):
            syntax_errors.append(
                {
                    "error": "UNBALANCED_BRACKETS",
                    "open": output.count("["),
                    "close": output.count("]"),
                }
            )

        # Extract all tokens
        import re

        tokens = re.findall(r"\[([^\]]+)\]", output)

        for token in tokens:
            # Validate token format: TYPE:VALUE or TYPE:VALUE:ATTR=VAL
            parts = token.split(":")
            if len(parts) < 2:
                syntax_errors.append(
                    {
                        "error": "INVALID_FORMAT",
                        "token": token,
                        "expected": "TYPE:VALUE:ATTR=VAL",
                    }
                )
                continue

            token_type = parts[0]
            if token_type not in ["REQ", "TARGET", "EXTRACT", "CTX", "OUT", "REF"]:
                syntax_errors.append(
                    {"error": "UNKNOWN_TOKEN_TYPE", "type": token_type, "token": token}
                )

            # Validate attribute format (key=value)
            for part in parts[2:]:
                if "=" in part:
                    key, value = part.split("=", 1)
                    if not key or not value:
                        syntax_errors.append(
                            {
                                "error": "MALFORMED_ATTRIBUTE",
                                "attribute": part,
                                "token": token,
                            }
                        )

        if syntax_errors:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                severity=self.severity,
                score=0.0,
                message=f"Found {len(syntax_errors)} syntax errors",
                metadata={"errors": syntax_errors},
                failures=[e["error"] for e in syntax_errors],
            )

        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=1.0,
            message="Syntax valid",
            metadata={"token_count": len(tokens)},
            failures=[],
        )


class GrammarComplianceGate(_QualityGate):
    def __init__(self):
        self.name = "GRAMMAR_COMPLIANCE"
        self.severity = GateSeverity.WARNING  # Can be relaxed
        # Canonical order: REQ → TARGET → EXTRACT → CTX → OUT
        self.canonical_order = ["REQ", "TARGET", "EXTRACT", "CTX", "OUT", "REF"]

    def validate(self, input: str, output: CompressionResult) -> GateResult:
        import re

        tokens = re.findall(r"\[([^\]]+)\]", output.compressed)
        token_types = [t.split(":")[0] for t in tokens]

        # Check if ordering follows canonical sequence
        type_positions = {t: [] for t in self.canonical_order}
        for idx, token_type in enumerate(token_types):
            if token_type in type_positions:
                type_positions[token_type].append(idx)

        order_violations = []
        last_position = -1
        for expected_type in self.canonical_order:
            positions = type_positions[expected_type]
            if positions:
                first_pos = min(positions)
                if first_pos < last_position:
                    order_violations.append(
                        {
                            "type": expected_type,
                            "expected_after": self.canonical_order[
                                self.canonical_order.index(expected_type) - 1
                            ],
                            "position": first_pos,
                        }
                    )
                last_position = max(positions)

        if order_violations:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.DEGRADED,
                severity=self.severity,
                score=0.7,
                message=f"Token order violations: {len(order_violations)}",
                metadata={"violations": order_violations, "actual_order": token_types},
                failures=["ORDER_VIOLATION"],
            )

        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=1.0,
            message="Token order correct",
            metadata={"token_order": token_types},
            failures=[],
        )
