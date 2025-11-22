import json
import sys
from pathlib import Path

# Add the cllm directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "cllm"))

from src.core.encoder import CLLMEncoder


def load_prompts() -> list[dict[str, str]]:
    data: list[dict[str, str]] = []
    with open("./data/raw/system_prompts.json", "r") as f:
        data = json.load(f)
    return data

def main(prompt):
    encoder = CLLMEncoder()

    compressed = encoder.encode(prompt, verbose=True)  # type: ignore
    print("Compressed 1", compressed.compressed)

main("""You are a Call QA & Compliance Scoring System for customer service operations.

TASK:
Analyze the transcript and score the agent’s compliance across required QA categories.

ANALYSIS CRITERIA:

Mandatory disclosures and verification steps

Policy adherence

Soft-skill behaviors (empathy, clarity, ownership)

Process accuracy

Compliance violations or risks

Customer sentiment trajectory

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
0.90–1.00: Excellent""")
if __name__ == "__main__":
    pass
    # main(load_prompts())
