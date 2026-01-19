# CLM Configuration

## Overview

The `CLMConfig` object is the central configuration system for CLM compression. It controls language selection, compression behavior, and provides access to language-specific vocabularies and pattern matching rules.

**Key components:**
- Language selection (4 supported languages)
- Structured data compression configuration
- System prompt compression configuration
- Language-specific vocabularies (semantic tokens)
- Language-specific rules (regex patterns)

---

## CLMConfig Object

### Structure

```python
from clm_core import CLMConfig, SDCompressionConfig, SysPromptConfig

config = CLMConfig(
    lang="en",                              # Language selection
    ds_config=SDCompressionConfig(...),    # Structured data config
    sys_prompt_config=SysPromptConfig(...) # System prompt config
)
```

### Parameters

#### `lang` (string, default: `"en"`)

**Supported languages:**

| Code | Language | Status | Vocabulary | Rules |
|------|----------|--------|------------|-------|
| `en` | English | ✅ Full | Complete | Complete |
| `pt` | Portuguese | ✅ Full | Complete | Partial |
| `es` | Spanish | ✅ Full | Complete | Partial |
| `fr` | French | ✅ Full | Complete | Partial |

**Usage:**
```python
# English (full support)
config = CLMConfig(lang="en")

# Portuguese (full support)
config = CLMConfig(lang="pt")

# Spanish (full support)
config = CLMConfig(lang="es")

# French (full support)
config = CLMConfig(lang="fr")
```

**Note:** Languages marked as Beta have limited vocabulary and rule coverage. Production use is recommended only for fully supported languages (en, pt, es, fr).

#### `ds_config` (SDCompressionConfig)

Configuration for structured data compression. See [Structured Data Encoder](../sd_encoder.md) for complete documentation.

**Default behavior:**
```python
# Auto-created with defaults if not provided
config = CLMConfig(lang="en")  # Uses default SDCompressionConfig
```

**Custom configuration:**
```python
from clm_core import SDCompressionConfig, CLMConfig

config = CLMConfig(
    lang="en",
    ds_config=SDCompressionConfig(
        dataset_name="PRODUCT",
        importance_threshold=0.7,
        max_field_length=150
    )
)
```

#### `sys_prompt_config` (SysPromptConfig)

Configuration for system prompt compression. See [System Prompt Encoder](../sys_prompt/index.md) for complete documentation.

**Default behavior:**
```python
# Auto-created with defaults if not provided
config = CLMConfig(lang="en")  # Uses default SysPromptConfig
```

**Custom configuration:**
```python
from clm_core import SysPromptConfig, CLMConfig

config = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=True,
        add_attrs=False,
        use_structured_output_abstraction=True
    )
)
```

### SysPromptConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `infer_types` | bool | `False` | Add type annotations to JSON output fields |
| `add_attrs` | bool | `False` | Include enums, ranges, and constraints in output |
| `use_structured_output_abstraction` | bool | `True` | Compress output format to CL tokens |

**`infer_types`** - When `True`, adds explicit type information to JSON fields:
```
# infer_types=False
[OUT_JSON:{summary,score}]

# infer_types=True
[OUT_JSON:{summary:STR,score:FLOAT}]
```

**`add_attrs`** - When `True`, preserves enums, ranges, and constraints:
```
# add_attrs=False
[OUT_JSON:{score:FLOAT}]

# add_attrs=True
[OUT_JSON:{score:FLOAT}:ENUMS={"ranges":[{"min":0.0,"max":0.49,"label":"FAIL"}]}]
```

**`use_structured_output_abstraction`** - When `True`, compresses output format definitions into CL tokens. When `False`, output format remains in natural language. This is particularly useful for Configuration Prompts where output format should be encoded in CL tokens rather than kept in NL.

---

## Computed Properties

### `vocab` Property

**Purpose:** Provides access to the language-specific vocabulary for semantic token generation.

**Type:** `BaseVocabulary`

**Usage:**
```python
config = CLMConfig(lang="en")

# Access vocabulary
vocab = config.vocab

# Vocabulary contains mappings for:
# - REQ tokens (actions/operations)
# - TARGET tokens (objects/data sources)
# - EXTRACT tokens (fields to extract)
# - CTX tokens (contextual information)
# - OUT tokens (output formats)
# - REF tokens (references/IDs)
```

**Language-specific vocabularies:**
```python
# Each language has its own vocabulary
en_config = CLMConfig(lang="en")
en_vocab = en_config.vocab  # ENVocabulary()

pt_config = CLMConfig(lang="pt")
pt_vocab = pt_config.vocab  # PTVocabulary()

es_config = CLMConfig(lang="es")
es_vocab = es_config.vocab  # ESVocabulary()

fr_config = CLMConfig(lang="fr")
fr_vocab = fr_config.vocab  # FRVocabulary()
```

**Vocabulary mapping structure:**

Each vocabulary defines mappings from natural language to semantic tokens:

```python
# Example vocabulary mappings (conceptual)
{
    # REQ (Request/Action) tokens
    "analyze": "ANALYZE",
    "extract": "EXTRACT",
    "summarize": "SUMMARIZE",
    "diagnose": "DIAGNOSE",
    
    # TARGET tokens
    "transcript": "TRANSCRIPT",
    "document": "DOCUMENT",
    "invoice": "INVOICE",
    
    # EXTRACT tokens
    "sentiment": "SENTIMENT",
    "compliance": "COMPLIANCE",
    "entities": "ENTITIES",
    
    # ... and more
}
```

See [CLM Vocabulary](clm_vocabulary.md) for complete vocabulary documentation.

---

### `rules` Property

**Purpose:** Provides access to language-specific pattern matching rules for intelligent text analysis.

**Type:** `BaseRules`

**Usage:**
```python
config = CLMConfig(lang="en")

# Access rules
rules = config.rules

# Rules contain regex patterns for:
# - Comparison patterns (differences, similarities)
# - Duration patterns (time expressions)
# - Tone/style patterns
# - Explanation patterns
# - And more...
```

**Language-specific rules:**
```python
# Currently, only English has complete rules
en_config = CLMConfig(lang="en")
en_rules = en_config.rules  # ENRules() - Complete

pt_config = CLMConfig(lang="pt")
pt_rules = pt_config.rules  # None (uses fallback)

es_config = CLMConfig(lang="es")
es_rules = es_config.rules  # None (uses fallback)
```

**Rule categories:**

Rules are organized into pattern categories:

1. **COMPARISON_MAP** - Identifying comparison requests
2. **DURATION_PATTERNS** - Extracting time durations
3. **TONE_MAP** - Detecting tone/style requirements
4. **EXPLAIN_PATTERNS** - Recognizing explanation requests
5. **ACTION_PATTERNS** - Identifying action verbs
6. **And more...**

See [Pattern Matching Rules](#pattern-matching-rules) below for details.

---

## Pattern Matching Rules

### Overview

Rules use regular expressions to identify patterns in text and map them to compressed representations. This enables intelligent compression that preserves semantic meaning.

### Rule Structure

Each rule category contains regex patterns mapped to compressed tokens:

```python
class ENRules(BaseRules):
    @property
    def COMPARISON_MAP(self) -> dict[str, str]:
        return {
            r"\bdifferences?\b": "DIFFERENCES",
            r"\bdistinguish\b": "DIFFERENCES",
            r"\bcontrast\b": "DIFFERENCES",
            r"\bsimilarities?\b": "SIMILARITIES",
            r"\bcommon\b": "SIMILARITIES",
            r"\bpros\s*(and|&)?\s*cons\b": "PROS_CONS",
            r"\badvantages\s*(and|&)?\s*disadvantages\b": "PROS_CONS",
            r"\bbenefits\s*(and|&)?\s*drawbacks\b": "PROS_CONS",
            r"\btrade-?offs?\b": "TRADEOFFS",
        }
```

### COMPARISON_MAP

Identifies requests for comparisons and contrasts:

**Pattern examples:**
- "What are the **differences** between X and Y?" → `DIFFERENCES`
- "**Distinguish** between A and B" → `DIFFERENCES`
- "**Contrast** these approaches" → `DIFFERENCES`
- "What are the **similarities**?" → `SIMILARITIES`
- "What do they have in **common**?" → `SIMILARITIES`
- "List the **pros and cons**" → `PROS_CONS`
- "**Advantages and disadvantages**" → `PROS_CONS`
- "What are the **trade-offs**?" → `TRADEOFFS`

**Compression example:**
```
Original: "Compare the differences between approach A and approach B"
Compressed: [REQ:COMPARE] [TARGET:APPROACHES] [EXTRACT:DIFFERENCES]
```

---

### DURATION_PATTERNS

Extracts and normalizes time duration expressions:

**Pattern examples:**
- "**5 minutes**" → `5M`
- "**2 hours**" → `2H`
- "**3 days**" → `3D`
- "**1 week**" → `1W`
- "**6 months**" → `6MO`
- "**2 years**" → `2Y`

**Compression example:**
```
Original: "The call lasted 15 minutes and 30 seconds"
Compressed: [CALL:DURATION=15M30S]
```

**Regex patterns:**
```python
@property
def DURATION_PATTERNS(self) -> dict[str, str]:
    return {
        r"(\d+)\s*minutes?": r"\1M",
        r"(\d+)\s*hours?": r"\1H",
        r"(\d+)\s*days?": r"\1D",
        r"(\d+)\s*weeks?": r"\1W",
        r"(\d+)\s*months?": r"\1MO",
        r"(\d+)\s*years?": r"\1Y",
        r"(\d+)\s*seconds?": r"\1S",
    }
```

---

### TONE_MAP

Identifies tone and style requirements:

**Pattern examples:**
- "Use a **professional** tone" → `TONE_PROFESSIONAL`
- "Be **friendly** and approachable" → `TONE_FRIENDLY`
- "Keep it **formal**" → `TONE_FORMAL`
- "Use **casual** language" → `TONE_CASUAL`
- "Be **empathetic**" → `TONE_EMPATHETIC`
- "Stay **neutral**" → `TONE_NEUTRAL`

**Compression example:**
```
Original: "Respond in a friendly and empathetic tone"
Compressed: [CTX:TONE=FRIENDLY,EMPATHETIC]
```

**Regex patterns:**
```python
@property
def TONE_MAP(self) -> dict[str, str]:
    return {
        r"\bprofessional\b": "PROFESSIONAL",
        r"\bfriendly\b": "FRIENDLY",
        r"\bformal\b": "FORMAL",
        r"\bcasual\b": "CASUAL",
        r"\bempathetic\b": "EMPATHETIC",
        r"\bneutral\b": "NEUTRAL",
        r"\btechnical\b": "TECHNICAL",
        r"\bsimple\b": "SIMPLE",
    }
```

---

### EXPLAIN_PATTERNS

Recognizes explanation and elaboration requests:

**Pattern examples:**
- "**Explain** how this works" → `REQ:EXPLAIN`
- "**Describe** the process" → `REQ:DESCRIBE`
- "**Walk me through** the steps" → `REQ:GUIDE`
- "**Elaborate on** this topic" → `REQ:ELABORATE`
- "**Detail** the requirements" → `REQ:DETAIL`

**Compression example:**
```
Original: "Explain the differences between these two approaches"
Compressed: [REQ:EXPLAIN] [TARGET:APPROACHES] [EXTRACT:DIFFERENCES]
```

---

### ACTION_PATTERNS

Identifies action verbs and operations:

**Pattern examples:**
- "**Analyze** the data" → `REQ:ANALYZE`
- "**Extract** key information" → `REQ:EXTRACT`
- "**Summarize** the findings" → `REQ:SUMMARIZE`
- "**Classify** the issues" → `REQ:CLASSIFY`
- "**Validate** the input" → `REQ:VALIDATE`
- "**Generate** a report" → `REQ:GENERATE`

**Regex patterns:**
```python
@property
def ACTION_PATTERNS(self) -> dict[str, str]:
    return {
        r"\banalyze\b": "ANALYZE",
        r"\bextract\b": "EXTRACT",
        r"\bsummarize\b": "SUMMARIZE",
        r"\bclassify\b": "CLASSIFY",
        r"\bvalidate\b": "VALIDATE",
        r"\bgenerate\b": "GENERATE",
        r"\bdiagnose\b": "DIAGNOSE",
        r"\btroubleshoot\b": "TROUBLESHOOT",
    }
```

---

## Language Support Details

### Full Support Languages (en, pt, es, fr)

**Capabilities:**
✅ Complete vocabulary coverage (all token categories)
✅ Pattern matching rules (English has most comprehensive)
✅ Tested on production data
✅ High compression ratios (70-95%)
✅ High validation accuracy (>90%)

**Recommended for:**
- Production deployments
- Mission-critical applications
- High-volume processing

---

## Configuration Examples

### Example 1: Basic English Configuration

```python
from clm_core import CLMConfig

# Simple English configuration
config = CLMConfig(lang="en")

# Accessing vocabulary and rules
print(config.vocab)  # ENVocabulary()
print(config.rules)  # ENRules()
```

---

### Example 2: Portuguese with Custom Structured Data Config

```python
from clm_core import CLMConfig, SDCompressionConfig

config = CLMConfig(
    lang="pt",
    ds_config=SDCompressionConfig(
        dataset_name="PRODUTO",
        required_fields=["id", "nome"],
        importance_threshold=0.7
    )
)
```

---

### Example 3: Spanish with System Prompt Configuration

```python
from cllm import CLMConfig, SysPromptConfig

config = CLMConfig(
    lang="es",
    sys_prompt_config=SysPromptConfig(
        infer_types=True,
        add_attrs=False
    )
)
```

---

### Example 4: Multi-Language Processing

```python
from cllm import CLMConfig, CLMEncoder

# Process content in different languages
languages = ["en", "pt", "es", "fr"]

results = {}
for lang in languages:
    config = CLMConfig(lang=lang)
    encoder = CLMEncoder(cfg=config)
    
    # Compress content in this language
    result = encoder.encode(content[lang])
    results[lang] = result.compressed
```

---

### Example 5: Full Configuration

```python
from clm_core import CLMConfig, SDCompressionConfig, SysPromptConfig

# Complete configuration with all options
config = CLMConfig(
    lang="en",
    ds_config=SDCompressionConfig(
        dataset_name="CATALOG",
        auto_detect=True,
        required_fields=["id", "name"],
        importance_threshold=0.6,
        max_field_length=150,
        preserve_structure=True
    ),
    sys_prompt_config=SysPromptConfig(
        infer_types=True,
        add_attrs=True
    )
)

# Use configuration
encoder = CLMEncoder(cfg=config)
```

---

## Advanced: Understanding Rule Execution

### Rule Processing Order

1. **Pattern matching** - Regex rules identify patterns
2. **Token generation** - Patterns mapped to semantic tokens
3. **Vocabulary lookup** - Tokens resolved using language vocabulary
4. **Compression** - Final compressed output generated

### Example: Complete Flow

**Input:**
```text
"Analyze the transcript and extract sentiment, comparing differences 
between customer and agent responses over a 15 minute call"
```

**Rule Processing:**

1. **ACTION_PATTERNS** matches "Analyze" → `REQ:ANALYZE`
2. **ACTION_PATTERNS** matches "extract" → `REQ:EXTRACT`
3. **COMPARISON_MAP** matches "differences" → `DIFFERENCES`
4. **DURATION_PATTERNS** matches "15 minute" → `15M`

**Vocabulary Lookup:**
- "transcript" → `TARGET:TRANSCRIPT`
- "sentiment" → `EXTRACT:SENTIMENT`
- "customer and agent" → `SOURCE=CUSTOMER,AGENT`

**Compressed Output:**
```text
[REQ:ANALYZE,EXTRACT] [TARGET:TRANSCRIPT] 
[EXTRACT:SENTIMENT:SOURCE=CUSTOMER,AGENT] 
[EXTRACT:DIFFERENCES] [DURATION=15M]
```

---

## Best Practices

### 1. Use Fully Supported Languages for Production

```python
# Production ✅
config = CLMConfig(lang="en")  # Full support
config = CLMConfig(lang="pt")  # Full support

# Development only ⚠️
config = CLMConfig(lang="de")  # Beta
```

### 2. Configure Based on Use Case

```python
# Transcript compression
config = CLMConfig(
    lang="en"
    # Use default configs - optimized for transcripts
)

# Structured data
config = CLMConfig(
    lang="en",
    ds_config=SDCompressionConfig(
        dataset_name="YOUR_DATA",
        importance_threshold=0.7
    )
)

# System prompts
config = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=True  # If you need type hints
    )
)
```

### 3. Reuse Configuration Objects

```python
# Create once, use many times
config = CLMConfig(lang="en")
encoder = CLMEncoder(cfg=config)

# Reuse for multiple compressions
result1 = encoder.encode(content1)
result2 = encoder.encode(content2)
result3 = encoder.encode(content3)
```

### 4. Test with Representative Data

```python
# Test configuration with real data
config = CLMConfig(lang="en")
encoder = CLMEncoder(cfg=config)

# Validate compression quality
test_data = load_test_set()
for item in test_data:
    result = encoder.encode(item)
    assert result.compression_ratio >= 0.70
    assert validate_output(result.compressed)
```

---

## Extending CLLM (Advanced)

### Adding Custom Rules

While not officially supported, you can understand the pattern for extending rules:

```python
# Example: Custom rule pattern (conceptual)
class CustomENRules(ENRules):
    @property
    def CUSTOM_PATTERNS(self) -> dict[str, str]:
        return {
            r"\bcritical\b": "CRITICAL",
            r"\burgent\b": "URGENT",
            r"\bhigh[-\s]priority\b": "HIGH_PRIORITY",
        }
```

**Note:** This requires deep understanding of CLLM internals and is not recommended for production use without consultation.

---

## Troubleshooting

### Issue: Language Not Fully Supported

**Symptom:** Lower compression ratios or accuracy in non-English languages

**Solution:**
```python
# Check language support status
config = CLMConfig(lang="de")  # Beta language

# If compression quality insufficient:
# 1. Use English if possible
# 2. Wait for language maturity
# 3. Contact support for enterprise language support
```

### Issue: Rules Not Matching

**Symptom:** Patterns not being recognized

**Solution:**
```python
# Ensure language has rule support
config = CLMConfig(lang="en")  # Full rules
print(config.rules)  # Should not be None

# Test specific patterns
text = "analyze the differences"
# Should match both ACTION_PATTERNS and COMPARISON_MAP
```

### Issue: Vocabulary Mismatches

**Symptom:** Unexpected token generation

**Solution:**
```python
# Inspect vocabulary
config = CLMConfig(lang="en")
vocab = config.vocab

# Check available mappings
# (Vocabulary inspection methods depend on implementation)
```

---

## Next Steps

- **[CLM Vocabulary](clm_vocabulary.md)** - Complete vocabulary reference
- **[Token Hierarchy](clm_tokenization.md)** - Understanding semantic tokens
- **[System Prompt Encoder](../sys_prompt/index.md)** - Overview of system prompt compression
  - [Task Prompts](../sys_prompt/task_prompt.md) - Action-oriented instruction compression
  - [Configuration Prompts](../sys_prompt/configuration_prompt.md) - Template-based agent configuration
- **[Transcript Encoder](../transcript_encoder.md)** - Using transcript compression
- **[Structured Data Encoder](../sd_encoder.md)** - Using structured data compression

---
