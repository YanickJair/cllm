from typing import Optional, Literal, Any

from . import (
    KolmogorovAnalyzer,
    PerplexityAnalyzer,
    CompressionQualityReport,
    KolmogorovModel,
    ConditionalEntropyResult,
    PerplexityResult,
    ConditionalEntropyAnalyzer,
)


class CompressionQualityGate:
    """
    Orchestrates all three entropy methods and produces a unified report.

    Example:
        analyzer = CompressionQualityAnalyzer()
        report = analyzer.analyze(original_transcript, cllm_output)

        print(report.verdict)          # "lossless"
        print(report.retention_score)  # 97.4
        print(report.summary())        # full breakdown
    """

    def __init__(self, llm_client: Literal["anthropic", "openai"]):
        self.kolmogorov = KolmogorovAnalyzer()
        self.conditional = ConditionalEntropyAnalyzer()
        self.perplexity = PerplexityAnalyzer(llm_client=llm_client)

    def analyze(
        self,
        original: str,
        compressed: str,
        structured: Optional[dict[str, Any]] = None,
        run_perplexity: bool = True,
        verbose: bool = False,
    ) -> CompressionQualityReport:
        """
        Run all three analyses and return a unified report.

        Args:
            original:        Raw source text (transcript, prompt, etc.)
            compressed:      CLLM encoder output token string
            structured:      CLLM structured extraction dict (Thread Encoder output).
                             If provided, ConditionalEntropy uses it directly.
                             If None, conditional entropy is skipped (returns perfect score).
            run_perplexity:  Set False to skip API calls (fast / CI mode)
            verbose:         Print progress
        """
        if verbose:
            print("[ 1/3 ] Kolmogorov complexity analysis...")
        k_result = self.kolmogorov.analyze(original, compressed)

        if verbose:
            print("[ 2/3 ] Conditional entropy analysis...")
        c_result = (
            self.conditional.analyze(structured, compressed)
            if structured is not None
            else self._conditional_skipped()
        )

        if verbose:
            print("[ 3/3 ] Perplexity / LLM comprehension test...")
        p_result = (
            self.perplexity.analyze(original, compressed, verbose=verbose)
            if run_perplexity
            else self._perplexity_skipped()
        )

        verdict = self._compute_verdict(k=k_result, c=c_result, p=p_result)
        retention = self._compute_retention_score(k=k_result, c=c_result, p=p_result)

        return CompressionQualityReport(
            original=original,
            compressed=compressed,
            kolmogorov=k_result,
            conditional=c_result,
            perplexity=p_result,
            verdict=verdict,
            retention_score=retention,
        )

    @staticmethod
    def _compute_verdict(
        *,
        k: KolmogorovModel,
        c: ConditionalEntropyResult,
        p: PerplexityResult,
    ) -> Literal["lossless", "acceptable", "high_risk"]:
        passed_count = sum([k.passed, c.passed, p.passed])
        if passed_count == 3:
            return "lossless"
        elif passed_count >= 2 and c.passed:
            return "acceptable"
        else:
            return "high_risk"

    @staticmethod
    def _compute_retention_score(
        *,
        k: KolmogorovModel,
        c: ConditionalEntropyResult,
        p: PerplexityResult,
    ) -> float:
        k_score = min(1.0, k.information_efficiency) * 100
        c_score = (
            c.weighted_coverage * 100
        )  # weighted coverage — more meaningful than raw
        p_score = p.comprehension_score * 100
        return round(k_score * 0.25 + c_score * 0.50 + p_score * 0.25, 1)

    @staticmethod
    def _conditional_skipped() -> ConditionalEntropyResult:
        return ConditionalEntropyResult(
            field_results=[],
            slots_total=0,
            slots_matched=0,
            slots_lost=[],
            slots_null_in_source=[],
            weighted_coverage=1.0,
            raw_coverage=1.0,
            residual_entropy=0.0,
            bits_per_lost_field={},
            passed=True,
        )

    @staticmethod
    def _perplexity_skipped() -> PerplexityResult:
        return PerplexityResult(
            original_response_tokens=0,
            compressed_response_tokens=0,
            original_latency_ms=0,
            compressed_latency_ms=0,
            latency_improvement=0,
            response_similarity=1.0,
            structure_preserved=True,
            key_facts_preserved=[],
            facts_lost=[],
            comprehension_score=1.0,
            passed=True,
        )
