import json
from datetime import datetime
from pathlib import Path

from src.core.compressors.statistical.schemas import Pattern, PatternStats


class PatternDatabase:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.patterns: dict[str, Pattern] = {}
        self.load()


    def load(self) -> None:
        """Load patterns from disk"""
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                data = json.load(f)
                for pattern_dict in data.get("patterns", []):
                    # Convert date strings back to datetime objects
                    if isinstance(pattern_dict.get('first_seen'), str):
                        pattern_dict['first_seen'] = datetime.fromisoformat(pattern_dict['first_seen'])
                    if isinstance(pattern_dict.get('last_seen'), str):
                        pattern_dict['last_seen'] = datetime.fromisoformat(pattern_dict['last_seen'])
                    pattern = Pattern(**pattern_dict)
                    self.patterns[pattern.id] = pattern

    def save(self) -> None:
        """Save patterns to disk"""
        stats = self.get_stats()
        data = {
            "patterns": [
                {
                    "id": p.id,
                    "pattern": p.pattern,
                    "frequency": p.frequency,
                    "first_seen": p.first_seen.isoformat(),
                    "last_seen": p.last_seen.isoformat(),
                    "compression_gain": p.compression_gain,
                    "domains": p.domains,
                    "examples": p.examples,
                    "version": p.version
                }
                for p in self.patterns.values()
            ],
            "stats": {
                "total_patterns": stats.total_patterns,
                "total_uses": stats.total_uses,
                "total_tokens_saved": stats.total_tokens_saved,
                "avg_compression_gain": stats.avg_compression_gain,
                "most_used_pattern": {
                    "id": stats.most_used_pattern.id,
                    "pattern": stats.most_used_pattern.pattern,
                    "frequency": stats.most_used_pattern.frequency,
                    "first_seen": stats.most_used_pattern.first_seen.isoformat(),
                    "last_seen": stats.most_used_pattern.last_seen.isoformat(),
                    "compression_gain": stats.most_used_pattern.compression_gain,
                    "domains": stats.most_used_pattern.domains,
                    "examples": stats.most_used_pattern.examples,
                    "version": stats.most_used_pattern.version
                } if stats.most_used_pattern else None
            }
        }

        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)

    def add_pattern(self, pattern: Pattern) -> None:
        """Add or update a pattern"""
        if pattern.id in self.patterns:
            # Update existing pattern
            existing = self.patterns[pattern.id]
            existing.frequency += pattern.frequency
            existing.last_seen = datetime.now()
        else:
            self.patterns[pattern.id] = pattern

    def add_patterns(self, patterns: list[Pattern]) -> None:
        """Bulk add patterns"""
        for pattern in patterns:
            self.add_pattern(pattern)
        self.save()

    def get_pattern(self, pattern_id: str) -> Pattern:
        return self.patterns[pattern_id]

    def get_top_patterns(self, n: int = 100, domain: str | None = None) -> list[Pattern]:
        """Get top N patterns by value score"""
        patterns = list(self.patterns.values())

        # Filter by domain if specified
        if domain:
            patterns = [p for p in patterns if domain in p.domains]

        # Sort by value score
        patterns.sort(key=lambda p: p.value_score, reverse=True)

        return patterns[:n]

    def search_patterns(self, token_sequence: str) -> list[tuple[Pattern, int]]:
        """
        Find patterns that match the token sequence
        Returns list of (pattern, start_position) tuples
        """
        matches = []
        for pattern in self.patterns.values():
            # Find all occurrences
            pos = 0
            while pos < len(token_sequence):
                idx = token_sequence.find(pattern.pattern, pos)
                if idx == -1:
                    break
                matches.append((pattern, idx))
                pos = idx + len(pattern.pattern)

        # Sort by position
        matches.sort(key=lambda x: x[1])
        return matches

    def get_stats(self) -> PatternStats:
        """Get database statistics"""
        if not self.patterns:
            return PatternStats(
                total_patterns=0,
                total_uses=0,
                total_tokens_saved=0,
                avg_compression_gain=0.0,
                most_used_pattern=None
            )

        total_uses = sum(p.frequency for p in self.patterns.values())
        total_tokens_saved = sum(p.frequency * p.compression_gain
                                 for p in self.patterns.values())
        avg_compression_gain = sum(p.compression_gain for p in self.patterns.values()) / len(self.patterns)
        most_used = max(self.patterns.values(), key=lambda p: p.frequency)

        return PatternStats(
            total_patterns=len(self.patterns),
            total_uses=total_uses,
            total_tokens_saved=int(total_tokens_saved),
            avg_compression_gain=avg_compression_gain,
            most_used_pattern=most_used
        )