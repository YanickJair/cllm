import re
from typing import Any

from src.core.compressors.statistical.pattern_db import PatternDatabase
from src.core.compressors.statistical.schemas import Pattern


class StatisticalCompressor:
    def __init__(self, pattern_db: PatternDatabase, min_pattern_length: int = 2):
        self.pattern_db = pattern_db
        self.min_pattern_length = min_pattern_length

    def compress(
        self, semantic_tokens: str, domain: str | None = None
    ) -> tuple[str, dict]:
        """
        Apply statistical compression by replacing patterns with REF tokens

        Args:
            semantic_tokens: Output from semantic encoder
            domain: Optional domain hint for better pattern matching

        Returns:
            (compressed_output, metadata)
        """
        metadata: dict[str, Any] = {
            "original_tokens": len(re.findall(r"\[[^\]]+\]", semantic_tokens)),
            "patterns_applied": [],
            "tokens_saved": 0,
            "pattern_coverage": 0.0,
        }

        patterns = self.pattern_db.get_top_patterns(n=100, domain=domain)

        if not patterns:
            return semantic_tokens, metadata

        matches: list[dict] = []
        for pattern in patterns:
            if pattern.pattern in semantic_tokens:
                pos = 0
                while True:
                    idx = semantic_tokens.find(pattern.pattern, pos)
                    if idx == -1:
                        break
                    matches.append(
                        {
                            "pattern": pattern,
                            "start": idx,
                            "end": idx + len(pattern.pattern),
                            "length": len(pattern.pattern),
                        }
                    )
                    pos = idx + 1
        if not matches:
            return semantic_tokens, metadata

        # Sort by start position and resolve overlaps (greedy: prefer longer/higher value patterns)
        matches.sort(key=lambda m: (m["start"], -m["pattern"].value_score))
        selected_matches = []
        last_end = 0
        for match in matches:
            if match["start"] >= last_end:
                selected_matches.append(match)
                last_end = match["end"]

        compressed = semantic_tokens
        for match in reversed(selected_matches):
            p: Pattern = match["pattern"]
            ref_token = p.ref_token

            compressed = (
                compressed[: match["start"]] + ref_token + compressed[match["end"] :]
            )

            metadata.get("patterns_applied", []).append(
                {
                    "pattern_id": p.id,
                    "pattern": p.pattern,
                    "ref_token": ref_token,
                    "tokens_saved": p.compression_gain,
                }
            )
            metadata["tokens_saved"] += p.compression_gain

        final_token_count = len(re.findall(r"\[[^\]]+\]", compressed))
        metadata["compressed_tokens"] = final_token_count
        metadata["additional_compression_ratio"] = (
            metadata["tokens_saved"] / metadata["original_tokens"]
            if metadata["original_tokens"] > 0
            else 0.0
        )

        return compressed, metadata

    def batch_compress(
        self, semantic_corpus: list[str], domains: list[str | None] | None = None
    ) -> list[tuple[str, dict]]:
        """Batch compress multiple prompts"""
        if domains is None:
            domains = [None] * len(semantic_corpus)

        results = []
        for semantic_tokens, domain in zip(semantic_corpus, domains):
            compressed, metadata = self.compress(semantic_tokens, domain)
            results.append((compressed, metadata))

        return results
