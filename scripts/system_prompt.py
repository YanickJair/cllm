import json

from clm_core import CLMEncoder, SysPromptConfig
from clm_core import CLMConfig

def load_prompts() -> list[dict[str, str]]:
    data: list[dict[str, str]] = []
    with open("./data/raw/system_prompts.json", "r") as f:
        data = json.load(f)
    return data

def single_prompt():
    nl_spec = """
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
    0.00–0.49: Fail
    0.50–0.74: Needs Improvement
    0.75–0.89: Good
    0.90–1.00: Excellent
    """
    cfg = CLMConfig(
        lang="en",
        sys_prompt_config=SysPromptConfig(
            infer_types=True,
            add_attrs=True,
        )
    )
    encoder = CLMEncoder(cfg=cfg)
    compressed = encoder.encode(nl_spec, verbose=False)
    print(compressed.compressed, compressed.compression_ratio)

def main(prompts):
    cfg = CLMConfig(
        lang="en",
        sys_prompt_config=SysPromptConfig(
            infer_types=True,
            add_attrs=True,
        )
    )
    encoder = CLMEncoder(cfg=cfg)
    results = []

    for prompt in prompts:
        compressed = encoder.encode(prompt.get("prompt"), verbose=False)  # type: ignore
        if compressed:
            results.append(compressed.model_dump())
        else:
            print("failed for ", prompt)

    with open("sys_prompt_compression-v2.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    main(load_prompts())
    # single_prompt()
