# Phase 1: Train statistical compressor on your 100 validated prompts

# Load your validation results
import json

from src.core.compressors.statistical.pattern_db import PatternDatabase
from src.core.compressors.statistical.pattern_matcher import StatisticalCompressor
from src.core.compressors.statistical.pattern_trainer import StatisticalTrainer

with open("validation_results_100.json", "r") as f:
    validation_data = json.load(f)

print("Data size:", len(validation_data))
# Extract compressed prompts
compressed_corpus = [item["compressed"] for item in validation_data]
original_corpus = [item["prompt"] for item in validation_data]

# Initialize
pattern_db = PatternDatabase("cllm_patterns.json")
trainer = StatisticalTrainer(
    pattern_db,
    min_frequency=3,  # Lower threshold for small corpus
    min_compression_gain=2.0
)

# Train
stats = trainer.train(compressed_corpus, original_corpus)

print("\n=== Training Results ===")
print(f"Patterns discovered: {stats['patterns_discovered']}")
print(f"Patterns added to DB: {stats['patterns_added']}")
print(f"Estimated tokens saved: {stats['estimated_tokens_saved']}")

print("\n=== Top 10 Patterns ===")
for i, pattern in enumerate(stats['top_patterns'], 1):
    print(f"{i}. {pattern['id']} (used {pattern['frequency']}x)")
    print(f"   Pattern: {pattern['pattern']}")
    print(f"   Domains: {', '.join(pattern['domains'])}")
    print(f"   Saves: {pattern['compression_gain']} tokens/use")
    print(f"   Value: {pattern['value_score']}")
    print()

# Phase 2: Use statistical compressor

compressor = StatisticalCompressor(pattern_db)

# Compress a new prompt
semantic_output = "[REQ:ANALYZE] [TARGET:TRANSCRIPT:DOMAIN=SUPPORT] [EXTRACT:ISSUE+SENTIMENT]"
compressed, metadata = compressor.compress(semantic_output, domain="customer_support")

print("\n=== Compression Example ===")
print(f"Semantic: {semantic_output}")
print(f"Statistical: {compressed}")
# print(f"Additional compression: {metadata['additional_compression_ratio']:.1%}")
print(f"Patterns applied: {len(metadata['patterns_applied'])}")