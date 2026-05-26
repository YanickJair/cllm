# System Prompt Encoder

The System Prompt Encoder compresses verbose system instructions into a compact CLM representation.

Use it when your input is a prompt that tells the model:

- who it is
- what it should do
- what rules it should follow
- what format it should return

This section is the fastest way to get started. If you need deeper details, use the dedicated pages for [Task Prompt](task_prompt.md) and [Configuration Prompt](configuration_prompt.md).

---

## Start Here

The easiest way to use the encoder is through `CLMEncoder`. It detects the prompt type for you.

If you want to skip detection, set `prompt_mode` directly in `SysPromptConfig`. That forces CLM to use the mode you chose instead of guessing from the text.

### 1. Create a config

```python
from clm_core import CLMConfig, CLMEncoder, PromptMode, SysPromptConfig

cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(prompt_mode=PromptMode.CONFIGURATION),
)
encoder = CLMEncoder(cfg=cfg)
```

### 2. Pass in your system prompt

```python
system_prompt = """
You are a customer service quality analyst.
Analyze call transcripts for compliance issues and sentiment problems.
Return the result as JSON.
"""

result = encoder.encode(system_prompt)
```

### 3. Read the compressed output

```python
print(result.compressed)
print(result.compression_ratio)
print(result.metadata)
```

`result.compressed` is the CLM token sequence. `result.metadata` contains the parsed prompt details.

The configuration prompt example above mirrors `scripts/system_prompt.py:single_prompt()`: the prompt mode is forced to `CONFIGURATION`, then the prompt is compressed and bound with runtime values.

---

## Which Prompt Type Is This?

CLM treats system prompts as one of two shapes:

| Prompt type | What it looks like | Typical goal |
|-------------|--------------------|--------------|
| Task prompt | "Analyze...", "Generate...", "Extract..." | Perform a specific action |
| Configuration prompt | "You are...", `<role>`, `<basic_rules>` | Define persistent behavior |

If your prompt begins with role or rule language, CLM will usually classify it as a configuration prompt.

### Task Prompt Example

```text
You are a betting analysis system.
Analyze soccer matches and return win, draw, and lose probabilities.
```

Compressed form:

```text
[REQ:PREDICT:SPECS:BETTING_ODDS][TARGET:REPORT:DOMAIN=BUSINESS][OUT_JSON:{win:FLOAT,draw:FLOAT,lose:FLOAT}]
```

### Configuration Prompt Example

```text
<role>You are a helpful customer support agent</role>

<basic_rules>
Be polite and professional.
</basic_rules>

<custom_rules>
Always address the customer as {{customer_name}}.
</custom_rules>

Custom instructions are paramount.
```

Compressed form:

```text
[PROMPT_MODE:CONFIGURATION][ROLE:CUSTOMER_SUPPORT_AGENT][RULES:BASIC,CUSTOM][PRIORITY:CUSTOM_OVER_BASIC]
```

The minimizer is not something you call directly in normal usage. It runs internally after CL tokens capture the structured parts of a configuration prompt, so the returned prompt stays shorter and less repetitive.

### End-to-end example

This is the full flow for a configuration prompt with placeholders:

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

In code, that comes from compressing the prompt first and then binding runtime values:

```python
from clm_core import CLMConfig, CLMEncoder, PromptMode, SysPromptConfig

cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(prompt_mode=PromptMode.CONFIGURATION),
)
encoder = CLMEncoder(cfg=cfg)

result = encoder.encode(config_prompt)
bound_prompt = encoder.bind(
    result,
    customer_name="Yanick",
    account_tier="premium",
    language="en",
)
```

---

## What You Get Back

`encoder.encode(...)` returns a `CLMOutput` object.

Useful fields:

- `compressed`: the CLM token sequence
- `original`: the original prompt
- `compression_ratio`: estimated token reduction
- `metadata`: parsed details such as role, rules, placeholders, and output format

Example:

```python
print(result.compressed)
print(result.original)
print(result.compression_ratio)
print(result.metadata["prompt_mode"])
```

---

## Configuration Prompts With Placeholders

If your prompt includes placeholders like `{{customer_name}}`, compress it first and bind values later.

```python
config_prompt = """
<role>You are a helpful support agent</role>

<custom_rules>
Always greet the customer by name: {{customer_name}}
</custom_rules>
"""

result = encoder.encode(config_prompt)
bound_prompt = encoder.bind(result, customer_name="Melissa")
```

Use `bind()` only for configuration prompts. It fills placeholders and returns a prompt ready for runtime use.

---

## Practical Rules

- Put the important role, task, or rule language near the top of the prompt.
- Keep placeholders in the `{{name}}` format.
- Use `CLMEncoder` unless you specifically need the lower-level system prompt classes.
- If you want explicit control over prompt mode, set `prompt_mode` in `SysPromptConfig`.

---

## Next Steps

- Read [Task Prompt](task_prompt.md) for action-oriented prompts.
- Read [Configuration Prompt](configuration_prompt.md) for role- and rule-based prompts.
- Review [CLM Output](../advanced/clm_output.md) for metadata and output fields.
- Review [CLM Tokenization](../advanced/clm_tokenization.md) for the underlying token vocabulary.
