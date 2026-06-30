from typing import Literal, Any

from pydantic import BaseModel, Field


class KolmogorovModel(BaseModel):
    """
    Structural information equivalence via compression ratio comparison.

    Intuition: If zlib compresses both strings to similar sizes, they carry
    simil
    """

    original_bytes: int = Field(..., description="Original bytes of the input data")
    compressed_bytes: int = Field(..., description="zlib size of the input data")
    clm_bytes: int = Field(
        ..., description="zlib size of the CLM compressed output data"
    )
    original_zlib_bytes: int = Field(..., description="raw bytes before zlib")
    clm_zlib_bytes: int = Field(..., description="raw bytes after zlib")
    complexity_ratio: float = Field(
        ..., description="Compression ratio between original and CLM"
    )
    information_efficiency: float = Field(
        ..., description="How much info per byte in compressed vs original"
    )
    passed: bool = Field(..., description="True if structural content is preserved")


class FieldResult(BaseModel):
    """Outcome for a single semantic field comparison."""

    field: str = Field(..., description="e.g. customerIntent")
    token_key: str = Field(..., description="e.g. CUSTOMER_INTENT")
    expected_value: Any = Field(..., description="value from CLLM structured dict")
    found_in_compressed: bool = Field(
        ..., description="whether it appears in the token string"
    )
    weight: float = Field(
        ..., description="importance weight (HIGH=1.0, MEDIUM=0.6, LOW=0.3)"
    )
    null_in_source: bool = Field(
        ..., description="True if the source dict had None/empty — not a loss"
    )


class ConditionalEntropyResult(BaseModel):
    """
     Semantic losslessness: H(Structured | Compressed)

    Compares the CLLM structured extraction dict against the compressed
    token string. Answers: did the tokenization step lose any of the
    semantic content that was already extracted?

    H(X|Y) = 0 means the compressed token string fully determines the
    structured dict — perfect lossless tokenization.
    """

    field_results: list[FieldResult] = Field(..., description="per-field breakdown")
    slots_total: int = Field(..., description="non-null fields in structured dict")
    slots_matched: int = Field(..., description="found in compressed token string")
    slots_lost: list[str] = Field(
        ..., description="Field names dropped during tokenization"
    )
    slots_null_in_source: list[str] = Field(
        ..., description="fields that were None/empty — not a loss"
    )
    weighted_coverage: float = Field(
        ..., description="importance-weighted coverage 0–1"
    )
    raw_coverage: float = Field(..., description="simple slot count coverage 0–1")
    residual_entropy: float = Field(
        ..., description="estimated H(struct | compressed) in bits"
    )
    bits_per_lost_field: dict[str, float] = Field(
        ..., description="entropy contribution per lost field"
    )
    passed: bool = Field(..., description="True if coverage >= threshold")


class PerplexityConfig(BaseModel):
    llm_model: str = Field(..., description="LLM model")
    api_key: str = Field(..., description="LLM API key")
    host_url: str = Field(..., description="LLM host url")
    temperature: float = Field(default=0.0, description="LLM temperature")


class PerplexityResult(BaseModel):
    """
    LLM-native comprehension: does the model understand compressed tokens fluently?

    Method: send both prompts to the LLM and compare response quality + latency.
    Low perplexity proxy → coherent, on-topic response with consistent structure.
    """

    original_response_tokens: int = Field(..., description="Original response tokens")
    compressed_response_tokens: int = Field(
        ..., description="Compressed response tokens"
    )
    original_latency_ms: float = Field(..., description="Original latency ms")
    compressed_latency_ms: float = Field(..., description="Compressed latency ms")
    latency_improvement: float = Field(
        ..., description="% faster with compressed input"
    )
    response_similarity: float = Field(
        ..., description="0–1, semantic similarity of both responses"
    )
    structure_preserved: bool = Field(
        ..., description="Compressed response has same JSON/format structure"
    )
    key_facts_preserved: list[str] = Field(
        ..., description="Facts present in both responses"
    )
    facts_lost: list[str] = Field(
        ..., description="Facts in original response missing from compressed"
    )
    comprehension_score: float = Field(..., description="Composite 0–1 score")
    passed: bool = Field(
        ..., description="True if responses present in original or compressed"
    )


class CompressionQualityReport(BaseModel):
    """
    Full quality report combining all three entropy methods.

    verdict logic:
        lossless   → all three passed
        acceptable → kolmogorov + conditional passed, perplexity borderline
        high_risk  → any critical failure
    """

    original: str = Field(..., description="Original input data")
    compressed: str = Field(..., description="Compressed data")
    kolmogorov: KolmogorovModel = Field(..., description="Kolmogorov model")
    conditional: ConditionalEntropyResult | None = Field(
        default=None, description="Conditional entropy result"
    )
    perplexity: PerplexityResult = Field(..., description="Perplexity result")
    verdict: Literal["lossless", "acceptable", "high_risk"]
    retention_score: float = Field(..., description="Retention score - 0–100")

    def summary(self) -> str:
        c = self.conditional
        lost_with_bits = (
            ", ".join(f"{f}({b:.1f}b)" for f, b in c.bits_per_lost_field.items())
            or "none"
        )
        lines = [
            f"Verdict:              {self.verdict.upper()}",
            f"Retention Score:      {self.retention_score:.1f}%",
            "",
            "[Kolmogorov]",
            f"  Complexity ratio:   {self.kolmogorov.complexity_ratio:.3f}",
            f"  Info efficiency:    {self.kolmogorov.information_efficiency:.2f}x",
            f"  Passed:             {self.kolmogorov.passed}",
            "",
            "[Conditional Entropy]",
            f"  Slots (total/matched): {c.slots_total}/{c.slots_matched}",
            f"  Null in source:     {len(c.slots_null_in_source)} fields skipped",
            f"  Weighted coverage:  {c.weighted_coverage * 100:.1f}%",
            f"  Raw coverage:       {c.raw_coverage * 100:.1f}%",
            f"  Residual entropy:   {c.residual_entropy:.2f} bits",
            f"  Lost fields:        {lost_with_bits}",
            f"  Passed:             {c.passed}",
            "",
            "[Perplexity]",
            f"  Comprehension:      {self.perplexity.comprehension_score:.2f}",
            f"  Latency saved:      {self.perplexity.latency_improvement:.1f}%",
            f"  Response similarity:{self.perplexity.response_similarity:.2f}",
            f"  Passed:             {self.perplexity.passed}",
        ]
        return "\n".join(lines)


# Maps CLLM structured dict keys → expected token keys in compressed string.
# weight reflects information importance (used for weighted coverage score).
# domain_bits is the Shannon information content of each field:
#   log2(cardinality of the field's value domain).
#   e.g. CHANNEL has ~6 possible values → log2(6) ≈ 2.6 bits
#   CUSTOMER_INTENT has ~50+ values → log2(50) ≈ 5.6 bits
#
# This lets us compute residual entropy as:
#   H(struct | compressed) ≈ Σ domain_bits[field] for each lost field
FIELD_SCHEMA: list[dict] = [
    {"key": "channel", "token": "CHANNEL", "weight": 0.8, "bits": 2.6},
    {"key": "lang", "token": "LANG", "weight": 0.4, "bits": 2.0},
    {"key": "domain", "token": "DOMAIN", "weight": 0.9, "bits": 4.0},
    {"key": "service", "token": "SERVICE", "weight": 0.7, "bits": 3.5},
    {"key": "customerIntent", "token": "CUSTOMER_INTENT", "weight": 1.0, "bits": 5.6},
    {"key": "secondaryIntent", "token": "SECONDARY_INTENT", "weight": 0.6, "bits": 5.6},
    {"key": "state", "token": "STATE", "weight": 0.9, "bits": 4.5},
    {"key": "resolution", "token": "RESOLUTION", "weight": 1.0, "bits": 4.5},
    {"key": "sentiment", "token": "SENTIMENT", "weight": 0.9, "bits": 3.2},
    {"key": "agentActions", "token": "AGENT_ACTIONS", "weight": 0.8, "bits": 6.0},
    {"key": "systemActions", "token": "SYSTEM_ACTIONS", "weight": 0.6, "bits": 4.0},
    {"key": "commitments", "token": "COMMITMENT", "weight": 0.9, "bits": 5.0},
    {"key": "artifacts", "token": "ARTIFACTS", "weight": 0.7, "bits": 8.0},
    {"key": "supportTrigger", "token": "SUPPORT_TRIGGER", "weight": 0.7, "bits": 4.5},
    {
        "key": "interactionTrigger",
        "token": "INTERACTION_TRIGGER",
        "weight": 0.8,
        "bits": 4.5,
    },
    {"key": "context", "token": "CONTEXT", "weight": 0.5, "bits": 3.0},
    {"key": "durationSeconds", "token": "DURATION", "weight": 0.3, "bits": 4.0},
    {"key": "id", "token": "ID", "weight": 0.5, "bits": 16.0},
]

CRITICAL_FIELDS = {"customerIntent", "resolution", "domain", "state"}
OPTIONAL_FIELDS = {"secondaryIntent", "artifacts", "id", "createdAt"}
