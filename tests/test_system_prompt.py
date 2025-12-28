import json

from clm_core import CLMEncoder
from clm_core import CLMConfig

def load_prompts() -> list[dict[str, str]]:
    data: list[dict[str, str]] = []
    with open("./data/raw/system_prompts.json", "r") as f:
        data = json.load(f)
    return data

def single_prompt():
    nl_spec = """Your response must be a list of dictionaries, where each dictionary represents an insight.
    Every dictionary should contain the following keys:
    • "insight" → a short description of the observation
    • "evidence" → the exact quote or behavior from the transcript supporting it
    • "impact" → a natural-language explanation of why it matters

    Do not use JSON, code blocks, or headings in the output.
    Just return the list of dictionaries directly as plain text."""
    cfg = CLMConfig(
        lang="en",
    )
    encoder = CLMEncoder(cfg=cfg)
    compressed = encoder.encode(nl_spec, verbose=False)
    print(compressed.compressed)

def main(prompts):
    cfg = CLMConfig(
        lang="en",
    )
    encoder = CLMEncoder(cfg=cfg)
    results = []

    for prompt in prompts:
        compressed = encoder.encode(prompt.get("prompt"), verbose=False)  # type: ignore
        results.append(compressed.model_dump())
        break

    with open("sys_prompt_compression-v2.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    # main(load_prompts())
    single_prompt()
