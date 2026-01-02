# Structured Data Encoder

## Overview

The Structured Data Encoder is designed to compress structured datasets like NBA (Next Best Action) catalogs, knowledge bases, product configurations, and business rules. Unlike transcript or system prompt compression, this encoder works with **tabular or nested structured data** in JSON/dictionary format.

**Key characteristics:**
- Compresses arrays of structured objects
- Preserves field relationships and hierarchy
- Highly configurable field selection
- Maintains data integrity for downstream processing
- Optimized for catalog and configuration data

**Typical compression:** 70-85% token reduction

---

## What Gets Compressed

Structured data compression targets:

### Primary Use Cases

| Data Type | Examples | Compression |
|-----------|----------|-------------|
| **NBA Catalogs** | Next Best Action recommendations, offers, suggestions | 75-85% |
| **Knowledge Bases** | Help articles, FAQs, documentation entries | 70-80% |
| **Product Catalogs** | SKUs, configurations, specifications | 75-85% |
| **Business Rules** | Validation rules, workflows, decision trees | 70-80% |
| **Configuration Data** | System settings, feature flags, parameters | 80-90% |

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
from cllm import CLMEncoder, CLMConfig, SDCompressionConfig

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
        dataset_name="ARTICLE",
        auto_detect=True,
        required_fields=["article_id", "title"],
        field_importance={"tags": 0.8, "content": 0.9},
        max_field_length=100
    )
)

# Compress
encoder = CLMEncoder(cfg=config)
result = encoder.encode(kb_catalog)
print(result.compressed)
```

**Output:**
```text
[KB_CATALOG:2]{ARTICLE_ID,TITLE,CONTENT,CATEGORY,TAGS,VIEWS,LAST_UPDATED}
[KB-001,HOW_TO_RESET_PASSWORD,TO_RESET_YOUR_PASSWORD_GO_TO_THE_LOGIN_PAGE_AND_CLICK,ACCOUNT,[PASSWORD,SECURITY,ACCOUNT],1523,2024-10-15]
[KB-002,UPDATE_EMAIL_ADDRESS,TO_UPDATE_YOUR_EMAIL_NAVIGATE_TO_SETTINGS,ACCOUNT,[EMAIL,SETTINGS],892,2024-10-12]
```

**Compression:** ~78% token reduction

---

## Configuration Reference

### SDCompressionConfig Parameters

```python
from cllm import SDCompressionConfig

config = SDCompressionConfig(
    dataset_name="CATALOG",              # Dataset identifier
    auto_detect=True,                    # Auto-detect important fields
    required_fields=["id", "name"],      # Always include these
    excluded_fields=["metadata"],        # Never include these
    field_importance={"desc": 0.9},      # Custom importance scores
    importance_threshold=0.5,            # Include fields above this
    max_field_length=200,                # Truncate long text
    preserve_structure=True,             # Keep nested dicts/lists
    simple_fields=["id", "title"],       # Fields to simplify
    default_fields_order=["id", "name"]  # Field ordering priority
)
```

### Core Parameters

#### `dataset_name` (string)
- **Purpose:** Identifies the type of data being compressed
- **Examples:** `"ARTICLE"`, `"NBA"`, `"PRODUCT"`, `"RULE"`
- **Impact:** Used in compressed output header: `[DATASET_NAME:COUNT]`

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

#### `max_field_length` (int, default: `200`)
- **Purpose:** Maximum length for text fields (in characters)
- **Impact:** Long descriptions are truncated
- **Recommendation:** Adjust based on field type (50-500)
- **Note:** Only applies to string fields

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
| `id`, `external_id`, `status` | **CRITICAL** | Always included | Identifiers, state |
| `name`, `title`, `type`, `category`, `tags`, `description`, `priority`, `severity`, `resolution`, `owner`, `channel` | **HIGH** | Usually included | Core attributes |
| `subcategory`, `details`, `assignee`, `department`, `language` | **MEDIUM** | Often included | Secondary info |
| `notes`, `source`, `metadata`, `created_at`, `updated_at`, `version` | **LOW** | Rarely included | Metadata |

**Importance Scale:**
- **CRITICAL**: 1.0 (always included unless explicitly excluded)
- **HIGH**: 0.8 (included with default threshold)
- **MEDIUM**: 0.6 (included with threshold ≤ 0.6)
- **LOW**: 0.3 (excluded with default threshold)

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
    dataset_name="ARTICLE",
    auto_detect=True,
    required_fields=["article_id", "title"],
    field_importance={
        "content": 0.9,      # Very important
        "tags": 0.8,         # Important
        "views": 0.5         # Moderate importance
    },
    importance_threshold=0.5,
    max_field_length=150
)
```

**Result:** Includes ID, title, content (truncated), category, tags, views  
**Compression:** ~75%

---

### Example 2: NBA Catalog (Aggressive)

```python
# Maximum compression for large catalogs
config = SDCompressionConfig(
    dataset_name="NBA",
    auto_detect=True,
    required_fields=["nba_id", "action"],
    excluded_fields=["created_at", "updated_at", "version"],
    importance_threshold=0.7,  # Higher threshold
    max_field_length=100
)
```

**Result:** Only critical and high-importance fields  
**Compression:** ~85%

---

### Example 3: Product Catalog (Conservative)

```python
# Preserve more detail for product specs
config = SDCompressionConfig(
    dataset_name="PRODUCT",
    auto_detect=True,
    required_fields=["sku", "name", "price"],
    field_importance={
        "specifications": 1.0,  # Critical
        "description": 0.9,
        "features": 0.8
    },
    importance_threshold=0.4,  # Lower threshold
    max_field_length=300,      # Longer fields
    preserve_structure=True    # Keep nested specs
)
```

**Result:** Comprehensive product information preserved  
**Compression:** ~70%

---

### Example 4: Business Rules (Minimal)

```python
# Lightweight compression for rules
config = SDCompressionConfig(
    dataset_name="RULE",
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
**Compression:** ~80%

---

## Complete Examples

### Example 1: NBA Catalog

```python
from cllm import CLMEncoder, CLMConfig, SDCompressionConfig

# Next Best Action recommendations
nba_catalog = [
    {
        "nba_id": "NBA-001",
        "action": "Offer Premium Upgrade",
        "description": "Recommend premium tier to qualified customers",
        "conditions": ["tenure > 12 months", "no recent complaints"],
        "priority": "high",
        "channel": "phone",
        "script": "Based on your loyalty, we'd like to offer...",
        "expected_value": 450,
        "created_at": "2024-01-15",
        "updated_at": "2024-10-20"
    },
    {
        "nba_id": "NBA-002",
        "action": "Cross-sell Credit Card",
        "description": "Offer co-branded credit card to active users",
        "conditions": ["good credit score", "active checking"],
        "priority": "medium",
        "channel": "email",
        "script": "Earn rewards on every purchase...",
        "expected_value": 300,
        "created_at": "2024-02-10",
        "updated_at": "2024-10-18"
    }
]

config = CLMConfig(
    lang="en",
    ds_config=SDCompressionConfig(
        dataset_name="NBA",
        required_fields=["nba_id", "action"],
        excluded_fields=["created_at", "updated_at"],
        field_importance={
            "conditions": 0.9,
            "priority": 0.8,
            "expected_value": 0.7,
            "script": 0.6
        },
        importance_threshold=0.6,
        max_field_length=100
    )
)

encoder = CLMEncoder(cfg=config)
result = encoder.encode(nba_catalog)
```

**Output:**
```text
[NBA_CATALOG:2]{NBA_ID,ACTION,DESCRIPTION,CONDITIONS,PRIORITY,CHANNEL,SCRIPT,EXPECTED_VALUE}
[NBA-001,OFFER_PREMIUM_UPGRADE,RECOMMEND_PREMIUM_TIER_TO_QUALIFIED_CUSTOMERS,[TENURE>12M,NO_COMPLAINTS],HIGH,PHONE,BASED_ON_YOUR_LOYALTY_WE_OFFER,450]
[NBA-002,CROSS_SELL_CREDIT_CARD,OFFER_COBRANDED_CARD_TO_ACTIVE_USERS,[GOOD_CREDIT,ACTIVE_CHECKING],MEDIUM,EMAIL,EARN_REWARDS_ON_EVERY_PURCHASE,300]
```

**Compression:** ~82%

---

### Example 2: Product Configuration

```python
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
        dataset_name="PRODUCT",
        required_fields=["sku", "name", "price"],
        field_importance={
            "specifications": 1.0,
            "features": 0.8,
            "stock": 0.7,
            "category": 0.6
        },
        importance_threshold=0.5,
        preserve_structure=True,  # Keep nested specs
        max_field_length=200
    )
)

result = encoder.encode(products)
```

**Output:**
```text
[PRODUCT_CATALOG:1]{SKU,NAME,CATEGORY,PRICE,SPECIFICATIONS,FEATURES,STOCK}
[LAPTOP-001,PROFESSIONAL_LAPTOP_15,ELECTRONICS,1299.99,{PROCESSOR:I7-12700H,RAM:16GB_DDR5,STORAGE:512GB_SSD,DISPLAY:15.6_FHD},[BACKLIT_KB,FINGERPRINT,THUNDERBOLT4],45]
```

**Compression:** ~75%

---

### Example 3: Business Rules

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
        dataset_name="RULE",
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

**Output:**
```text
[RULE_CATALOG:1]{RULE_ID,NAME,CONDITION,ACTION,PRIORITY,ACTIVE}
[RULE-REFUND-001,AUTO_APPROVE_SMALL_REFUNDS,AMOUNT<50_AND_TENURE>6M,APPROVE_REFUND,HIGH,TRUE]
```

**Compression:** ~78%

---

## Output Format

### Structure

Compressed structured data uses a header + rows format:

```
[DATASET_NAME:COUNT]{FIELD1,FIELD2,FIELD3,...}
[value1,value2,value3,...]
[value1,value2,value3,...]
```

**Header:**
- `DATASET_NAME`: From `dataset_name` config parameter
- `COUNT`: Number of records
- `{FIELDS}`: Comma-separated list of included fields

**Rows:**
- One row per record
- Fields in same order as header
- Values compressed (uppercase, underscores, truncated)

### Data Type Handling

| Type | Original | Compressed |
|------|----------|------------|
| String | `"Hello World"` | `HELLO_WORLD` |
| Number | `1299.99` | `1299.99` |
| Boolean | `true` | `TRUE` |
| Array | `["a", "b", "c"]` | `[A,B,C]` |
| Null | `null` | `NULL` |
| Date | `"2024-10-15"` | `2024-10-15` |
| Nested | `{"key": "value"}` | `{KEY:VALUE}` |

---

## Best Practices

### 1. Define Required Fields

Always specify critical identifiers:

```python
config = SDCompressionConfig(
    required_fields=["id", "name"],  # Never compress these out
    # ... other settings
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
    max_field_length=50   # For short fields (titles, names)
    max_field_length=200  # For descriptions
    max_field_length=500  # For detailed content
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
assert "ID" in result.compressed
assert "NAME" in result.compressed

# Check compression ratio
assert result.compression_ratio >= 0.70
```

---

## Use Cases

### 1. NBA Optimization

Compress large recommendation catalogs:

```python
# 1000+ NBA actions
config = SDCompressionConfig(
    dataset_name="NBA",
    required_fields=["nba_id", "action"],
    excluded_fields=["metadata", "timestamps"],
    importance_threshold=0.7,
    max_field_length=100
)

# Daily catalog updates
nba_catalog = load_nba_catalog()
compressed = encoder.encode(nba_catalog)

# Send to LLM for recommendation
llm.complete(
    system=f"NBA Catalog: {compressed.compressed}",
    user="Recommend action for customer..."
)
```

**Benefit:** 85% token reduction on catalog context

---

### 2. Knowledge Base Compression

Optimize help article search:

```python
# Compress articles for semantic search
config = SDCompressionConfig(
    dataset_name="ARTICLE",
    required_fields=["article_id", "title"],
    field_importance={
        "content": 0.9,
        "tags": 0.8,
        "category": 0.7
    },
    max_field_length=150
)

articles = get_kb_articles()
compressed = encoder.encode(articles)

# Faster retrieval with compressed context
relevant_articles = search_compressed(query, compressed.compressed)
```

**Benefit:** 75% token reduction, faster search

---

### 3. Product Catalog for Recommendations

Compress product specs for LLM:

```python
# E-commerce product recommendations
config = SDCompressionConfig(
    dataset_name="PRODUCT",
    required_fields=["sku", "name", "price"],
    field_importance={
        "specifications": 1.0,
        "features": 0.8,
        "stock": 0.6
    },
    preserve_structure=True
)

products = get_available_products()
compressed = encoder.encode(products)

# LLM-powered recommendations
llm.complete(
    system=f"Products: {compressed.compressed}",
    user="Recommend laptop for programming under $1500"
)
```

**Benefit:** Include more products in context window

---

### 4. Configuration Management

Compress system configurations:

```python
# System settings for AI assistant
config = SDCompressionConfig(
    dataset_name="CONFIG",
    required_fields=["key", "value"],
    excluded_fields=["description", "updated_at"],
    importance_threshold=0.8
)

settings = get_system_config()
compressed = encoder.encode(settings)

# Provide to LLM for context
llm.complete(
    system=f"System Config: {compressed.compressed}",
    user="What's the max file upload size?"
)
```

**Benefit:** Compact system context

---

## Performance Optimization

### Batch Processing

```python
# Process large catalogs in chunks
def compress_large_catalog(items, chunk_size=100):
    compressed_chunks = []
    
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        result = encoder.encode(chunk)
        compressed_chunks.append(result.compressed)
    
    return "\n".join(compressed_chunks)

# Usage
large_catalog = load_catalog()  # 10,000 items
compressed = compress_large_catalog(large_catalog)
```

### Caching

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def get_compressed_catalog(catalog_hash: str):
    """Cache compressed catalogs by content hash."""
    catalog = load_catalog_by_hash(catalog_hash)
    return encoder.encode(catalog).compressed

# Usage
catalog_hash = hashlib.md5(
    str(catalog).encode()
).hexdigest()
compressed = get_compressed_catalog(catalog_hash)
```

---

## Troubleshooting

### Issue: Too Much Compression

**Symptom:** Critical fields missing

**Solution:**
```python
# Add to required_fields
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
# Increase threshold
config = SDCompressionConfig(
    importance_threshold=0.7,  # Higher
    # AND/OR exclude more fields
    excluded_fields=["notes", "metadata", "timestamps"],
    # AND/OR reduce field length
    max_field_length=100
)
```

### Issue: Nested Data Lost

**Symptom:** Hierarchical structure flattened

**Solution:**
```python
# Ensure structure preservation
config = SDCompressionConfig(
    preserve_structure=True  # Must be True for nested data
)
```

---

## Next Steps

- **[System Prompt Encoding](sys_prompt_encoder.md)** - Compress agent instructions
- **[Transcript Encoding](transcript_encoder.md)** - Compress conversations
- **[Advanced: Token Hierarchy](advanced/clm_tokenization.md)** - Understanding semantic tokens
- **[Advanced: CLM Dictionary](advanced/clm_dictionary.md)** - Language vocabularies

---

## Support

Questions about structured data compression?

- 📖 **Documentation**: [docs.cllm.io](https://yanickjair.github.io/cllm/)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/YanickJar/cllm/discussions)
- 🐛 **Issues**: [GitHub Issues](https://github.com/YanickJar/cllm/issues)
- 📧 **Email**: support@cllm.io