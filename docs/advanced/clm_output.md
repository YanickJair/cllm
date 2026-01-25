# CLM Output

## Overview

`CLMOutput` is the unified return object for all three CLM encoders. It provides a consistent interface for accessing compressed content, metadata, and compression metrics regardless of which encoder was used.

**Purpose:**
- Standardized output format across all encoders
- Easy access to compressed content
- Automatic compression ratio calculation
- Rich metadata for analysis and debugging

**Returned by:**
- System Prompt Encoder
- Transcript Encoder
- Structured Data Encoder

---

## CLMOutput Structure

```python
from pydantic import BaseModel, computed_field

class CLMOutput(BaseModel):
    original: str | list | dict        # Original input
    component: str                     # Encoder name
    compressed: str                    # Compressed output (whitespace normalized)
    metadata: dict                     # Encoder-specific metadata

    # Computed properties
    n_tokens: int                      # Estimated input token count
    c_tokens: int                      # Estimated compressed token count
    compression_ratio: float           # Token reduction percentage
```

### Key Features

- **Token-based metrics**: `n_tokens` and `c_tokens` estimate token counts (~4 chars/token)
- **Whitespace normalization**: All whitespace in `compressed` is normalized to single spaces
- **Automatic fallback**: If compression would increase size, original is used instead
- **Pydantic model**: Full validation and serialization support

### Fields

#### `original` (str | list | dict)

**Purpose:** The original input provided to the encoder

**Type:** Generic - accepts multiple formats
- `str` - System prompts, text
- `list` - Multiple transcripts, structured data records
- `dict` - Single structured data record

**Examples:**

**System Prompt:**
```python
original = "You are a customer service analyst. Analyze transcripts..."
```

**Transcript:**
```python
original = "Customer: I have a billing issue..."
```

**Structured Data:**
```python
original = [
    {"nba_id": "NBA-001", "action": "Offer Premium", ...},
    {"nba_id": "NBA-002", "action": "Cross-sell", ...}
]
```

---

#### `component` (str)

**Purpose:** Identifies which encoder was used

**Possible values:**
- `"System Prompt"` - System Prompt Encoder
- `"Transcript"` - Transcript Encoder
- `"SD"` - Structured Data Encoder

**Usage:**
```python
result = encoder.encode(content)

if result.component == "System Prompt":
    print("This is a compressed system prompt")
elif result.component == "Transcript":
    print("This is a compressed transcript")
elif result.component == "SD":
    print("This is compressed structured data")
```

---

#### `compressed` (str)

**Purpose:** The compressed output in semantic token format

**Whitespace Normalization:** All whitespace (tabs, newlines, multiple spaces) is automatically collapsed to single spaces and trimmed.

**Format:** Depends on encoder type
- **System Prompt:** Token hierarchy (PROMPT_MODE, ROLE, OUT_JSON, etc.)
- **Transcript:** Domain tokens (CALL, ISSUE, ACTION, etc.)
- **Structured Data:** Header + row format `{fields}[values]`

**Examples:**

**System Prompt:**
```python
compressed = "[REQ:ANALYZE] [TARGET:TRANSCRIPT:DOMAIN=SUPPORT] [EXTRACT:SENTIMENT,URGENCY]"
```

**Transcript:**
```python
compressed = """[CALL:SUPPORT:AGENT=Raj:DURATION=9m:CHANNEL=voice]
[CUSTOMER] [CONTACT:EMAIL=user@example.com]
[ISSUE:BILLING_DISPUTE:SEVERITY=LOW]
[ACTION:REFUND:RESULT=COMPLETED]
[RESOLUTION:RESOLVED:TIMELINE=TODAY]
[SENTIMENT:NEUTRAL→SATISFIED→GRATEFUL]"""
```

**Structured Data:**
```python
compressed = "{id,action,priority}[NBA-001,Offer Premium Upgrade,high][NBA-002,Cross-sell Credit Card,medium]"
```

---

#### `metadata` (dict)

**Purpose:** Encoder-specific information about the compression process

**Content varies by encoder:**

**System Prompt metadata:**
```python
{
    "config": {
        "infer_types": False,
        "add_attrs": False
    },
    "tokens_used": {
        "REQ": ["ANALYZE", "EXTRACT"],
        "TARGET": ["TRANSCRIPT"],
        "EXTRACT": ["SENTIMENT", "URGENCY"]
    },
    "compression_level": "Level 1"
}
```

**Transcript metadata:**
```python
{
    "call_duration": "9m",
    "agent": "Raj",
    "channel": "voice",
    "issue_type": "BILLING_DISPUTE",
    "severity": "LOW",
    "resolution_status": "RESOLVED",
    "sentiment_trajectory": "NEUTRAL→SATISFIED→GRATEFUL"
}
```

**Structured Data metadata:**
```python
{
    "dataset_name": "NBA_CATALOG",
    "record_count": 2,
    "fields": ["NBA_ID", "ACTION", "PRIORITY"],
    "config": {
        "importance_threshold": 0.7,
        "max_field_length": 100
    }
}
```

---

#### `n_tokens` (int) - Computed Property

**Purpose:** Estimated token count for the original input

**Formula:** `max(1, len(original_text) // 4)`

**Note:** Uses ~4 characters per token estimation

---

#### `c_tokens` (int) - Computed Property

**Purpose:** Estimated token count for the compressed output

**Formula:** `max(1, len(compressed) // 4)`

---

#### `compression_ratio` (float) - Computed Property

**Purpose:** Automatic calculation of token reduction percentage

**Formula:** `(1 - c_tokens / n_tokens) * 100`

**Returns:** Float rounded to 1 decimal place (e.g., 73.6%)

**Interpretation:**
- `70.7%` means the compressed version uses 70.7% fewer tokens than the original
- Higher percentage = better compression
- `0.0%` means no compression (or automatic fallback was triggered)
- Typical ranges: 30-90% depending on content and configuration

**Examples:**
```python
result = encoder.encode(content)

print(f"Input tokens: {result.n_tokens}")
print(f"Output tokens: {result.c_tokens}")
print(f"Compression: {result.compression_ratio}%")
# Output: Input tokens: 150
#         Output tokens: 45
#         Compression: 70.0%

if result.compression_ratio >= 70:
    print("Excellent compression")
elif result.compression_ratio >= 50:
    print("Good compression")
else:
    print("Low compression")
```

---

#### Automatic Fallback Behavior

If the compressed output would be **larger** than the original (negative compression), the encoder automatically falls back to the original input:

```python
result = encoder.encode(short_content)

# If compression would increase size:
# - result.compressed == result.original (or JSON string of original)
# - result.compression_ratio == 0.0
# - result.metadata["description"] explains the fallback

if result.metadata.get("description"):
    print(f"Note: {result.metadata['description']}")
    # Output: Note: CL Tokens greater than NL token. Keeping NL input
```

This ensures compression **never** increases token usage.

---

## Complete Examples

### Example 1: System Prompt Encoding

```python
from clm_core import CLMEncoder, CLMConfig, SysPromptConfig

# Create encoder
config = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=False,
        add_attrs=False
    )
)
encoder = CLMEncoder(cfg=config)

# Original system prompt
system_prompt = """You are a customer service quality analyst.

TASK:
Analyze call transcripts and extract key information about sentiment,
urgency level, and any compliance issues.

OUTPUT:
Return the analysis as JSON with sentiment, urgency, and compliance fields.
"""

# Encode
result = encoder.encode(system_prompt)

# Access output
print("Component:", result.component)
# Output: Component: System Prompt

print("Input tokens:", result.n_tokens)
# Output: Input tokens: 71

print("Compressed:")
print(result.compressed)
# Output: [PROMPT_MODE:CONFIGURATION][ROLE:CUSTOMER_SERVICE_QUALITY_ANALYST]
#         [OUT_JSON:{sentiment,urgency,compliance}]

print("Output tokens:", result.c_tokens)
# Output: Output tokens: 25

print("Compression ratio:", result.compression_ratio, "%")
# Output: Compression ratio: 64.8 %

print("Metadata:")
print(result.metadata)
# Output: {'config': {'infer_types': False, 'add_attrs': False}, ...}
```

---

### Example 2: Transcript Encoding

```python
from clm_core import CLMEncoder, CLMConfig

# Create encoder
config = CLMConfig(lang="en")
encoder = CLMEncoder(cfg=config)

# Original transcript
transcript = """Agent Raj: Thank you for calling. How can I help you?

Customer: Hi, I was charged twice for my subscription this month.

Agent Raj: I apologize for that. Let me check your account...

[After checking]

Agent Raj: I see the duplicate charge. I'll process a refund right away. 
Reference number RFD-908712. It will take 3-5 business days.

Customer: Thank you so much!

Agent Raj: You're welcome. Have a great day!
"""

# Encode
result = encoder.encode(transcript)

# Access output
print("Component:", result.component)
# Output: Component: Transcript

print("Original length:", len(result.original))
# Output: Original length: 450

print("Compressed:")
print(result.compressed)
# Output: [CALL:SUPPORT:AGENT=Raj:DURATION=9m:CHANNEL=voice]
#         [CUSTOMER] [CONTACT:EMAIL=...]
#         [ISSUE:BILLING_DISPUTE:SEVERITY=LOW]
#         [ACTION:REFUND:REFERENCE=RFD-908712:TIMELINE=3-5_DAYS:RESULT=COMPLETED]
#         [RESOLUTION:RESOLVED:TIMELINE=TODAY]
#         [SENTIMENT:NEUTRAL→SATISFIED→GRATEFUL]

print("Compressed length:", len(result.compressed))
# Output: Compressed length: 280

print("Compression ratio:", result.compression_ratio, "%")
# Output: Compression ratio: 37.8 %

print("Metadata:")
print(result.metadata)
# Output: {
#     'call_duration': '9m',
#     'agent': 'Raj',
#     'issue_type': 'BILLING_DISPUTE',
#     'resolution_status': 'RESOLVED',
#     ...
# }
```

---

### Example 3: Structured Data Encoding

```python
from clm_core import CLMEncoder, CLMConfig, SDCompressionConfig

# Create encoder
config = CLMConfig(
    lang="en",
    ds_config=SDCompressionConfig(
        dataset_name="NBA",
        required_fields=["nba_id", "action"],
        importance_threshold=0.7
    )
)
encoder = CLMEncoder(cfg=config)

# Original structured data
nba_catalog = [
    {
        "nba_id": "NBA-001",
        "action": "Offer Premium Upgrade",
        "description": "Recommend premium tier",
        "conditions": ["tenure > 12 months"],
        "priority": "high",
        "channel": "phone"
    },
    {
        "nba_id": "NBA-002",
        "action": "Cross-sell Credit Card",
        "description": "Offer co-branded card",
        "conditions": ["good credit score"],
        "priority": "medium",
        "channel": "email"
    }
]

# Encode
result = encoder.encode(nba_catalog)

# Access output
print("Component:", result.component)
# Output: Component: SD

print("Original:", result.original)
# Output: [{'nba_id': 'NBA-001', ...}, {'nba_id': 'NBA-002', ...}]

print("Compressed:")
print(result.compressed)
# Output: {id,action,description,priority,channel}[NBA-001,Offer Premium Upgrade,Recommend premium tier,high,phone][NBA-002,Cross-sell Credit Card,Offer co-branded card,medium,email]

print("Input tokens:", result.n_tokens)
print("Output tokens:", result.c_tokens)
print("Compression ratio:", result.compression_ratio, "%")
# Output: Input tokens: 95
#         Output tokens: 45
#         Compression ratio: 52.6 %

print("Metadata:")
print(result.metadata)
# Output: {
#     'dataset_name': 'NBA_CATALOG',
#     'record_count': 2,
#     'fields': ['NBA_ID', 'ACTION', 'DESCRIPTION', 'CONDITIONS', 'PRIORITY', 'CHANNEL'],
#     ...
# }
```

---

## Using CLMOutput

### Accessing Compressed Content

**Direct access:**
```python
result = encoder.encode(content)
compressed_text = result.compressed

# Use in LLM call
llm.complete(
    system=compressed_text,
    user="Analyze this call"
)
```

**With validation:**
```python
result = encoder.encode(content)

# Check compression quality
if result.compression_ratio < 50:
    print("Warning: Low compression ratio")
    print("Original:", len(result.original))
    print("Compressed:", len(result.compressed))
```

---

### Working with Metadata

**Extract specific information:**
```python
result = encoder.encode(transcript)

# Transcript-specific metadata
if result.component == "Transcript":
    agent = result.metadata.get("agent")
    duration = result.metadata.get("call_duration")
    resolution = result.metadata.get("resolution_status")
    
    print(f"Agent: {agent}")
    print(f"Duration: {duration}")
    print(f"Status: {resolution}")
```

**Configuration tracking:**
```python
result = encoder.encode(system_prompt)

# System prompt-specific metadata
if result.component == "System Prompt":
    config_info = result.metadata.get("config", {})
    infer_types = config_info.get("infer_types")
    add_attrs = config_info.get("add_attrs")
    
    print(f"Type inference: {infer_types}")
    print(f"Attributes: {add_attrs}")
```

---

### Compression Ratio Analysis

**Track compression performance:**
```python
results = []

for content in content_batch:
    result = encoder.encode(content)
    results.append({
        "n_tokens": result.n_tokens,
        "c_tokens": result.c_tokens,
        "ratio": result.compression_ratio,
        "fallback": result.compression_ratio == 0.0
    })

# Calculate average compression
avg_ratio = sum(r["ratio"] for r in results) / len(results)
fallback_count = sum(1 for r in results if r["fallback"])
print(f"Average compression: {avg_ratio:.1f}%")
print(f"Fallbacks triggered: {fallback_count}/{len(results)}")
```

**Quality monitoring:**
```python
result = encoder.encode(content)

# Alert on poor compression
MIN_COMPRESSION = 40.0

if result.compression_ratio < MIN_COMPRESSION:
    print(f"Alert: Compression ratio {result.compression_ratio}% below threshold {MIN_COMPRESSION}%")
    print(f"Content type: {result.component}")
    print(f"Input tokens: {result.n_tokens}")
    print(f"Output tokens: {result.c_tokens}")

    if result.compression_ratio == 0.0:
        print("Note: Fallback to original was triggered")
```

---

### Batch Processing

**Process multiple items:**
```python
def compress_batch(contents: list[str]) -> list[CLMOutput]:
    """Compress multiple items and return results"""
    results = []
    
    for content in contents:
        result = encoder.encode(content)
        results.append(result)
    
    return results

# Process batch
contents = [prompt1, prompt2, prompt3]
results = compress_batch(contents)

# Analyze results
for i, result in enumerate(results, 1):
    print(f"Item {i}:")
    print(f"  Component: {result.component}")
    print(f"  Compression: {result.compression_ratio}%")
    print(f"  Length: {len(result.original)} → {len(result.compressed)}")
```

---

### Logging and Debugging

**Track compression operations:**
```python
import logging

def log_compression(result: CLMOutput):
    """Log compression details for monitoring"""
    logging.info(
        f"Compressed {result.component}: "
        f"{len(result.original)} → {len(result.compressed)} chars "
        f"({result.compression_ratio}% reduction)"
    )
    
    logging.debug(f"Metadata: {result.metadata}")

# Use in production
result = encoder.encode(content)
log_compression(result)
```

**Error handling:**
```python
try:
    result = encoder.encode(content)

    # Validate output
    if not result.compressed:
        raise ValueError("Compression failed - empty output")

    # Check for fallback (compression ratio of 0 means original was used)
    if result.compression_ratio == 0.0 and result.n_tokens > 10:
        logging.warning(f"Compression fallback triggered for {result.component}")
        logging.warning(f"Reason: {result.metadata.get('description', 'Unknown')}")

except Exception as e:
    logging.error(f"Compression error: {e}")
    logging.error(f"Content type: {type(content)}")
    logging.error(f"Content preview: {str(content)[:100]}")
```

---

## Comparison by Component

### Compression Ratios by Type

| Component | Typical Range | Best Case | Configuration Dependent |
|-----------|---------------|-----------|-------------------------|
| **System Prompt** | 65-90% | 90% | ✅ Yes (types, attrs) |
| **Transcript** | 85-92% | 95% | ⚠️ Minimal |
| **Structured Data** | 70-85% | 90% | ✅ Yes (threshold, fields) |

### Metadata by Component

**System Prompt:**
```python
{
    "config": {
        "infer_types": bool,
        "add_attrs": bool
    },
    "tokens_used": {
        "REQ": list,
        "TARGET": list,
        "EXTRACT": list
    },
    "compression_level": str
}
```

**Transcript:**
```python
{
    "call_duration": str,
    "agent": str,
    "channel": str,
    "issue_type": str,
    "severity": str,
    "resolution_status": str,
    "sentiment_trajectory": str,
    "actions_count": int
}
```

**Structured Data:**
```python
{
    "dataset_name": str,
    "record_count": int,
    "fields": list[str],
    "config": {
        "importance_threshold": float,
        "max_field_length": int
    },
    "excluded_fields": list[str]
}
```

---

## Best Practices

### 1. Always Check Component Type

```python
result = encoder.encode(content)

# Handle based on component
if result.component == "System Prompt":
    # Use in system prompt position
    llm.complete(system=result.compressed, user=query)
elif result.component == "Transcript":
    # Use as context
    llm.complete(system="Analyze this call:", user=result.compressed)
elif result.component == "SD":
    # Use as structured context
    llm.complete(system=f"Data: {result.compressed}", user=query)
```

### 2. Validate Compression Quality

```python
result = encoder.encode(content)

# Define quality thresholds
EXCELLENT = 80.0
GOOD = 60.0
ACCEPTABLE = 40.0

if result.compression_ratio >= EXCELLENT:
    status = "excellent"
elif result.compression_ratio >= GOOD:
    status = "good"
elif result.compression_ratio >= ACCEPTABLE:
    status = "acceptable"
else:
    status = "poor"
    logging.warning(f"Low compression ratio: {result.compression_ratio}%")

print(f"Compression quality: {status}")
```

### 3. Store Metadata for Analysis

```python
import json

def save_compression_result(result: CLMOutput, filepath: str):
    """Save compression result for later analysis"""
    data = {
        "original": result.original,
        "component": result.component,
        "compressed": result.compressed,
        "metadata": result.metadata,
        "compression_ratio": result.compression_ratio,
        "original_length": len(result.original),
        "compressed_length": len(result.compressed)
    }
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

# Usage
result = encoder.encode(content)
save_compression_result(result, "compression_log.json")
```

### 4. Use Type Hints

```python
from clm_core import CLMOutput

def process_compression(result: CLMOutput) -> dict:
    """Process compression result with type safety"""
    return {
        "component": result.component,
        "ratio": result.compression_ratio,
        "success": result.compression_ratio >= 60.0,
        "compressed": result.compressed
    }

# Type checker will catch errors
result = encoder.encode(content)
processed = process_compression(result)  # Type-safe
```

---

## Troubleshooting

### Issue: Zero Compression Ratio

**Symptom:** `compression_ratio` is `0.0%`

**Cause:** Automatic fallback was triggered because compression would have increased size

**Explanation:**
As of v0.0.4, CLMOutput automatically falls back to the original input when compression would increase token count. This means you'll never see negative compression ratios.

**Detection:**
```python
result = encoder.encode(content)

if result.compression_ratio == 0.0:
    # Check if fallback was triggered
    if result.metadata.get("description"):
        print(f"Fallback triggered: {result.metadata['description']}")
        # Output: Fallback triggered: CL Tokens greater than NL token. Keeping NL input

    # The compressed field contains the original content
    print(f"Using original: {result.compressed[:50]}...")
```

**Common causes:**
- Very short inputs where token overhead exceeds savings
- Content that doesn't compress well (already optimized)
- Inappropriate encoder for the content type

### Issue: Empty Compressed Output

**Symptom:** `result.compressed` is empty string

**Cause:** Encoding failed or input was invalid

**Solution:**
```python
result = encoder.encode(content)

if not result.compressed:
    print("Error: Compression produced empty output")
    print(f"Component: {result.component}")
    print(f"Original type: {type(result.original)}")
    print(f"Metadata: {result.metadata}")
    
    # Check for error messages in metadata
    if "error" in result.metadata:
        print(f"Error: {result.metadata['error']}")
```

### Issue: Unexpected Component Type

**Symptom:** `component` doesn't match expected encoder

**Cause:** Wrong encoder used or misconfiguration

**Solution:**
```python
# Be explicit about encoder type
from clm_core import CLMEncoder, CLMConfig, SysPromptConfig

# For system prompts
sys_config = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig()
)
sys_encoder = CLMEncoder(cfg=sys_config)

result = sys_encoder.encode(system_prompt)
assert result.component == "System Prompt"
```

---

## Advanced Usage

### Custom Processing Pipeline

```python
from typing import Callable

def compression_pipeline(
    content: str,
    encoder: CLMEncoder,
    validators: list[Callable[[CLMOutput], bool]]
) -> CLMOutput:
    """
    Compress with validation pipeline
    """
    result = encoder.encode(content)
    
    # Run validators
    for validator in validators:
        if not validator(result):
            raise ValueError(f"Validation failed for {result.component}")
    
    return result

# Define validators
def check_min_compression(result: CLMOutput) -> bool:
    return result.compression_ratio >= 50.0

def check_output_not_empty(result: CLMOutput) -> bool:
    return bool(result.compressed)

# Use pipeline
validators = [check_min_compression, check_output_not_empty]
result = compression_pipeline(content, encoder, validators)
```

### A/B Testing Configurations

```python
def compare_configurations(
    content: str,
    configs: list[tuple[str, CLMConfig]]
) -> dict:
    """
    Compare different compression configurations
    """
    results = {}
    
    for name, config in configs:
        encoder = CLMEncoder(cfg=config)
        result = encoder.encode(content)
        
        results[name] = {
            "ratio": result.compression_ratio,
            "length": len(result.compressed),
            "metadata": result.metadata
        }
    
    return results

# Compare configs
configs = [
    ("Level 1", CLMConfig(lang="en", sys_prompt_config=SysPromptConfig(infer_types=False, add_attrs=False))),
    ("Level 4", CLMConfig(lang="en", sys_prompt_config=SysPromptConfig(infer_types=True, add_attrs=True)))
]

comparison = compare_configurations(system_prompt, configs)
for name, data in comparison.items():
    print(f"{name}: {data['ratio']}% compression")
```

---

## Next Steps

- **[System Prompt Encoder](../sys_prompt/index.md)** - Creating system prompt compressions
- **[Transcript Encoder](../transcript_encoder.md)** - Creating transcript compressions
- **[Structured Data Encoder](../sd_encoder.md)** - Creating structured data compressions
- **[CLM Tokenization](clm_tokenization.md)** - Understanding the output format
- **[CLM Configuration](clm_configuration.md)** - Configuring encoders

---