<p align="center">
  <img width="320" height="190" src="https://raw.githubusercontent.com/YanickJair/cllm/main/docs/img/cllm_logo_mythological.svg" alt="CLM Encoder">
</p>

<h1 align="center">clm-encoder</h1>
<h3 align="center">Rust-Accelerated Structured Data Encoder for LLMs</h3>

<p align="center">
  <a href="https://github.com/YanickJair/cllm/actions"><img src="https://github.com/YanickJar/cllm/workflows/Test%20Suite/badge.svg" alt="Test Suite"></a>
  <a href="https://pypi.org/project/clm-encoder/"><img src="https://img.shields.io/pypi/v/clm-encoder.svg" alt="PyPI"></a>
  <a href="https://github.com/YanickJar/cllm/blob/main/LICENSE-AGPL"><img src="https://img.shields.io/badge/license-AGPL--3.0-blue.svg" alt="License"></a>
</p>

<p align="center"><em>Compress structured data into compact token sequences — 40–85% fewer tokens, no model retraining, no heavy dependencies.</em></p>

---

`sd-encoder` is the standalone Structured Data Encoder from [CLM](https://pypi.org/project/sd-encoder/), compiled in Rust and exposed as a Python extension. It encodes dicts, lists, and nested objects into compact token sequences that LLMs interpret with equal or better accuracy at a fraction of the token cost.

Install it on its own if you only need structured data encoding — no spaCy, no NLP stack, no unnecessary overhead.

| Input | Typical Compression |
|-------|---------------------|
| Product catalogs | 55–85% |
| Knowledge bases | 40–75% |
| Business rules | 50–80% |
| API responses | 45–70% |

---

## Installation

```bash
pip install clm-encoder
```

No additional downloads required. Pre-built wheels are available for Linux (x86_64, aarch64), macOS (Intel, Apple Silicon), and Windows.

---

## Quick Start

```python
from sd_encoder import SDEncoderV2, SDCompressionConfig

config = SDCompressionConfig(preserve_structure=True, auto_detect=True)
encoder = SDEncoderV2(config)

catalog = [
    {"article_id": "KB-001", "title": "Reset Password", "content": "To reset your password...", "tags": ["security"]},
    {"article_id": "KB-002", "title": "Update Billing",  "content": "To update your billing...",  "tags": ["billing"]},
]

result = encoder.encode_validated(catalog)
print(result.compressed)
# {article_id,title,content,tags}[KB-001,Reset Password,To reset your password...,security][KB-002,Update Billing,To update your billing...,billing]

print(f"{result.compression_ratio():.1f}% reduction")
print(f"{result.n_tokens()} → {result.c_tokens()} tokens")
```

---

## Configuration

`SDCompressionConfig` controls field selection, truncation, and structure preservation. All parameters are optional.

```python
from sd_encoder import SDCompressionConfig, FieldImportance

config = SDCompressionConfig(
    # Field selection
    required_fields=["id", "title", "status"],      # always include these
    excluded_fields=["internal_notes", "raw_log"],  # always drop these
    drop_non_required_fields=False,                 # if True, emit only required_fields

    # Importance filtering
    auto_detect=True,                               # infer importance from field name/value
    importance_threshold=FieldImportance.MEDIUM,    # drop fields below this level
    field_importance={                              # explicit overrides
        "summary": FieldImportance.HIGH,
        "version": FieldImportance.LOW,
    },

    # Truncation
    max_truncation_length=300,                      # global string truncation
    max_truncation_mapping={                        # per-field truncation
        "description": 150,
        "content": 500,
    },

    # Structure
    preserve_structure=True,                        # encode nested objects inline
    default_fields_order=["id", "title", "status"], # pin ordering of known fields
)
```

### Field Importance

`FieldImportance` controls the auto-detection threshold. Values are ordered — `NEVER < LOW < MEDIUM < HIGH < CRITICAL`.

```python
from sd_encoder import FieldImportance

FieldImportance.NEVER    # always drop
FieldImportance.LOW      # drop when filtering
FieldImportance.MEDIUM   # include by default
FieldImportance.HIGH     # always include unless explicitly excluded
FieldImportance.CRITICAL # never drop (ids, names, titles)

# Comparable
FieldImportance.HIGH >= FieldImportance.MEDIUM  # True
int(FieldImportance.HIGH)                       # 3
```

Auto-detection applies heuristics to field names and values when `auto_detect=True`:

| Pattern | Detected importance |
|---------|---------------------|
| `id`, `uuid`, `name`, `title` | `CRITICAL` |
| `status`, `priority`, `details` | `HIGH` |
| `description`, `type`, `channel` | `MEDIUM` |
| `source`, `version`, `metadata` | `LOW` |
| `_*`, `*_at`, `*_date` | `NEVER` |
| Empty or very short values | `NEVER` |

---

## Output

`encode_validated` runs compression then strips redundant whitespace and falls back to the original if the compressed output is larger.

```python
result = encoder.encode_validated(data)

result.compressed        # str — the encoded token sequence
result.original          # original input, returned as Python dict/list
result.component         # "ds_compression"
result.n_tokens()        # estimated token count of original
result.c_tokens()        # estimated token count of compressed
result.compression_ratio()  # float — percentage reduction

# Validate manually if needed
result = encoder.encode(data)
result.validate_compression_ratio()  # fall back to original if compressed is larger
result.validate_compressed()         # strip redundant whitespace
```

Use `encode` directly when you want to inspect the output before deciding whether to validate.

---

## Encoding Examples

**Single object:**
```python
encoder.encode_validated({"id": "T-42", "title": "Login fails", "status": "open", "priority": "high"})
# {id,title,status,priority}[T-42,Login fails,open,high]
```

**Nested object:**
```python
encoder.encode_validated({
    "user": {"id": "U-1", "name": "Ana"},
    "ticket": {"id": "T-42", "status": "open"}
})
# {user:{id,name},ticket:{id,status}}[U-1,Ana][T-42,open]
```

**List of dicts (table encoding):**
```python
encoder.encode_validated([
    {"id": 1, "name": "Laptop",  "status": "active"},
    {"id": 2, "name": "Monitor", "status": "active"},
])
# {id,name,status}[1,Laptop,active][2,Monitor,active]
```

**With field filtering:**
```python
config = SDCompressionConfig(
    required_fields=["id", "title"],
    drop_non_required_fields=True,
)
encoder = SDEncoderV2(config)
encoder.encode_validated({"id": 1, "title": "Test", "internal_log": "...", "raw": "..."})
# {id,title}[1,Test]
```

---

## Relationship to CLM

`clm-encoder` is the engine behind the Structured Data encoder in [CLM](https://pypi.org/project/clm-core/). If you need thread or system prompt encoding alongside structured data, install the full library instead:

```bash
pip install clm-core
```

`clm-encoder` is the right choice when:
- You only need structured data encoding
- You want to avoid the spaCy dependency
- You're deploying in a constrained environment
- You're integrating encoding into a Rust or polyglot pipeline

---

## License

Dual-licensed:

- **AGPL-3.0** — free for open source use ([LICENSE-AGPL](LICENSE-AGPL))
- **Commercial** — for proprietary products and SaaS ([contact](mailto:yanick.jair.ta@gmail.com))

---

<p align="center">
  <a href="https://github.com/YanickJair/cllm/issues">Issues</a> ·
  <a href="https://github.com/YanickJair/cllm/discussions">Discussions</a> ·
  <a href="mailto:yanick.jair.ta@gmail.com">Contact</a>
</p>
