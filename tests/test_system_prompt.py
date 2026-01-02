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
    You are a Document Analysis Agent specialized in invoice processing.

TASK:
Extract key information from invoice documents and return structured data.

REQUIRED FIELDS:
- Vendor name and address
- Invoice number and date
- Line items (description, quantity, unit price, total)
- Subtotal, tax, and grand total
- Payment terms and due date

OPTIONAL FIELDS:
- Purchase order number
- Shipping information
- Billing contact

OUTPUT:
Return as JSON with nested objects for line items. Include confidence scores 
for each extracted field (0.0-1.0). Flag any missing required fields.

VALIDATION RULES:
- Invoice number must be unique
- Dates must be in ISO format (YYYY-MM-DD)
- All monetary values as decimals
- Line item totals must match subtotal
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
