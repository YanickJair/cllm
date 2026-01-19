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
class CLMOutput:
    original: str | list | dict        # Original input
    component: str                     # Encoder name
    compressed: str                    # Compressed output
    metadata: dict                     # Encoder-specific metadata
    compression_ratio: float           # Computed property (%)
```

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

**Format:** Depends on encoder type
- **System Prompt:** Token hierarchy (REQ, TARGET, EXTRACT, etc.)
- **Transcript:** Domain tokens (CALL, ISSUE, ACTION, etc.)
- **Structured Data:** Header + row format

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
compressed = """[NBA_CATALOG:2]{NBA_ID,ACTION,PRIORITY}
[NBA-001,OFFER_PREMIUM_UPGRADE,HIGH]
[NBA-002,CROSS_SELL_CREDIT_CARD,MEDIUM]"""
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

#### `compression_ratio` (float) - Computed Property

**Purpose:** Automatic calculation of compression percentage

**Formula:** `(1 - len(compressed) / len(original)) * 100`

**Returns:** Float rounded to 1 decimal place (e.g., 73.6%)

**Interpretation:**
- `70.7%` means the compressed version is 70.7% smaller than the original
- Higher percentage = better compression
- Typical ranges: 60-95% depending on content and configuration

**Examples:**
```python
result = encoder.encode(content)

print(f"Compression: {result.compression_ratio}%")
# Output: Compression: 73.6%

if result.compression_ratio >= 70:
    print("Excellent compression")
elif result.compression_ratio >= 50:
    print("Good compression")
else:
    print("Low compression")
```

---

## Complete Examples

### Example 1: System Prompt Encoding

```python
from cllm import CLMEncoder, CLMConfig, SysPromptConfig

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

print("Original length:", len(result.original))
# Output: Original length: 285

print("Compressed:")
print(result.compressed)
# Output: [REQ:ANALYZE] [TARGET:TRANSCRIPT] 
#         [EXTRACT:SENTIMENT,URGENCY,COMPLIANCE] [OUT:JSON]

print("Compressed length:", len(result.compressed))
# Output: Compressed length: 83

print("Compression ratio:", result.compression_ratio, "%")
# Output: Compression ratio: 70.9 %

print("Metadata:")
print(result.metadata)
# Output: {'config': {'infer_types': False, 'add_attrs': False}, ...}
```

---

### Example 2: Transcript Encoding

```python
from cllm import CLMEncoder, CLMConfig

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
from cllm import CLMEncoder, CLMConfig, SDCompressionConfig

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
# Output: [NBA_CATALOG:2]{NBA_ID,ACTION,DESCRIPTION,CONDITIONS,PRIORITY,CHANNEL}
#         [NBA-001,OFFER_PREMIUM_UPGRADE,RECOMMEND_PREMIUM_TIER,[TENURE>12M],HIGH,PHONE]
#         [NBA-002,CROSS_SELL_CREDIT_CARD,OFFER_COBRANDED_CARD,[GOOD_CREDIT],MEDIUM,EMAIL]

print("Compression ratio:", result.compression_ratio, "%")
# Output: Compression ratio: 82.3 %

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
        "original_length": len(result.original),
        "compressed_length": len(result.compressed),
        "ratio": result.compression_ratio
    })

# Calculate average compression
avg_ratio = sum(r["ratio"] for r in results) / len(results)
print(f"Average compression: {avg_ratio:.1f}%")
```

**Quality monitoring:**
```python
result = encoder.encode(content)

# Alert on poor compression
MIN_COMPRESSION = 60.0

if result.compression_ratio < MIN_COMPRESSION:
    print(f"Alert: Compression ratio {result.compression_ratio}% below threshold {MIN_COMPRESSION}%")
    print(f"Content type: {result.component}")
    print(f"Original: {len(result.original)} chars")
    print(f"Compressed: {len(result.compressed)} chars")
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
    
    if result.compression_ratio < 0:
        raise ValueError("Compression failed - output larger than input")
    
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
from cllm import CLMOutput

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

### Issue: Negative Compression Ratio

**Symptom:** `compression_ratio` is negative (e.g., -15.0%)

**Cause:** Compressed output is larger than original input

**Solution:**
```python
result = encoder.encode(content)

if result.compression_ratio < 0:
    print("Warning: Compression increased size")
    print(f"Original: {len(result.original)}")
    print(f"Compressed: {len(result.compressed)}")
    
    # This may happen with very short inputs
    # or inappropriate encoder choice
    
    # Use original instead
    use_content = result.original if result.compression_ratio < 0 else result.compressed
```

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
from cllm import CLMEncoder, CLMConfig, SysPromptConfig

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