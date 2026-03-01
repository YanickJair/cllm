import re
from typing import Any

from . import (
    ConditionalEntropyResult,
    OPTIONAL_FIELDS,
    CRITICAL_FIELDS,
    FieldResult,
    FIELD_SCHEMA,
)


class ConditionalEntropyAnalyzer:
    """
    Estimates H(Structured | Compressed) using the CLLM structured extraction
    dict as the authoritative source of truth.

    The structured dict is what CLLM already extracted from the raw transcript.
    The compressed token string is the final output the LLM receives.
    This analyzer verifies that the tokenization step did not silently drop
    any of the semantic content the extractor already found.

    Input:
        structured: dict  — the full CLLM extraction result, e.g.:
            {
                'channel': 'VOICE',
                'customerIntent': 'REPORT_BILLING_ISSUE',
                'sentiment': ['NEUTRAL', 'SATISFIED', 'GRATEFUL'],
                'commitments': [{'type': 'CONFIRMATION_EMAIL', 'etaDays': 4}],
                ...
            }
        compressed: str   — the CLLM token string output, e.g.:
            "[INTERACTION:SUPPORT:CHANNEL=VOICE] [CUSTOMER_INTENT:REPORT_BILLING_ISSUE]..."

    Residual entropy H(struct | compressed) is estimated using per-field
    domain_bits from FIELD_SCHEMA — the information-theoretic cost of not
    knowing each lost field's value.
    """

    WEIGHTED_COVERAGE_THRESHOLD = 0.88
    RAW_COVERAGE_THRESHOLD = 0.85
    MAX_RESIDUAL_BITS = 3.0

    def analyze(self, structured: Any, compressed: str) -> ConditionalEntropyResult:
        # Flatten the compressed string into a set of uppercase token keys
        # present in the output. We do a broad search so token format variations
        # like [CUSTOMER_INTENT=X], [CUSTOMER_INTENT:X], etc. all match.
        compressed_upper = compressed.upper()
        compressed_tokens = set(re.findall(r"\b([A-Z][A-Z_]{2,})\b", compressed_upper))

        field_results: list[FieldResult] = []
        total_weight = 0.0
        matched_weight = 0.0
        slots_total = 0
        slots_matched = 0
        slots_lost: list[str] = []
        slots_null: list[str] = []
        bits_per_lost: dict[str, float] = {}

        for schema in FIELD_SCHEMA:
            dict_key = schema["key"]
            token_key = schema["token"]
            weight = schema["weight"]
            domain_bits = schema["bits"]

            raw_value = structured.get(dict_key)

            # Null / empty in source — not a loss, don't count it
            is_null = (
                raw_value is None
                or raw_value == []
                or raw_value == {}
                or raw_value == ""
            )
            if is_null:
                slots_null.append(dict_key)
                field_results.append(
                    FieldResult(
                        field=dict_key,
                        token_key=token_key,
                        expected_value=raw_value,
                        found_in_compressed=False,
                        weight=weight,
                        null_in_source=True,
                    )
                )
                continue

            slots_total += 1
            total_weight += weight

            # Check if the token key appears anywhere in the compressed string.
            # We also check for common abbreviations and aliases.
            token_aliases = self._aliases(token_key)
            found = any(alias in compressed_tokens for alias in token_aliases)

            # For list/dict values, also check if any value strings appear
            if not found:
                value_strings = self._extract_value_strings(raw_value)
                found = any(
                    v.upper() in compressed_upper for v in value_strings if len(v) > 3
                )

            if found:
                slots_matched += 1
                matched_weight += weight
            else:
                slots_lost.append(dict_key)
                bits_per_lost[dict_key] = domain_bits

            field_results.append(
                FieldResult(
                    field=dict_key,
                    token_key=token_key,
                    expected_value=raw_value,
                    found_in_compressed=found,
                    weight=weight,
                    null_in_source=False,
                )
            )

        raw_coverage = slots_matched / slots_total if slots_total else 1.0
        weighted_coverage = matched_weight / total_weight if total_weight else 1.0

        # Residual entropy: sum of domain_bits for each lost non-optional field
        residual_entropy = sum(
            bits
            for field, bits in bits_per_lost.items()
            if field not in OPTIONAL_FIELDS
        )

        # A lost critical field forces high_risk regardless of other scores
        critical_lost = [f for f in slots_lost if f in CRITICAL_FIELDS]

        passed = (
            not critical_lost
            and weighted_coverage >= self.WEIGHTED_COVERAGE_THRESHOLD
            and raw_coverage >= self.RAW_COVERAGE_THRESHOLD
            and residual_entropy <= self.MAX_RESIDUAL_BITS
        )

        return ConditionalEntropyResult(
            field_results=field_results,
            slots_total=slots_total,
            slots_matched=slots_matched,
            slots_lost=slots_lost,
            slots_null_in_source=slots_null,
            weighted_coverage=round(weighted_coverage, 4),
            raw_coverage=round(raw_coverage, 4),
            residual_entropy=round(residual_entropy, 4),
            bits_per_lost_field=bits_per_lost,
            passed=passed,
        )

    @staticmethod
    def _aliases(token_key: str) -> set[str]:
        """Return the token key plus known short-form aliases used by the encoder."""
        base = {token_key, token_key.replace("_", "")}
        alias_map = {
            "CUSTOMER_INTENT": {"INTENT", "CUST_INTENT"},
            "AGENT_ACTIONS": {"AGENT_ACTION", "ACTIONS"},
            "SYSTEM_ACTIONS": {"SYS_ACTIONS", "SYSTEM_ACTION"},
            "INTERACTION_TRIGGER": {"TRIGGER", "INT_TRIGGER"},
            "SUPPORT_TRIGGER": {"TRIGGER"},
            "DURATION": {"DUR"},
        }
        return base | alias_map.get(token_key, set())

    @staticmethod
    def _extract_value_strings(value: Any) -> list[str]:
        """
        Flatten structured values to a list of strings for token-string search.

        Examples:
            "VOICE"                        → ["VOICE"]
            ["NEUTRAL", "GRATEFUL"]        → ["NEUTRAL", "GRATEFUL"]
            [{"type": "REFUND", "etaDays": 4}] → ["REFUND", "4"]
            [{"key": "REFUND_REF", "value": "RFD-908712"}] → ["REFUND_REF", "RFD-908712"]
        """
        if isinstance(value, str):
            return [value]
        if isinstance(value, (int, float)):
            return [str(value)]
        if isinstance(value, list):
            results = []
            for item in value:
                if isinstance(item, str):
                    results.append(item)
                elif isinstance(item, dict):
                    results.extend(str(v) for v in item.values() if v is not None)
            return results
        if isinstance(value, dict):
            return [str(v) for v in value.values() if v is not None]
        return [str(value)]
