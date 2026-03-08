# Perplexity Analysis

## Overview

`PerplexityAnalyzer` validates that an LLM produces equivalent answers when given the compressed token string versus the original transcript. It directly tests CLM's core claim: an LLM can understand compressed tokens natively without fine-tuning.

**Core question:** Does the compressed token string give an LLM the same information as the original?

**Method:** Send both the original and compressed input to an LLM (Anthropic or OpenAI) with a fixed structured extraction task, then compare the responses across three dimensions.

This check carries a 25% weight in the final retention score. It supports Anthropic and OpenAI backends, and falls back to heuristic scoring when no API client is configured.

---

## How It Works

### API Mode

1. Send `original + EVALUATION_TASK` to the configured LLM
2. Send `compressed + EVALUATION_TASK` to the same LLM
3. Parse both responses as JSON
4. Compare across three dimensions

### Evaluation Task

Both prompts use the same structured JSON extraction task by default:

```json
{
  "primary_issue": "<what the customer needed>",
  "resolution": "<how it was resolved>",
  "sentiment": "<customer sentiment>",
  "follow_up_needed": true|false,
  "key_facts": ["<fact1>", "<fact2>", "<fact3>"]
}
```

You can override this with a custom `perplexity_task` argument in `gate.analyze()` or by subclassing — see [Tuning the evaluation task](#tuning-the-evaluation-task).

### Scoring Dimensions

| Dimension | Weight | Method |
|-----------|--------|--------|
| Fact overlap | 40% | Fraction of original `key_facts` with 2+ word overlap in compressed response |
| Field-level Jaccard | 40% | Jaccard similarity of `primary_issue`, `resolution`, `sentiment` across both responses |
| JSON structure preservation | 20% | All five expected keys present in compressed response |

```
comprehension_score = fact_score × 0.4
                    + response_similarity × 0.4
                    + structure_preserved × 0.2
```

**Pass condition:** `comprehension_score ≥ 0.82`

---

## Heuristic Fallback (Offline Mode)

When no `llm_client` is configured, or the API key cannot be loaded, the analyzer falls back to token overlap scoring:

```
orig_tokens = set of uppercase tokens (3+ chars) in original
clm_tokens  = set of uppercase tokens (3+ chars) in compressed

coverage = |orig_tokens ∩ clm_tokens| / |orig_tokens|
comprehension_score = coverage
```

This is a rough proxy that measures how much of the original's vocabulary is present in the compressed output. It is intentionally conservative — token overlap undercounts semantic preservation — and is suitable for CI/CD gating where you want to catch obvious failures without API calls.

**Skip perplexity entirely (synthetic perfect score):**

```python
report = gate.analyze(
    original=transcript,
    compressed=compressed,
    structured=structured,
    run_perplexity=False,  # perplexity result is a synthetic pass, no scoring done
)
```

---

## PerplexityConfig

`PerplexityConfig` holds the LLM connection settings passed to both `PerplexityAnalyzer` and `CompressionQualityGate`.

```python
from clm_core import PerplexityConfig

cfg = PerplexityConfig(
    llm_model="claude-haiku-4-5-20251001",
    api_key="sk-ant-...",
    host_url="https://api.anthropic.com",
    temperature=0.0,  # optional, default 0.0
)
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `llm_model` | `str` | — | Model identifier passed to the API |
| `api_key` | `str` | — | API key for the chosen provider |
| `host_url` | `str` | — | Base URL for the API endpoint |
| `temperature` | `float` | `0.0` | Sampling temperature |

---

## PerplexityResult

```python
class PerplexityResult(BaseModel):
    original_response_tokens: int       # Tokens in original response
    compressed_response_tokens: int     # Tokens in compressed response
    original_latency_ms: float          # LLM latency for original prompt
    compressed_latency_ms: float        # LLM latency for compressed prompt
    latency_improvement: float          # % faster with compressed input
    response_similarity: float          # 0–1, Jaccard field similarity
    structure_preserved: bool           # All expected JSON keys present
    key_facts_preserved: list[str]      # Facts present in both responses
    facts_lost: list[str]               # Facts from original missing in compressed
    comprehension_score: float          # Composite 0–1 score
    passed: bool                        # True if comprehension_score ≥ 0.82
```

---

## Standalone Usage

### With Anthropic

```python
from clm_core import PerplexityAnalyzer, PerplexityConfig

cfg = PerplexityConfig(
    llm_model="claude-haiku-4-5-20251001",
    api_key="sk-ant-...",
    host_url="https://api.anthropic.com",
)

analyzer = PerplexityAnalyzer(llm_client="anthropic", cfg=cfg)

result = analyzer.analyze(
    original=transcript_text,
    compressed=clm_token_string,
    verbose=True,
)

print(f"Comprehension score:  {result.comprehension_score:.2f}")
print(f"Response similarity:  {result.response_similarity:.2f}")
print(f"Structure preserved:  {result.structure_preserved}")
print(f"Latency improvement:  {result.latency_improvement:.1f}%")
print(f"Facts preserved:      {result.key_facts_preserved}")
print(f"Facts lost:           {result.facts_lost}")
print(f"Passed:               {result.passed}")
```

### With OpenAI

```python
from clm_core import PerplexityAnalyzer, PerplexityConfig

cfg = PerplexityConfig(
    llm_model="gpt-4o-mini",
    api_key="sk-...",
    host_url="https://api.openai.com/v1",
)

analyzer = PerplexityAnalyzer(llm_client="openai", cfg=cfg)

result = analyzer.analyze(
    original=transcript_text,
    compressed=clm_token_string,
)
```

### With a custom task

```python
result = analyzer.analyze(
    original=transcript_text,
    compressed=clm_token_string,
    task="""
    Given the above context, respond with a JSON object containing:
    {
      "billing_issue": "<the specific billing problem>",
      "refund_amount": "<amount if applicable>",
      "resolution_status": "<resolved|pending|escalated>",
      "key_facts": ["<fact1>", "<fact2>", "<fact3>"]
    }
    Respond ONLY with the JSON object.
    """,
)
```

---

## Latency as a Secondary Signal

`latency_improvement` is not used in the pass/fail decision, but it is captured as a secondary benefit metric. CLM's compressed tokens are shorter, so the LLM processes them faster. Negative values (compressed is slower) can indicate that the compressed string is unexpectedly verbose or that network variability dominated in a short test run.

---

## Interpreting Results

### Typical healthy output

```
comprehension_score:  0.89
response_similarity:  0.86
structure_preserved:  True
latency_improvement:  14.2%
facts_preserved:      ["duplicate charge confirmed", "refund initiated", "grateful customer"]
facts_lost:           []
passed:               True
```

### Warning signs

| Symptom | Likely cause |
|---------|-------------|
| `structure_preserved: False` | LLM produced malformed JSON from compressed input; token string may be ambiguous |
| `response_similarity < 0.5` | Core fields (`resolution`, `sentiment`) diverged significantly between responses |
| `facts_lost` contains critical facts | Key information not recoverable from compressed string |
| `comprehension_score` borderline (0.78–0.82) | May be LLM variability; re-run or accept as `acceptable` verdict |

### Relationship to verdict

Perplexity has no veto power. A failed perplexity check alongside a passed conditional entropy check results in `acceptable`, not `high_risk`. This is intentional: LLM response variability means perplexity can fail on a correctly compressed string, and that single failure should not block production use.

If perplexity consistently fails for a given compression pattern, investigate whether the CLM token format is being misunderstood by the model — the `EVALUATION_TASK` prompt in `PerplexityAnalyzer` can be tuned to your specific use case.

---

## Configuration

### Default models

| Client | Default model |
|--------|--------------|
| `anthropic` | `claude-haiku-4-5-20251001` |
| `openai` | `gpt-5-nano-2025-08-07` |

Pass a different model via `PerplexityConfig.llm_model`.

### Tuning the evaluation task

The `EVALUATION_TASK` prompt is designed for general customer service transcripts. For domain-specific validation, pass a custom task via `perplexity_task` at call time (no subclassing needed):

```python
report = gate.analyze(
    original=transcript,
    compressed=compressed,
    structured=structured,
    run_perplexity=True,
    perplexity_task="""
    Given the above context, respond with a JSON object containing:
    {
      "billing_issue": "<the specific billing problem>",
      "refund_amount": "<amount if applicable>",
      "refund_reference": "<reference number if applicable>",
      "resolution_status": "<resolved|pending|escalated>",
      "key_facts": ["<fact1>", "<fact2>", "<fact3>"]
    }
    Respond ONLY with the JSON object.
    """,
)
```

Or override the class constant via subclass for a permanent change:

```python
from clm_core import PerplexityAnalyzer

class BillingPerplexityAnalyzer(PerplexityAnalyzer):
    EVALUATION_TASK = """
    Given the above context, respond with a JSON object containing:
    {
      "billing_issue": "<the specific billing problem>",
      "refund_amount": "<amount if applicable>",
      "refund_reference": "<reference number if applicable>",
      "resolution_status": "<resolved|pending|escalated>",
      "key_facts": ["<fact1>", "<fact2>", "<fact3>"]
    }
    Respond ONLY with the JSON object.
    """
    COMPREHENSION_THRESHOLD = 0.90
```

---

## CI/CD Integration

For pipelines without API access, gate on Kolmogorov and Conditional Entropy only:

```python
from clm_core import CompressionQualityGate

gate = CompressionQualityGate()  # no llm_client → heuristic fallback for perplexity

report = gate.analyze(
    original=transcript,
    compressed=compressed,
    structured=structured,
    run_perplexity=False,   # skip perplexity entirely — gets synthetic perfect score
)

# Gate on the two deterministic checks
if report.conditional.passed and report.kolmogorov.passed:
    print("Quality gate passed (offline mode)")
else:
    print(f"Quality gate failed: {report.verdict}")
    exit(1)
```

---

## Next Steps

- **[Kolmogorov Complexity](kolmogorov.md)** — Structural information equivalence (25% weight)
- **[Conditional Entropy](conditional_entropy.md)** — Semantic slot comparison (50% weight)
- **[Quality Gate Index](index.md)** — Unified report, verdict logic, and retention score
