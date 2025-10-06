from cllm.src.core._schemas import CompressionResult
from cllm.src.quality_gate.base import _QualityGate
from cllm.src.quality_gate.schemas import GateResult, GateSeverity, GateStatus


class EntropyBoundsGate(_QualityGate):
    def __init__(self):
        self.name = "ENTROPY_BOUNDS"
        self.severity = GateSeverity.WARNING
    
    def validate(self, input: str, output: CompressionResult) -> GateResult:
        import math
        
        # Calculate theoretical entropy
        def calculate_entropy(text):
            from collections import Counter
            counts = Counter(text)
            total = len(text)
            entropy = -sum((count/total) * math.log2(count/total) 
                          for count in counts.values() if count > 0)
            return entropy
        
        input_entropy = calculate_entropy(input)
        output_entropy = calculate_entropy(output.compressed)
        
        # Entropy should not increase dramatically
        if output_entropy > input_entropy * 1.2:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.DEGRADED,
                severity=self.severity,
                score=0.7,
                message="Entropy increased - compression inefficient",
                metadata={
                    "input_entropy": input_entropy,
                    "output_entropy": output_entropy
                },
                failures=["ENTROPY_INCREASE"]
            )
        
        # Calculate compression efficiency
        theoretical_min = input_entropy * len(output)
        actual_bits = len(output) * 8  # Assuming 8-bit chars
        efficiency = theoretical_min / actual_bits if actual_bits > 0 else 0
        
        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=efficiency,
            message=f"Compression efficiency: {efficiency:.1%}",
            metadata={
                "input_entropy": input_entropy,
                "output_entropy": output_entropy,
                "efficiency": efficiency
            },
            failures=[]
        )