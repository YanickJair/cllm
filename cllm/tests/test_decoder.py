from collections import defaultdict
import json
import sys
import os

# Add the parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.decoder import CLLMDecoder


def load_compress_prompts() -> list[dict]:
    compressed_list = []
    with open("validation_results_5K.json", "r") as f:
        cp = json.load(f)

    for cp_ in cp[:100]:
        compressed_list.append({
            "compressed": cp_.get("compressed"),
            "expected": cp_.get("prompt")
        })
    return compressed_list


class DecoderValidationRunner:
    def __init__(self, decoder: CLLMDecoder):
        self.decoder: CLLMDecoder = decoder
        self.results = []
        self.stats = defaultdict()

    def run_validation(self, compressed_list: list[dict]) -> dict:
        print("\n" + "="*80)
        print("CLLM DECODER - FULL VALIDATION")
        print("="*80)
        print(f"\nValidating {len(compressed_list)} prompts...")
        print("This may take 1-2 minutes...\n")

        total = len(compressed_list)
        for i, compressed in enumerate(compressed_list):
            if i % 10 == 0:
                print(f"Progress: {i}/{total} ({i/total*100:.0f}%)")
            
            result = self.decoder.decompress(compressed.get("compressed"))
            self.results.append({
                "decoded": result,
                **compressed
            })
        print(f"\n✓ Validation complete!\n")



if __name__ == "__main__":
    compressed_list = load_compress_prompts()
    validator = DecoderValidationRunner(decoder=CLLMDecoder())
    results = validator.run_validation(compressed_list)
    with open("decoded_100_prompts.json", "w") as f:
        json.dump(validator.results, f)
