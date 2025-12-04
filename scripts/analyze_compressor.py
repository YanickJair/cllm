"""
Analyze the compression potential of your corpus
Shows exactly what patterns exist and how much they could save
"""

import json
import re
from collections import Counter
from typing import List


def load_corpus():
    """Load semantic corpus"""
    with open("validation_results_100.json") as f:
        data = json.load(f)
    return [
        item["compressed"]
        for item in data
        if item.get("compressed") and len(item["compressed"]) > 0
    ]


def count_tokens(corpus: List[str]) -> int:
    """Count total tokens in corpus"""
    total = 0
    for sem in corpus:
        tokens = re.findall(r"\[[^\]]+\]", sem)
        total += len(tokens)
    return total


def analyze_pattern_potential(corpus: List[str], max_length: int = 4):
    """Analyze all possible patterns and their compression potential"""

    print("=" * 80)
    print("📊 COMPRESSION POTENTIAL ANALYSIS")
    print("=" * 80 + "\n")

    total_tokens = count_tokens(corpus)
    print(f"Corpus size: {len(corpus)} prompts, {total_tokens} total tokens\n")

    # Analyze patterns at different lengths and frequencies
    results = {}

    for length in range(2, max_length + 1):
        print(f"\n{'=' * 80}")
        print(f"ANALYZING {length}-TOKEN PATTERNS")
        print("=" * 80)

        # Extract all sequences of this length
        all_sequences = []
        for sem in corpus:
            tokens = re.findall(r"\[[^\]]+\]", sem)
            for i in range(len(tokens) - length + 1):
                seq = " ".join(tokens[i : i + length])
                all_sequences.append(seq)

        sequence_counts = Counter(all_sequences)

        # Analyze at different frequency thresholds
        for min_freq in [2, 3, 5, 10, 20]:
            qualifying = {
                seq: count
                for seq, count in sequence_counts.items()
                if count >= min_freq
            }

            if not qualifying:
                continue

            # Calculate potential savings
            total_occurrences = sum(qualifying.values())
            compression_gain_per_pattern = length - 1
            tokens_saved = total_occurrences * compression_gain_per_pattern
            compression_pct = (tokens_saved / total_tokens) * 100

            results[(length, min_freq)] = {
                "num_patterns": len(qualifying),
                "total_occurrences": total_occurrences,
                "tokens_saved": tokens_saved,
                "compression_pct": compression_pct,
            }

            print(f"\n  Min frequency: {min_freq}")
            print(f"    Patterns found:     {len(qualifying):4d}")
            print(f"    Total occurrences:  {total_occurrences:5d}")
            print(f"    Tokens saved:       {tokens_saved:5d}")
            print(f"    Compression gain:   {compression_pct:5.2f}%")

    # Find optimal configuration
    print(f"\n\n{'=' * 80}")
    print("🎯 OPTIMAL CONFIGURATION ANALYSIS")
    print("=" * 80 + "\n")

    best_config = max(results.items(), key=lambda x: x[1]["tokens_saved"])
    length, min_freq = best_config[0]
    stats = best_config[1]

    print("Best single configuration:")
    print(f"  Length: {length} tokens")
    print(f"  Min frequency: {min_freq}")
    print(f"  Patterns: {stats['num_patterns']}")
    print(f"  Tokens saved: {stats['tokens_saved']} ({stats['compression_pct']:.2f}%)")

    # Simulate combined approach (2-token + 3-token patterns)
    print("\n\nCombined approach simulation:")

    for combo in [(2, 2), (2, 3), (3, 3), (3, 5)]:
        length, freq = combo
        if (length, freq) in results:
            s = results[(length, freq)]
            print(
                f"  Length={length}, MinFreq={freq}: {s['tokens_saved']:5d} tokens ({s['compression_pct']:.2f}%)"
            )

    return results


def show_top_patterns(
    corpus: List[str], length: int = 2, min_freq: int = 2, top_n: int = 30
):
    """Show the most valuable patterns"""

    print(f"\n\n{'=' * 80}")
    print(f"🔥 TOP {top_n} MOST VALUABLE {length}-TOKEN PATTERNS (freq >= {min_freq})")
    print("=" * 80 + "\n")

    # Extract sequences
    all_sequences = []
    for sem in corpus:
        tokens = re.findall(r"\[[^\]]+\]", sem)
        for i in range(len(tokens) - length + 1):
            seq = " ".join(tokens[i : i + length])
            all_sequences.append(seq)

    sequence_counts = Counter(all_sequences)

    # Filter and calculate value
    patterns = []
    for seq, count in sequence_counts.items():
        if count >= min_freq:
            compression_gain = length - 1
            value = count * compression_gain
            patterns.append(
                {
                    "pattern": seq,
                    "frequency": count,
                    "gain": compression_gain,
                    "value": value,
                }
            )

    # Sort by value
    patterns.sort(key=lambda x: x["value"], reverse=True)

    print(f"{'Rank':<6} {'Freq':<6} {'Gain':<6} {'Value':<7} Pattern")
    print("-" * 80)

    for i, p in enumerate(patterns[:top_n], 1):
        print(
            f"{i:<6} {p['frequency']:<6} {p['gain']:<6} {p['value']:<7} {p['pattern']}"
        )

    total_value = sum(p["value"] for p in patterns[:top_n])
    print("-" * 80)
    print(f"Total value of top {top_n}: {total_value} tokens\n")

    return patterns[:top_n]


def recommend_settings(results: dict):
    """Recommend optimal discovery settings"""

    print(f"\n{'=' * 80}")
    print("💡 RECOMMENDED SETTINGS")
    print("=" * 80 + "\n")

    # Find configurations that give > 1% compression
    good_configs = [(k, v) for k, v in results.items() if v["compression_pct"] > 1.0]

    if good_configs:
        print("✅ Good configurations (> 1% compression):\n")
        for (length, freq), stats in sorted(
            good_configs, key=lambda x: x[1]["compression_pct"], reverse=True
        ):
            print(f"  Length={length}, MinFreq={freq}:")
            print(
                f"    → {stats['tokens_saved']} tokens saved ({stats['compression_pct']:.2f}%)"
            )
    else:
        print("⚠️  No single configuration gives > 1% compression")
        print("    Your corpus may have high diversity\n")

        # Show best available
        best = max(results.items(), key=lambda x: x[1]["tokens_saved"])
        (length, freq), stats = best
        print(f"  Best available: Length={length}, MinFreq={freq}")
        print(
            f"    → {stats['tokens_saved']} tokens saved ({stats['compression_pct']:.2f}%)"
        )

    print("\n📋 Recommended discover_patterns.py settings:")
    print("-" * 80)

    # Multi-length strategy
    total_potential = sum(
        v["tokens_saved"] for k, v in results.items() if k[1] <= 3
    )  # Low frequency threshold
    total_pct = (total_potential / count_tokens(load_corpus())) * 100

    print(f"""
discover_patterns(
    corpus,
    min_frequency=2,     # Lower threshold to capture more patterns
    min_length=2,        # Start with 2-token patterns
    max_length=3         # Keep length modest for better matching
)

Expected improvement: ~{total_pct:.1f}% additional compression
""")


def main():
    """Run full analysis"""
    print("\n")

    # Load corpus
    corpus = load_corpus()

    # Analyze potential
    results = analyze_pattern_potential(corpus, max_length=4)

    # Show top patterns for recommended config
    show_top_patterns(corpus, length=2, min_freq=2, top_n=30)
    show_top_patterns(corpus, length=3, min_freq=2, top_n=20)

    # Recommendations
    recommend_settings(results)

    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Update discover_patterns.py with recommended settings")
    print("  2. Re-run pattern discovery")
    print("  3. Test compression again")
    print()


if __name__ == "__main__":
    main()
