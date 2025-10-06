import json

from src.core.compressors.statistical.pattern_db import PatternDatabase
from src.core.compressors.statistical.pattern_matcher import StatisticalCompressor
from src.core.compressors.statistical.pattern_trainer import StatisticalTrainer
from src.core.encoder import CLLMEncoder


def main():
    encoder = CLLMEncoder()

    test_prompts = [
        "Analyze this Python code and identify any potential bugs or security vulnerabilities.",
        "Extract all dates, names, and monetary amounts from this legal document and format as JSON.",
        "Summarize this customer support transcript briefly and identify the main issue.",
        "Generate a professional email declining a job offer while expressing gratitude.",
        "Explain quantum computing to a 10-year-old using simple analogies."
    ]
    
    print("\n" + "="*80)
    print("CLLM ENCODER - DEMO")
    print("="*80)
    
    # Compress each prompt
    for prompt in test_prompts:
        result = encoder.compress(prompt, verbose=True)
        print(result)


def pattern_train():
    with open("data/processed/validation_results_100.json", "r") as f:
        validation_data = json.load(f)

    compressed_corpus = [item["compressed"] for item in validation_data]
    original_corpus = [item["prompt"] for item in validation_data]

    pattern_db = PatternDatabase("data/processed/cllm_patterns.json")
    trainer = StatisticalTrainer(
        pattern_db,
        min_frequency=3,  # Lower threshold for small corpus
        min_compression_gain=2.0
    )
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

    compressor = StatisticalCompressor(pattern_db)
    semantic_output = "[REQ:ANALYZE] [TARGET:TRANSCRIPT:DOMAIN=SUPPORT] [EXTRACT:ISSUE+SENTIMENT]"
    compressed, metadata = compressor.compress(semantic_output, domain="customer_support")

    print("\n=== Compression Example ===")
    print(f"Semantic: {semantic_output}")
    print(f"Statistical: {compressed}")
    print(f"Additional compression: {metadata.get('additional_compression_ratio', 0.0):.1%}")
    print(f"Patterns applied: {len(metadata.get('patterns_applied', []))}")


if __name__ == "__main__":
    main()
    pattern_train()
