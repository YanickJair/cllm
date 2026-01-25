import json

from clm_core import CLMEncoder, SysPromptConfig
from clm_core import CLMConfig


def load_prompts() -> list[dict[str, str]]:
    data: list[dict[str, str]] = []
    with open("./data/raw/system_prompts_corpus.json", "r") as f:
        data = json.load(f)
    return data

def single_prompt():
    nl_spec = """
    You are an AI assistant specialized in {{domain}} operations.\n\nYour role is to help users with {{task_type}} tasks while maintaining high standards of accuracy and professionalism.\n\nCore Capabilities:\n- Process and analyze {{domain}} data\n- Generate reports and recommendations\n- Answer questions about {{domain}} policies\n- Maintain compliance with industry standards\n\nGuidelines:\n- Always verify information before providing answers\n- Ask clarifying questions when requirements are ambiguous\n- Provide sources and references when applicable\n- Maintain confidentiality of sensitive information\n\nOutput should be clear, structured, and actionable.
    """
    cfg = CLMConfig(
        lang="en",
        sys_prompt_config=SysPromptConfig(
            infer_types=False,
            add_attrs=False,
            use_structured_output_abstraction=True
        )
    )
    encoder = CLMEncoder(cfg=cfg)
    compressed_1 = encoder.encode(nl_spec, verbose=False)

    compressed_1.compressed = encoder.bind(
        out=compressed_1, domain='language', task_type='user_instruction'
    )
    print(compressed_1.compressed, compressed_1.n_tokens, compressed_1.c_tokens, compressed_1.compression_ratio)

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
    main(load_prompts())
    # single_prompt()
