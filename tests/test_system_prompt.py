import json
import sys
from pathlib import Path


from clm_core import CLMEncoder
from clm_core import CLMConfig


def load_prompts() -> list[dict[str, str]]:
    data: list[dict[str, str]] = []
    with open("./data/raw/system_prompts.json", "r") as f:
        data = json.load(f)
    return data

def main(prompts):
    cfg = CLMConfig(
        lang="en",
    )
    encoder = CLMEncoder(cfg=cfg)
    results = []

    prt =  "You are a Call QA & Compliance Scoring System for customer service operations.\n\nTASK:\nAnalyze the transcript and score the agent’s compliance across required QA categories.\n\nANALYSIS CRITERIA:\n\nMandatory disclosures and verification steps\n\nPolicy adherence\n\nSoft-skill behaviors (empathy, clarity, ownership)\n\nProcess accuracy\n\nCompliance violations or risks\n\nCustomer sentiment trajectory\n\nOUTPUT FORMAT:\n\n{\n  \"summary\": \"short_summary\",\n  \"qa_scores\": {\n    \"verification\": 0.0,\n    \"policy_adherence\": 0.0,\n    \"soft_skills\": 0.0,\n    \"accuracy\": 0.0,\n    \"compliance\": 0.0\n  },\n  \"violations\": [\"list_any_detected\"],\n  \"recommendations\": [\"improvement_suggestions\"]\n}\n\n\nSCORING:\n0.00–0.49: Fail\n0.50–0.74: Needs Improvement\n0.75–0.89: Good\n0.90–1.00: Excellent"
    compressed = encoder.encode(prt, verbose=False)
    print(compressed.compressed)

if __name__ == "__main__":
    main(load_prompts())
