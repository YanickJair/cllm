from core.compressors.statistical.pattern_db import PatternDatabase
from core.compressors.statistical.pattern_miner import PatternMiner


class StatisticalTrainer:
    """Train the statistical compressor by discovering patterns from corpus"""

    def __init__(
        self,
        pattern_db: PatternDatabase,
        min_frequency: int = 10,
        min_compression_gain: float = 2.0,
    ) -> None:
        self.pattern_db = pattern_db
        self.pattern_miner = PatternMiner(min_frequency=min_frequency)
        self.min_compression_gain = min_compression_gain

    def train(self, compressed_corpus: list[str], original_corpus: list[str]) -> dict:
        """
        Train on a corpus of compressed prompts

        Args:
            compressed_corpus: Semantic encode outputs
            original_corpus: Original prompts (for examples)

        Returns:
            Training statistics
        """
        # Step 1: Mine patterns
        patterns = self.pattern_miner.mine_patterns(compressed_corpus, original_corpus)

        # Step 2: Filter by compression gain
        valuable_patterns = [
            p for p in patterns if p.compression_gain >= self.min_compression_gain
        ]

        self.pattern_db.add_patterns(valuable_patterns)
        stats = {
            "total_prompts": len(compressed_corpus),
            "patterns_discovered": len(patterns),
            "patterns_added": len(valuable_patterns),
            "total_patterns_in_db": len(self.pattern_db.patterns),
            "estimated_tokens_saved": sum(
                p.frequency * p.compression_gain for p in valuable_patterns
            ),
            "top_patterns": [
                {
                    "id": p.id,
                    "pattern": p.pattern,
                    "frequency": p.frequency,
                    "compression_gain": p.compression_gain,
                    "value_score": p.value_score,
                    "domains": p.domains,
                }
                for p in valuable_patterns[:10]
            ],
        }

        return stats
