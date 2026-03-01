# Conditional Entropy Analysis

## Overview

`ConditionalEntropyAnalyzer` is the most semantically rigorous of the three quality gate checks and carries a 50% weight in the final retention score. It measures whether the CLM token string preserves the semantic content that the Thread Encoder already extracted.

**Core question:** Did the tokenization step silently drop any of the semantic slots that were already identified?

**Method:** Compare the Thread Encoder's structured extraction dict (the ground truth) against the compressed token string field by field, compute weighted coverage, and estimate the information cost of any lost fields.

---

## Theory

### H(Structured | Compressed)

Conditional entropy `H(X|Y)` measures how much uncertainty about `X` remains once `Y` is known. In this context:

- `X` = the structured extraction dict (Thread Encoder output)
- `Y` = the compressed token string (CLM output)

If `H(X|Y) = 0`, the compressed string fully determines the structured dict — perfect lossless tokenization. If `H(X|Y) > 0`, information was lost during the tokenization step.

Rather than computing true entropy (which requires probability distributions), the analyzer uses an approximation: for each field in the structured dict that is present but not found in the token string, it adds that field's `domain_bits` (the Shannon information content of the field's value domain) to the residual entropy estimate.

```
H(struct | compressed) ≈ Σ domain_bits[field] for each lost non-optional field
```

---

## Field Schema

The analyzer compares against a fixed schema of 18 CLM fields. Each field has a weight (importance to compression quality) and domain bits (information content of the value space).

| Field | Token | Weight | Bits | Notes |
|-------|-------|--------|------|-------|
| `customerIntent` | `CUSTOMER_INTENT` | 1.0 | 5.6 | **Critical** |
| `resolution` | `RESOLUTION` | 1.0 | 4.5 | **Critical** |
| `domain` | `DOMAIN` | 0.9 | 4.0 | **Critical** |
| `state` | `STATE` | 0.9 | 4.5 | **Critical** |
| `sentiment` | `SENTIMENT` | 0.9 | 3.2 | |
| `commitments` | `COMMITMENT` | 0.9 | 5.0 | |
| `channel` | `CHANNEL` | 0.8 | 2.6 | |
| `agentActions` | `AGENT_ACTIONS` | 0.8 | 6.0 | |
| `interactionTrigger` | `INTERACTION_TRIGGER` | 0.8 | 4.5 | |
| `service` | `SERVICE` | 0.7 | 3.5 | |
| `supportTrigger` | `SUPPORT_TRIGGER` | 0.7 | 4.5 | |
| `artifacts` | `ARTIFACTS` | 0.7 | 8.0 | Optional |
| `secondaryIntent` | `SECONDARY_INTENT` | 0.6 | 5.6 | Optional |
| `systemActions` | `SYSTEM_ACTIONS` | 0.6 | 4.0 | |
| `lang` | `LANG` | 0.4 | 2.0 | |
| `context` | `CONTEXT` | 0.5 | 3.0 | |
| `durationSeconds` | `DURATION` | 0.3 | 4.0 | |
| `id` | `ID` | 0.5 | 16.0 | Optional |

**Critical fields:** `customerIntent`, `resolution`, `domain`, `state` — losing any of these forces `high_risk` regardless of other scores.

**Optional fields:** `secondaryIntent`, `artifacts`, `id`, `createdAt` — excluded from residual entropy calculation; their loss is acceptable.

---

## Pass Conditions

A result passes when **all** of these hold:

| Condition | Threshold | Description |
|-----------|-----------|-------------|
| No critical field lost | — | `customerIntent`, `resolution`, `domain`, `state` must all be present |
| `weighted_coverage` | ≥ 0.88 | Importance-weighted slot coverage |
| `raw_coverage` | ≥ 0.85 | Simple slot count coverage |
| `residual_entropy` | ≤ 3.0 bits | Total entropy of lost non-optional fields |

---

## How Matching Works

The analyzer does not require exact string equality. It uses three layers of matching:

**1. Token key presence**

Scans the compressed string for the uppercase token key (e.g. `CUSTOMER_INTENT`). Token format variations like `[CUSTOMER_INTENT=X]`, `[CUSTOMER_INTENT:X]`, or bare `CUSTOMER_INTENT` all match.

**2. Known aliases**

Some fields have short-form aliases used by the encoder:

| Token | Aliases |
|-------|---------|
| `CUSTOMER_INTENT` | `INTENT`, `CUST_INTENT` |
| `AGENT_ACTIONS` | `AGENT_ACTION`, `ACTIONS` |
| `SYSTEM_ACTIONS` | `SYS_ACTIONS`, `SYSTEM_ACTION` |
| `INTERACTION_TRIGGER` | `TRIGGER`, `INT_TRIGGER` |
| `SUPPORT_TRIGGER` | `TRIGGER` |
| `DURATION` | `DUR` |

**3. Value string fallback**

If the token key is not found, the analyzer flattens the field's value (handling strings, lists, and nested dicts) and checks if any value string longer than 3 characters appears verbatim in the compressed output. This catches cases where the field value is embedded directly without its key label.

---

## ConditionalEntropyResult

```python
class ConditionalEntropyResult(BaseModel):
    field_results: list[FieldResult]       # Per-field breakdown
    slots_total: int                        # Non-null fields in structured dict
    slots_matched: int                      # Found in compressed string
    slots_lost: list[str]                   # Field names not found
    slots_null_in_source: list[str]         # Fields that were None/empty — not a loss
    weighted_coverage: float                # Importance-weighted coverage 0–1
    raw_coverage: float                     # Simple count coverage 0–1
    residual_entropy: float                 # Estimated H(struct|compressed) in bits
    bits_per_lost_field: dict[str, float]   # Entropy contribution per lost field
    passed: bool
```

### FieldResult

```python
class FieldResult(BaseModel):
    field: str              # e.g. "customerIntent"
    token_key: str          # e.g. "CUSTOMER_INTENT"
    expected_value: Any     # Value from structured dict
    found_in_compressed: bool
    weight: float           # Importance weight (critical=1.0, optional≈0.3)
    null_in_source: bool    # True if source was None/empty — not counted as a loss
```

---

## Standalone Usage

```python
from clm_core import ConditionalEntropyAnalyzer

analyzer = ConditionalEntropyAnalyzer()

structured = {
    'channel': 'VOICE',
    'domain': 'BILLING',
    'customerIntent': 'REPORT_BILLING_ISSUE',
    'resolution': 'REFUND_INITIATED',
    'state': 'PENDING_REFUND',
    'sentiment': ['NEUTRAL', 'SATISFIED', 'GRATEFUL'],
    'agentActions': ['ACCOUNT_LOOKUP', 'DUPLICATE_PAYMENT_CONFIRMED'],
    'commitments': [{'type': 'REFUND', 'etaDays': 4}],
    'artifacts': [{'key': 'REFUND_REF', 'value': 'RFD-908712'}],
}

compressed = (
    "[INTERACTION:SUPPORT:CHANNEL=VOICE] [DOMAIN:BILLING] "
    "[CUSTOMER_INTENT:REPORT_BILLING_ISSUE] "
    "[AGENT_ACTIONS:ACCOUNT_LOOKUP→DUPLICATE_PAYMENT_CONFIRMED] "
    "[RESOLUTION:REFUND_INITIATED] [STATE:PENDING_REFUND] "
    "[COMMITMENT:REFUND:ETA=4d] [ARTIFACTS:REFUND_REF=RFD-908712] "
    "[SENTIMENT:NEUTRAL→SATISFIED→GRATEFUL]"
)

result = analyzer.analyze(structured, compressed)

print(f"Slots total/matched: {result.slots_total}/{result.slots_matched}")
print(f"Weighted coverage:   {result.weighted_coverage * 100:.1f}%")
print(f"Raw coverage:        {result.raw_coverage * 100:.1f}%")
print(f"Residual entropy:    {result.residual_entropy:.2f} bits")
print(f"Lost fields:         {result.slots_lost}")
print(f"Null fields skipped: {result.slots_null_in_source}")
print(f"Passed:              {result.passed}")
```

**Per-field breakdown:**

```python
print(f"\n{'Field':<22} {'Token':<22} {'Found':<8} {'Weight'}")
print("-" * 60)
for fr in result.field_results:
    if fr.null_in_source:
        status = "NULL"
    elif fr.found_in_compressed:
        status = "✓"
    else:
        status = "✗ LOST"
    print(f"{fr.field:<22} {fr.token_key:<22} {status:<8} {fr.weight}")
```

---

## Handling Null Fields

Fields with `None`, `[]`, `{}`, or `""` in the structured dict are counted as `slots_null_in_source` and excluded from all coverage and entropy calculations. A field that was never extracted cannot be "lost" during tokenization.

Example: if `secondaryIntent` is `None`, the analyzer skips it. This is correct — the Thread Encoder found no secondary intent, so the token string not containing `SECONDARY_INTENT` is expected.

---

## Residual Entropy Calculation

Residual entropy answers: "if these fields were lost, how much information would an LLM be missing?"

```
residual_entropy = Σ domain_bits[field]
                  for each field in slots_lost
                  where field not in OPTIONAL_FIELDS
```

Each field's `domain_bits` is the Shannon information content of its value space:
- A field with 6 possible values carries `log₂(6) ≈ 2.6 bits`
- A field with 50+ possible values carries `log₂(50) ≈ 5.6 bits`

A residual entropy above 3.0 bits means at least one non-trivial field was dropped — for example, losing `customerIntent` (5.6 bits) immediately exceeds the threshold.

---

## Weighted Coverage

Raw coverage counts slots equally. Weighted coverage scales each slot by its importance:

```
weighted_coverage = Σ weight[matched_field] / Σ weight[all_non_null_fields]
```

This means losing `customerIntent` (weight=1.0) has ten times more impact on the score than losing `lang` (weight=0.1, but min weight from above table is 0.3). The weighted threshold (0.88) is therefore harder to satisfy when critical fields are lost.

---

## Next Steps

- **[Kolmogorov Complexity](kolmogorov.md)** — Structural information equivalence (25% weight)
- **[Perplexity](perplexity.md)** — LLM comprehension test (25% weight)
- **[Quality Gate Index](index.md)** — Unified report, verdict logic, and retention score
