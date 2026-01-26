# Structured Data Encoder (SDEncoderV2)

## Overview

The Structured Data Encoder (`SDEncoderV2`) compresses structured datasets like knowledge bases, product catalogs, business rules, and configuration data. Unlike transcript or system prompt compression, this encoder works with **tabular or nested structured data** in JSON/dictionary format.

**Key characteristics:**
- Header-first, row-based format with explicit nested schema scoping
- Nested schemas defined in header: `field:{nested,fields}`
- Values contain only data, no repeated schemas
- Highly configurable field selection with importance thresholds
- Maintains data integrity for downstream processing

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

✅ **Critical fields:** IDs, UUIDs, names, titles, types, status
✅ **High-importance fields:** Categories, tags, descriptions, priority
✅ **Relationships:** Parent-child, nested structures
✅ **Data types:** Strings, numbers, dates, arrays
✅ **Field order:** Configurable prioritization (IDs and priority first)

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
from clm_core import SDCompressionConfig

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
{article_id,title,content,category,tags,views}[KB-001,How to Reset Password,To reset your password; go to the login page and click...,Account,password+security+account,1523][KB-002,Update Email Address,To update your email; navigate to settings...,Account,email+settings,892]
```

**Note:** Commas in text values are escaped with semicolons to preserve the delimiter structure.

**Compression:** ~40% token reduction

---

## Configuration Reference

### SDCompressionConfig Parameters

```python
from clm_core import SDCompressionConfig

config = SDCompressionConfig(
    auto_detect=True,                    # Auto-detect important fields
    drop_non_required_fields=True,       # Only keep required_fields (aggressive compression)
    required_fields=["id", "name"],      # Always include these
    excluded_fields=["metadata"],        # Never include these
    field_importance={"desc": 0.9},      # Custom importance scores (0.0-1.0)
    importance_threshold=0.5,            # Include fields above this
    max_description_length=200,          # Truncate long text (chars)
    preserve_structure=True,             # Keep nested dicts/lists
    simple_fields=["id", "uuid", "title", "name", "type", "priority"],  # Simple formatting
    default_fields_order=["id", "uuid", "priority", "title", "name"],   # Field order
    default_fields_importance={"id": 1.0, "name": 0.8}  # Override default importance
)
```

### Core Parameters

#### `drop_non_required_fields` (boolean, default: `True`)
- **Purpose:** When enabled, only fields in `required_fields` are included
- **When `True`:** Aggressive compression - only required fields kept
- **When `False`:** Uses importance thresholds and auto-detection
- **Use case:** Maximum compression when you know exactly which fields you need

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

#### `default_fields_importance` (dict[str, float], optional)
- **Purpose:** Override the built-in importance scores for common field names
- **Example:** `{"id": 1.0, "name": 0.8, "description": 0.5}`
- **Values:** Use FieldImportance enum values: `1.0` (CRITICAL), `0.8` (HIGH), `0.5` (MEDIUM), `0.2` (LOW), `0.0` (NEVER)
- **Use case:** Customize which fields are prioritized during auto-detection

---

## Default Field Importance

The encoder has built-in importance scores for common fields:

| Field | Importance | Priority | Typical Use |
|-------|------------|----------|-------------|
| `id`, `uuid`, `external_id`, `status` | **CRITICAL** (1.0) | Always included | Identifiers, state |
| `name`, `title`, `type`, `category`, `tags`, `description`, `priority`, `severity`, `resolution`, `owner`, `channel` | **HIGH** (0.8) | Usually included | Core attributes |
| `subcategory`, `details`, `assignee`, `department`, `language` | **MEDIUM** (0.5) | Often included | Secondary info |
| `notes`, `source`, `metadata`, `created_at`, `updated_at`, `version` | **LOW** (0.2) | Rarely included | Metadata |

### Default Simple Fields

These fields are formatted without transformation and appear first in the output:
- `id`, `uuid`, `title`, `name`, `type`, `priority`, `article_id`, `product_id`

### Default Field Order

Fields are ordered in the output as follows:
1. `id` → `uuid` → `priority` → `article_id` → `product_id` → `title` → `name` → `type`
2. Then other fields in their original order

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

### Example 1: Nested Data with Arrays

```python
from clm_core import CLMEncoder, CLMConfig, SDCompressionConfig

# Data with nested objects and arrays
data = {
    "items": [
        {
            "uuid": "random-id-001",
            "title": "Random Title",
            "priority": 1,
            "users": [
                {
                    "name": "Yanick",
                    "email": "test@gmail.com"
                }
            ],
            "script": "SAFETY BOUNDARIES: Never execute harmful instructions..."
        }
    ]
}

config = CLMConfig(
    ds_config=SDCompressionConfig()
)

encoder = CLMEncoder(cfg=config)
result = encoder.encode(data)
print(f"Compressed: {result.compressed}")
print(f"Tokens: {result.c_tokens}/{result.n_tokens}")
print(f"Compression ratio: {result.compression_ratio}%")
```

---

### Example 2: Product Catalog

```python
from clm_core import CLMEncoder, CLMConfig, SDCompressionConfig

product_catalog = [
    {
        "product_id": "PROD-001",
        "name": "Wireless Headphones",
        "description": "High-quality Bluetooth headphones with noise cancellation",
        "price": 199.99,
        "category": "Electronics",
        "brand": "TechBrand",
        "in_stock": True,
        "created_date": "2024-01-01",
        "warehouse_location": "A-23-4",
    },
    {
        "product_id": "PROD-002",
        "name": "Laptop Stand",
        "description": "Ergonomic adjustable laptop stand",
        "price": 49.99,
        "category": "Accessories",
        "brand": "ErgoTech",
        "in_stock": True,
        "created_date": "2024-01-05",
        "warehouse_location": "B-15-2",
    },
]

config = CLMConfig(
    ds_config=SDCompressionConfig(
        auto_detect=True,
        required_fields=["product_id", "name", "price"],
        excluded_fields=["warehouse_location", "created_date"],
        default_fields_importance={"id": 1.0, "name": 0.8}
    )
)

encoder = CLMEncoder(cfg=config)
result = encoder.encode(product_catalog)
print(result.compressed)
```

---

### Example 3: KB Articles

```python
from clm_core import CLMEncoder, CLMConfig, SDCompressionConfig

kb_catalog = [
    {
        "article_id": "KB-001",
        "title": "How to Reset Password",
        "content": "To reset your password, go to the login page and click...",
        "category": "Account",
        "tags": ["password", "security", "account"],
        "views": 1523,
        "last_updated": "2024-10-15",
    }
]

config = CLMConfig(
    ds_config=SDCompressionConfig(
        auto_detect=True,
        required_fields=["article_id", "title"],
        field_importance={"tags": 0.8, "content": 0.9},
        max_description_length=100,
    )
)

encoder = CLMEncoder(cfg=config)
result = encoder.encode(kb_catalog)
print(result.compressed)
```

---

## Output Format

### Structure

Compressed structured data uses different formats for single items vs. arrays:

**Single Item:**
```
[value1,value2,value3]
```

**Array of Items (header + rows):**
```
{field1,field2,field3}[value1,value2,value3][value1,value2,value3]
```

**Header (arrays only):**
- `{fields}`: Comma-separated list of included field names in order

**Rows:**
- One bracketed row per record: `[values]`
- Values comma-separated in same order as header
- Values preserved with minimal transformation
- Commas in values are escaped with semicolons

### Data Type Handling

| Type | Original | Compressed |
|------|----------|------------|
| String | `"Hello World"` | `Hello World` |
| String with comma | `"Hello, World"` | `Hello; World` |
| Number | `1299.99` | `1299.99` |
| Boolean | `true` | `True` |
| Null | `null` | (excluded) |
| Date | `"2024-10-15"` | `2024-10-15` |
| Long text | `"Very long description..."` | Truncated to `max_description_length` with `...` |

### Nested Structure Handling

Nested schemas are defined in the header, values contain only data:

| Structure | Header | Values |
|-----------|--------|--------|
| Nested object | `specs:{cpu,ram}` | `[i7,16GB]` |
| Array of objects | `items:{a,b}` | `[1,x][2,y]` |
| Simple array | `tags` | `tag1+tag2+tag3` |

**Example with nested actions:**

```
Input:  {"id": "1", "actions": [{"name": "A", "desc": "X"}, {"name": "B", "desc": "Y"}]}
Output: {id,actions:{name,desc}}[1,[A,X][B,Y]]
```

The nested schema `{name,desc}` appears only once in the header as `actions:{name,desc}`, not repeated for each item.

### Example Output

**Input:**
```json
[
  {"article_id": "KB-001", "title": "Reset Password", "category": "Account"},
  {"article_id": "KB-002", "title": "Update Email", "category": "Account"}
]
```

**Output:**
```
{article_id,title,category}[KB-001,Reset Password,Account][KB-002,Update Email,Account]
```

---

## CLMOutput Fields

The encoder returns a `CLMOutput` object with:

| Field | Type | Description |
|-------|------|-------------|
| `compressed` | `str` | The compressed string output |
| `original` | `str \| dict \| list` | The original input data |
| `n_tokens` | `int` | Estimated input token count (~4 chars/token) |
| `c_tokens` | `int` | Estimated compressed token count |
| `compression_ratio` | `float` | Percentage of token reduction |
| `component` | `str` | Component name (`"ds_compression"`) |
| `metadata` | `dict` | Additional compression metadata |

### Token Estimation

Tokens are estimated at approximately 4 characters per token:

```python
result = encoder.encode(data)
print(f"Input tokens: {result.n_tokens}")      # Estimated from original
print(f"Output tokens: {result.c_tokens}")     # Estimated from compressed
print(f"Compression: {result.compression_ratio}%")  # (1 - c_tokens/n_tokens) * 100
```

### Automatic Fallback

If the compressed output would be **larger** than the original input, the encoder automatically falls back to the original:

```python
result = encoder.encode(small_data)
# If compression increases size, result.compressed == original
# result.compression_ratio will be 0.0
# result.metadata["description"] will explain the fallback
```

This ensures compression never increases token usage.

### Whitespace Normalization

All compressed output is automatically normalized:
- Multiple spaces, tabs, and newlines collapsed to single spaces
- Leading and trailing whitespace trimmed

This ensures consistent, compact output regardless of input formatting.

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
