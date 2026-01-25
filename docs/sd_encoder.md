# Structured Data Encoder

## Overview

The Structured Data Encoder compresses structured datasets like knowledge bases, product catalogs, business rules, and configuration data. Unlike transcript or system prompt compression, this encoder works with **tabular or nested structured data** in JSON/dictionary format.

**Key characteristics:**
- Compresses arrays of structured objects
- Preserves field relationships and hierarchy
- Highly configurable field selection
- Maintains data integrity for downstream processing
- Optimized for catalog and configuration data

**Typical compression:** 40-85% token reduction

---

## What Gets Compressed

Structured data compression targets:

### Primary Use Cases

| Data Type | Examples | Compression |
|-----------|----------|-------------|
| **Knowledge Bases** | Help articles, FAQs, documentation entries | 70-80% |
| **Product Catalogs** | SKUs, configurations, specifications | 75-85% |
| **Business Rules** | Validation rules, workflows, decision trees | 70-80% |
| **Configuration Data** | System settings, feature flags, parameters | 80-90% |
| **Recommendation Catalogs** | Offers, suggestions, actions | 75-85% |

### What Gets Preserved

✅ **Critical fields:** IDs, names, titles, types
✅ **High-importance fields:** Categories, tags, descriptions
✅ **Relationships:** Parent-child, nested structures
✅ **Data types:** Strings, numbers, dates, arrays
✅ **Field order:** Configurable prioritization

### What Gets Optimized

- **Text fields:** Compressed while preserving meaning
- **Long descriptions:** Truncated to configurable length
- **Low-importance fields:** Excluded based on thresholds
- **Redundant information:** Deduplicated across records
- **Metadata:** Optional exclusion of timestamps, versions

---

## Basic Usage

### Simple Example

```python
from clm_core import CLMEncoder, CLMConfig
from clm_core.types import SDCompressionConfig

# Knowledge Base articles
kb_catalog = [
    {
        "article_id": "KB-001",
        "title": "How to Reset Password",
        "content": "To reset your password, go to the login page and click...",
        "category": "Account",
        "tags": ["password", "security", "account"],
        "views": 1523,
        "last_updated": "2024-10-15",
    },
    {
        "article_id": "KB-002",
        "title": "Update Email Address",
        "content": "To update your email, navigate to settings...",
        "category": "Account",
        "tags": ["email", "settings"],
        "views": 892,
        "last_updated": "2024-10-12",
    }
]

# Configure compression
config = CLMConfig(
    lang="en",
    ds_config=SDCompressionConfig(
        auto_detect=True,
        required_fields=["article_id", "title"],
        field_importance={"tags": 0.8, "content": 0.9},
        max_description_length=100
    )
)

# Compress
encoder = CLMEncoder(cfg=config)
result = encoder.encode(kb_catalog)
print(result.compressed)
```

**Output:**
```text
{article_id,title,content,category,tags,views}[KB-001,How to Reset Password,To reset your password go to the login page and click...,Account,password+security+account,1523][KB-002,Update Email Address,To update your email navigate to settings...,Account,email+settings,892]
```

**Compression:** ~50% token reduction

---

## Configuration Reference

### SDCompressionConfig Parameters

```python
from clm_core.types import SDCompressionConfig

config = SDCompressionConfig(
    auto_detect=True,                    # Auto-detect important fields
    required_fields=["id", "name"],      # Always include these
    excluded_fields=["metadata"],        # Never include these
    field_importance={"desc": 0.9},      # Custom importance scores
    importance_threshold=0.5,            # Include fields above this
    max_description_length=200,          # Truncate long text
    preserve_structure=True,             # Keep nested dicts/lists
    simple_fields=["id", "title"],       # Fields for simple formatting
    default_fields_order=["id", "name"]  # Field ordering priority
)
```

### Core Parameters

#### `auto_detect` (boolean, default: `True`)
- **Purpose:** Automatically detect and prioritize important fields
- **When `True`:** Uses default importance scores and heuristics
- **When `False`:** Relies solely on explicit configuration
- **Recommendation:** Keep `True` unless you have very specific requirements

#### `required_fields` (list[str], optional)
- **Purpose:** Fields that must always be included, regardless of importance
- **Examples:** `["id", "article_id", "product_id", "title"]`
- **Priority:** Highest - never excluded
- **Use case:** Ensuring critical identifiers are preserved

#### `excluded_fields` (list[str], optional)
- **Purpose:** Fields that should never be included
- **Examples:** `["metadata", "internal_notes", "debug_info"]`
- **Priority:** Absolute - always excluded
- **Use case:** Removing sensitive or irrelevant data

#### `field_importance` (dict[str, float], optional)
- **Purpose:** Custom importance scores for specific fields (0.0-1.0)
- **Example:** `{"description": 0.9, "tags": 0.8, "notes": 0.3}`
- **Impact:** Overrides default importance scores
- **Range:** 0.0 (lowest) to 1.0 (highest)

#### `importance_threshold` (float, default: `0.5`)
- **Purpose:** Minimum importance score for field inclusion
- **Range:** 0.0-1.0
- **Example:** `0.7` = only include fields with importance ≥ 0.7
- **Trade-off:** Higher threshold = more compression, less detail

#### `max_description_length` (int, default: `200`)
- **Purpose:** Maximum length for text fields (in characters)
- **Impact:** Long descriptions are truncated with `...`
- **Recommendation:** Adjust based on field type (50-500)
- **Note:** Only applies to non-simple string fields

#### `preserve_structure` (boolean, default: `True`)
- **Purpose:** Maintain nested dictionaries and lists
- **When `True`:** Nested data preserved as-is
- **When `False`:** Flattens nested structures
- **Use case:** Keep `True` for complex hierarchical data

---

## Default Field Importance

The encoder has built-in importance scores for common fields:

| Field | Importance | Priority | Typical Use |
|-------|------------|----------|-------------|
| `id`, `uuid`, `external_id`, `status` | **CRITICAL** | Always included | Identifiers, state |
| `name`, `title`, `type`, `category`, `tags`, `description`, `priority`, `severity`, `resolution`, `owner`, `channel` | **HIGH** | Usually included | Core attributes |
| `subcategory`, `details`, `assignee`, `department`, `language` | **MEDIUM** | Often included | Secondary info |
| `notes`, `source`, `metadata`, `created_at`, `updated_at`, `version` | **LOW** | Rarely included | Metadata |

**Importance Scale:**
- **CRITICAL**: 1.0 (always included unless explicitly excluded)
- **HIGH**: 0.8 (included with default threshold)
- **MEDIUM**: 0.5 (included with threshold ≤ 0.5)
- **LOW**: 0.2 (excluded with default threshold)
- **NEVER**: 0.0 (always excluded)

You can override these with the `field_importance` parameter:

```python
config = SDCompressionConfig(
    field_importance={
        "created_at": 0.9,  # Override: LOW → HIGH
        "description": 0.4  # Override: HIGH → MEDIUM
    }
)
```

---

## Configuration Examples

### Example 1: Knowledge Base (Balanced)

```python
# Balanced compression for help articles
config = SDCompressionConfig(
    auto_detect=True,
    required_fields=["article_id", "title"],
    field_importance={
        "content": 0.9,      # Very important
        "tags": 0.8,         # Important
        "views": 0.5         # Moderate importance
    },
    importance_threshold=0.5,
    max_description_length=150
)
```

**Result:** Includes ID, title, content (truncated), category, tags, views
**Compression:** ~50%

---

### Example 2: Product Catalog (Conservative)

```python
# Preserve more detail for product specs
config = SDCompressionConfig(
    auto_detect=True,
    required_fields=["sku", "name", "price"],
    field_importance={
        "specifications": 1.0,  # Critical
        "description": 0.9,
        "features": 0.8
    },
    importance_threshold=0.4,  # Lower threshold
    max_description_length=300,      # Longer fields
    preserve_structure=True    # Keep nested specs
)
```

**Result:** Comprehensive product information preserved
**Compression:** ~45%

---

### Example 3: Business Rules (Minimal)

```python
# Lightweight compression for rules
config = SDCompressionConfig(
    auto_detect=False,  # Explicit control
    required_fields=["rule_id", "condition", "action"],
    excluded_fields=["author", "created_at", "metadata"],
    field_importance={
        "condition": 1.0,
        "action": 1.0,
        "priority": 0.9
    },
    importance_threshold=0.8
)
```

**Result:** Only rule logic, no metadata
**Compression:** ~60%

---

## Complete Examples

### Example 1: Product Catalog

```python
from clm_core import CLMEncoder, CLMConfig
from clm_core.types import SDCompressionConfig

# Product specs with nested data
products = [
    {
        "sku": "LAPTOP-001",
        "name": "Professional Laptop 15",
        "category": "Electronics",
        "price": 1299.99,
        "specifications": {
            "processor": "Intel i7-12700H",
            "ram": "16GB DDR5",
            "storage": "512GB NVMe SSD",
            "display": "15.6\" FHD IPS"
        },
        "features": ["Backlit keyboard", "Fingerprint reader", "Thunderbolt 4"],
        "stock": 45,
        "warehouse": "WH-EAST-01"
    }
]

config = CLMConfig(
    lang="en",
    ds_config=SDCompressionConfig(
        required_fields=["sku", "name", "price"],
        excluded_fields=["warehouse"],
        field_importance={
            "specifications": 1.0,
            "features": 0.8,
            "stock": 0.7,
            "category": 0.6
        },
        importance_threshold=0.5,
        preserve_structure=True,
        max_description_length=200
    )
)

encoder = CLMEncoder(cfg=config)
result = encoder.encode(products)
print(result.compressed)
print(f"Compression ratio: {result.compression_ratio}%")
```

---

### Example 2: Business Rules

```python
# Decision rules for automation
rules = [
    {
        "rule_id": "RULE-REFUND-001",
        "name": "Auto-approve Small Refunds",
        "condition": "amount < 50 AND tenure > 6 months",
        "action": "APPROVE_REFUND",
        "priority": "high",
        "department": "Customer Service",
        "created_by": "admin",
        "created_at": "2024-01-01",
        "active": True
    }
]

config = CLMConfig(
    lang="en",
    ds_config=SDCompressionConfig(
        required_fields=["rule_id", "condition", "action"],
        excluded_fields=["created_by", "created_at"],
        field_importance={
            "priority": 0.9,
            "active": 0.8,
            "name": 0.7
        },
        importance_threshold=0.6
    )
)

result = encoder.encode(rules)
```

---

## Output Format

### Structure

Compressed structured data uses a header + rows format:

```
{field1,field2,field3}[value1,value2,value3][value1,value2,value3]
```

**Header:**
- `{FIELDS}`: Comma-separated list of included fields in order

**Rows:**
- One bracketed row per record
- Fields in same order as header
- Values preserved with minimal transformation

### Data Type Handling

| Type | Original | Compressed |
|------|----------|------------|
| String | `"Hello World"` | `Hello World` |
| Number | `1299.99` | `1299.99` |
| Boolean | `true` | `True` |
| Array | `["a", "b", "c"]` | `a+b+c` |
| Null | `null` | (excluded) |
| Date | `"2024-10-15"` | `2024-10-15` |
| Nested | `{"key": "value"}` | `value` |

---

## CLMOutput Fields

The encoder returns a `CLMOutput` object with:

| Field | Description |
|-------|-------------|
| `compressed` | The compressed string output |
| `original` | The original input data |
| `n_tokens` | Estimated input token count |
| `c_tokens` | Estimated compressed token count |
| `compression_ratio` | Percentage of token reduction |
| `metadata` | Additional compression metadata |

```python
result = encoder.encode(data)
print(f"Input tokens: {result.n_tokens}")
print(f"Output tokens: {result.c_tokens}")
print(f"Compression: {result.compression_ratio}%")
```

---

## Best Practices

### 1. Define Required Fields

Always specify critical identifiers:

```python
config = SDCompressionConfig(
    required_fields=["id", "name"],  # Never compress these out
)
```

### 2. Tune Importance Threshold

Balance compression vs. detail:

```python
# High-volume, cost-sensitive
importance_threshold=0.7  # More compression

# Detail-critical applications
importance_threshold=0.4  # More detail
```

### 3. Set Appropriate Field Lengths

Adjust based on content type:

```python
config = SDCompressionConfig(
    max_description_length=50   # For short fields (titles, names)
    max_description_length=200  # For descriptions
    max_description_length=500  # For detailed content
)
```

### 4. Exclude Unnecessary Metadata

Remove timestamps and internal fields:

```python
config = SDCompressionConfig(
    excluded_fields=[
        "created_at",
        "updated_at",
        "created_by",
        "internal_notes",
        "debug_info"
    ]
)
```

### 5. Test with Representative Data

Validate compression with real examples:

```python
# Test with sample data
sample = catalog[:5]
result = encoder.encode(sample)

# Verify critical fields present
assert "ID" in result.compressed or "id" in result.compressed

# Check compression ratio
assert result.compression_ratio >= 30
```

---

## Troubleshooting

### Issue: Too Much Compression

**Symptom:** Critical fields missing

**Solution:**
```python
config = SDCompressionConfig(
    required_fields=["id", "name", "missing_field"],
    # OR lower threshold
    importance_threshold=0.4
)
```

### Issue: Not Enough Compression

**Symptom:** Compression ratio too low

**Solution:**
```python
config = SDCompressionConfig(
    importance_threshold=0.7,  # Higher
    excluded_fields=["notes", "metadata", "timestamps"],
    max_description_length=100
)
```

### Issue: Nested Data Lost

**Symptom:** Hierarchical structure flattened

**Solution:**
```python
config = SDCompressionConfig(
    preserve_structure=True  # Must be True for nested data
)
```

---

## Next Steps

- **[Transcript Encoding](transcript_encoder.md)** - Compress conversations
- **[System Prompt Encoding](sys_prompt/index.md)** - Compress instructions
- **[Advanced: Token Hierarchy](advanced/clm_tokenization.md)** - Understanding semantic tokens
- **[Advanced: CLM Dictionary](advanced/clm_vocabulary.md)** - Language vocabularies

---

## Support

Questions about structured data compression?

- 📖 **Documentation**: [docs.clm.io](https://yanickjair.github.io/clm/)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/YanickJair/clm/discussions)
- 🐛 **Issues**: [GitHub Issues](https://github.com/YanickJair/clm/issues)
