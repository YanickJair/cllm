<p align="center">
  <img width="320" height="190" src="https://raw.githubusercontent.com/YanickJair/cllm/main/docs/img/cllm_logo_mythological.svg" alt="CLM">
</p>

<h1 align="center">CLM</h1>
<h3 align="center">Semantic Token Encoding for LLMs</h3>

<p align="center">
  <a href="https://github.com/YanickJar/cllm/actions"><img src="https://github.com/YanickJar/cllm/workflows/Test%20Suite/badge.svg" alt="Test Suite"></a>
  <a href="https://pypi.org/project/clm-core/"><img src="https://img.shields.io/pypi/v/clm-core.svg" alt="PyPI"></a>
  <a href="https://github.com/YanickJar/cllm/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
</p>

<p align="center"><em>Compress transcripts, structured data, and system prompts — 60–95% fewer tokens, no model retraining.</em></p>

---

CLM is an open-source semantic compression library. It encodes verbose content into compact structured token sequences that LLMs interpret with equal or better accuracy, at a fraction of the token cost.

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

If you want the structured-data encoder as part of the same install, add the extra:

```bash
pip install "clm-core[sd_encoder]"
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

### Structured Data Encoder (SDE)

SDE was moved to a standalone sub-library. You can find more about it [here](./crates/sd_encoder/README.md)

```python
catalog = [{"article_id": "KB-001", "title": "Reset Password", "content": "...", "tags": ["security"]}]
result = encoder.encode(catalog)
print(result.compressed)
# {article_id,title,content,tags}[KB-001,Reset Password,To reset your password...,security]
```

### System Prompt Encoder

System prompts are encoded through the same `CLMEncoder` interface used for the other components. CLM usually classifies the prompt for you, but it helps to think of them as either task prompts or configuration prompts.

```python
cfg = CLMConfig(lang="en")
encoder = CLMEncoder(cfg=cfg)

task_prompt = """
You are a customer service quality analyst.
Analyze call transcripts for compliance issues and sentiment problems.
Return the result as JSON.
"""

task_result = encoder.encode(task_prompt)
print(task_result.metadata["prompt_mode"])
print(task_result.compressed)
```

If you need the step-by-step guide, start with [docs/sys_prompt/index.md](docs/sys_prompt/index.md).

Task prompts are usually compressed into a single CL token sequence. Configuration prompts can also be bound after compression:

```python
config_prompt = """
<role>You are a helpful support agent</role>

<custom_rules>
Always greet the customer as {{customer_name}}.
</custom_rules>
"""

result = encoder.encode(config_prompt)
bound_prompt = encoder.bind(result, customer_name="Melissa")

print(result.metadata["prompt_mode"])
print(result.compressed)
print(bound_prompt)
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

## Release

This repository publishes two independent Python packages from one main branch:

| Package | Source | Workflow | PyPI trigger |
|---------|--------|----------|--------------|
| `clm-core` | `clm_core/` | `.github/workflows/publish.yml` | `clm_core-v*` tags |
| `sd_encoder` | `crates/sd_encoder/python/` | `.github/workflows/publish-sd-encoder.yml` | `sd_encoder-v*` tags |

Use package-specific tags instead of release branches.

### Release `clm-core`

1. Update `clm_core/__version__.py`.
2. Commit and push the change to `main`.
3. Create and push a matching tag:

```bash
git tag clm_core-v1.0.9
git push origin clm_core-v1.0.9
```

### Release `sd_encoder`

1. Update the version in `crates/sd_encoder/Cargo.toml`.
2. Commit and push the change to `main`.
3. Create and push a matching tag:

```bash
git tag sd_encoder-v0.1.0
git push origin sd_encoder-v0.1.0
```

Pushes to `main` publish changed packages to TestPyPI. Release tags publish the matching package to PyPI. Both workflows also support manual dispatch with `none`, `testpypi`, or `pypi`.

---
## Star History

<a href="https://www.star-history.com/?repos=YanickJair%cllm&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=YanickJair/cllm&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=YanickJair/cllm&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=YanickJair/cllm&type=date&legend=top-left" />
 </picture>
</a>

---
## License

MIT — see [LICENSE](LICENSE).

---

<p align="center">
  <a href="https://github.com/YanickJar/cllm/issues">Issues</a> ·
  <a href="https://github.com/YanickJar/cllm/discussions">Discussions</a> ·
  <a href="mailto:info@clm-lang.com">Contact</a>
</p>
