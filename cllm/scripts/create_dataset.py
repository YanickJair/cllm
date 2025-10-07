# Create dataset from prompt files
import json
from pathlib import Path


def load_data_file(path: str) -> list:
    path = Path(path)
    prompts = []
    print(path.exists())
    if path.exists():
        with open(path, 'r') as f:
            data = json.load(f)
            for i, d in enumerate(data):
                prompt = d.get("instruction")
                if input_ := d.get("input", None):
                    prompt += f"\n{input_}"

                prompts.append({
                    "id": f"general_{i+1:03d}",
                    "prompt": prompt,
                    "category": "general",
                    "subcategory": ""
                })
    return prompts


if __name__ == "__main__":
    data = load_data_file("./data/raw/alpaca_data_cleaned.json")
    with open("raw_set_of_instructions.json", "w") as f:
        json.dump(data, f)
