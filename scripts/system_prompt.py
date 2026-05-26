import json

from clm_core import CLMEncoder, PromptMode, SysPromptConfig
from clm_core import CLMConfig


def load_prompts() -> list[dict[str, str]]:
    data: list[dict[str, str]] = []
    with open("./data/raw/system_prompts_corpus.json", "r") as f:
        data = json.load(f)
    return data

def single_prompt():
    prompt = """
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
    """
    cfg = CLMConfig(
        lang="en",
        sys_prompt_config=SysPromptConfig(
            infer_types=False,
            add_attrs=False,
            prompt_mode=PromptMode.CONFIGURATION,
            use_structured_output_abstraction=True
        )
    )
    encoder = CLMEncoder(cfg=cfg)
    compressed = encoder.encode(prompt, verbose=False)

    if compressed:
        compressed.compressed = encoder.bind(out=compressed, **{"account_tier": "premium", "customer_name": "Yanick", "language": "en"})
        print(compressed.compressed, compressed.n_tokens, compressed.c_tokens, compressed.compression_ratio)

def main(prompts):
    cfg = CLMConfig(
        lang="en",
        sys_prompt_config=SysPromptConfig(
            infer_types=False,
            add_attrs=False,
            use_structured_output_abstraction=True
        )
    )
    encoder = CLMEncoder(cfg=cfg)
    results = []

    for prompt in prompts:
        compressed = encoder.encode(prompt.get("prompt"), verbose=False)  # type: ignore
        if compressed:
            compressed.compressed = encoder.bind(compressed, **prompt.get("placeholders", {}))
            compressed.metadata["placeholders"] = prompt.get("placeholders", {})
            results.append(compressed.model_dump())
        else:
            print("failed for ", prompt)

    with open("sys_prompt_compression-v3.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    # main(load_prompts())
    single_prompt()
