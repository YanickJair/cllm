# Thread Encoder

> The Thread Encoder is CLM's compression engine for **conversation-based content** — support calls, chat transcripts, email threads, and any structured two-sided exchange. It acts as the umbrella component for all conversation encoding modes in the SDK.

---

## Overview

Thread Encoder compresses conversation threads into compact semantic token sequences that LLMs can parse just as well as — often better than — the original text, at a fraction of the token cost.

**Typical compression:** 75–80% for customer service transcripts

**Key capabilities:**
- Conversation-level semantic extraction (intent, domain, actions, resolution)
- Ordered system/agent action chains
- Sentiment trajectory tracking
- PII-safe context representation (fact-of-information, not the data itself)
- Commitment and artifact extraction
- Redaction pattern support
- Four languages: EN, PT, ES, FR

---

## Architecture

```
CLMEncoder.encode(input_=transcript, metadata={...})
        │
        ▼
  DataClassifier  ──→  DataTypes.TRANSCRIPT
        │
        ▼
  ThreadEncoder.encode(transcript=..., metadata=...)
        │
        ├──▶  TranscriptAnalyzer.analyze(...)
        │          │
        │          ├── Turn segmentation + spaCy NLP
        │          ├── Domain / service classification
        │          ├── Intent detection (customer utterances)
        │          ├── Agent action extraction
        │          ├── Sentiment trajectory
        │          ├── Promise / commitment detection
        │          ├── Artifact extraction (IDs, amounts, refs)
        │          └── Redacted field detection
        │
        └──▶  Token assembly → ThreadOutput
```

**Core files:**

| File | Purpose |
|------|---------|
| `encoder.py` | Token assembly — converts `TranscriptAnalysis` into CLM v2 tokens |
| `analyzer.py` | NLP pipeline — produces `TranscriptAnalysis` from raw text |
| `_schemas.py` | Pydantic data models (`TranscriptAnalysis`, `ThreadOutput`, etc.) |
| `patterns.py` | `TranscriptPatterns` dataclass — language-specific constants |

---

## Quick Start

```python
from clm_core import CLMConfig, CLMEncoder

transcript = """
Agent: Thank you for calling support. This is Raj. How can I help you?
Customer: Hi, I was charged twice for my subscription this month.
Agent: I'm sorry to hear that. Let me look into your account...
Agent: I can see the duplicate charge. I'm processing a refund now.
         Your reference number is RFD-908712. You'll see it in 3-5 business days.
Customer: Thank you so much!
"""

cfg = CLMConfig(lang="en")
encoder = CLMEncoder(cfg=cfg)

result = encoder.encode(
    input_=transcript,
    metadata={
        "call_id": "CX-0001",
        "channel": "voice",
        "duration": "6m"
    }
)

print(result.compressed)
# [INTERACTION:SUPPORT:CHANNEL=VOICE] [DURATION=3m] [LANG=EN]
# [DOMAIN:BILLING] [SERVICE:SUBSCRIPTION]
# [CUSTOMER_INTENT:REPORT_DUPLICATE_CHARGE]
# [AGENT_ACTIONS:ACCOUNT_VERIFIED→REFUND_INITIATED]
# [RESOLUTION:REFUND_INITIATED] [STATE:PENDING_CUSTOMER]
# [COMMITMENT:REFUND_3-5_BUSINESS_DAYS]
# [ARTIFACT:REFUND_REF=RFD-908712]
# [SENTIMENT:NEUTRAL→GRATEFUL]
```

---

## Encoding Modes

Thread Encoder supports two encoding modes, selected automatically via format detection or set explicitly with the `transcript_format` parameter:

| Mode | Description | Typical Content |
|------|-------------|-----------------|
| **Transcript** | Two-sided conversations with labeled speaker turns | Voice calls, live chat, email support with `Agent:` / `Customer:` prefixes |
| **Free-Form** | Unstructured prose without consistent speaker labels | Emails, Slack threads, SMS, raw case notes |

The encoder detects the format automatically: if at least 50% of non-empty lines carry a recognized speaker prefix the input is treated as `"turns"`, otherwise as `"free_form"`. You can also override detection explicitly:

```python
result = encoder.encode(input_=text, metadata={...}, transcript_format="free_form")
```

- See [Transcript Encoder](transcript_encoder.md) for the labeled-turn format reference.
- See [Free-Form Encoder](free_form_encoder.md) for emails, threads, and unstructured text.

---

## ThreadOutput

`ThreadEncoder.encode()` returns a `ThreadOutput` object (a subclass of `CLMOutput`).

### Compressed String

```python
result.compressed   # "[INTERACTION:SUPPORT:CHANNEL=VOICE] [DOMAIN:BILLING] ..."
result.n_tokens     # Estimated input token count
result.c_tokens     # Estimated compressed token count
result.compression_ratio  # e.g. 88.3 (percent reduction)
```

### Structured Dict — `to_dict()`

`result.to_dict()` parses the compressed token string into a typed Python dictionary. All recognised fields are present; tokens absent from the output have `None` as their value.

```python
result_dict = result.to_dict()
```

**Dict structure:**

```python
{
    # Identifiers (from metadata)
    "id": "CX-0001",
    "createdAt": None,

    # Call metadata
    "channel": "VOICE",         # VOICE | CHAT | EMAIL | SLACK
    "lang": "EN",
    "durationSeconds": 360,     # Converted from [DURATION=6m]

    # Classification
    "domain": "BILLING",
    "service": "SUBSCRIPTION",

    # Intent
    "customerIntent": "REPORT_DUPLICATE_CHARGE",
    "secondaryIntent": None,    # Set when [CUSTOMER_INTENTS:PRIMARY=...;SECONDARY=...]

    # What triggered the contact
    "supportTrigger": None,     # e.g. "FIELD_LOCKED", "MISSING_DELIVERY"

    # Context provided (PII-safe)
    "context": ["EMAIL_PROVIDED"],

    # Actions
    "agentActions": ["ACCOUNT_VERIFIED", "REFUND_INITIATED"],
    "systemActions": None,      # e.g. ["PAYMENT_RETRY_DETECTED"]

    # Outcome
    "resolution": "REFUND_INITIATED",
    "state": "PENDING_CUSTOMER",

    # Commitments with ETA days
    "commitments": [
        {"type": "REFUND", "etaDays": 4}
    ],

    # Artifacts (identifiers, amounts)
    "artifacts": [
        {"key": "REFUND_REF", "value": "RFD-908712"}
    ],

    # Sentiment trajectory
    "sentiment": ["NEUTRAL", "GRATEFUL"]
}
```

**ETA day mapping for commitments:**

| Timeline token | `etaDays` |
|----------------|-----------|
| `3-5_BUSINESS_DAYS` | 4 |
| `1-3_BUSINESS_DAYS` | 2 |
| `WITHIN_24_HOURS` | 1 |
| `WITHIN_48_HOURS` | 2 |
| `TODAY` | 0 |
| `TOMORROW` | 1 |

---

## Configuration

Thread Encoder behaviour is controlled via `ThreadConfig`, passed as `thread_config` inside `CLMConfig`.

```python
from clm_core import CLMConfig
from clm_core.types import ThreadConfig

# Minimal — uses all defaults
cfg = CLMConfig(lang="en")

# With custom ThreadConfig
cfg = CLMConfig(
    lang="en",
    thread_config=ThreadConfig(
        detect_lang=True,
        include_ctx_values=True,
        estimate_thread_duration=True,
        include_summary=True,
        custom_summary_template=None,              # Uses built-in template when None
        redaction_pattern=r"\[.*?REDACTED.*?\]",
    )
)
```

### `ThreadConfig` parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `detect_lang` | `bool` | `True` | Detect the thread language and include it in the compressed output as `[LANG=...]` |
| `include_ctx_values` | `bool` | `False` | Include the actual NER-extracted values in context tokens. When `False`, only the fact of detection is emitted (e.g. `[CONTEXT:EMAIL_PROVIDED]`); when `True`, the value is appended (e.g. `[CONTEXT:EMAIL_PROVIDED:doe@mail.com]`) |
| `estimate_thread_duration` | `bool` | `False` | Estimate thread duration from the conversation content. When `True`, overrides any `duration` value supplied in the metadata |
| `include_summary` | `bool` | `False` | Generate a natural-language summary of the thread from the compressed output. Reduces the need for a separate LLM call for basic summarisation tasks |
| `custom_summary_template` | `str \| None` | `None` | Jinja2 template used for summary generation. When `None`, the built-in template is used (see [Summary Templates](#summary-templates)) |
| `redaction_pattern` | `str` | Built-in pattern | Regex used to detect redacted PII fields in the input text. Defaults to matching `[*REDACTED*]`, `[REDACTED]`, `***`, `<redacted>`, `XXX`, `[PII]` |

`CLMConfig.lang` controls the spaCy model and language dictionary used by the encoder. All other analysis decisions (what to extract, what to drop) are governed by the language dictionary and the internal NLP pipeline.

---

## Redaction Support

When a transcript contains redacted PII (e.g. `[*REDACTED*]`, `***`, `[PHONE_NUMBER]`), Thread Encoder detects the surrounding context and emits `CONTEXT:FIELD_REDACTED` tokens instead of silently dropping the information.

```python
from clm_core.types import ThreadConfig

# Default pattern covers common redaction styles
cfg = CLMConfig(lang="en")
# Matches: [*REDACTED*], [REDACTED], ***, <redacted>, XXX, [PII]

# Custom pattern for your own redaction format
cfg = CLMConfig(
    lang="en",
    thread_config=ThreadConfig(redaction_pattern=r"\[.*?REDACTED.*?\]")
)
```

**Output example:**
```text
[CONTEXT:PHONE_REDACTED]
[CONTEXT:EMAIL_REDACTED]
```

---

## Summary Templates

When `include_summary=True`, CLM generates a natural-language summary from the compressed token output without an additional LLM call. A custom Jinja2 template can be provided via `custom_summary_template`; when omitted, the built-in template is used.

**Available template variables:**

| Variable | Description |
|----------|-------------|
| `DOMAIN` | Classified domain (e.g. `BILLING`, `TECHNICAL`) |
| `CHANNEL` | Interaction channel (e.g. `VOICE`, `CHAT`) |
| `CUSTOMER_INTENT` | Primary customer intent |
| `SERVICE` | Service classification |
| `AGENT_ACTIONS` | List of agent action strings |
| `SYSTEM_ACTIONS` | List of system-detected action strings |
| `RESOLUTION` | Resolution outcome token |
| `STATE` | Resolution state token |
| `COMMITMENT` | Commitment type token (if present) |
| `ARTIFACT` | Artifact key=value string (if present) |
| `SENTIMENT_START` | Opening sentiment label |
| `SENTIMENT_END` | Closing sentiment label |

**Example with a custom template:**

```python
from clm_core.types import ThreadConfig

template = """
Support {{ CHANNEL | lower }} – {{ DOMAIN | lower }}: {{ CUSTOMER_INTENT | lower }}.
Outcome: {{ RESOLUTION | lower }}.
{% if COMMITMENT %}Next step: {{ COMMITMENT | lower }}.{% endif %}
""".strip()

cfg = CLMConfig(
    lang="en",
    thread_config=ThreadConfig(
        include_summary=True,
        custom_summary_template=template,
    )
)
```

---

## Language Support

| Code | Language | spaCy model | Status |
|------|----------|-------------|--------|
| `en` | English | `en_core_web_sm` | Full |
| `pt` | Portuguese | `pt_core_news_sm` | Full |
| `es` | Spanish | `es_core_news_sm` | Full |
| `fr` | French | `fr_core_news_sm` | Full |

Each language ships its own dictionary (`clm_core/dictionary/{lang}/`) with:
- Speaker label detection
- Action vocabulary
- Intent patterns
- Commitment and timeline patterns
- Sentiment keywords

---

## Data Models

All models are exported from `clm_core.components.thread_encoder`:

```python
from clm_core.components.thread_encoder import (
    TranscriptAnalysis,   # Complete analysis result
    ThreadOutput,         # Compressed output (returned by encode)
    CallInfo,             # Call/session metadata
    Turn,                 # Single conversation turn
    Issue,                # Customer issue
    Action,               # Agent action
    Resolution,           # How the conversation resolved
    SentimentTrajectory,  # Sentiment across the call
    ResolutionState,      # Granular resolution state
    RefundReference,      # Billing/refund case details
    PromiseCommitment,    # Agent commitments
    MonetaryAmount,       # Extracted monetary values
    ConversationTimeline, # Timeline of key events
    TimelineEvent,        # Single timeline event
    TemporalPattern,      # Extracted temporal expressions
)
```

### Key model: `TranscriptAnalysis`

Holds the full structured result of the NLP pipeline, accessible via `encoder._ts_encoder.analysis` after a call to `encode()`:

```python
result = encoder.encode(input_=transcript, metadata=metadata)

# Access the raw analysis
analysis = encoder._ts_encoder.analysis

print(analysis.domain)           # "BILLING"
print(analysis.service)          # "SUBSCRIPTION"
print(analysis.customer_intent)  # "REPORT_DUPLICATE_CHARGE"
print(analysis.secondary_intent) # None

for action in analysis.actions:
    print(f"{action.type}: {action.result}")

for promise in analysis.promises:
    print(f"{promise.type} → {promise.timeline} (conf: {promise.confidence})")

if analysis.refund_reference:
    print(analysis.refund_reference.reference_number)
    print(analysis.refund_reference.amount)

print(analysis.resolution_state.type)
print(analysis.resolution_state.customer_satisfaction)
```

---

## Next Steps

- **[Transcript Encoder](transcript_encoder.md)** — Complete reference: token schema, examples, use cases, best practices
- **[Free-Form Encoder](free_form_encoder.md)** — Encoding emails, Slack threads, and unstructured prose
- **[Advanced: Token Hierarchy](../advanced/clm_tokenization.md)** — Token structure deep-dive
- **[Advanced: CLM Dictionary](../advanced/clm_dictionary.md)** — Language-specific vocabularies
- **[CLM Output](../advanced/clm_output.md)** — `CLMOutput` / `ThreadOutput` reference

---
