import pytest
from pytest_mock import MockerFixture

from clm_core.components.intent_detector_v2 import IntentDetectorV2
from clm_core.components.sys_prompt import Intent, REQ, Signal
from clm_core.utils.vocabulary import BaseVocabulary
from spacy import Language


class DummyVocab(BaseVocabulary):
    # Implement abstract properties minimally for tests
    STOPWORDS = ()
    CODE_INDICATORS = ()
    QUANTIFIER_WORDS = ()
    DEMONSTRATIVES = []
    PRONOUNS = ()
    MODALS = ()
    ACTION_VERBS = ()
    COMPOUND_PHRASES = {}
    domain_candidates = {}
    REQ_TOKENS = {}
    TARGET_TOKENS = {}
    NOISE_VERBS = set()
    CONTEXT_FILTERS = {}
    EXTRACT_FIELDS = ()
    OUTPUT_FORMATS = {}
    IMPERATIVE_PATTERNS = []
    QUESTION_WORDS = []
    CONCEPT_INDICATORS = []
    MEETING_WORDS = ()
    PROPOSAL_WORDS = []
    ARTICLES = []

    @property
    def rank_triggers(self) -> set:
        return set()

    @property
    def EPISTEMIC_KEYWORDS(self) -> dict[str, list[str]]:
        return {
            "future": [],
            "uncertainty": [],
            "real_world": [],
        }


@pytest.fixture
def nlp_mock(mocker: MockerFixture):
    return mocker.create_autospec(Language, instance=True)


@pytest.fixture
def vocab_base():
    return DummyVocab()


def make_detector_with_req_tokens(nlp_mock, tokens):
    class V(DummyVocab):
        REQ_TOKENS = tokens
    return IntentDetectorV2(nlp_mock, V())


def test_detect_returns_validate_on_validation_signal_or_artifact(nlp_mock, vocab_base, mocker: MockerFixture):
    # Case 1: validation artifact in text
    detector = make_detector_with_req_tokens(nlp_mock, tokens={})
    text_with_validation_artifact = "Please validate the inputs and ensure compliance."
    result = detector.detect(text_with_validation_artifact)
    assert isinstance(result, Intent)
    assert result.token == REQ.VALIDATE

    # Case 2: validation signal via vocabulary
    tokens = {"VALIDATE": ["verify", "check compliance"]}
    detector2 = make_detector_with_req_tokens(nlp_mock, tokens=tokens)
    result2 = detector2.detect("Kindly VERIFY all records.")
    assert isinstance(result2, Intent)
    assert result2.token == REQ.VALIDATE


def test_detect_returns_extract_on_extraction_signal(nlp_mock):
    tokens = {"EXTRACT": ["pull data", "extract", "retrieve"]}
    detector = make_detector_with_req_tokens(nlp_mock, tokens=tokens)
    # Include artifacts that would otherwise lead to GENERATE to ensure signal wins
    text = "Please EXTRACT the fields and provide a report."
    result = detector.detect(text)
    assert isinstance(result, Intent)
    assert result.token == REQ.EXTRACT


def test_detect_returns_generate_on_artifacts_without_higher_priority(nlp_mock):
    detector = make_detector_with_req_tokens(nlp_mock, tokens={})

    # Structured artifact
    result1 = detector.detect("Return object like {\"a\": 1}")
    assert isinstance(result1, Intent)
    assert result1.token == REQ.GENERATE
    # List artifact
    result2 = detector.detect("- item one\n- item two")
    assert isinstance(result2, Intent)
    assert result2.token == REQ.GENERATE
    # Text artifact via 'report' or 'analysis'
    result3 = detector.detect("Prepare an analysis of quarterly figures.")
    assert isinstance(result3, Intent)
    assert result3.token == REQ.GENERATE


def test_probability_artifact_with_and_without_prediction_signal(nlp_mock):
    # With prediction signal -> PREDICT
    tokens_pred = {"PREDICT": ["predict", "forecast", "calculate"]}
    detector_pred = make_detector_with_req_tokens(nlp_mock, tokens=tokens_pred)
    text_prob_pred = "Predict the probability of success."
    result_pred = detector_pred.detect(text_prob_pred)
    assert isinstance(result_pred, Intent)
    assert result_pred.token == REQ.PREDICT

    # Without prediction signal -> GENERATE
    detector_no_pred = make_detector_with_req_tokens(nlp_mock, tokens={})
    text_prob_only = "What is the probability of rain tomorrow?"
    result_gen = detector_no_pred.detect(text_prob_only)
    assert isinstance(result_gen, Intent)
    assert result_gen.token == REQ.GENERATE


def test_detect_signals_case_insensitive_substring_matching(nlp_mock):
    # _detect_signals lowercases text and checks substring inclusion
    tokens = {"TRANSFORM": ["convert data", "transform"], "FORMAT": ["format output"]}
    detector = make_detector_with_req_tokens(nlp_mock, tokens=tokens)

    # Mixed case and substring presence
    result1 = detector.detect("Please TrAnSfOrM the dataset.")
    assert isinstance(result1, Intent)
    assert result1.token == REQ.TRANSFORM
    # Embedded phrase - avoid words like "ensure" that trigger validation artifact
    result2 = detector.detect("Remember to reFORMAT OUTPUT to CSV.")
    assert isinstance(result2, Intent)
    assert result2.token == REQ.FORMAT


def test_ranking_decision_precedence_in_detection_order(nlp_mock):
    # Decision artifact should yield RANK, but only if no earlier rules match
    tokens = {}  # no earlier signals
    detector = make_detector_with_req_tokens(nlp_mock, tokens=tokens)

    # No generation artifacts present; contains decision keyword
    text_decision_no_artifacts = "Please choose the best option among these alternatives."
    result1 = detector.detect(text_decision_no_artifacts)
    assert isinstance(result1, Intent)
    assert result1.token == REQ.RANK

    # If generation artifacts exist, GENERATE should win earlier; ensure that decision is after generation
    text_with_artifact_and_decision = "Provide an analysis and choose the best option."
    result2 = detector.detect(text_with_artifact_and_decision)
    assert isinstance(result2, Intent)
    assert result2.token == REQ.GENERATE


def test_detect_returns_transform_on_transformation_signal(nlp_mock):
    tokens = {"TRANSFORM": ["transform", "convert", "normalize"]}
    detector = make_detector_with_req_tokens(nlp_mock, tokens=tokens)
    result = detector.detect("Transform this text to lowercase.")
    assert isinstance(result, Intent)
    assert result.token == REQ.TRANSFORM


def test_detect_defaults_to_analyze_when_no_matches(nlp_mock):
    detector = make_detector_with_req_tokens(nlp_mock, tokens={})
    result = detector.detect("Consider various aspects and provide insights")
    assert isinstance(result, Intent)
    assert result.token == REQ.ANALYZE


def test_detect_returns_format_on_formatting_signal(nlp_mock):
    tokens = {"FORMAT": ["format", "reformat"]}
    detector = make_detector_with_req_tokens(nlp_mock, tokens=tokens)
    result = detector.detect("Format the document to APA style.")
    assert isinstance(result, Intent)
    assert result.token == REQ.FORMAT


def test_late_signals_do_not_override_earlier_conditions(nlp_mock):
    # Ensure that DEBUG, SEARCH, EXECUTE do not override earlier conditions
    tokens_debug = {
        "DEBUG": ["debug", "troubleshoot"],
        "SEARCH": ["search", "find"],
        "EXECUTE": ["execute", "run"],
        "FORMAT": ["format"],  # earlier than debug/search/execute in detection order
    }
    detector = make_detector_with_req_tokens(nlp_mock, tokens=tokens_debug)

    # Formatting should take precedence over later signals
    text_with_multiple = "Please format the output and then debug and execute."
    result = detector.detect(text_with_multiple)
    assert isinstance(result, Intent)
    assert result.token == REQ.FORMAT

    # If no earlier conditions, then late signals apply
    tokens_late_only = {
        "DEBUG": ["debug"],
        "SEARCH": ["search"],
        "EXECUTE": ["execute"],
    }
    detector_late = make_detector_with_req_tokens(nlp_mock, tokens=tokens_late_only)
    result_debug = detector_late.detect("We need to debug the process.")
    assert isinstance(result_debug, Intent)
    assert result_debug.token == REQ.DEBUG
    result_search = detector_late.detect("Search the database for entries.")
    assert isinstance(result_search, Intent)
    assert result_search.token == REQ.SEARCH
    result_exec = detector_late.detect("Execute the deployment script.")
    assert isinstance(result_exec, Intent)
    assert result_exec.token == REQ.EXECUTE

def test_intent_build_token_without_specs():
    """Test that build_token returns REQ:<token> when no specs are provided"""
    intent = Intent(token=REQ.ANALYZE, specs=[])
    assert intent.build_token() == "REQ:ANALYZE"

    intent2 = Intent(token=REQ.VALIDATE, specs=[])
    assert intent2.build_token() == "REQ:VALIDATE"

    intent3 = Intent(token=REQ.EXTRACT, specs=[])
    assert intent3.build_token() == "REQ:EXTRACT"


def test_intent_build_token_with_single_spec():
    """Test that build_token returns REQ:<token>:SPECS:<spec> with one spec"""
    intent = Intent(token=REQ.GENERATE, specs=["JSON_OBJECT"])
    assert intent.build_token() == "REQ:GENERATE:SPECS:JSON_OBJECT"

    intent2 = Intent(token=REQ.PREDICT, specs=["PROBABILITY_DISTRIBUTION"])
    assert intent2.build_token() == "REQ:PREDICT:SPECS:PROBABILITY_DISTRIBUTION"

    intent3 = Intent(token=REQ.VALIDATE, specs=["VALIDATION_RESULT"])
    assert intent3.build_token() == "REQ:VALIDATE:SPECS:VALIDATION_RESULT"


def test_intent_build_token_with_multiple_specs():
    """Test that build_token joins multiple specs with underscores"""
    intent = Intent(token=REQ.GENERATE, specs=["REPORT", "SUMMARY", "FORECAST"])
    assert intent.build_token() == "REQ:GENERATE:SPECS:REPORT_SUMMARY_FORECAST"

    intent2 = Intent(token=REQ.ANALYZE, specs=["JSON_OBJECT", "ENTITIES"])
    assert intent2.build_token() == "REQ:ANALYZE:SPECS:JSON_OBJECT_ENTITIES"

    intent3 = Intent(token=REQ.EXTRACT, specs=["FIELDS", "ENTITIES", "VALIDATION_RESULT"])
    assert intent3.build_token() == "REQ:EXTRACT:SPECS:FIELDS_ENTITIES_VALIDATION_RESULT"


def test_intent_build_token_all_req_types():
    """Test that build_token works correctly for all REQ enum values"""
    for req in REQ:
        intent = Intent(token=req, specs=[])
        expected = f"REQ:{req.value}"
        assert intent.build_token() == expected


def test_intent_build_token_with_specs_from_detector(nlp_mock):
    """Test that build_token works with specs detected by IntentDetectorV2"""
    detector = make_detector_with_req_tokens(nlp_mock, tokens={})

    # Test with structured artifact (should include JSON_OBJECT spec)
    result = detector.detect("Return object like {\"a\": 1}")
    token = result.build_token()
    assert token.startswith("REQ:GENERATE")
    # May contain specs if detected

    # Test with probability artifact
    result2 = detector.detect("What is the probability of success?")
    token2 = result2.build_token()
    assert token2.startswith("REQ:GENERATE")


def test_intent_build_token_specs_ordering():
    """Test that specs maintain their order in the built token"""
    intent = Intent(token=REQ.GENERATE, specs=["ALPHA", "BETA", "GAMMA"])
    assert intent.build_token() == "REQ:GENERATE:SPECS:ALPHA_BETA_GAMMA"

    # Different order should produce different result
    intent2 = Intent(token=REQ.GENERATE, specs=["GAMMA", "BETA", "ALPHA"])
    assert intent2.build_token() == "REQ:GENERATE:SPECS:GAMMA_BETA_ALPHA"
    assert intent.build_token() != intent2.build_token()


def test_intent_build_token_with_empty_string_spec():
    """Test behavior when specs list contains empty strings"""
    intent = Intent(token=REQ.ANALYZE, specs=["", "REPORT", ""])
    # Empty strings are still joined with underscores
    assert intent.build_token() == "REQ:ANALYZE:SPECS:_REPORT_"


def test_intent_build_token_with_special_characters_in_specs():
    """Test that specs with special characters are included as-is"""
    intent = Intent(token=REQ.GENERATE, specs=["JSON-OBJECT", "KEY_VALUE", "SOME.SPEC"])
    assert intent.build_token() == "REQ:GENERATE:SPECS:JSON-OBJECT_KEY_VALUE_SOME.SPEC"


def test_intent_build_token_consistency():
    """Test that build_token returns the same result when called multiple times"""
    intent = Intent(token=REQ.TRANSFORM, specs=["FORMAT", "NORMALIZE"])
    token1 = intent.build_token()
    token2 = intent.build_token()
    token3 = intent.build_token()
    assert token1 == token2 == token3 == "REQ:TRANSFORM:SPECS:FORMAT_NORMALIZE"
