"""
Optimized Pattern Discovery for CLLM
Uses settings tuned for semantic token compression
"""

import json
import re
from collections import Counter
from datetime import datetime
from typing import List


def extract_token_sequences(semantic_output: str, min_length: int = 2, max_length: int = 4) -> List[str]:
    """Extract all possible token sequences"""
    tokens = re.findall(r'\[[^\]]+\]', semantic_output)

    sequences = []
    for n in range(min_length, max_length + 1):
        for i in range(len(tokens) - n + 1):
            seq = ' '.join(tokens[i:i + n])
            sequences.append(seq)

    return sequences


def discover_patterns_optimized(corpus: List[str]) -> list:
    """
    Optimized pattern discovery with multiple strategies

    Strategy:
    - 2-token patterns: freq >= 2 (capture common pairs)
    - 3-token patterns: freq >= 2 (capture common triplets)
    - 4-token patterns: freq >= 3 (only very common longer patterns)
    """

    print("🔍 Discovering patterns with optimized settings...\n")

    all_patterns = []
    pattern_id = 1
    current_time = datetime.now()

    # Strategy 1: 2-token patterns (most common, freq >= 2)
    print("  Finding 2-token patterns (min_freq=2)...")
    sequences_2 = []
    for sem in corpus:
        sequences_2.extend(extract_token_sequences(sem, min_length=2, max_length=2))

    counts_2 = Counter(sequences_2)
    for seq, freq in counts_2.items():
        if freq >= 2:
            all_patterns.append({
                "id": f"PATTERN_{pattern_id:04d}",
                "pattern": seq,
                "frequency": freq,
                "first_seen": current_time.isoformat(),
                "last_seen": current_time.isoformat(),
                "compression_gain": 1,  # 2 tokens -> 1 REF = 1 saved
                "domains": [],
                "examples": [],
                "version": 1
            })
            pattern_id += 1

    print(f"    Found {len([p for p in all_patterns if p['compression_gain'] == 1])} patterns")

    # Strategy 2: 3-token patterns (freq >= 2)
    print("  Finding 3-token patterns (min_freq=2)...")
    sequences_3 = []
    for sem in corpus:
        sequences_3.extend(extract_token_sequences(sem, min_length=3, max_length=3))

    counts_3 = Counter(sequences_3)
    initial_count = len(all_patterns)
    for seq, freq in counts_3.items():
        if freq >= 2:
            all_patterns.append({
                "id": f"PATTERN_{pattern_id:04d}",
                "pattern": seq,
                "frequency": freq,
                "first_seen": current_time.isoformat(),
                "last_seen": current_time.isoformat(),
                "compression_gain": 2,  # 3 tokens -> 1 REF = 2 saved
                "domains": [],
                "examples": [],
                "version": 1
            })
            pattern_id += 1

    print(f"    Found {len(all_patterns) - initial_count} patterns")

    # Strategy 3: 4-token patterns (freq >= 3, more selective)
    print("  Finding 4-token patterns (min_freq=3)...")
    sequences_4 = []
    for sem in corpus:
        sequences_4.extend(extract_token_sequences(sem, min_length=4, max_length=4))

    counts_4 = Counter(sequences_4)
    initial_count = len(all_patterns)
    for seq, freq in counts_4.items():
        if freq >= 3:
            all_patterns.append({
                "id": f"PATTERN_{pattern_id:04d}",
                "pattern": seq,
                "frequency": freq,
                "first_seen": current_time.isoformat(),
                "last_seen": current_time.isoformat(),
                "compression_gain": 3,  # 4 tokens -> 1 REF = 3 saved
                "domains": [],
                "examples": [],
                "version": 1
            })
            pattern_id += 1

    print(f"    Found {len(all_patterns) - initial_count} patterns")

    # Sort by value (frequency × compression_gain)
    all_patterns.sort(key=lambda p: p['frequency'] * p['compression_gain'], reverse=True)

    print(f"\n✅ Total patterns discovered: {len(all_patterns)}")

    # Calculate potential savings
    total_savings = sum(p['frequency'] * p['compression_gain'] for p in all_patterns)
    print(f"   Potential tokens saved: {total_savings}")

    return all_patterns


def save_patterns(patterns: list, output_file: str = "patterns.json"):
    """Save patterns to file"""
    total_uses = sum(p['frequency'] for p in patterns)
    total_tokens_saved = sum(p['frequency'] * p['compression_gain'] for p in patterns)
    avg_gain = sum(p['compression_gain'] for p in patterns) / len(patterns) if patterns else 0
    most_used = max(patterns, key=lambda p: p['frequency']) if patterns else None

    data = {
        "patterns": patterns,
        "stats": {
            "total_patterns": len(patterns),
            "total_uses": total_uses,
            "total_tokens_saved": total_tokens_saved,
            "avg_compression_gain": avg_gain,
            "most_used_pattern": most_used
        }
    }

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n💾 Saved to {output_file}")


def show_top_patterns(patterns: list, n: int = 20):
    """Display top patterns"""
    print(f"\n🔥 Top {n} patterns by value:")
    print("-" * 80)
    print(f"{'#':<4} {'Freq':<6} {'Gain':<6} {'Value':<7} Pattern")
    print("-" * 80)

    for i, p in enumerate(patterns[:n], 1):
        value = p['frequency'] * p['compression_gain']
        print(f"{i:<4} {p['frequency']:<6} {p['compression_gain']:<6} {value:<7} {p['pattern'][:55]}")


def main():
    """Main optimized discovery"""
    print("\n" + "=" * 80)
    print("🚀 CLLM OPTIMIZED PATTERN DISCOVERY")
    print("=" * 80 + "\n")

    # Load corpus
    print("📂 Loading semantic corpus...")
    try:
        with open("validation_results_100.json") as f:
            data = json.load(f)

        corpus = [item['compressed'] for item in data
                  if item.get('compressed') and len(item['compressed']) > 0]

        print(f"   Loaded {len(corpus)} semantic outputs\n")

    except FileNotFoundError:
        print("❌ validation_results_5K.json not found!")
        return

    # Discover patterns
    print("=" * 80)
    patterns = discover_patterns_optimized(corpus)

    if not patterns:
        print("\n❌ No patterns found!")
        return

    # Show results
    show_top_patterns(patterns, n=30)

    # Save
    print("\n" + "=" * 80)
    save_patterns(patterns)

    print("\n✅ Pattern discovery complete!")
    print("\n📋 Next steps:")
    print("   1. Run: python test_statistical_compression.py")
    print("   2. Check for improved compression results")
    print()


if __name__ == "__main__":
    main()