import json
import sys
from pathlib import Path

# Add the cllm directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "cllm"))

from src.core.encoder import CLLMEncoder
from src.utils.schemas import CLMConfig

def load_prompts() -> list[dict[str, str]]:
    data: list[dict[str, str]] = []
    with open("./data/raw/system_prompts.json", "r") as f:
        data = json.load(f)
    return data

def main(prompts):
    cfg = CLMConfig(
        lang="en",
    )
    encoder = CLLMEncoder(cfg=cfg)
    results = []

    for prompt in prompts:
        compressed = encoder.encode(prompt.get("prompt"), verbose=True)  # type: ignore
        results.append(compressed.model_dump())

    with open("sys_prompt_compression-v2.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    main(load_prompts())
