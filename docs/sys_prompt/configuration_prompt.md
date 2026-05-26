# Configuration Prompt Encoding

Configuration prompts are system prompts that define persistent behavior.

Use this format when the prompt describes:

- the assistant's role
- the rules it should follow
- how to resolve conflicts between rules
- runtime values that should be filled in later
- an output shape or response schema

If you want a quick overview of the system prompt encoder first, see [System Prompt Encoder](index.md).

---

## What Makes a Prompt "Configuration"?

A configuration prompt usually has two parts:

1. A stable instruction set, such as role and rules
2. One or more placeholders that change at runtime

Example:

```text
<role>You are a helpful customer support agent</role>

<basic_rules>
Be polite and professional.
</basic_rules>

<custom_rules>
Always address the customer as {{customer_name}}.
Use {{tone}} tone.
</custom_rules>

Custom instructions are paramount.
```

CLM detects the role, rules, priority language, and placeholders, then stores them in the compressed output metadata.

The minimizer is part of the internal compression flow. You normally do not call it yourself. CLM uses it after the structured CL token has already captured role, rules, priority, or output-format information, so the natural-language prompt can be trimmed without losing meaning.

---

## The Two Things the Encoder Does

When you call `encoder.encode(...)` on a configuration prompt, CLM does two things:

1. It creates a compact CL token representation.
2. It keeps a minimized version of the original prompt text.

The minimizer exists so the final prompt is not redundant. If the CL token already captures the role, rules, or priority statement, the repeated natural-language explanation can be trimmed down.

That means:

- the CL token carries the structured meaning
- the minimized NL keeps only the parts that still need to be read as text

You usually do not call the minimizer directly unless you are debugging prompt cleanup or comparing the raw prompt with the minimized form.

---

## Quick Start

```python
from clm_core import CLMConfig, CLMEncoder, PromptMode, SysPromptConfig

cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=False,
        add_attrs=False,
        prompt_mode=PromptMode.CONFIGURATION,
        use_structured_output_abstraction=True,
    ),
)
encoder = CLMEncoder(cfg=cfg)

config_prompt = """
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

Custom instructions are paramount.
"""

result = encoder.encode(config_prompt)
print(result.compressed)
print(result.metadata["placeholders"])
```

Example output:

```text
[PROMPT_MODE:CONFIGURATION][ROLE:FRIENDLY_CUSTOMER_SUPPORT_AGENT][RULES:BASIC,CUSTOM][PRIORITY:CUSTOM_OVER_BASIC][OUT_STRUCTURED]
```

Metadata will include the placeholders that were found:

```python
["account_tier", "customer_name", "language"]
```

---

## Binding Runtime Values

After compression, call `bind()` to fill the placeholders with runtime values.

`bind()` does not take a special `attributes=` object. It accepts keyword arguments whose names must match the placeholder names in the prompt.

```python
bound_prompt = encoder.bind(
    result,
    customer_name="Yanick",
    account_tier="premium",
    language="en",
)
```

Use the exact placeholder names from the template:

- `{{customer_name}}` becomes `customer_name="Yanick"`
- `{{account_tier}}` becomes `account_tier="premium"`
- `{{language}}` becomes `language="en"`

If you omit a placeholder, binding fails.
If you provide extra keyword arguments, CLM ignores the unused ones and logs a warning.

### Final result

After binding, the prompt becomes runtime-ready. The compressed CL token stays at the top, followed by the minimized natural-language prompt with values filled in:

```text
[PROMPT_MODE:CONFIGURATION][ROLE:FRIENDLY_CUSTOMER_SUPPORT_AGENT][RULES:BASIC,CUSTOM][PRIORITY:CUSTOM_OVER_BASIC][OUT_STRUCTURED]

<basic_rules>
Standard support guidelines:
- Always be polite and professional
- Verify customer identity before discussing account details
- Escalate complex issues to tier 2 support
- Document all interactions
</basic_rules>

<custom_rules>
Customer-specific instructions:
- Address customer as: Yanick
- Account tier: premium
- Preferred language: en
</custom_rules>

OUTPUT:
{
    "response": "your message to the customer",
    "internal_notes": "notes for support team",
    "escalate": true/false
}
```

Metrics:
- `n_tokens`: 224
- `c_tokens`: 158
- `ratio`: 29.5%

---

## Output Format And Attributes

If your configuration prompt includes an output format, CLM can capture that too when structured output abstraction is enabled in `SysPromptConfig`.

Example:

```text
Return your response as JSON:
{
  "response": "your message",
  "sentiment": "positive|neutral|negative"
}
```

The encoder can store this in metadata as `output_format`, and the compressed token may include an `OUT_JSON` style representation.

If you are using structured output and you also have placeholders inside the prompt, bind the placeholders the same way:

```python
bound_prompt = encoder.bind(
    result,
    customer_name="Melissa",
    account_type="Premium",
)
```

There is no separate placeholder-attribute API. The runtime values are just keyword arguments that match the template placeholders.

---

## Minimization Behavior

The minimizer removes text that is already represented by CL tokens.

### What it removes

- repeated priority statements like "Custom instructions are paramount"
- role text when the role is already encoded
- rule-following reminders when the rules are already encoded
- verbose output-format explanations when the output schema is already encoded

### What it keeps

- actual instruction content that still matters to the prompt
- placeholder-driven text that must remain visible
- the core rule blocks, when they are still needed in the minimized prompt

### Example

Before minimization:

```text
<role>You are a helpful assistant</role>

<basic_rules>
Be clear and accurate.
</basic_rules>

<custom_rules>
Always address the user as {{user_name}}.
</custom_rules>

Custom instructions are paramount.
```

After CL-aware minimization:

```text
<basic_rules>
Be clear and accurate.
</basic_rules>

<custom_rules>
Always address the user as {{user_name}}.
</custom_rules>
```

That is why the minimizer exists: it keeps the prompt readable after the structured meaning has already been captured in CL.

### Compressed, minimized, and bound example

This is the shape you get after compression, internal minimization, and binding runtime values.

#### Stage 1: Compressed CL token

```text
[PROMPT_MODE:CONFIGURATION][ROLE:FRIENDLY_CUSTOMER_SUPPORT_AGENT][RULES:BASIC,CUSTOM][PRIORITY:CUSTOM_OVER_BASIC][OUT_STRUCTURED]
```

#### Stage 2: Minimized prompt

```text
<basic_rules>• Detect input language automatically • Apply appropriate grammar and style • Improve clarity and readability • Output only the enhanced text</basic_rules>
<custom_rules>
Customer-specific instructions:
    - Address customer as: Yanick
    - Account tier: premium
    - Preferred language: en
</custom_rules>

Follow the basic rules as your foundation.

OUTPUT:
{
  "response": "your message to the customer",
  "internal_notes": "notes for support team",
  "escalate": true/false
}
```

Metrics:
- `n_tokens`: 224
- `c_tokens`: 158
- `ratio`: 29.5%

#### Stage 3: Bound runtime prompt

If you want the same prompt with placeholders filled, bind first and let `encoder.bind(...)` fill them:

```python
bound_prompt = encoder.bind(
    result,
    customer_name="Yanick",
    account_tier="premium",
    language="en",
)
```

The bound prompt is the runtime-ready version. The CL token stays the same; only the natural-language part changes when placeholders are filled.

---

## Validation And Safety Checks

The configuration prompt pipeline validates templates and bound prompts.

Template validation checks for things like:

- missing role text
- duplicate or empty placeholders
- priority statements without supporting rules

Bound-prompt validation checks for:

- missing runtime values
- unresolved placeholders
- empty bound prompts

If you want the prompt to stay valid after binding, make sure every placeholder is supplied with a matching keyword argument.

### Forcing the mode explicitly

The `scripts/system_prompt.py:single_prompt()` example shows the explicit path:

```python
from clm_core import CLMConfig, CLMEncoder, PromptMode, SysPromptConfig

cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        prompt_mode=PromptMode.CONFIGURATION,
        infer_types=False,
        add_attrs=False,
        use_structured_output_abstraction=True,
    ),
)
encoder = CLMEncoder(cfg=cfg)
```

Setting `prompt_mode=PromptMode.CONFIGURATION` tells CLM to skip detection and treat the prompt as configuration content.

---

## When To Use This Encoder Directly

Use the configuration prompt encoder when:

- the prompt is clearly role-based or rule-based
- you need runtime substitution with placeholders
- you want the compressed CL token plus a minimized natural-language prompt

Use the higher-level `CLMEncoder` when you want automatic prompt-type detection.

---

## Next Steps

- Read [Task Prompt](task_prompt.md) for action-oriented prompts.
- Review [System Prompt Encoder](index.md) for the full flow.
- Review [CLM Output](../advanced/clm_output.md) for metadata details.
