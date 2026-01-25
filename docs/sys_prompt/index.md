# System Prompt Encoder

## Overview

System Prompts (also called **System Instructions**) are processed by LLM models before they begin processing user input. They define the **model's identity**, **task**, and **behavior** - essentially establishing who the AI should be and what it should do.

**Key characteristics:**
- Processed before every user interaction
- Define model behavior and constraints
- Often repeated thousands of times per day
- Can be 500-5,000+ tokens
- Critical for consistent model performance

The more detailed a system prompt, the better the model understands and performs its intended task. However, detailed prompts are token-intensive and costly at scale.

**Typical compression:** 75-90% token reduction

---

## Prompt Modes

CLM recognizes two distinct types of system prompts, each with specialized compression strategies:

### Task Prompts

Task prompts are **action-oriented instructions** that tell the model what to do for a specific task. They typically include:

- **Intent**: The primary action (analyze, extract, generate, summarize)
- **Target**: What to operate on (transcript, document, data)
- **Output Format**: Expected response structure (JSON, text, table)
- **Constraints**: Rules, validations, and boundaries

**Example:**
```text
You are a Betting Analysis system. Analyze soccer matches and provide betting odds.
Return your analysis as: {"win": 0.45, "draw": 0.30, "lose": 0.25}
```

**Compressed:**
```text
[REQ:PREDICT:SPECS:BETTING_ODDS][TARGET:REPORT:DOMAIN=BUSINESS][OUT_JSON:{win:FLOAT,draw:FLOAT,lose:FLOAT}]
```

[Learn more about Task Prompts](task_prompt.md)

---

### Configuration Prompts

Configuration prompts are **template-based instructions** that define persistent behavior and can be parameterized at runtime. They typically include:

- **Role**: The assistant's identity and persona
- **Rules**: Basic and custom behavioral rules
- **Priority**: How to handle rule conflicts
- **Placeholders**: Runtime variables (e.g., `{{user_name}}`, `{{context}}`)
- **Output Format**: Structured output requirements

**Example:**
```text
<role>You are a helpful assistant</role>

<basic_rules>
Follow standard guidelines for clarity and accuracy.
</basic_rules>

<custom_rules>
Always greet the user by name: {{user_name}}
</custom_rules>

Custom instructions are paramount. If there are conflicts, prioritize custom rules.
```

**Compressed:**
```text
[PROMPT_MODE:CONFIGURATION][ROLE:HELPFUL_ASSISTANT][RULES:BASIC,CUSTOM][PRIORITY:CUSTOM_OVER_BASIC]
```

[Learn more about Configuration Prompts](configuration_prompt.md)

---

## When to Use Each Mode

| Aspect | Task Prompt | Configuration Prompt |
|--------|-------------|---------------------|
| **Purpose** | Execute a specific task | Define persistent model behavior |
| **Structure** | Action + Target + Output | Role + Rules + Placeholders |
| **Runtime** | Static per request | Parameterized with runtime values |
| **Use Case** | Data extraction, analysis, generation | Chatbots, assistants, configurable systems |
| **Compression Focus** | Intent, extraction fields, output schema | Role, rules, meta-instructions |

---

## Why Compress System Prompts?

### The Scale Problem

In production environments, system prompts create significant overhead:

| Scenario | Details                                       | Impact |
|----------|-----------------------------------------------|--------|
| **Contact Center** | 1,000 users x 20,000 calls/day                | 20M prompt tokens/day |
| **Chatbot Service** | 10,000 concurrent users x 50 interactions/day | 500K prompt tokens/day |
| **Enterprise Tool** | 500 employees x 100 queries/day               | 50K prompt tokens/day |

### Benefits of Compression

**Cost Reduction**
- 75-90% fewer tokens = 75-90% cost savings on system prompts
- At scale, this translates to significant monthly savings

**Faster Processing**
- Smaller prompts = faster inference
- Reduced latency by 30-73%
- Better user experience

**Higher Context Window Utilization**
- More room for actual conversation
- Longer context histories
- More examples in few-shot learning

**Better Scalability**
- Handle more concurrent requests
- Lower infrastructure requirements
- Smoother peak load handling

---

## Quick Start

### Task Prompt Compression

```python
from clm_core import CLMConfig, CLMEncoder

cfg = CLMConfig(lang="en")
encoder = CLMEncoder(cfg=cfg)

task_prompt = """
You are a customer service quality analyst. Analyze call transcripts
for compliance violations and sentiment issues.
"""

result = encoder.encode(task_prompt)
print(result.compressed)
# [REQ:ANALYZE][TARGET:TRANSCRIPT:DOMAIN=QA][EXTRACT:COMPLIANCE,SENTIMENT,ISSUE]
```

### Configuration Prompt Compression

```python
from clm_core import CLMConfig, CLMEncoder
from clm_core.components.sys_prompt import ConfigurationPromptEncoder

cfg = CLMConfig(lang="en")
encoder = CLMEncoder(cfg=cfg)

config_prompt = """
<role>You are a helpful customer support agent</role>

<basic_rules>
Be polite and professional.
</basic_rules>

<custom_rules>
Always address the customer as {{customer_name}}.
</custom_rules>

Custom instructions are paramount.
"""

# The encoder automatically detects configuration prompts
result = encoder.encode(config_prompt)
print(result.compressed)
# [PROMPT_MODE:CONFIGURATION][ROLE:CUSTOMER_SUPPORT_AGENT][RULES:BASIC,CUSTOM][PRIORITY:CUSTOM_OVER_BASIC]
```

---

## Next Steps

- **[Task Prompt Encoding](task_prompt.md)** - Deep dive into task-oriented compression
- **[Configuration Prompt Encoding](configuration_prompt.md)** - Learn about template-based compression
- **[Advanced: Token Hierarchy](../advanced/clm_tokenization.md)** - Understand semantic tokens
- **[Advanced: CLM Dictionary](../advanced/clm_vocabulary.md)** - Language-specific vocabularies
