# Free-Form Encoder

> **Part of Thread Encoder** — Free-Form is one of the encoding modes within the **Thread Encoder** component (`clm_core/components/thread_encoder`). It handles unstructured text that does not follow the canonical `Speaker: text` turn format — emails, SMS messages, Slack threads, raw case notes, and any other prose-style conversation content.

## Overview

Not all conversations arrive as clean two-sided transcripts. The Free-Form Encoder extends Thread Encoder to handle unstructured text by automatically detecting the input format and splitting prose into pseudo-turns before running the standard analysis pipeline.

**Typical inputs:**
- Email threads
- Slack / Teams message threads
- SMS conversations
- Support ticket notes
- Chat logs without consistent speaker labels

**Typical compression:** 70–85% token reduction (varies with prose density)

---

## How It Works

### Format Detection

When `transcript_format="auto"` (the default), the encoder runs `detect_format()` on the raw input before analysis:

```
Raw input
    │
    ▼
detect_format()
    │
    ├──▶ "turns"      → Standard transcript path (Speaker: text lines)
    │
    └──▶ "free_form"  → Free-Form path
              │
              ▼
         split_free_form()
              │
              ▼
         [Turn(speaker="unknown", text=...), ...]
              │
              ▼
         TranscriptAnalyzer.analyze(turns=...)
              │
              ▼
         Token assembly → ThreadOutput
```

**Detection rule:** If at least 50% of non-empty lines carry a recognized speaker prefix (`Agent:`, `Customer:`, or language equivalents), the input is classified as `"turns"`. Otherwise it is classified as `"free_form"`. An empty string is always `"free_form"`.

### Splitting

`split_free_form()` splits unstructured text into chunks that become turns:

1. **Paragraph mode** — blank-line-separated blocks are used as chunk boundaries (preferred)
2. **Line-by-line fallback** — when no blank lines exist (single paragraph), each non-empty line becomes a separate turn

Each chunk is wrapped as `Turn(speaker="unknown", text=chunk)`. The full NLP analysis pipeline then runs on these turns exactly as it does for a labeled transcript.

---

## Quick Start

```python
from clm_core import CLMConfig, CLMEncoder

# Email thread — no speaker labels
email_thread = """
Hi support team,

I noticed my account was charged twice this month — one on the 2nd and another on the 3rd.
Can you please look into this? My account email is melissa.jordan@example.com.

Thanks,
Melissa

---

Hi Melissa,

Thanks for reaching out. I can confirm the duplicate charge — it was caused by a payment
retry that fired after the first transaction already succeeded.

I've initiated a full refund on the second charge. You'll see it within 3–5 business days.
Your reference number is RFD-908712.

Best,
Raj – Support Team
"""

cfg = CLMConfig(lang="en")
encoder = CLMEncoder(cfg=cfg)

result = encoder.encode(
    input_=email_thread,
    metadata={
        "call_id": "EMAIL-0042",
        "channel": "email",
    }
)

print(result.compressed)
```

**Output:**
```text
[INTERACTION:SUPPORT:CHANNEL=EMAIL]
[LANG=EN]
[DOMAIN:BILLING]
[SERVICE:SUBSCRIPTION]
[CUSTOMER_INTENT:REPORT_DUPLICATE_CHARGE]
[CONTEXT:EMAIL_PROVIDED]
[AGENT_ACTIONS:REFUND_INITIATED]
[RESOLUTION:ISSUE_RESOLVED]
[STATE:RESOLVED]
[COMMITMENT:REFUND_3-5_DAYS]
[ARTIFACT:REFUND_REF=RFD-908712]
[SENTIMENT:NEUTRAL→GRATEFUL]
```

---

## The `transcript_format` Parameter

`ThreadEncoder.encode()` (and therefore `CLMEncoder.encode()`) exposes a `transcript_format` parameter:

| Value | Behaviour |
|-------|-----------|
| `"auto"` | **Default.** Heuristic detection — inspects the input and picks `"turns"` or `"free_form"` automatically |
| `"turns"` | Skips detection; treats the input as a labeled `Speaker: text` transcript |
| `"free_form"` | Skips detection; forces the free-form splitting path regardless of content |

```python
# Force free-form mode (e.g. input is known to be an email)
result = encoder.encode(
    input_=email_thread,
    metadata={"channel": "email"},
    transcript_format="free_form",
)

# Force turn mode (e.g. input always has speaker labels)
result = encoder.encode(
    input_=transcript,
    metadata={"channel": "voice"},
    transcript_format="turns",
)
```

The resolved format is recorded in `result.metadata["transcript_format"]`:

```python
print(result.metadata["transcript_format"])  # "free_form" or "turns"
```

---

## Supported Input Shapes

### Email Thread

```python
email = """
Customer email — no consistent speaker labels, prose paragraphs separated by blank lines.

Each paragraph becomes one turn.
"""

result = encoder.encode(input_=email, metadata={"channel": "email"})
```

### Slack / Chat Thread

```python
slack = """
Hey, my export has been stuck for 2 hours — is something broken?

Hi! Sorry to hear that. Can you share the export ID?

Sure — EXP-7712.

Got it. Our jobs queue had a backlog earlier today. I've manually re-queued yours.
It should complete within the next 15 minutes.
"""

result = encoder.encode(input_=slack, metadata={"channel": "chat"})
```

### Raw Case Notes

```python
notes = """
Customer called about a locked account. Says they never changed their password.
Ran identity verification — passed.
Unlocked the account and reset temporary credentials.
Customer confirmed access was restored.
"""

result = encoder.encode(input_=notes, metadata={"channel": "voice"})
```

---

## Output

Free-form inputs produce the same `ThreadOutput` as structured transcripts. All standard tokens apply:

```python
result.compressed          # CLM token string
result.n_tokens            # Estimated original token count
result.c_tokens            # Estimated compressed token count
result.compression_ratio   # Percent reduction
result.to_dict()           # Typed Python dict (same schema as transcript mode)
```

See the [Thread Encoder index](index.md#threadoutput) for the full `to_dict()` schema and field reference.

---

## Differences from Transcript Mode

| Aspect | Transcript (Turns) | Free-Form |
|--------|--------------------|-----------|
| Input format | `Speaker: text` per line | Prose paragraphs or lines |
| Speaker detection | Labeled (`Agent`, `Customer`, …) | All turns attributed to `"unknown"` |
| Turn splitting | Built-in by line | `split_free_form()` (blank-line then line) |
| Analysis pipeline | Full NLP pipeline | Same full NLP pipeline |
| Token output schema | CLM v2 | Same CLM v2 |
| `transcript_format` | `"turns"` | `"free_form"` |

Because all turns are `"unknown"` in free-form mode, the encoder relies more heavily on vocabulary and pattern matching for domain, intent, and action classification rather than speaker-attributed utterance segmentation. Compression ratios are typically slightly lower than for well-labeled transcripts.

---

## Configuration

Free-Form uses the same `CLMConfig` as the rest of Thread Encoder. No additional settings are required.

```python
cfg = CLMConfig(
    lang="en",                        # Language: en, pt, es, fr
    redaction_pattern=r"\[.*?\]"      # Optional: detect redacted PII fields
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lang` | `str` | `"en"` | Language for NLP model and dictionary |
| `redaction_pattern` | `str` | Built-in | Regex to detect redacted PII in the text |

---

## Low-Level API

The two free-form utilities are importable directly from the `free_form` subpackage:

```python
from clm_core.components.thread_encoder.free_form.splitter import (
    detect_format,
    split_free_form,
)
from clm_core.components.thread_encoder.patterns import TranscriptPatterns

patterns = TranscriptPatterns(...)  # or load from dictionary

# Classify raw text
fmt = detect_format(text, patterns)  # "turns" | "free_form"

# Split into turns
turns = split_free_form(text)
# [Turn(speaker="unknown", text="..."), Turn(speaker="unknown", text="..."), ...]
```

---

## Next Steps

- **[Thread Encoder Overview](index.md)** — Architecture, `ThreadOutput` reference, data models
- **[Transcript Encoder](transcript_encoder.md)** — Full reference for labeled two-sided transcripts
- **[Advanced: CLM Dictionary](../advanced/clm_vocabulary.md)** — Language-specific vocabularies
- **[Advanced: Token Hierarchy](../advanced/clm_tokenization.md)** — Token structure deep-dive

---
