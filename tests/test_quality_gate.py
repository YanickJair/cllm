import json
import pytest
from unittest.mock import MagicMock, patch

from thread_encoder.quality_gate import (
    KolmogorovAnalyzer,
    KolmogorovModel,
    ConditionalEntropyAnalyzer,
    ConditionalEntropyResult,
    PerplexityAnalyzer,
    PerplexityResult,
    CompressionQualityGate,
    CompressionQualityReport,
    FIELD_SCHEMA,
    OPTIONAL_FIELDS,
)

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

LONG_TRANSCRIPT = (
    "Agent: Thank you for calling support. How can I help you today? "
    "Customer: Hi, I have a billing issue. I was charged twice for my subscription. "
    "Agent: I'm sorry to hear that. Let me look into your account. "
    "Customer: My account number is 12345 and I was charged on March 1st and March 3rd. "
    "Agent: I can see the duplicate charge. I'll issue a refund right away. "
    "Customer: Thank you so much! I really appreciate that. "
    "Agent: The refund will appear in 3-5 business days. Is there anything else? "
    "Customer: No, that's all. Thank you! "
    "Agent: Have a great day!"
) * 3  # repeat to make it longer than any realistic compressed output

GOOD_COMPRESSED = (
    "[INTERACTION:SUPPORT:CHANNEL=VOICE:LANG=EN] "
    "[CUSTOMER_INTENT:BILLING_ISSUE] "
    "[DOMAIN:BILLING] "
    "[STATE:RESOLVED] "
    "[RESOLUTION:REFUND_ISSUED] "
    "[SENTIMENT:SATISFIED:GRATEFUL] "
    "[AGENT_ACTIONS:ACCOUNT_LOOKUP:REFUND_ISSUED] "
    "[COMMITMENT:REFUND:ETA=3-5_DAYS] "
    "[DURATION:300]"
)

STRUCTURED_DICT = {
    "channel": "VOICE",
    "lang": "EN",
    "domain": "BILLING",
    "service": "SUBSCRIPTION",
    "customerIntent": "BILLING_ISSUE",
    "secondaryIntent": None,
    "state": "RESOLVED",
    "resolution": "REFUND_ISSUED",
    "sentiment": ["SATISFIED", "GRATEFUL"],
    "agentActions": ["ACCOUNT_LOOKUP", "REFUND_ISSUED"],
    "systemActions": None,
    "commitments": [{"type": "REFUND", "etaDays": 5}],
    "artifacts": [],
    "supportTrigger": None,
    "interactionTrigger": None,
    "context": "BILLING",
    "durationSeconds": 300,
    "id": None,
}


def _make_kolmogorov(
    *,
    passed: bool = True,
    complexity_ratio: float = 0.5,
    information_efficiency: float = 1.2,
) -> KolmogorovModel:
    return KolmogorovModel(
        original_bytes=1000,
        compressed_bytes=500,
        clm_bytes=500,
        original_zlib_bytes=400,
        clm_zlib_bytes=200,
        complexity_ratio=complexity_ratio,
        information_efficiency=information_efficiency,
        passed=passed,
    )


def _make_conditional(
    *,
    passed: bool = True,
    weighted_coverage: float = 0.95,
    raw_coverage: float = 0.92,
    residual_entropy: float = 0.5,
    slots_lost: list[str] | None = None,
) -> ConditionalEntropyResult:
    return ConditionalEntropyResult(
        field_results=[],
        slots_total=10,
        slots_matched=9,
        slots_lost=slots_lost or [],
        slots_null_in_source=[],
        weighted_coverage=weighted_coverage,
        raw_coverage=raw_coverage,
        residual_entropy=residual_entropy,
        bits_per_lost_field={},
        passed=passed,
    )


def _make_perplexity(
    *,
    passed: bool = True,
    comprehension_score: float = 0.9,
    response_similarity: float = 0.9,
    latency_improvement: float = 60.0,
) -> PerplexityResult:
    return PerplexityResult(
        original_response_tokens=100,
        compressed_response_tokens=80,
        original_latency_ms=500.0,
        compressed_latency_ms=200.0,
        latency_improvement=latency_improvement,
        response_similarity=response_similarity,
        structure_preserved=True,
        key_facts_preserved=["billing issue", "refund issued"],
        facts_lost=[],
        comprehension_score=comprehension_score,
        passed=passed,
    )


@pytest.fixture
def heuristic_perplexity() -> PerplexityAnalyzer:
    """PerplexityAnalyzer bypassing __init__, set to heuristic-only mode."""
    analyzer = PerplexityAnalyzer.__new__(PerplexityAnalyzer)
    analyzer.llm_client = "anthropic"
    analyzer._api_available = False
    return analyzer


@pytest.fixture
def api_perplexity() -> PerplexityAnalyzer:
    """PerplexityAnalyzer with a mocked LLM client."""
    analyzer = PerplexityAnalyzer.__new__(PerplexityAnalyzer)
    analyzer.llm_client = "anthropic"
    analyzer._api_available = True
    analyzer.client = MagicMock()
    return analyzer


# ---------------------------------------------------------------------------
# KolmogorovAnalyzer
# ---------------------------------------------------------------------------


class TestKolmogorovAnalyzer:
    def setup_method(self):
        self.analyzer = KolmogorovAnalyzer()

    def test_analyze_returns_kolmogorov_model(self):
        result = self.analyzer.analyze(LONG_TRANSCRIPT, GOOD_COMPRESSED)
        assert isinstance(result, KolmogorovModel)

    def test_passes_when_compressed_is_much_smaller(self):
        result = self.analyzer.analyze(LONG_TRANSCRIPT, GOOD_COMPRESSED)
        assert result.passed is True
        assert result.complexity_ratio < KolmogorovAnalyzer.COMPLEXITY_THRESHOLD

    def test_fails_when_compressed_matches_original(self):
        # Use the same text for both — ratio ≈ 1.0, above threshold
        result = self.analyzer.analyze(LONG_TRANSCRIPT, LONG_TRANSCRIPT)
        assert result.passed is False
        assert result.complexity_ratio > KolmogorovAnalyzer.COMPLEXITY_THRESHOLD

    def test_original_bytes_reflects_utf8_length(self):
        original = "hello"
        result = self.analyzer.analyze(original, "HI")
        assert result.original_bytes == len(original.encode("utf-8"))

    def test_complexity_ratio_rounded_to_4_places(self):
        result = self.analyzer.analyze(LONG_TRANSCRIPT, GOOD_COMPRESSED)
        assert result.complexity_ratio == round(result.complexity_ratio, 4)

    def test_information_efficiency_rounded_to_4_places(self):
        result = self.analyzer.analyze(LONG_TRANSCRIPT, GOOD_COMPRESSED)
        assert result.information_efficiency == round(result.information_efficiency, 4)

    def test_clm_bytes_equals_compressed_bytes(self):
        result = self.analyzer.analyze(LONG_TRANSCRIPT, GOOD_COMPRESSED)
        assert result.clm_bytes == result.compressed_bytes

    def test_original_zlib_bytes_equals_clm_zlib_bytes_when_same_input(self):
        # When original == compressed, both zlib sizes should be equal
        text = "VOICE BILLING RESOLVED REFUND"
        result = self.analyzer.analyze(text, text)
        assert result.original_zlib_bytes == result.clm_zlib_bytes


# ---------------------------------------------------------------------------
# ConditionalEntropyAnalyzer
# ---------------------------------------------------------------------------


class TestConditionalEntropyAnalyzer:
    def setup_method(self):
        self.analyzer = ConditionalEntropyAnalyzer()

    def test_analyze_returns_conditional_entropy_result(self):
        result = self.analyzer.analyze(STRUCTURED_DICT, GOOD_COMPRESSED)
        assert isinstance(result, ConditionalEntropyResult)

    def test_all_critical_fields_present_passes(self):
        compressed = (
            "[CUSTOMER_INTENT:BILLING_ISSUE] [DOMAIN:BILLING] "
            "[STATE:RESOLVED] [RESOLUTION:REFUND_ISSUED] "
            "[CHANNEL:VOICE] [LANG:EN] [SENTIMENT:SATISFIED] "
            "[AGENT_ACTIONS:REFUND] [COMMITMENT:REFUND] [DURATION:300] "
            "[CONTEXT:BILLING] [SERVICE:SUBSCRIPTION]"
        )
        structured = {
            "channel": "VOICE",
            "lang": "EN",
            "domain": "BILLING",
            "service": "SUBSCRIPTION",
            "customerIntent": "BILLING_ISSUE",
            "state": "RESOLVED",
            "resolution": "REFUND_ISSUED",
            "sentiment": "SATISFIED",
            "agentActions": ["REFUND"],
            "commitments": [{"type": "REFUND"}],
            "durationSeconds": 300,
            "context": "BILLING",
        }
        result = self.analyzer.analyze(structured, compressed)
        assert result.passed is True

    def test_missing_critical_field_fails(self):
        # Remove customerIntent from compressed string entirely
        compressed = "[DOMAIN:BILLING] [STATE:RESOLVED] [RESOLUTION:REFUND]"
        structured = {
            "customerIntent": "BILLING_ISSUE",
            "domain": "BILLING",
            "state": "RESOLVED",
            "resolution": "REFUND",
        }
        result = self.analyzer.analyze(structured, compressed)
        assert result.passed is False
        assert "customerIntent" in result.slots_lost

    def test_null_field_excluded_from_slots_total(self):
        structured = {
            "channel": "VOICE",
            "customerIntent": None,
            "domain": None,
        }
        result = self.analyzer.analyze(structured, "[CHANNEL:VOICE]")
        assert "customerIntent" in result.slots_null_in_source
        assert "domain" in result.slots_null_in_source
        assert result.slots_total == 1  # only channel is non-null

    def test_empty_list_treated_as_null(self):
        structured = {"artifacts": [], "channel": "VOICE"}
        result = self.analyzer.analyze(structured, "[CHANNEL:VOICE]")
        assert "artifacts" in result.slots_null_in_source

    def test_empty_string_treated_as_null(self):
        structured = {"context": "", "channel": "VOICE"}
        result = self.analyzer.analyze(structured, "[CHANNEL:VOICE]")
        assert "context" in result.slots_null_in_source

    def test_empty_dict_treated_as_null(self):
        structured = {"context": {}, "channel": "VOICE"}
        result = self.analyzer.analyze(structured, "[CHANNEL:VOICE]")
        assert "context" in result.slots_null_in_source

    def test_all_null_fields_gives_perfect_coverage(self):
        structured = {k["key"]: None for k in FIELD_SCHEMA}
        result = self.analyzer.analyze(structured, "")
        assert result.slots_total == 0
        assert result.raw_coverage == 1.0
        assert result.weighted_coverage == 1.0

    def test_residual_entropy_excludes_optional_fields(self):
        # Make optional fields be the only ones lost
        optional_key = next(iter(OPTIONAL_FIELDS))
        structured = {optional_key: "SOME_VALUE"}
        result = self.analyzer.analyze(structured, "NO_MATCH_HERE")
        # Optional field lost should not contribute to residual entropy
        assert result.residual_entropy == 0.0

    def test_residual_entropy_includes_non_optional_lost_fields(self):
        # channel is not optional; lose it
        structured = {"channel": "VOICE"}
        result = self.analyzer.analyze(structured, "NO_MATCH_HERE")
        schema_entry = next(s for s in FIELD_SCHEMA if s["key"] == "channel")
        assert result.residual_entropy == schema_entry["bits"]

    def test_raw_coverage_is_matched_over_total(self):
        # 1 field, found → coverage 1.0
        structured = {"channel": "VOICE"}
        result = self.analyzer.analyze(structured, "[CHANNEL:VOICE]")
        assert result.slots_total == 1
        assert result.slots_matched == 1
        assert result.raw_coverage == 1.0

    def test_weighted_coverage_uses_field_weights(self):
        structured = {"channel": "VOICE"}
        result_found = self.analyzer.analyze(structured, "[CHANNEL:VOICE]")
        result_lost = self.analyzer.analyze(structured, "NO_MATCH")
        assert result_found.weighted_coverage > result_lost.weighted_coverage

    def test_list_value_matched_via_value_string_fallback(self):
        # SENTIMENT token absent but value "GRATEFUL" appears in compressed
        structured = {"sentiment": ["NEUTRAL", "GRATEFUL"]}
        compressed = "CONTEXT=GRATEFUL"  # no SENTIMENT token, but value present
        result = self.analyzer.analyze(structured, compressed)
        assert result.slots_matched == 1

    def test_dict_value_matched_via_value_string_fallback(self):
        # COMMITMENT token absent but commitment type appears in compressed
        structured = {"commitments": [{"type": "CONFIRMATION_EMAIL", "etaDays": 4}]}
        compressed = "CONFIRMATION_EMAIL"
        result = self.analyzer.analyze(structured, compressed)
        assert result.slots_matched == 1

    def test_field_results_include_all_schema_fields(self):
        result = self.analyzer.analyze(STRUCTURED_DICT, GOOD_COMPRESSED)
        result_keys = {fr.field for fr in result.field_results}
        schema_keys = {s["key"] for s in FIELD_SCHEMA}
        assert result_keys == schema_keys


class TestConditionalEntropyAliases:
    def test_customer_intent_aliases(self):
        aliases = ConditionalEntropyAnalyzer._aliases("CUSTOMER_INTENT")
        assert "INTENT" in aliases
        assert "CUST_INTENT" in aliases
        assert "CUSTOMER_INTENT" in aliases

    def test_agent_actions_aliases(self):
        aliases = ConditionalEntropyAnalyzer._aliases("AGENT_ACTIONS")
        assert "AGENT_ACTION" in aliases
        assert "ACTIONS" in aliases

    def test_duration_aliases(self):
        aliases = ConditionalEntropyAnalyzer._aliases("DURATION")
        assert "DUR" in aliases

    def test_unknown_token_returns_base_and_no_underscore_variant(self):
        aliases = ConditionalEntropyAnalyzer._aliases("SOME_FIELD")
        assert "SOME_FIELD" in aliases
        assert "SOMEFIELD" in aliases

    def test_alias_includes_no_underscore_variant(self):
        aliases = ConditionalEntropyAnalyzer._aliases("SYSTEM_ACTIONS")
        assert "SYSTEMACTIONS" in aliases


class TestConditionalEntropyExtractValueStrings:
    def test_string_value(self):
        result = ConditionalEntropyAnalyzer._extract_value_strings("VOICE")
        assert result == ["VOICE"]

    def test_int_value(self):
        result = ConditionalEntropyAnalyzer._extract_value_strings(42)
        assert result == ["42"]

    def test_float_value(self):
        result = ConditionalEntropyAnalyzer._extract_value_strings(3.14)
        assert result == ["3.14"]

    def test_list_of_strings(self):
        result = ConditionalEntropyAnalyzer._extract_value_strings(["A", "B"])
        assert result == ["A", "B"]

    def test_list_of_dicts(self):
        result = ConditionalEntropyAnalyzer._extract_value_strings(
            [{"type": "REFUND", "etaDays": 4}]
        )
        assert "REFUND" in result
        assert "4" in result

    def test_list_of_dicts_skips_none_values(self):
        result = ConditionalEntropyAnalyzer._extract_value_strings(
            [{"type": "REFUND", "etaDays": None}]
        )
        assert "REFUND" in result
        assert None not in result

    def test_dict_value(self):
        result = ConditionalEntropyAnalyzer._extract_value_strings(
            {"channel": "VOICE", "lang": "EN"}
        )
        assert "VOICE" in result
        assert "EN" in result

    def test_dict_skips_none_values(self):
        result = ConditionalEntropyAnalyzer._extract_value_strings(
            {"channel": "VOICE", "lang": None}
        )
        assert "VOICE" in result
        assert "None" not in result

    def test_other_type_converted_to_str(self):
        result = ConditionalEntropyAnalyzer._extract_value_strings(True)
        assert result == ["True"]


# ---------------------------------------------------------------------------
# PerplexityAnalyzer – heuristic path (no API)
# ---------------------------------------------------------------------------


class TestPerplexityAnalyzerHeuristic:
    def test_analyze_returns_perplexity_result(self, heuristic_perplexity):
        result = heuristic_perplexity.analyze("HELLO WORLD TEST", "HELLO WORLD TEST")
        assert isinstance(result, PerplexityResult)

    def test_identical_strings_gives_full_coverage(self, heuristic_perplexity):
        text = "BILLING ISSUE RESOLVED VOICE CHANNEL"
        result = heuristic_perplexity.analyze(text, text)
        assert result.comprehension_score == 1.0
        assert result.passed is True

    def test_high_overlap_passes_threshold(self, heuristic_perplexity):
        original = "CUSTOMER BILLING ISSUE RESOLVED VOICE CHANNEL SENTIMENT"
        compressed = "CUSTOMER BILLING ISSUE RESOLVED VOICE CHANNEL SENTIMENT"
        result = heuristic_perplexity.analyze(original, compressed)
        assert result.passed is True

    def test_low_overlap_fails_threshold(self, heuristic_perplexity):
        original = "BILLING ISSUE CUSTOMER ACCOUNT RESOLVED REFUND VOICE CHANNEL"
        compressed = "COMPLETELY DIFFERENT CONTENT"
        result = heuristic_perplexity.analyze(original, compressed)
        assert result.passed is False

    def test_empty_original_gives_coverage_1(self, heuristic_perplexity):
        result = heuristic_perplexity.analyze("", "SOME TOKENS")
        # orig_tokens is empty set → coverage = 1.0
        assert result.comprehension_score == 1.0

    def test_heuristic_latency_and_tokens_are_zero(self, heuristic_perplexity):
        result = heuristic_perplexity.analyze("BILLING", "BILLING")
        assert result.original_response_tokens == 0
        assert result.compressed_response_tokens == 0
        assert result.original_latency_ms == 0.0
        assert result.compressed_latency_ms == 0.0
        assert result.latency_improvement == 0.0

    def test_heuristic_structure_preserved_always_true(self, heuristic_perplexity):
        result = heuristic_perplexity.analyze("ANYTHING", "SOMETHING_ELSE")
        assert result.structure_preserved is True

    def test_facts_lost_are_tokens_in_original_not_in_compressed(
        self, heuristic_perplexity
    ):
        result = heuristic_perplexity.analyze("BILLING VOICE RESOLVED", "BILLING")
        assert "VOICE" in result.facts_lost or "RESOLVED" in result.facts_lost

    def test_key_facts_preserved_are_overlapping_tokens(self, heuristic_perplexity):
        result = heuristic_perplexity.analyze("BILLING VOICE", "BILLING CHANNEL")
        assert "BILLING" in result.key_facts_preserved


class TestPerplexityAnalyzerSafeParseJson:
    def test_parse_valid_json(self):
        data = {"primary_issue": "billing", "key_facts": ["fact1"]}
        result = PerplexityAnalyzer._safe_parse_json(json.dumps(data))
        assert result == data

    def test_parse_json_with_markdown_fence(self):
        text = "```\n{\"primary_issue\": \"billing\"}\n```"
        result = PerplexityAnalyzer._safe_parse_json(text)
        assert result == {"primary_issue": "billing"}

    def test_parse_json_with_json_code_fence(self):
        text = "```json\n{\"resolution\": \"refund\"}\n```"
        result = PerplexityAnalyzer._safe_parse_json(text)
        assert result == {"resolution": "refund"}

    def test_parse_invalid_json_returns_empty_dict(self):
        result = PerplexityAnalyzer._safe_parse_json("not json at all")
        assert result == {}

    def test_parse_empty_string_returns_empty_dict(self):
        result = PerplexityAnalyzer._safe_parse_json("")
        assert result == {}


class TestPerplexityAnalyzerApiPath:
    def _make_llm_response(self, data: dict) -> tuple[str, float, int]:
        return json.dumps(data), 300.0, 80

    def test_analyze_calls_llm_twice(self, api_perplexity):
        response_data = {
            "primary_issue": "billing",
            "resolution": "refund",
            "sentiment": "satisfied",
            "follow_up_needed": False,
            "key_facts": ["duplicate charge", "refund issued"],
        }
        api_perplexity._call_llm = MagicMock(
            return_value=self._make_llm_response(response_data)
        )
        api_perplexity._analyze_via_api("original text", "compressed text", False)
        assert api_perplexity._call_llm.call_count == 2

    def test_analyze_detects_structure_preserved(self, api_perplexity):
        response_data = {
            "primary_issue": "billing",
            "resolution": "refund",
            "sentiment": "satisfied",
            "follow_up_needed": False,
            "key_facts": [],
        }
        api_perplexity._call_llm = MagicMock(
            return_value=self._make_llm_response(response_data)
        )
        result = api_perplexity._analyze_via_api("original", "compressed", False)
        assert result.structure_preserved is True

    def test_analyze_detects_missing_structure(self, api_perplexity):
        api_perplexity._call_llm = MagicMock(
            return_value=(json.dumps({"primary_issue": "billing"}), 300.0, 80)
        )
        result = api_perplexity._analyze_via_api("original", "compressed", False)
        assert result.structure_preserved is False

    def test_analyze_computes_latency_improvement(self, api_perplexity):
        orig_response = (json.dumps({"primary_issue": "x", "resolution": "y",
                                     "sentiment": "z", "follow_up_needed": False,
                                     "key_facts": []}), 1000.0, 100)
        clm_response = (json.dumps({"primary_issue": "x", "resolution": "y",
                                    "sentiment": "z", "follow_up_needed": False,
                                    "key_facts": []}), 200.0, 80)
        api_perplexity._call_llm = MagicMock(side_effect=[orig_response, clm_response])
        result = api_perplexity._analyze_via_api("original", "compressed", False)
        assert result.latency_improvement == pytest.approx(80.0, abs=0.1)

    def test_analyze_routes_to_api_when_available(self, api_perplexity):
        response_data = {
            "primary_issue": "b", "resolution": "r",
            "sentiment": "s", "follow_up_needed": False, "key_facts": [],
        }
        api_perplexity._call_llm = MagicMock(
            return_value=self._make_llm_response(response_data)
        )
        with patch.object(
            api_perplexity, "_analyze_via_api", wraps=api_perplexity._analyze_via_api
        ) as spy:
            api_perplexity.analyze("original", "compressed")
            spy.assert_called_once()

    def test_analyze_routes_to_heuristic_when_unavailable(self, heuristic_perplexity):
        with patch.object(
            heuristic_perplexity,
            "_analyze_heuristic",
            wraps=heuristic_perplexity._analyze_heuristic,
        ) as spy:
            heuristic_perplexity.analyze("BILLING", "BILLING")
            spy.assert_called_once()


# ---------------------------------------------------------------------------
# CompressionQualityGate – static methods
# ---------------------------------------------------------------------------


class TestCompressionQualityGateVerdict:
    def test_all_pass_is_lossless(self):
        k = _make_kolmogorov(passed=True)
        c = _make_conditional(passed=True)
        p = _make_perplexity(passed=True)
        assert CompressionQualityGate._compute_verdict(k=k, c=c, p=p) == "lossless"

    def test_k_c_pass_p_fail_is_acceptable(self):
        k = _make_kolmogorov(passed=True)
        c = _make_conditional(passed=True)
        p = _make_perplexity(passed=False)
        assert CompressionQualityGate._compute_verdict(k=k, c=c, p=p) == "acceptable"

    def test_k_fail_c_pass_p_pass_is_acceptable(self):
        k = _make_kolmogorov(passed=False)
        c = _make_conditional(passed=True)
        p = _make_perplexity(passed=True)
        assert CompressionQualityGate._compute_verdict(k=k, c=c, p=p) == "acceptable"

    def test_c_fail_gives_high_risk_even_with_k_p_pass(self):
        k = _make_kolmogorov(passed=True)
        c = _make_conditional(passed=False)
        p = _make_perplexity(passed=True)
        assert CompressionQualityGate._compute_verdict(k=k, c=c, p=p) == "high_risk"

    def test_all_fail_is_high_risk(self):
        k = _make_kolmogorov(passed=False)
        c = _make_conditional(passed=False)
        p = _make_perplexity(passed=False)
        assert CompressionQualityGate._compute_verdict(k=k, c=c, p=p) == "high_risk"

    def test_only_k_passes_is_high_risk(self):
        k = _make_kolmogorov(passed=True)
        c = _make_conditional(passed=False)
        p = _make_perplexity(passed=False)
        assert CompressionQualityGate._compute_verdict(k=k, c=c, p=p) == "high_risk"

    def test_only_p_passes_is_high_risk(self):
        k = _make_kolmogorov(passed=False)
        c = _make_conditional(passed=False)
        p = _make_perplexity(passed=True)
        assert CompressionQualityGate._compute_verdict(k=k, c=c, p=p) == "high_risk"


class TestCompressionQualityGateRetentionScore:
    def test_all_perfect_gives_100(self):
        k = _make_kolmogorov(information_efficiency=1.0)
        c = _make_conditional(weighted_coverage=1.0)
        p = _make_perplexity(comprehension_score=1.0)
        score = CompressionQualityGate._compute_retention_score(k=k, c=c, p=p)
        assert score == 100.0

    def test_weights_applied_correctly(self):
        # k=0, c=1, p=0 → k_score=0, c_score=100, p_score=0
        # retention = 0*0.25 + 100*0.50 + 0*0.25 = 50.0
        k = _make_kolmogorov(information_efficiency=0.0)
        c = _make_conditional(weighted_coverage=1.0)
        p = _make_perplexity(comprehension_score=0.0)
        score = CompressionQualityGate._compute_retention_score(k=k, c=c, p=p)
        assert score == pytest.approx(50.0)

    def test_efficiency_capped_at_1(self):
        # information_efficiency > 1 should be clamped to 1 before multiplying
        k = _make_kolmogorov(information_efficiency=5.0)
        c = _make_conditional(weighted_coverage=1.0)
        p = _make_perplexity(comprehension_score=1.0)
        score = CompressionQualityGate._compute_retention_score(k=k, c=c, p=p)
        assert score == 100.0


class TestCompressionQualityGateSkipped:
    def test_conditional_skipped_is_perfect(self):
        result = CompressionQualityGate._conditional_skipped()
        assert result.passed is True
        assert result.weighted_coverage == 1.0
        assert result.raw_coverage == 1.0
        assert result.residual_entropy == 0.0
        assert result.slots_total == 0
        assert result.slots_matched == 0

    def test_perplexity_skipped_is_perfect(self):
        result = CompressionQualityGate._perplexity_skipped()
        assert result.passed is True
        assert result.comprehension_score == 1.0
        assert result.response_similarity == 1.0
        assert result.structure_preserved is True


class TestCompressionQualityGateAnalyze:
    """Integration tests for CompressionQualityGate.analyze() with mocked sub-analyzers."""

    @pytest.fixture
    def gate(self):
        """Gate with all sub-analyzers mocked to avoid API calls and the init bug."""
        with patch("thread_encoder.quality_gate.gate.PerplexityAnalyzer") as MockPerplexity:
            MockPerplexity.return_value = MagicMock()
            g = CompressionQualityGate.__new__(CompressionQualityGate)
            g.kolmogorov = KolmogorovAnalyzer()
            g.conditional = ConditionalEntropyAnalyzer()
            g.perplexity = MagicMock()
        return g

    def test_analyze_skips_perplexity_when_flag_false(self, gate):
        result = gate.analyze(
            original=LONG_TRANSCRIPT, compressed=GOOD_COMPRESSED, structured=None, run_perplexity=False
        )
        gate.perplexity.analyze.assert_not_called()
        assert result.perplexity.passed is True  # skipped → perfect

    def test_analyze_skips_conditional_when_no_structured(self, gate):
        result = gate.analyze(
            original=LONG_TRANSCRIPT, compressed=GOOD_COMPRESSED, structured=None, run_perplexity=False
        )
        assert result.conditional.slots_total == 0  # skipped result

    def test_analyze_uses_conditional_when_structured_provided(self, gate):
        result = gate.analyze(
            original=LONG_TRANSCRIPT,
            compressed=GOOD_COMPRESSED,
            structured=STRUCTURED_DICT,
            run_perplexity=False,
        )
        assert result.conditional is not None
        assert result.conditional.slots_total > 0

    def test_analyze_returns_report_with_correct_original_and_compressed(self, gate):
        result = gate.analyze(original=LONG_TRANSCRIPT, compressed=GOOD_COMPRESSED, structured=None, run_perplexity=False)
        assert result.original == LONG_TRANSCRIPT
        assert result.compressed == GOOD_COMPRESSED

    def test_analyze_calls_perplexity_when_flag_true(self, gate):
        gate.perplexity.analyze.return_value = _make_perplexity()
        gate.analyze(original=LONG_TRANSCRIPT, compressed=GOOD_COMPRESSED, structured=None, run_perplexity=True)
        gate.perplexity.analyze.assert_called_once()

    def test_analyze_verdict_is_valid_literal(self, gate):
        result = gate.analyze(original=LONG_TRANSCRIPT, compressed=GOOD_COMPRESSED, structured=None, run_perplexity=False)
        assert result.verdict in ("lossless", "acceptable", "high_risk")

    def test_analyze_retention_score_in_range(self, gate):
        result = gate.analyze(original=LONG_TRANSCRIPT, compressed=GOOD_COMPRESSED, structured=None, run_perplexity=False)
        assert 0.0 <= result.retention_score <= 100.0


# ---------------------------------------------------------------------------
# CompressionQualityReport.summary()
# ---------------------------------------------------------------------------


class TestCompressionQualityReportSummary:
    @pytest.fixture
    def report(self):
        return CompressionQualityReport(
            original=LONG_TRANSCRIPT,
            compressed=GOOD_COMPRESSED,
            kolmogorov=_make_kolmogorov(
                passed=True, complexity_ratio=0.45, information_efficiency=1.3
            ),
            conditional=_make_conditional(
                passed=True, weighted_coverage=0.96, raw_coverage=0.91
            ),
            perplexity=_make_perplexity(
                passed=True, comprehension_score=0.95, latency_improvement=60.0
            ),
            verdict="lossless",
            retention_score=94.5,
        )

    def test_summary_contains_verdict(self, report):
        summary = report.summary()
        assert "LOSSLESS" in summary

    def test_summary_contains_retention_score(self, report):
        summary = report.summary()
        assert "94.5" in summary

    def test_summary_contains_kolmogorov_section(self, report):
        summary = report.summary()
        assert "Kolmogorov" in summary
        assert "0.450" in summary  # complexity_ratio formatted to 3 dp

    def test_summary_contains_conditional_entropy_section(self, report):
        summary = report.summary()
        assert "Conditional Entropy" in summary
        assert "96.0%" in summary  # weighted_coverage * 100

    def test_summary_contains_perplexity_section(self, report):
        summary = report.summary()
        assert "Perplexity" in summary
        assert "0.95" in summary  # comprehension_score

    def test_summary_shows_passed_flags(self, report):
        summary = report.summary()
        assert "True" in summary
