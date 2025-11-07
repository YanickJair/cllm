import json

from src.core.compressors.statistical.pattern_db import PatternDatabase
from src.core.compressors.statistical.pattern_matcher import StatisticalCompressor

# Load patterns
pattern_db = PatternDatabase("patterns.json")
compressor = StatisticalCompressor(pattern_db)

# Load your validation results
with open("validation_results_100.json", "r") as f:
    validation_data = json.load(f)

# Test on a few examples
print("=" * 80)
print("STATISTICAL COMPRESSION WITH REF TOKENS")
print("=" * 80)

test_cases = validation_data  # First 10 prompts

total_original = 0
total_compressed = 0
total_with_ref = 0

for i, item in enumerate(test_cases, 1):
    original = item["prompt"]
    semantic = item["compressed"]

    # Apply statistical compression
    with_ref, metadata = compressor.compress(semantic, domain="customer_support")

    original_tokens = len(original.split())
    semantic_tokens = len(semantic.split())
    ref_tokens = len(with_ref.split())

    total_original += original_tokens
    total_compressed += semantic_tokens
    total_with_ref += ref_tokens

    if metadata["patterns_applied"]:  # Only show cases where REF was applied
        print(f"\n--- Example {i} ---")
        print(f"Original ({original_tokens} tokens):")
        print(f"  {original[:100]}...")
        print(f"\nSemantic ({semantic_tokens} tokens):")
        print(f"  {semantic}")
        print(f"\nWith REF ({ref_tokens} tokens):")
        print(f"  {with_ref}")
        print(f"\nPatterns applied: {len(metadata['patterns_applied'])}")
        for pattern_info in metadata["patterns_applied"]:
            print(
                f"  - {pattern_info['pattern_id']}: saved {pattern_info['tokens_saved']} tokens"
            )

print("\n" + "=" * 80)
print("OVERALL STATISTICS")
print("=" * 80)
print(f"Original:         {total_original} tokens")
print(
    f"Semantic:         {total_compressed} tokens ({(1 - total_compressed / total_original) * 100:.1f}% compression)"
)
print(
    f"With REF:         {total_with_ref} tokens ({(1 - total_with_ref / total_original) * 100:.1f}% compression)"
)
print(f"REF improvement:  {total_compressed - total_with_ref} additional tokens saved")
print(
    f"                  ({(1 - total_with_ref / total_compressed) * 100:.1f}% better than semantic)"
)
