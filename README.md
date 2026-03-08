<p align="center">
  <img width="320" height="190" src="https://raw.githubusercontent.com/YanickJair/cllm/main/docs/img/cllm_logo_mythological.svg" alt="CLM">
</p>

<h1 align="center">CLM</h1>
<h3 align="center">Semantic Token Encoding for LLMs</h3>

<p align="center">
  <a href="https://github.com/YanickJar/cllm/actions"><img src="https://github.com/YanickJar/cllm/workflows/Test%20Suite/badge.svg" alt="Test Suite"></a>
  <a href="https://pypi.org/project/clm-core/"><img src="https://img.shields.io/pypi/v/clm-core.svg" alt="PyPI"></a>
  <a href="https://github.com/YanickJar/cllm/blob/main/LICENSE-AGPL"><img src="https://img.shields.io/badge/license-AGPL--3.0-blue.svg" alt="License"></a>
</p>

<p align="center"><em>Compress transcripts, structured data, and system prompts — 60–95% fewer tokens, no model retraining.</em></p>

---

CLM is a patent-pending semantic compression library. It encodes verbose content into compact structured token sequences that LLMs interpret with equal or better accuracy, at a fraction of the token cost.

Three targets, one encoder:

| Encoder | Input | Typical Compression |
|---------|-------|---------------------|
| **Thread** | Support calls, chat transcripts, email threads | 62–80%              |
| **Structured Data** | Product catalogs, knowledge bases, business rules | 40–85%              |
| **System Prompt** | Task instructions, role definitions, agent configs | 65–90%              |

---

## Installation

```bash
pip install clm-core
```

Install the spaCy model for your language:

```bash
python -m spacy download en_core_web_sm   # English
python -m spacy download pt_core_news_sm  # Portuguese
python -m spacy download es_core_news_sm  # Spanish
python -m spacy download fr_core_news_sm  # French
```

---

## Usage

All three encoders share the same interface. CLM auto-detects the input type.

```python
from clm_core import CLMConfig, CLMEncoder

cfg = CLMConfig(lang="en")
encoder = CLMEncoder(cfg=cfg)
```

### Thread Encoder — Transcripts

```python
result = encoder.encode(input_=transcript, metadata={"channel": "voice"})
print(result.compressed)
```

```text
[INTERACTION:SUPPORT:CHANNEL=VOICE] [DURATION=6m] [LANG=EN]
[DOMAIN:BILLING] [SERVICE:SUBSCRIPTION]
[CUSTOMER_INTENT:REPORT_DUPLICATE_CHARGE] [CONTEXT:EMAIL_PROVIDED]
[AGENT_ACTIONS:ACCOUNT_VERIFIED→DIAGNOSTIC_PERFORMED→REFUND_INITIATED]
[SYSTEM_ACTIONS:PAYMENT_RETRY_DETECTED]
[RESOLUTION:REFUND_INITIATED] [STATE:PENDING_CUSTOMER]
[COMMITMENT:REFUND_3-5_BUSINESS_DAYS] [ARTIFACT:REFUND_REF=RFD-908712]
[SENTIMENT:NEUTRAL→GRATEFUL]
```

Parse into a structured dict for downstream use:

```python
data = result.to_dict()
# {"channel": "VOICE", "domain": "BILLING", "customerIntent": "REPORT_DUPLICATE_CHARGE",
#  "state": "PENDING_CUSTOMER", "agentActions": [...], "commitments": [...], ...}
```

### Structured Data Encoder

```python
catalog = [{"article_id": "KB-001", "title": "Reset Password", "content": "...", "tags": ["security"]}]
result = encoder.encode(catalog)
print(result.compressed)
# {article_id,title,content,tags}[KB-001,Reset Password,To reset your password...,security]
```

### System Prompt Encoder

```python
result = encoder.encode(system_prompt)
print(result.compressed)
# [REQ:ANALYZE] [TARGET:TRANSCRIPT:DOMAIN=QA]
# [EXTRACT:COMPLIANCE,DISCLOSURES,SOFT_SKILLS,SENTIMENT]
# [OUT_JSON:{summary,qa_scores,violations,recommendations}]
```

---

## Performance

Based on a dataset test across 5,000+ samples:

### Thread Encoder

| Metric | Value |
|--------|-------|
| Token reduction | 72–80% |
| Latency improvement | Up to 56% |
| Semantic preservation | Validated via Shannon Entropy |
| Languages | EN, PT, ES, FR |
| Schema version | v2.0 |
| Language detection | `detect_lang` (default: on) |
| Context values | `include_ctx_values` — emit raw NER values alongside context tokens |
| Duration estimation | `estimate_thread_duration` — infer duration from content |
| Built-in summary | `include_summary` + optional `custom_summary_template` (Jinja2) |
| Custom redaction | `redaction_pattern` — regex for PII placeholder detection |

### Structured Data Encoder

| Metric | Value |
|--------|-------|
| Token reduction | 40–85% |
| Supports | Single objects, arrays, nested structures |
| Field filtering | Importance threshold + required/excluded |
| Per-field truncation | Configurable |

### System Prompt Encoder

| Metric | Value |
|--------|-------|
| Token reduction | 65–90% |
| Output | Hierarchical CLM token vocabulary |
| Type inference | Optional (`infer_types=True`) |
| Attribute preservation | Optional (`add_attrs=True`) |

---

## Documentation

**Official documentation:** [https://yanickjair.github.io/cllm](https://yanickjair.github.io/cllm)

| Topic | Link |
|-------|------|
| Getting started | [docs/index.md](docs/index.md) |
| Thread Encoder | [docs/thread_encoder/index.md](docs/thread_encoder/index.md) |
| Transcript encoding | [docs/thread_encoder/transcript_encoder.md](docs/thread_encoder/transcript_encoder.md) |
| Free-Form Encoder | [docs/thread_encoder/free_form_encoder.md](docs/thread_encoder/free_form_encoder.md) |
| Structured Data Encoder | [docs/sd_encoder.md](docs/sd_encoder.md) |
| System Prompt Encoder | [docs/sys_prompt/index.md](docs/sys_prompt/index.md) |
| CLM Configuration | [docs/advanced/clm_configuration.md](docs/advanced/clm_configuration.md) |
| Token hierarchy | [docs/advanced/clm_tokenization.md](docs/advanced/clm_tokenization.md) |
| Output reference | [docs/advanced/clm_output.md](docs/advanced/clm_output.md) |

---

## License

Dual-licensed:

- **AGPL-3.0** — free for open source use ([LICENSE-AGPL](LICENSE-AGPL))
- **Commercial** — for proprietary products and SaaS ([contact](mailto:yanick.jair.ta@gmail.com))

---

<p align="center">
  <a href="https://github.com/YanickJar/cllm/issues">Issues</a> ·
  <a href="https://github.com/YanickJar/cllm/discussions">Discussions</a> ·
  <a href="mailto:yanick.jair.ta@gmail.com">Contact</a>
</p>
