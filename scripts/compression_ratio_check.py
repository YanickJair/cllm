input_ = """You are a Call QA & Compliance Scoring System for customer service operations.

TASK:
Analyze the transcript and score the agent's compliance across required QA categories.

ANALYSIS CRITERIA:
- Mandatory disclosures and verification steps
- Policy adherence
- Soft-skill behaviors (empathy, clarity, ownership)
- Compliance violations or risks

OUTPUT FORMAT:
{
    "summary": "short_summary",
    "qa_scores": {"verification": 0.0, "policy_adherence": 0.0, "soft_skills": 0.0},
    "violations": ["list_any_detected"]
}"""

from clm_core import CLMEncoder, CLMConfig, SysPromptConfig, DataTypes, OutputMode


cfg = CLMConfig(
    lang="en",
    sys_prompt_config=SysPromptConfig(infer_types=True, output_mode=OutputMode.MINIMIZED),
)
encoder = CLMEncoder(cfg=cfg)
encoded = encoder.encode(input_=input_, verbose=True, data_type=DataTypes.SYSTEM_PROMPT)

if encoded:
    print("Ratio", encoded.compression_ratio)
    print(encoded.compressed)
