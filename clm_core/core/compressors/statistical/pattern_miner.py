import hashlib
import re
from collections import Counter
from datetime import datetime
from typing import Annotated

from annotated_doc import Doc

from .schemas import Pattern


class PatternMiner:
    def __init__(
        self,
        min_frequency: Annotated[
            int,
            Doc(
                "Minimum number of occurrences required for a token n-gram to qualify as a pattern."
            ),
        ] = 10,
        min_tokens: Annotated[
            int,
            Doc("Minimum number of tokens a pattern must contain to be considered."),
        ] = 2,
    ) -> None:
        self.min_frequency = min_frequency
        self.min_tokens = min_tokens
        self.patterns: dict = {}  # pattern_hash -> Pattern object

    def mine_patterns(
        self,
        compressed_corpus: Annotated[
            list[str],
            Doc("List of compressed token sequences to mine for frequent n-gram patterns."),
        ],
        original_corpus: Annotated[
            list[str] | None,
            Doc("Optional list of original prompts used to collect pattern examples."),
        ] = None,
    ) -> list[Pattern]:
        """Mine patterns from a corpus of compressed prompts."""
        ngram_counts = self._extract_ngrams(compressed_corpus)

        frequent_patterns = {
            ngram: count for ngram, count in ngram_counts.items() if count >= self.min_frequency
        }

        filtered_patterns = self._filter_subsumed(frequent_patterns)

        patterns: list[Pattern] = []
        for pattern_str, frequency in filtered_patterns.items():
            pattern = self._create_pattern(
                pattern_tuple=pattern_str,
                frequency=frequency,
                compressed_corpus=compressed_corpus,
                original_corpus=original_corpus,
            )
            patterns.append(pattern)
            self.patterns[pattern.id] = pattern

        patterns.sort(key=lambda p: p.value_score, reverse=True)
        return patterns

    def _extract_ngrams(
        self,
        compressed_corpus: Annotated[
            list[str],
            Doc("List of compressed token strings from which to extract token n-grams."),
        ],
    ) -> Counter:
        """Extract all token n-grams from corpus"""
        ngrams: Counter = Counter()

        for compressed in compressed_corpus:
            tokens = re.findall(r"\[[^\]]+\]", compressed)
            for n in range(self.min_tokens, min(6, len(tokens) + 1)):
                for i in range(len(tokens) - n + 1):
                    ngram = tuple(tokens[1 : i + n])
                    ngrams[ngram] += 1

        return ngrams

    def _filter_subsumed(
        self,
        patterns: Annotated[
            dict[tuple, int],
            Doc(
                "Dict mapping token n-gram tuples to their occurrence counts, to be pruned of subsumed entries."
            ),
        ],
    ) -> dict[tuple, int]:
        """Remove patterns that are substrings of more frequent longer patterns"""
        filtered: dict[tuple, int] = {}
        sorted_patterns = sorted(patterns.items(), key=lambda x: (len(x[0]), x[1]), reverse=True)

        for pattern, count in sorted_patterns:
            is_subsumed = False
            for longer_pattern in filtered:
                if self._is_subsequence(pattern, longer_pattern):
                    if filtered[longer_pattern] >= count * 0.8:
                        is_subsumed = True
                        break

            if not is_subsumed:
                filtered[pattern] = count
        return filtered

    @staticmethod
    def _is_subsequence(
        short: Annotated[tuple, Doc("The shorter n-gram tuple to check for containment.")],
        long: Annotated[tuple, Doc("The longer n-gram tuple to search within.")],
    ) -> bool:
        """Check if short is a contiguous subsequence of long"""
        for i in range(len(long) - len(short) + 1):
            if long[i : i + len(short)] == long:
                return True
        return False

    def _create_pattern(
        self,
        pattern_tuple: Annotated[
            tuple[str], Doc("N-gram token tuple representing the pattern string.")
        ],
        frequency: Annotated[int, Doc("Number of times this n-gram was observed in the corpus.")],
        compressed_corpus: Annotated[
            list[str],
            Doc("Full corpus of compressed token strings used to collect pattern examples."),
        ],
        original_corpus: Annotated[
            list[str] | None,
            Doc("Optional list of original prompts aligned with compressed_corpus for examples."),
        ] = None,
    ) -> Pattern:
        """Create Pattern object from n-gram."""
        pattern_str = " ".join(pattern_tuple)

        pattern_hash = hashlib.md5(pattern_str.encode()).hexdigest()[:8].upper()
        pattern_id = f"PTTN_{pattern_hash}"

        original_tokens = len(pattern_tuple)
        ref_tokens = 1
        compression_gain = original_tokens - ref_tokens

        examples = []
        for i, compressed in enumerate(compressed_corpus):
            if pattern_str in compressed:
                if original_corpus and i < len(original_corpus):
                    examples.append(original_corpus[i])
                if len(examples) >= 3:
                    break

        domains = self._detect_domains(examples)
        return Pattern(
            id=pattern_id,
            pattern=pattern_str,
            frequency=frequency,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            compression_gain=compression_gain,
            domains=domains,
            examples=examples,
            version=1,
        )

    @staticmethod
    def _detect_domains(
        examples: Annotated[
            list[str],
            Doc("Sample original prompts used to infer which domains this pattern belongs to."),
        ],
    ) -> list[str]:
        """Detect which domains this pattern belongs to"""
        domains = set()
        domain_keywords = {
            "customer_support": ["customer", "ticket", "support", "complaint"],
            "code_analysis": [
                "code",
                "function",
                "bug",
                "debug",
                "python",
                "javascript",
            ],
            "data_analysis": ["data", "csv", "analyze", "extract", "metrics"],
            "content_generation": [
                "write",
                "draft",
                "generate",
                "create",
                "email",
                "produce",
                "design",
            ],
        }
        for example in examples:
            example_lower = example.lower()
            for domain, keywords in domain_keywords.items():
                if any(keyword in example_lower for keyword in keywords):
                    domains.add(domain)

        return list(domains) if domains else ["general"]
