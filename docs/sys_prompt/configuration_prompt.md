# Configuration Prompt Encoding

## Overview

Configuration prompts are **template-based system instructions** that define an agent's persistent behavior and can be parameterized at runtime. Unlike task prompts that focus on a specific action, configuration prompts establish the agent's identity, rules, and behavioral patterns.

**Key characteristics:**
- Define agent role and persona
- Contain basic and custom behavioral rules
- Support runtime placeholders for dynamic values
- Include priority definitions for rule conflicts
- Often include structured output requirements

**Typical compression:** 60-80% token reduction (CL tokens + NL minimization)

---

## Anatomy of a Configuration Prompt

Configuration prompts typically contain these elements:

### 1. Role Definition
Establishes the agent's identity:
```xml
<role>You are a helpful customer support agent</role>
```
or:
```text
You are a professional technical writer.
```

### 2. Basic Rules
Standard behavioral guidelines:
```xml
<basic_rules>
- Detect input language automatically
- Apply appropriate grammar and style
- Improve clarity and readability
- Output only the enhanced text
</basic_rules>
```

### 3. Custom Rules
User-specific or context-specific instructions:
```xml
<custom_rules>
Always address the customer by name: {{customer_name}}
Use formal language when dealing with enterprise clients.
</custom_rules>
```

### 4. Priority Definition
How to handle rule conflicts:
```text
Custom instructions are paramount. If there are conflicts between
basic rules and custom instructions, prioritize custom instructions.
```

### 5. Placeholders
Runtime variables for dynamic behavior:
```text
{{user_name}}, {{context}}, {{language}}, {{tone}}
```

### 6. Output Format
Structured output requirements (optional):
```text
Return your response as JSON:
{
    "response": "your message",
    "sentiment": "positive|neutral|negative"
}
```

---

## Example: Configuration Prompt Structure

### Full Configuration Prompt

```text
<role>You are a helpful customer support agent</role>

<basic_rules>
Core capabilities and standard guidelines:
- Detect input language automatically
- Apply appropriate grammar and style
- Improve clarity and readability
- Output only the enhanced text
</basic_rules>

<custom_rules>
Context-specific instructions:
- Always greet the customer by name: {{customer_name}}
- Reference their account type: {{account_type}}
- Use {{tone}} tone throughout the conversation
</custom_rules>

<general_prompt>
Follow the basic rules as a foundation. If there are conflicts between
basic rules and custom instructions, prioritize custom instructions.
Custom instructions are paramount.
</general_prompt>

OUTPUT FORMAT:
Return your response as:
{
    "greeting": "personalized greeting",
    "response": "main response content",
    "next_steps": ["action1", "action2"]
}
```

**Token count:** ~180 tokens

### Compressed Representation

**CL (Compressed Language) Token:**
```text
[PROMPT_MODE:CONFIGURATION][ROLE:CUSTOMER_SUPPORT_AGENT][RULES:BASIC,CUSTOM][PRIORITY:CUSTOM_OVER_BASIC][OUT_JSON:{greeting:STR,response:STR,next_steps:[STR]}]
```

**Minimized NL (Natural Language):**
```text
<basic_rules>
- Detect input language automatically
- Apply appropriate grammar and style
- Improve clarity and readability
- Output only the enhanced text
</basic_rules>

<custom_rules>
- Always greet the customer by name: {{customer_name}}
- Reference their account type: {{account_type}}
- Use {{tone}} tone throughout the conversation
</custom_rules>
```

**Combined compression:** ~65% reduction

---

## How Configuration Prompt Compression Works

CLM uses a two-phase approach for configuration prompts:

### Phase 1: CL Token Generation

The `ConfigurationPromptEncoder` extracts semantic elements and generates compressed tokens:

1. **Role Detection**: Identifies agent role from `<role>` tags or "You are..." patterns
2. **Rules Extraction**: Detects basic and custom rule blocks
3. **Priority Analysis**: Identifies priority/conflict resolution statements
4. **Placeholder Discovery**: Finds all `{{placeholder}}` patterns
5. **Output Format Parsing**: Extracts structured output requirements

**Result:** A deterministic CL token like:
```text
[PROMPT_MODE:CONFIGURATION][ROLE:ASSISTANT][RULES:BASIC,CUSTOM][PRIORITY:CUSTOM_OVER_BASIC]
```

### Phase 2: NL Minimization

The `ConfigurationPromptMinimizer` removes redundant natural language:

1. **Meta-instruction Removal**: Removes statements about following/prioritizing rules
2. **Priority Explanation Suppression**: Removes conflict resolution explanations (encoded in CL)
3. **Role Block Suppression**: Removes `<role>` blocks when role is encoded
4. **Output Block Extraction**: Removes output format descriptions when encoded
5. **Basic Rules Trimming**: Condenses verbose rule explanations

**Result:** A minimized NL prompt containing only essential content.

---

## Configuration

### Basic Usage

```python
from clm_core import CLMConfig, CLMEncoder
from clm_core.components.sys_prompt import (
    ConfigurationPromptEncoder,
    ConfigurationPromptMinimizer,
    SysPromptConfig
)

cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        use_structured_output_abstraction=True  # Enable output format compression
    )
)

encoder = CLMEncoder(cfg=cfg)

config_prompt = """
<role>You are a helpful assistant</role>

<basic_rules>
Be polite and professional at all times.
</basic_rules>

<custom_rules>
Always address the user as {{user_name}}.
</custom_rules>

Custom instructions are paramount.
"""

result = encoder.encode(config_prompt)
print(result.compressed)
# [PROMPT_MODE:CONFIGURATION][ROLE:HELPFUL_ASSISTANT][RULES:BASIC,CUSTOM][PRIORITY:CUSTOM_OVER_BASIC]

print(result.metadata)
# {
#     "prompt_mode": "CONFIGURATION",
#     "role": "HELPFUL_ASSISTANT",
#     "rules": {"basic": True, "custom": True},
#     "priority": "CUSTOM_OVER_BASIC",
#     "placeholders": ["user_name"],
#     "output_format": None
# }
```

### Configuration Options

```python
from clm_core.components.sys_prompt import SysPromptConfig

config = SysPromptConfig(
    use_structured_output_abstraction=True,  # Compress output format to CL tokens
    infer_types=True,                        # Add type annotations to output schema
    add_attrs=False                          # Include enums/constraints in output
)
```

**`use_structured_output_abstraction` (boolean)**
- When `True`: Output format is compressed into CL tokens
- When `False`: Output format remains in natural language
- Default: `True`

---

## Using the Minimizer

The `ConfigurationPromptMinimizer` can be used independently to reduce NL prompt size:

```python
from clm_core.components.sys_prompt import ConfigurationPromptMinimizer

prompt = """
<role>You are a helpful assistant</role>

Follow the basic rules as a foundation. If there are conflicts between
basic rules and custom instructions, prioritize custom instructions.
Custom instructions are paramount.

<basic_rules>
Core capabilities:
- Be helpful and accurate
- Respond clearly
</basic_rules>

Remember: Custom instructions override basic rules when there are conflicts.
"""

# Basic minimization (no CL metadata)
minimized = ConfigurationPromptMinimizer.minimize(prompt)
print(minimized)

# CL-aware minimization (suppresses content encoded in CL)
cl_metadata = {
    "role": "HELPFUL_ASSISTANT",
    "priority": "CUSTOM_OVER_BASIC",
    "rules": {"basic": True, "custom": False}
}
minimized_with_cl = ConfigurationPromptMinimizer.minimize(prompt, cl_metadata)
print(minimized_with_cl)
```

### Minimization Features

**Meta-instruction Removal:**
```text
# Before
"Follow the basic rules. If there are conflicts, prioritize custom instructions."

# After
(removed - encoded as [PRIORITY:CUSTOM_OVER_BASIC])
```

**Priority Statement Suppression:**
```text
# Before
"Remember: Custom instructions are paramount."

# After
(removed - encoded in CL token)
```

**Basic Rules Trimming:**
```text
# Before (verbose)
<basic_rules>
You should always detect the input language automatically and respond
in the same language. Make sure to apply appropriate grammar rules
and maintain a professional style throughout your responses.
</basic_rules>

# After (condensed)
<basic_rules>
- Detect input language automatically
- Apply appropriate grammar and style
- Improve clarity and readability
- Output only the enhanced text
</basic_rules>
```

---

## Template Binding

Configuration prompts support runtime placeholder binding via `PromptTemplate`:

```python
from clm_core.components.sys_prompt import PromptAssembler, PromptTemplate

# Create template from compressed result
template = PromptTemplate(
    raw_template=original_prompt,
    placeholders=["customer_name", "account_type", "tone"],
    role="CUSTOMER_SUPPORT_AGENT",
    rules={"basic": True, "custom": True},
    priority="CUSTOM_OVER_BASIC",
    compressed="[PROMPT_MODE:CONFIGURATION][ROLE:CUSTOMER_SUPPORT_AGENT]..."
)

# Bind runtime values
assembler = PromptAssembler()
final_prompt = assembler.assemble_system_prompt(
    template=template,
    runtime_values={
        "customer_name": "John Smith",
        "account_type": "Premium",
        "tone": "friendly"
    }
)

print(final_prompt)
# [PROMPT_MODE:CONFIGURATION][ROLE:CUSTOMER_SUPPORT_AGENT]...
#
# <custom_rules>
# - Always greet the customer by name: John Smith
# - Reference their account type: Premium
# - Use friendly tone throughout the conversation
# </custom_rules>
```

### Validation

Templates are validated for common issues:

```python
from clm_core.components.sys_prompt import (
    PromptTemplateValidator,
    BoundPromptValidator,
    ValidationLevel
)

# Validate template structure
template_issues = PromptTemplateValidator.validate(template)
for issue in template_issues:
    if issue.level == ValidationLevel.ERROR:
        print(f"ERROR: {issue.message}")
    else:
        print(f"WARNING: {issue.message}")

# Validate bound prompt (after placeholder substitution)
bound_prompt = template.bind(customer_name="John", account_type="Basic", tone="formal")
bound_issues = BoundPromptValidator.validate(bound_prompt)
```

**Validation Rules:**

| Rule | Level | Description |
|------|-------|-------------|
| Empty placeholder | ERROR | Placeholder name is empty |
| Invalid placeholder name | WARNING | Non-alphanumeric characters in placeholder |
| Duplicate placeholders | ERROR | Same placeholder appears multiple times |
| Priority without rules | WARNING | Priority defined but no rules detected |
| Missing role | WARNING | No role detected in configuration prompt |
| Unresolved placeholders | ERROR | Placeholders remain after binding |
| Empty bound prompt | ERROR | Bound prompt is empty |

---

## Examples

### Example 1: Customer Support Agent

**Original:**
```text
<role>You are a friendly customer support agent for TechCorp</role>

<basic_rules>
Standard support guidelines:
- Always be polite and professional
- Verify customer identity before discussing account details
- Escalate complex issues to tier 2 support
- Document all interactions
</basic_rules>

<custom_rules>
Customer-specific instructions:
- Address customer as: {{customer_name}}
- Account tier: {{account_tier}}
- Preferred language: {{language}}
</custom_rules>

Follow the basic rules as your foundation. If there are any conflicts
between basic rules and custom instructions, always prioritize the
custom instructions. Custom instructions are paramount.

OUTPUT:
{
    "response": "your message to the customer",
    "internal_notes": "notes for support team",
    "escalate": true/false
}
```

**Compressed CL Token:**
```text
[PROMPT_MODE:CONFIGURATION][ROLE:CUSTOMER_SUPPORT_AGENT][RULES:BASIC,CUSTOM][PRIORITY:CUSTOM_OVER_BASIC][OUT_JSON:{response:STR,internal_notes:STR,escalate:BOOL}]
```

**Minimized NL:**
```text
<basic_rules>
- Always be polite and professional
- Verify customer identity before discussing account details
- Escalate complex issues to tier 2 support
- Document all interactions
</basic_rules>

<custom_rules>
- Address customer as: {{customer_name}}
- Account tier: {{account_tier}}
- Preferred language: {{language}}
</custom_rules>
```

**Metrics:**
- Original: ~180 tokens
- CL + Minimized NL: ~70 tokens
- Reduction: ~61%

---

### Example 2: Content Moderator

**Original:**
```text
You are a content moderation assistant. Your role is to review user-generated
content and flag potentially harmful material.

<basic_rules>
Core moderation guidelines:
- Flag content containing hate speech, violence, or explicit material
- Consider context before flagging
- Err on the side of caution for edge cases
- Provide clear reasoning for all decisions
</basic_rules>

<custom_rules>
Platform-specific rules for {{platform_name}}:
- Strictness level: {{strictness}}
- Allow political content: {{allow_political}}
- Age rating: {{age_rating}}
</custom_rules>

Custom instructions override basic rules when applicable.

Return your assessment as:
{
    "flagged": true/false,
    "category": "hate_speech|violence|explicit|spam|safe",
    "confidence": 0.0-1.0,
    "reasoning": "explanation"
}
```

**Compressed:**
```text
[PROMPT_MODE:CONFIGURATION][ROLE:CONTENT_MODERATION_ASSISTANT][RULES:BASIC,CUSTOM][PRIORITY:CUSTOM_OVER_BASIC][OUT_JSON:{flagged:BOOL,category:STR,confidence:FLOAT,reasoning:STR}:ENUMS={"category":["hate_speech","violence","explicit","spam","safe"]}]
```

---

### Example 3: Translation Assistant

**Original:**
```text
<role>You are a professional translator</role>

<basic_rules>
Translation best practices:
- Preserve meaning over literal translation
- Maintain tone and style of original
- Handle idioms appropriately
- Flag untranslatable terms
</basic_rules>

<custom_rules>
Translation context:
- Source language: {{source_lang}}
- Target language: {{target_lang}}
- Domain: {{domain}}
- Formality: {{formality}}
</custom_rules>

Basic rules provide the foundation. Custom instructions take precedence
when there are conflicts.
```

**Compressed:**
```text
[PROMPT_MODE:CONFIGURATION][ROLE:PROFESSIONAL_TRANSLATOR][RULES:BASIC,CUSTOM][PRIORITY:CUSTOM_OVER_BASIC]
```

**Placeholders detected:** `source_lang`, `target_lang`, `domain`, `formality`

---

## Token Structure for Configuration Prompts

### PROMPT_MODE Token
Identifies the prompt type:
```text
[PROMPT_MODE:CONFIGURATION]
[PROMPT_MODE:TASK]
```

### ROLE Token
Specifies agent identity:
```text
[ROLE:CUSTOMER_SUPPORT_AGENT]
[ROLE:CONTENT_MODERATOR]
[ROLE:PROFESSIONAL_TRANSLATOR]
```

### RULES Token
Indicates active rule sets:
```text
[RULES:BASIC]
[RULES:CUSTOM]
[RULES:BASIC,CUSTOM]
```

### PRIORITY Token
Defines rule conflict resolution:
```text
[PRIORITY:CUSTOM_OVER_BASIC]
```

### OUT Token
Defines output format (when `use_structured_output_abstraction=True`):
```text
[OUT_JSON:{field1:TYPE,field2:TYPE}]
[OUT_JSON:{field:STR}:ENUMS={"field":["a","b","c"]}]
```

---

## Best Practices

### 1. Use Consistent Tag Structure

```xml
<!-- Good: Clear, consistent tags -->
<role>You are a helpful assistant</role>
<basic_rules>...</basic_rules>
<custom_rules>...</custom_rules>

<!-- Avoid: Inconsistent formatting -->
You are a helpful assistant.
Basic rules: ...
CUSTOM RULES: ...
```

### 2. Keep Placeholders Descriptive

```text
<!-- Good: Clear placeholder names -->
{{customer_name}}, {{account_tier}}, {{preferred_language}}

<!-- Avoid: Ambiguous names -->
{{name}}, {{tier}}, {{lang}}
```

### 3. Separate Static and Dynamic Content

```text
<!-- Good: Clear separation -->
<basic_rules>
Static rules that never change
</basic_rules>

<custom_rules>
Dynamic rules with {{placeholders}}
</custom_rules>

<!-- Avoid: Mixed content -->
<rules>
Be polite. Address user as {{name}}. Follow guidelines.
</rules>
```

### 4. Let CL Handle Meta-Instructions

Since CL tokens encode priority and rule information, you can remove verbose explanations:

```text
<!-- Before (verbose) -->
Follow the basic rules as your foundation. However, if there are any
conflicts between the basic rules and custom instructions, you should
always prioritize the custom instructions. Remember that custom
instructions are paramount and should override basic rules.

<!-- After (CL handles this) -->
[PRIORITY:CUSTOM_OVER_BASIC]
```

### 5. Validate Before Deployment

```python
# Always validate templates before production use
issues = PromptTemplateValidator.validate(template)
errors = [i for i in issues if i.level == ValidationLevel.ERROR]
if errors:
    raise ValueError(f"Template validation failed: {errors}")
```

---

## Troubleshooting

### Issue: Role Not Detected

**Symptom:** `role` is `None` in metadata

**Possible causes:**
1. Role not in recognized format
2. Missing `<role>` tags or "You are..." pattern

**Solutions:**
```text
# Use recognized patterns:
<role>You are a helpful assistant</role>
# or
You are a helpful assistant.
# or
Your role is an assistant.
```

### Issue: Placeholders Not Binding

**Symptom:** `TemplateBindingError` when calling `bind()`

**Possible causes:**
1. Missing required placeholder values
2. Extra values not in template

**Solutions:**
```python
# Check required placeholders
print(template.placeholders)  # ['name', 'tier']

# Provide exact matches
bound = template.bind(name="John", tier="Premium")  # Correct
bound = template.bind(name="John")  # Error: missing 'tier'
bound = template.bind(name="John", tier="Premium", extra="x")  # Error: extra value
```

### Issue: Priority Not Detected

**Symptom:** `priority` is `None` despite having priority statements

**Possible causes:**
1. Non-standard priority phrasing
2. Missing keywords

**Solutions:**
```text
# Use recognized patterns:
"Custom instructions are paramount"
"custom instructions override basic rules"
"prioritize custom instructions"
```

---

## Next Steps

- **[Task Prompt Encoding](task_prompt.md)** - Learn about action-oriented compression
- **[Advanced: Token Hierarchy](../advanced/clm_tokenization.md)** - Deep dive into semantic tokens
- **[Advanced: CLM Dictionary](../advanced/clm_vocabulary.md)** - Language-specific vocabularies
