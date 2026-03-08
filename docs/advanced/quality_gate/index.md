# Quality Gate

## Overview

The CLM Quality Gate validates that compressed token strings produced by the Thread Encoder preserve the semantic meaning of the original transcript. Compression that silently drops critical information is worse than no compression at all — the Quality Gate catches this before it reaches production.

**Core question:** Did the tokenization step lose any meaning that matters?

**Method:** Three independent entropy analyses, each targeting a different failure mode:

| Analyzer | Method | Catches |
|----------|--------|---------|
| **Kolmogorov** | zlib compression ratio | Structural simplification gone too far |
| **Conditional Entropy** | Slot-level structured comparison | Silent semantic field loss |
| **Perplexity** | LLM comprehension test via API | LLM understanding degradation |

---

## Quick Start

### Offline / CI mode (no API calls)

```python
from clm_core import CompressionQualityGate

gate = CompressionQualityGate()

report = gate.analyze(
    original=transcript_text,
    compressed=clm_token_string,
    structured=thread_encoder_output_dict,  # optional but recommended
    run_perplexity=False,                   # skip LLM call — perplexity gets synthetic perfect score
)

print(report.verdict)          # "lossless", "acceptable", or "high_risk"
print(report.retention_score)  # 0–100
print(report.summary())        # full human-readable breakdown
```

### With LLM perplexity analysis

```python
from clm_core import CompressionQualityGate, PerplexityConfig

cfg = PerplexityConfig(
    llm_model="claude-haiku-4-5-20251001",
    api_key="sk-ant-...",
    host_url="https://api.anthropic.com",
)

gate = CompressionQualityGate(llm_client="anthropic", perplexity_cfg=cfg)

report = gate.analyze(
    original=transcript_text,
    compressed=clm_token_string,
    structured=thread_encoder_output_dict,
    run_perplexity=True,
)

print(report.verdict)
print(report.retention_score)
print(report.summary())
```

---

## CompressionQualityGate

Single entry point that orchestrates all three analyzers.

```python
from clm_core import CompressionQualityGate, PerplexityConfig

# Offline (Kolmogorov + Conditional Entropy only)
gate = CompressionQualityGate()

# With Anthropic perplexity
gate = CompressionQualityGate(
    llm_client="anthropic",
    perplexity_cfg=PerplexityConfig(
        llm_model="claude-haiku-4-5-20251001",
        api_key="sk-ant-...",
        host_url="https://api.anthropic.com",
    ),
)

# With OpenAI perplexity
gate = CompressionQualityGate(
    llm_client="openai",
    perplexity_cfg=PerplexityConfig(
        llm_model="gpt-4o-mini",
        api_key="sk-...",
        host_url="https://api.openai.com/v1",
    ),
)
```

**Constructor parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm_client` | `"anthropic" \| "openai" \| None` | `None` | LLM backend for perplexity analysis. If `None`, perplexity falls back to heuristic scoring. |
| `perplexity_cfg` | `PerplexityConfig \| None` | `None` | LLM connection config (model, API key, host URL). Required when `llm_client` is set. |

### PerplexityConfig

```python
from clm_core import PerplexityConfig

cfg = PerplexityConfig(
    llm_model="claude-haiku-4-5-20251001",  # Model to use for evaluation
    api_key="sk-ant-...",                    # API key for the chosen provider
    host_url="https://api.anthropic.com",   # Base URL for the API
    temperature=0.0,                        # Sampling temperature (default: 0.0)
)
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `llm_model` | `str` | — | Model identifier for the LLM call |
| `api_key` | `str` | — | API key for the chosen provider |
| `host_url` | `str` | — | Base URL for the API endpoint |
| `temperature` | `float` | `0.0` | Sampling temperature |

### `analyze()`

```python
report = gate.analyze(
    original: str,
    compressed: str,
    structured: dict | None = None,
    run_perplexity: bool = False,
    verbose: bool = False,
    perplexity_task: str | None = None,
) -> CompressionQualityReport
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `original` | `str` | — | Raw transcript or source text |
| `compressed` | `str` | — | CLM encoder output token string |
| `structured` | `dict \| None` | `None` | Thread Encoder structured extraction dict. If `None`, conditional entropy is skipped (assumed perfect). |
| `run_perplexity` | `bool` | `False` | Set `True` to run LLM perplexity analysis. Set `False` to skip API calls — useful for batch validation or CI/CD pipelines. |
| `verbose` | `bool` | `False` | Print progress to stdout as each stage runs. |
| `perplexity_task` | `str \| None` | `None` | Custom task prompt sent to the LLM for both original and compressed inputs. If `None`, uses the built-in structured JSON extraction task. |

---

## CompressionQualityReport

The unified report combining results from all three analyzers.

```python
class CompressionQualityReport(BaseModel):
    original: str
    compressed: str
    kolmogorov: KolmogorovModel
    conditional: ConditionalEntropyResult | None
    perplexity: PerplexityResult
    verdict: Literal["lossless", "acceptable", "high_risk"]
    retention_score: float  # 0–100
```

### Fields

#### `verdict`

Three possible outcomes:

| Verdict | Condition | Meaning |
|---------|-----------|---------|
| `lossless` | All three analyzers passed | Compression is semantically safe |
| `acceptable` | Kolmogorov + Conditional passed, perplexity borderline | Usable with monitoring |
| `high_risk` | Conditional entropy failed, or two or more failed | Compression likely dropped meaning |

**Conditional entropy has veto power.** A borderline perplexity score alone will not push a result to `high_risk`, but a failed conditional entropy check always does — because it is the most direct measure of semantic loss.

#### `retention_score`

Weighted composite score from 0 to 100:

```
retention_score = (kolmogorov × 0.25) + (conditional × 0.50) + (perplexity × 0.25)
```

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Kolmogorov information efficiency | 25% | Structural signal, low variance |
| Conditional entropy weighted coverage | 50% | Direct semantic slot comparison |
| Perplexity comprehension score | 25% | LLM understanding, API-dependent |

#### `summary()`

Returns a human-readable multi-line breakdown of all metrics:

```
Verdict:              LOSSLESS
Retention Score:      96.8%

[Kolmogorov]
  Complexity ratio:   0.412
  Info efficiency:    1.18x
  Passed:             True

[Conditional Entropy]
  Slots (total/matched): 14/14
  Null in source:     4 fields skipped
  Weighted coverage:  100.0%
  Raw coverage:       100.0%
  Residual entropy:   0.00 bits
  Lost fields:        none
  Passed:             True

[Perplexity]
  Comprehension:      0.87
  Latency saved:      12.3%
  Response similarity:0.85
  Passed:             True
```

---

## Complete Example

```python
from clm_core import CompressionQualityGate, PerplexityConfig

ORIGINAL = """
Customer called in to report a duplicate charge on their account.
Agent verified the billing issue, confirmed a duplicate payment had been
processed, and initiated a refund of $49.99 with reference RFD-908712.
A confirmation email was sent. Customer sentiment moved from neutral to
satisfied to grateful over the 7-minute voice call.
"""

STRUCTURED = {
    'channel': 'VOICE',
    'lang': 'EN',
    'domain': 'BILLING',
    'service': 'PAYMENT',
    'customerIntent': 'REPORT_BILLING_ISSUE',
    'state': 'PENDING_REFUND',
    'resolution': 'REFUND_INITIATED',
    'sentiment': ['NEUTRAL', 'SATISFIED', 'GRATEFUL'],
    'agentActions': ['ACCOUNT_LOOKUP', 'DUPLICATE_PAYMENT_CONFIRMED', 'CUSTOMER_NOTIFIED'],
    'commitments': [{'type': 'REFUND', 'etaDays': 4}],
    'artifacts': [{'key': 'REFUND_REF', 'value': 'RFD-908712'}],
    'durationSeconds': 420,
}

COMPRESSED = (
    "[INTERACTION:SUPPORT:CHANNEL=VOICE] [DURATION=7m] [LANG=EN] "
    "[DOMAIN:BILLING] [SERVICE:PAYMENT] "
    "[CUSTOMER_INTENT:REPORT_BILLING_ISSUE] "
    "[AGENT_ACTIONS:ACCOUNT_LOOKUP→DUPLICATE_PAYMENT_CONFIRMED→CUSTOMER_NOTIFIED] "
    "[RESOLUTION:REFUND_INITIATED] [STATE:PENDING_REFUND] "
    "[COMMITMENT:REFUND:ETA=4d] [ARTIFACTS:REFUND_REF=RFD-908712] "
    "[SENTIMENT:NEUTRAL→SATISFIED→GRATEFUL]"
)

# Offline validation (Kolmogorov + Conditional Entropy)
gate = CompressionQualityGate()
report = gate.analyze(
    original=ORIGINAL,
    compressed=COMPRESSED,
    structured=STRUCTURED,
    verbose=True,
)

print(report.summary())

# Per-field breakdown
print("\n[Field-by-field Conditional Entropy]")
for fr in report.conditional.field_results:
    status = "NULL" if fr.null_in_source else ("✓" if fr.found_in_compressed else "✗ LOST")
    print(f"{fr.field:<22} {fr.token_key:<22} {status:<8} weight={fr.weight}")
```

**With LLM perplexity enabled:**

```python
cfg = PerplexityConfig(
    llm_model="claude-haiku-4-5-20251001",
    api_key="sk-ant-...",
    host_url="https://api.anthropic.com",
)
gate = CompressionQualityGate(llm_client="anthropic", perplexity_cfg=cfg)
report = gate.analyze(
    original=ORIGINAL,
    compressed=COMPRESSED,
    structured=STRUCTURED,
    run_perplexity=True,
    verbose=True,
)
print(report.summary())
```

---

## Architecture

The three analyzers run sequentially and independently — a failure in one does not prevent the others from running. The gate always returns a complete report.

```
gate.analyze(original, compressed, structured)
    │
    ├─ KolmogorovAnalyzer.analyze(original, compressed)
    │       └─ KolmogorovModel
    │
    ├─ ConditionalEntropyAnalyzer.analyze(structured, compressed)
    │       └─ ConditionalEntropyResult
    │
    └─ PerplexityAnalyzer.analyze(original, compressed)
            └─ PerplexityResult
                    │
                    ├─ via API (anthropic or openai) if llm_client set + run_perplexity=True
                    └─ via heuristic token overlap if not
```

When `structured` is `None`, the conditional entropy result is a synthetic perfect score (coverage=1.0, entropy=0.0, passed=True), so it does not influence the verdict.

When `run_perplexity=False`, the perplexity result is similarly a synthetic perfect score, enabling fast offline validation.

---

## Interpreting Results

### Lossless compression — expected for well-formed CLM output

All three analyzers pass. The token string is structurally simpler (as expected and healthy), retains all semantic slots, and an LLM produces equivalent answers from both inputs.

### Acceptable — usable with monitoring

Kolmogorov and conditional entropy passed. Perplexity fell short of its threshold, which can happen due to LLM response variability or domain-specific token phrasing. Monitor in production.

### High risk — review the encoder output

At minimum, a critical semantic field was dropped (`customerIntent`, `resolution`, `domain`, or `state`) or weighted coverage fell below 88%. Do not use this compressed output without investigation.

---

## Next Steps

- **[Kolmogorov Complexity](kolmogorov.md)** — Structural information equivalence via compression ratio
- **[Conditional Entropy](conditional_entropy.md)** — Semantic slot comparison and field schema
- **[Perplexity](perplexity.md)** — LLM comprehension test and heuristic fallback
