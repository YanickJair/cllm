# Task Prompt Encoding

Task prompts are system prompts that tell the model to do a specific job.

Use this format when the prompt is centered on:

- analyzing something
- extracting fields
- generating content
- transforming text or data
- validating or classifying input

If the prompt reads like "You are a ...", use [Configuration Prompt](configuration_prompt.md) instead.

---

## What A Task Prompt Usually Contains

A good task prompt usually has three parts:

1. Who the model is
2. What the model should do
3. How the output should look

Example:

```text
You are a customer service quality analyst.
Analyze call transcripts for compliance violations and sentiment issues.
Return the result as JSON.
```

CLM turns that into a compact token sequence that preserves the task, target, and output structure.

---

## Quick Start

```python
from clm_core import CLMConfig, CLMEncoder

cfg = CLMConfig(lang="en")
encoder = CLMEncoder(cfg=cfg)

task_prompt = """
You are a customer service quality analyst.
Analyze call transcripts for compliance violations and sentiment issues.
Return the result as JSON.
"""

result = encoder.encode(task_prompt)
print(result.compressed)
print(result.compression_ratio)
```

Example compressed output:

```text
[REQ:ANALYZE][TARGET:TRANSCRIPT:DOMAIN=QA][EXTRACT:COMPLIANCE,SENTIMENT,ISSUE][OUT_JSON:{summary,qa_scores,violations,recommendations}]
```

The exact token details depend on the prompt wording and the `SysPromptConfig` options you use.

---

## How To Write A Better Task Prompt

Keep the prompt direct and focused.

### Good ingredients

- a single primary action
- the object being acted on
- the output shape or schema
- any constraints that change the answer

### Avoid

- long role descriptions
- repeated rule reminders
- template-style placeholders
- extra background that does not change the task

### Example

Better:

```text
Analyze the transcript for compliance violations and sentiment issues.
Return JSON with summary, violations, and recommendations.
```

Less clear:

```text
You are an AI assistant. Your role is to analyze this transcript carefully and thoughtfully.
Please follow the instructions and make sure the output is useful.
```

---

## Configuration Options

Task prompt compression is controlled by `SysPromptConfig`.

```python
from clm_core import CLMConfig, SysPromptConfig

cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(
        infer_types=False,
        add_attrs=False,
    ),
)
```

Useful options:

- `infer_types`: adds explicit type hints to structured output
- `add_attrs`: keeps extra attributes like enums, ranges, or categories
- `use_structured_output_abstraction`: controls whether output schema text is abstracted into CL tokens

If you want the simplest setup, use the defaults.

---

## What To Expect In The Output

The compressed result usually reflects:

- the main request
- the target object
- extraction fields or task-specific details
- the output format

Example metadata fields may include:

- `prompt_mode`
- `target`
- `extractions`
- `output_format`

---

## When To Use This Encoder Directly

Use the task prompt encoder when the prompt is clearly task-focused and you want the compressed form without extra configuration-prompt handling.

Use the higher-level `CLMEncoder` when you want CLM to decide whether the prompt is task-oriented or configuration-oriented.

---

## Next Steps

- Read [System Prompt Encoder](index.md) for the full flow.
- Read [Configuration Prompt](configuration_prompt.md) for template-style prompts.
- Review [CLM Tokenization](../advanced/clm_tokenization.md) for the token vocabulary.
