from cllm.src.core._schemas import CompressionResult
from cllm.src.quality_gate.base import _QualityGate
from cllm.src.quality_gate.schemas import GateResult, GateSeverity, GateStatus


class CompressionRatioGate(_QualityGate):
    def __init__(self, min_ratio: float = 0.3, max_ratio: float = 0.9):
        self.name = "COMPRESSION_RATIO"
        self.severity = GateSeverity.WARNING
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio
    
    def validate(self, input: str, output: CompressionResult) -> GateResult:
        input_tokens = len(input.split())
        output_tokens = len(output.compressed())
        
        if input_tokens == 0:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                severity=GateSeverity.CRITICAL,
                score=0.0,
                message="Empty input",
                metadata={},
                failures=["EMPTY_INPUT"]
            )
        
        compression_ratio = 1 - (output_tokens / input_tokens)
        
        # Suspiciously low compression
        if compression_ratio < self.min_ratio:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.DEGRADED,
                severity=self.severity,
                score=compression_ratio / self.min_ratio,
                message=f"Low compression: {compression_ratio:.1%}",
                metadata={
                    "ratio": compression_ratio,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                },
                failures=["LOW_COMPRESSION"]
            )
        
        # Suspiciously high compression (possible information loss)
        if compression_ratio > self.max_ratio:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.DEGRADED,
                severity=GateSeverity.WARNING,
                score=1 - (compression_ratio - self.max_ratio),
                message=f"High compression: {compression_ratio:.1%} - verify no loss",
                metadata={
                    "ratio": compression_ratio,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens
                },
                failures=["EXCESSIVE_COMPRESSION"]
            )
        
        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=1.0,
            message=f"Compression ratio: {compression_ratio:.1%}",
            metadata={"ratio": compression_ratio},
            failures=[]
        )
    
class ReversibilityGate(_QualityGate):
    def __init__(self, decoder, similarity_threshold: float = 0.95):
        self.name = "REVERSIBILITY"
        self.severity = GateSeverity.CRITICAL
        self.decoder = decoder
        self.threshold = similarity_threshold
    
    def validate(self, input: str, output: CompressionResult) -> GateResult:
        # Attempt to reconstruct original from compressed
        try:
            reconstructed = self.decoder.decompress(output.compressed)
        except Exception as e:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                severity=self.severity,
                score=0.0,
                message=f"Decompression failed: {str(e)}",
                metadata={"error": str(e)},
                failures=["DECOMPRESSION_ERROR"]
            )
        
        # Calculate semantic similarity (could use embeddings)
        similarity = self._calculate_similarity(input, reconstructed)
        
        if similarity < self.threshold:
            return GateResult(
                gate_name=self.name,
                status=GateStatus.FAIL,
                severity=self.severity,
                score=similarity,
                message=f"Low semantic similarity: {similarity:.1%}",
                metadata={
                    "original": input[:200],
                    "reconstructed": reconstructed[:200],
                    "similarity": similarity
                },
                failures=["LOW_SIMILARITY"]
            )
        
        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=similarity,
            message=f"Reversible with {similarity:.1%} similarity",
            metadata={"similarity": similarity},
            failures=[]
        )
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        # Simple approach: normalized edit distance
        # Better: sentence embeddings (SBERT, OpenAI, etc.)
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1, text2).ratio()
    
class CriticalInfoGate(_QualityGate):
    def __init__(self):
        self.name = "CRITICAL_INFO"
        self.severity = GateSeverity.CRITICAL
    
    def validate(self, input: str, output: CompressionResult) -> GateResult:
        import re
        
        critical_elements = {
            "numbers": re.findall(r'\b\d+(?:\.\d+)?\b', input),
            "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', input),
            "dates": output.metadata.get("detected_dates", []),
            "names": output.metadata.get("detected_names", []),
            "urls": re.findall(r'https?://[^\s]+', input)
        }
        
        # Check if critical elements are represented in output
        # (either explicitly or via metadata attributes)
        missing_elements = {}
        
        for element_type, elements in critical_elements.items():
            if elements:
                # Check if represented in compressed output
                represented = 0
                for element in elements:
                    if str(element) in output or str(element) in str(output.metadata):
                        represented += 1
                
                coverage = represented / len(elements)
                if coverage < 0.8:  # Less than 80% represented
                    missing_elements[element_type] = {
                        "total": len(elements),
                        "represented": represented,
                        "coverage": coverage,
                        "examples": elements[:3]
                    }
        
        if missing_elements:
            # This might be OK if elements are in REF or implicit
            # Severity depends on element type
            severity = GateSeverity.WARNING
            for elem_type in missing_elements:
                if elem_type in ["numbers", "dates"]:
                    severity = GateSeverity.CRITICAL
                    break
            
            return GateResult(
                gate_name=self.name,
                status=GateStatus.DEGRADED if severity == GateSeverity.WARNING else GateStatus.FAIL,
                severity=severity,
                score=0.5,
                message=f"Potential information loss in: {list(missing_elements.keys())}",
                metadata={"missing": missing_elements},
                failures=["MISSING_CRITICAL_INFO"]
            )
        
        return GateResult(
            gate_name=self.name,
            status=GateStatus.PASS,
            severity=self.severity,
            score=1.0,
            message="All critical information preserved",
            metadata={"checked": list(critical_elements.keys())},
            failures=[]
        )