# Task Prompt Encoding

## Overview

Task prompts are **action-oriented system instructions** that tell the model what to do for a specific task. They are the most common type of system prompt, used for data extraction, analysis, generation, and transformation tasks.

**Typical compression:** 65-85% token reduction

---

## Anatomy of a Task Prompt

Effective task prompts typically contain three core elements:

### 1. Identity (Who)
Defines the agent's role and persona:
```
"You are a customer service quality analyst"
"You are a technical support specialist"
"You are a sports betting analysis agent"
```

### 2. Task (What)
Specifies what the agent should do:
```
"Analyze call transcripts for compliance violations"
"Troubleshoot network connectivity issues"
"Analyze team performance and provide betting odds"
```

### 3. Output (How)
Defines the expected response format:
```
"Return as JSON: {compliance_score, violations, recommendations}"
"Provide step-by-step troubleshooting guide"
"Output: {win: 0.0-1.0, draw: 0.0-1.0, lose: 0.0-1.0}"
```

Additional elements often include:
- **Context**: Domain knowledge, constraints, policies
- **Examples**: Sample inputs and expected outputs
- **Guidelines**: Tone, style, ethical boundaries

---

## Example: Task Prompt Structure

### Detailed Task Prompt

```text
You are a Betting Analysis agent. Your task is to analyze soccer matches by
evaluating each team's performance throughout the season and provide accurate
betting odds.

ANALYSIS CRITERIA:
- Review recent match results (last 10 games)
- Analyze home vs. away performance
- Consider head-to-head history
- Factor in injuries and suspensions
- Evaluate current league position
- Assess offensive and defensive statistics

EXAMPLE:
Analyze Chelsea FC's season performance by reviewing statistics from each game.
Based on win rate, goals scored/conceded, clean sheets, and recent form,
calculate the probability of win, draw, or loss for their next match.

OUTPUT FORMAT:
Return your analysis as a dictionary object with odds as decimal probabilities:
{
    "win": 0.45,
    "draw": 0.30,
    "lose": 0.25
}

Note: Odds must sum to 1.0. Consider all factors before providing final odds.
```

**Token count:** ~180 tokens

### Compressed Task Prompt

```text
[REQ:PREDICT:SPECS:BETTING_ODDS]
[TARGET:REPORT:DOMAIN=BUSINESS:TOPIC=BETTING_ANALYSIS_AGENT]
[EXTRACT:PERFORMANCE,ACCURACY:DOMAIN=QA]
[OUT_JSON:{win:FLOAT,draw:FLOAT,lose:FLOAT}]
```

**Token count:** ~45 tokens
**Compression:** 82.0% reduction

---

## CLM Compression Strategy

**CLM semantic encoding**:
- Models understand compressed tokens natively
- No decompression needed
- Semantic meaning preserved
- Structured, predictable format

### How CLM Compresses Task Prompts

1. **Intent Detection**: Identifies primary action (analyze, extract, generate)
2. **Role Extraction**: Captures agent identity and domain
3. **Task Decomposition**: Breaks down instructions into atomic operations
4. **Constraint Mapping**: Identifies rules and boundaries
5. **Output Structure**: Preserves expected format
6. **Token Generation**: Creates hierarchical semantic tokens

---

## Configuration

### Basic Configuration

```python
from clm_core import CLMConfig, CLMEncoder, SysPromptConfig

# Minimal setup (Level 1: Maximum compression)
cfg = CLMConfig(lang="en")  # Uses default: infer_types=False, add_attrs=False
encoder = CLMEncoder(cfg=cfg)

system_prompt = """
You are a customer service quality analyst. Analyze call transcripts
for compliance violations and sentiment issues in agent responses.
"""

result = encoder.encode(system_prompt)
print(result.compressed)
# Output: [REQ:ANALYZE] [TARGET:TICKET:DOMAIN=SUPPORT] [EXTRACT:COMPLIANCE,SENTIMENT,ISSUE:DOMAIN=LEGAL] [OUT_JSON:STR]

print(f"Compression: {result.compression_ratio:.1%}")
# Output: Compression: 25.3%
```

### Configuration Options

Task prompt compression is controlled through `SysPromptConfig` with two key parameters:

```python
from clm_core import CLMConfig, SysPromptConfig

cfg = CLMConfig(
    lang="en",                          # Language: en, pt, es, fr
    sys_prompt_config=SysPromptConfig(
        infer_types=False,              # Add type annotations to JSON fields
        add_attrs=False                 # Include additional attributes (enums, ranges)
    )
)
```

### Configuration Parameters

**`infer_types` (boolean)**
- When `True`: Adds type information to JSON output structures
- Example: `{summary:STR, score:FLOAT, items:[STR]}`
- Impact: Reduces compression by ~5% but provides explicit typing
- Use when: LLM needs clear type hints for structured output

**`add_attrs` (boolean)**
- When `True`: Preserves additional attributes like enums, ranges, and categories
- Example: `ENUMS={"ranges": [{"min": 0.0, "max": 0.49, "label": "FAIL"}]}`
- Impact: Reduces compression significantly (~40%) but preserves full semantic detail
- Use when: Complex constraints and validation rules are critical

### Compression Levels

You can combine these parameters to achieve different compression ratios:

**Level 1: Maximum Compression (70-75% reduction)**
```python
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=False,
        add_attrs=False
    )
)
```
- Minimal semantic detail in output
- Best for: Simple, repetitive instructions
- Trade-off: Less explicit structure

**Level 2: Type-Annotated (65-70% reduction)**
```python
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=True,   # Type annotations added
        add_attrs=False
    )
)
```
- Adds explicit type information to JSON fields
- Best for: When LLM needs type hints
- Trade-off: Slightly larger but clearer structure

**Level 3: Attribute-Rich (30-35% reduction)**
```python
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=False,
        add_attrs=True      # Enums and constraints added
    )
)
```
- Preserves enums, ranges, and categorical values
- Best for: Complex validation requirements
- Trade-off: Lower compression but full semantic preservation

**Level 4: Full Annotation (25-30% reduction)**
```python
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=True,   # Types
        add_attrs=True      # Attributes
    )
)
```
- Maximum semantic detail preservation
- Best for: Critical systems requiring full specification
- Trade-off: Lowest compression but complete information

---

## Choosing the Right Configuration

The configuration choice depends on your specific requirements:

### When to Use Level 1 (Default: No Types, No Attrs)

**Compression:** 70-75%

**Best for:**
- High-volume contact center operations
- Cost-sensitive deployments
- Simple, repetitive tasks
- When output structure is well-understood by the LLM

**Example use case:**
```python
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(infer_types=False, add_attrs=False)
)
```

### When to Use Level 2 (Types Only)

**Compression:** 65-70%

**Best for:**
- Structured JSON output generation
- Type-sensitive downstream processing
- When LLM needs explicit type hints
- APIs expecting strongly-typed responses

**Example use case:**
```python
# JSON API - need explicit types for validation
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(infer_types=True, add_attrs=False)
)
```

### When to Use Level 3 (Attributes Only)

**Compression:** 30-35%

**Best for:**
- Complex business rules with enums
- Validation-heavy applications
- Compliance-critical systems
- When ranges and categorical values matter

**Example use case:**
```python
# QA scoring with strict ranges and categories
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(infer_types=False, add_attrs=True)
)
```

### When to Use Level 4 (Full Annotation)

**Compression:** 25-30%

**Best for:**
- Mission-critical applications
- Complex regulatory requirements
- Systems requiring audit trails
- When every semantic detail matters

**Example use case:**
```python
# Healthcare compliance - maximum preservation
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(infer_types=True, add_attrs=True)
)
```

### Configuration Decision Tree

```
Do you need maximum cost savings?
+- YES -> Level 1 (Default)
+- NO -> Continue...

Does your LLM struggle with JSON types?
+- YES -> Add infer_types=True
+- NO -> Continue...

Do you have complex enums/ranges/categories?
+- YES -> Add add_attrs=True
+- NO -> Use Level 1

Are both type hints AND attributes critical?
+- YES -> Level 4 (Both True)
```

---

## Examples

### Example 1: Customer Service QA

**Original System Prompt:**
```text
You are a Call QA & Compliance Scoring System for customer service operations.

TASK:
Analyze the transcript and score the agent's compliance across required QA categories.

ANALYSIS CRITERIA:
- Mandatory disclosures and verification steps
- Policy adherence
- Soft-skill behaviors (empathy, clarity, ownership)
- Process accuracy
- Compliance violations or risks
- Customer sentiment trajectory

OUTPUT FORMAT:
{
    "summary": "short_summary",
    "qa_scores": {
        "verification": 0.0,
        "policy_adherence": 0.0,
        "soft_skills": 0.0,
        "accuracy": 0.0,
        "compliance": 0.0
    },
    "violations": ["list_any_detected"],
    "recommendations": ["improvement_suggestions"]
}

SCORING:
0.00-0.49: Fail
0.50-0.74: Needs Improvement
0.75-0.89: Good
0.90-1.00: Excellent
```

**Original tokens:** 285 tokens

---

#### Level 1: Maximum Compression (70.7% reduction)

```python
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=False,
        add_attrs=False
    )
)
```

**Compressed:**
```text
[REQ:GENERATE:SPECS:SUMMARY] [TARGET:TRANSCRIPT:DOMAIN=QA]
[EXTRACT:COMPLIANCE,DISCLOSURES,VERIFICATION,POLICY,SOFT_SKILLS,ACCURACY,SENTIMENT:TYPE=LIST,DOMAIN=LEGAL]
[OUT_JSON:{summary,qa_scores:{verification,policy_adherence,soft_skills,accuracy,compliance},violations,recommendations}]
```

**Compressed tokens:** 83 tokens
**Reduction:** 69.1%
**Use case:** High-volume, cost-sensitive operations

---

#### Level 2: Type-Annotated (65.7% reduction)

```python
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=True,   # Types added
        add_attrs=False
    )
)
```

**Compressed:**
```text
[REQ:GENERATE:SPECS:SUMMARY] [TARGET:TRANSCRIPT:DOMAIN=QA]
[EXTRACT:COMPLIANCE,DISCLOSURES,VERIFICATION,POLICY,SOFT_SKILLS,ACCURACY,SENTIMENT:TYPE=LIST,DOMAIN=LEGAL]
[OUT_JSON:{summary:STR,qa_scores:{verification:FLOAT,policy_adherence:FLOAT,soft_skills:FLOAT,accuracy:FLOAT,compliance:FLOAT},violations:[STR],recommendations:[STR]}
```

**Compressed tokens:** 98 tokens
**Reduction:** 64.1%
**Use case:** When LLM needs explicit type hints for JSON generation

---

#### Level 3: Attribute-Rich (31.6% reduction)

```python
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=False,
        add_attrs=True      # Enums and constraints added
    )
)
```

**Compressed:**
```text
[REQ:GENERATE:SPECS:SUMMARY] [TARGET:TRANSCRIPT:DOMAIN=QA]
[EXTRACT:COMPLIANCE,DISCLOSURES,VERIFICATION,POLICY,SOFT_SKILLS,ACCURACY,SENTIMENT:TYPE=LIST,DOMAIN=LEGAL]
[OUT_JSON:{summary,qa_scores:{verification,policy_adherence,soft_skills,accuracy,compliance},violations,recommendations}:ENUMS={"ranges": [{"min": 0.0, "max": 0.49, "label": "FAIL"}, {"min": 0.5, "max": 0.74, "label": "NEEDS_IMPROVEMENT"}, {"min": 0.75, "max": 0.89, "label": "GOOD"}, {"min": 0.9, "max": 1.0, "label": "EXCELLENT"}]}
```

**Compressed tokens:** 195 tokens
**Reduction:** 46.1%
**Use case:** Complex validation rules and compliance requirements

---

#### Level 4: Full Annotation (26.6% reduction)

```python
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=True,   # Types
        add_attrs=True      # Attributes
    )
)
```

**Compressed:**
```text
[REQ:GENERATE:SPECS:SUMMARY] [TARGET:TRANSCRIPT:DOMAIN=QA]
[EXTRACT:COMPLIANCE,DISCLOSURES,VERIFICATION,POLICY,SOFT_SKILLS,ACCURACY,SENTIMENT:TYPE=LIST,DOMAIN=LEGAL]
[OUT_JSON:{summary:STR,qa_scores:{verification:FLOAT,policy_adherence:FLOAT,soft_skills:FLOAT,accuracy:FLOAT,compliance:FLOAT},violations:[STR],recommendations:[STR]}:ENUMS={"ranges": [{"min": 0.0, "max": 0.49, "label": "FAIL"}, {"min": 0.5, "max": 0.74, "label": "NEEDS_IMPROVEMENT"}, {"min": 0.75, "max": 0.89, "label": "GOOD"}, {"min": 0.9, "max": 1.0, "label": "EXCELLENT"}]}]
```

**Compressed tokens:** 209 tokens
**Reduction:** 41.2%
**Use case:** Mission-critical systems requiring maximum semantic preservation

---

#### Comparison Table

| Level | Config | Tokens | Reduction | Best For |
|-------|--------|--------|-----------|----------|
| **1** | Default | 83 | 70.7% | Cost optimization, high volume |
| **2** | +Types | 98 | 65.7% | Type-safe JSON generation |
| **3** | +Attrs | 195 | 31.6% | Complex validation rules |
| **4** | Both | 209 | 26.6% | Maximum semantic preservation |

---

### Example 2: Technical Support Agent

**Original System Prompt:**
```text
You are a Technical Support Specialist for network connectivity issues.

Your responsibilities:
1. Diagnose the root cause of connectivity problems
2. Provide step-by-step troubleshooting instructions
3. Escalate to Tier 2 if issue persists after basic troubleshooting
4. Document all steps taken

Troubleshooting Steps:
- Check physical connections
- Verify network adapter settings
- Test with different devices
- Reset router/modem
- Check for service outages

Output should be:
- Clear, numbered steps
- Non-technical language
- Estimated time for each step
- Success criteria for each step
```

**Compressed:**
```text
[REQ:GENERATE:SPECS:SUPPORT_RESPONSE] [TARGET:TICKET:DOMAIN=SUPPORT]
[OUT_JSON:STR:ENUMS={"troubleshooting_steps": {"kind": "categorical", "values": ["CHECK PHYSICAL CONNECTIONS", "VERIFY NETWORK ADAPTER SETTINGS", "TEST WITH DIFFERENT DEVICES", "RESET ROUTER/MODEM", "CHECK FOR SERVICE OUTAGES"]}}:CONSTRAINTS={"output_should_be": {"kind": "required", "items": ["Clear, numbered steps", "Non-technical language", "Estimated time for each step", "Success criteria for each step"]}}]
```

**Metrics:**
- Original: ~160 tokens
- Compressed: ~100 tokens
- Reduction: 37-40%

---

### Example 3: Data Extraction Agent

**Original System Prompt:**
```text
You are a Document Analysis Agent specialized in invoice processing.

TASK:
Extract key information from invoice documents and return structured data.

REQUIRED FIELDS:
- Vendor name and address
- Invoice number and date
- Line items (description, quantity, unit price, total)
- Subtotal, tax, and grand total
- Payment terms and due date

OPTIONAL FIELDS:
- Purchase order number
- Shipping information
- Billing contact

OUTPUT:
Return as JSON with nested objects for line items. Include confidence scores
for each extracted field (0.0-1.0). Flag any missing required fields.

VALIDATION RULES:
- Invoice number must be unique
- Dates must be in ISO format (YYYY-MM-DD)
- All monetary values as decimals
- Line item totals must match subtotal
```

**Compressed:**
```text
[REQ:EXTRACT] [TARGET:REPORT:DOMAIN=FINANCE:TOPIC=ANALYSIS_AGENT]
[EXTRACT:NAMES,ADDRESSES,DATES:TYPE=LIST,DOMAIN=ENTITIES]
[OUT_JSON:STR:CONSTRAINTS={"required_fields": {"kind": "required", "items": ["Vendor name and address", "Invoice number and date", "Line items (description, quantity, unit price, total)", "Subtotal, tax, and grand total", "Payment terms and due date"]}}]
```

**Metrics:**
- Original: 245 tokens
- Compressed: 98 tokens
- Reduction: 55.6%

---

## Token Structure for Task Prompts

### REQ Token
Specifies required actions:
```
[REQ:GENERATE:SPECS:SUPPORT_RESPONSE]
[REQ:GENERATE:SPECS:SUMMARY]
```

### TARGET Token
Identifies what to operate on:
```
[TARGET:TRANSCRIPT]
[TARGET:DOCUMENT:TYPE=INVOICE]
[TARGET:MATCH_PERFORMANCE]
```

### EXTRACT Token
Lists fields or data to extract:
```
[EXTRACT:COMPLIANCE,SENTIMENT,VIOLATIONS]
[EXTRACT:NAME,EMAIL,PHONE:REQUIRED=TRUE]
[EXTRACT:STATS:METRICS=GOALS,ASSISTS,CLEAN_SHEETS]
```

### OUT Token
Defines output format:
```
[OUT_JSON:{field1,field2,field3}]
[OUT_STEPS:NUMBERED,TIME_EST]
[OUT_TABLE:COLUMNS=3]
```

### CTX Token
Provides context and constraints:
```
[CTX:ESCALATE_IF=BASIC_FAILED:TARGET=TIER2]
[CTX:LANGUAGE=NON_TECHNICAL]
[CTX:CONFIDENCE_THRESHOLD=0.8]
```

See [Token Hierarchy](../advanced/clm_tokenization.md) for complete reference.

---

## Advanced Usage

### Multi-Stage System Prompts

For complex workflows with multiple phases:

```python
# Stage 1: Initial analysis
stage1_prompt = """
You are an initial triage agent. Review the customer issue and categorize it.
"""
compressed_stage1 = encoder.encode(stage1_prompt)

# Stage 2: Deep analysis
stage2_prompt = """
You are a specialist analyst. Perform detailed analysis based on the category.
"""
compressed_stage2 = encoder.encode(stage2_prompt)

# Combine for multi-stage workflow
full_workflow = f"{compressed_stage1.compressed} -> {compressed_stage2.compressed}"
```

### Dynamic System Prompts

For prompts that change based on context:

```python
def get_compressed_prompt(user_tier: str, language: str):
    """Generate compressed prompt based on user context."""

    base_prompt = f"""
    You are a {user_tier} support agent.
    Respond in {language}.
    """

    if user_tier == "premium":
        base_prompt += "Provide white-glove service with detailed explanations."
    else:
        base_prompt += "Provide efficient, standard support."

    return encoder.encode(base_prompt)

# Usage
premium_prompt = get_compressed_prompt("premium", "en")
standard_prompt = get_compressed_prompt("standard", "en")
```

### Versioning System Prompts

Track different versions for A/B testing:

```python
prompts = {
    "v1": encoder.encode(prompt_v1),
    "v2": encoder.encode(prompt_v2),
    "v3": encoder.encode(prompt_v3)
}

# Use in production
def get_system_prompt(version="v2"):
    return prompts[version].compressed

# A/B testing
import random
version = random.choice(["v2", "v3"])
system_prompt = get_system_prompt(version)
```

---

## Best Practices

### 1. Test Compressed Prompts

Always validate that compression preserves intended behavior:

```python
# Original prompt
original = """You are a helpful assistant..."""
compressed = encoder.encode(original)

# Test with real LLM
original_response = llm.complete(system=original, user="Test query")
compressed_response = llm.complete(system=compressed.compressed, user="Test query")

# Compare responses
assert similar_enough(original_response, compressed_response)
```

### 2. Choose Configuration Based on Requirements

Select the appropriate level based on your use case:

```python
# High-volume, cost-sensitive (70% reduction)
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=False,
        add_attrs=False
    )
)

# Need type hints for JSON (65% reduction)
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=True,   # Add if LLM needs explicit types
        add_attrs=False
    )
)

# Complex validation rules (30% reduction)
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=False,
        add_attrs=True      # Add if enums/ranges critical
    )
)

# Mission-critical systems (25% reduction)
cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=True,   # Maximum semantic preservation
        add_attrs=True
    )
)
```

**Decision matrix:**
- Need explicit types in JSON? -> Set `infer_types=True`
- Have complex enums/ranges/constraints? -> Set `add_attrs=True`
- Cost-sensitive high volume? -> Keep both `False`
- Mission-critical accuracy? -> Set both `True`

### 3. Document Compression Mappings

Maintain a mapping of original to compressed prompts:

```python
prompt_registry = {
    "qa_analyst_v1": {
        "original": original_text,
        "compressed": compressed_text,
        "compression_ratio": 0.65,
        "last_tested": "2024-12-31",
        "performance": "Verified"
    }
}
```

### 4. Monitor in Production

Track compression performance:

```python
import time

start = time.time()
result = encoder.encode(system_prompt)
compression_time = time.time() - start

# Log metrics
metrics = {
    "original_tokens": result.original_tokens,
    "compressed_tokens": result.compressed_tokens,
    "ratio": result.compression_ratio,
    "time_ms": compression_time * 1000
}

logger.info("Compression metrics", extra=metrics)
```

---

## Use Cases

### 1. Contact Center Operations

Compress agent instructions for consistency:

```python
# Different prompts for different issue types
prompts = {
    "billing": encoder.encode(billing_agent_prompt),
    "technical": encoder.encode(technical_agent_prompt),
    "sales": encoder.encode(sales_agent_prompt)
}

# Route based on issue
def get_agent_prompt(issue_type: str):
    return prompts.get(issue_type, prompts["general"])
```

### 2. Chatbot Services

Optimize system prompts for conversational AI:

```python
# Persona-based prompts
personas = {
    "friendly": encoder.encode(friendly_assistant_prompt),
    "professional": encoder.encode(professional_assistant_prompt),
    "expert": encoder.encode(expert_advisor_prompt)
}

# Switch based on user preference
def set_persona(user_preference: str):
    return personas[user_preference].compressed
```

### 3. Document Processing Pipelines

Streamline extraction instructions:

```python
# Document-type specific prompts
extractors = {
    "invoice": encoder.encode(invoice_extraction_prompt),
    "contract": encoder.encode(contract_extraction_prompt),
    "receipt": encoder.encode(receipt_extraction_prompt)
}

# Process based on document type
def extract_data(document, doc_type):
    system_prompt = extractors[doc_type].compressed
    return llm.extract(system=system_prompt, document=document)
```

---

## Performance Optimization

### Caching Compressed Prompts

Compress once, reuse many times:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_compressed_prompt(prompt_key: str):
    """Cache compressed prompts to avoid recompression."""
    original = load_prompt(prompt_key)
    return encoder.encode(original).compressed

# Reuse without recompression
prompt1 = get_compressed_prompt("qa_analyst")  # Compresses
prompt2 = get_compressed_prompt("qa_analyst")  # From cache
```

### Batch Compression

Compress multiple prompts efficiently:

```python
prompts_to_compress = [
    ("qa", qa_prompt),
    ("tech", tech_prompt),
    ("sales", sales_prompt)
]

compressed_prompts = {}
for key, prompt in prompts_to_compress:
    result = encoder.encode(prompt)
    compressed_prompts[key] = {
        "compressed": result.compressed,
        "metrics": {
            "original": result.original_tokens,
            "compressed": result.compressed_tokens,
            "ratio": result.compression_ratio
        }
    }

# Save for later use
import json
with open("compressed_prompts.json", "w") as f:
    json.dump(compressed_prompts, f, indent=2)
```

---

## Troubleshooting

### Issue: Low Compression Ratio

**Symptom:** Compression is only 40-50% instead of expected 75-85%

**Possible causes:**
1. Prompt is already concise
2. Many specific terms that can't be compressed
3. Complex nested structures

**Solutions:**
```python
# Try higher compression level
cfg = CLMConfig(lang="en", compression_level=3)

# Check if prompt is already optimized
if result.original_tokens < 100:
    print("Prompt already concise, limited compression possible")

# Review what's not compressing
print(result.metadata.get("uncompressed_terms"))
```

### Issue: Loss of Important Details

**Symptom:** Compressed prompt loses critical nuance

**Solutions:**
```python
# Use conservative compression
cfg = CLMConfig(
    lang="en",
    compression_level=1,
    preserve_entities=True,
    preserve_numbers=True
)

# Explicitly mark critical sections
prompt = """
CRITICAL: The following must be preserved exactly:
- Compliance requirement X
- Legal constraint Y

[Rest of prompt...]
"""
```

### Issue: Inconsistent Results

**Symptom:** Same prompt compresses differently sometimes

**Causes:**
- Using different encoder instances
- Configuration changes between calls

**Solutions:**
```python
# Use consistent configuration
ENCODER_CONFIG = CLMConfig(lang="en", compression_level=2)
encoder = CLMEncoder(cfg=ENCODER_CONFIG)

# Reuse same encoder instance
result1 = encoder.encode(prompt)
result2 = encoder.encode(prompt)  # Consistent
```

---

## Measuring Success

### Key Metrics to Track

1. **Compression Ratio**
   ```python
   ratio = result.compression_ratio
   assert 0.75 <= ratio <= 0.90, "Compression out of expected range"
   ```

2. **Response Quality**
   ```python
   # Compare outputs with original vs compressed prompts
   quality_score = compare_responses(original_output, compressed_output)
   assert quality_score > 0.95, "Quality degradation detected"
   ```

3. **Cost Savings**
   ```python
   daily_calls = 20000
   tokens_saved = (original_tokens - compressed_tokens) * daily_calls
   cost_saved = tokens_saved * 0.00025 / 1000  # $0.25 per 1M tokens
   print(f"Daily savings: ${cost_saved:.2f}")
   ```

4. **Latency Improvement**
   ```python
   original_latency = measure_latency(original_prompt)
   compressed_latency = measure_latency(compressed_prompt)
   improvement = (original_latency - compressed_latency) / original_latency
   print(f"Latency improvement: {improvement:.1%}")
   ```

---

## Next Steps

- **[Configuration Prompt Encoding](configuration_prompt.md)** - Learn about template-based compression
- **[Advanced: Token Hierarchy](../advanced/clm_tokenization.md)** - Deep dive into semantic tokens
- **[Advanced: CLM Dictionary](../advanced/clm_vocabulary.md)** - Language-specific vocabularies
