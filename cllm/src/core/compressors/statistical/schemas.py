from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Pattern:
    """Represents a discovered pattern"""
    id: str  # Unique identifier (e.g., "REF:CS_STD_001")
    pattern: str  # The token sequence
    frequency: int  # How many times seen
    first_seen: datetime  # When first discovered
    last_seen: datetime  # Most recent occurrence
    compression_gain: float  # Tokens saved per use
    domains: list[str]  # Which domains use this (e.g., ["customer_support"])
    examples: list[str]  # Original prompts that matched
    version: int  # Pattern version (for evolution)

    @property
    def ref_token(self) -> str:
        """Generate REF token for this pattern"""
        return f"[REF:{self.id}:v{self.version}]"

    @property
    def value_score(self) -> float:
        """Calculate value: frequency × compression gain"""
        return self.frequency * self.compression_gain


@dataclass
class PatternStats:
    """Statistics for pattern database"""
    total_patterns: int
    total_uses: int
    total_tokens_saved: int
    avg_compression_gain: float
    most_used_pattern: Optional[Pattern]