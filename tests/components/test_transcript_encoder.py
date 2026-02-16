import pytest
from unittest.mock import MagicMock, patch

from clm_core.components.transcript.encoder import TranscriptEncoder
from clm_core.components.transcript import (
    CallInfo,
    CustomerProfile,
    Issue,
    Action,
    Resolution,
    SentimentTrajectory,
    TranscriptAnalysis,
    Turn,
    ResolutionState,
    RefundReference,
    PromiseCommitment,
)
from clm_core.types import CLMOutput


@pytest.fixture
def nlp():
    """Load spaCy model for tests"""
    import spacy
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        pytest.skip("spaCy model en_core_web_sm not available")


@pytest.fixture
def vocab():
    """Mock vocabulary"""
    from clm_core.dictionary.en.vocabulary import ENVocabulary
    return ENVocabulary()


@pytest.fixture
def rules():
    """Mock rules"""
    from clm_core.dictionary.en.rules import ENRules
    return ENRules()


@pytest.fixture
def patterns():
    """English transcript patterns"""
    from clm_core.dictionary import patterns_map
    return patterns_map["en"]


@pytest.fixture
def encoder(nlp, vocab, rules, patterns):
    """Create encoder instance, clearing singleton"""
    # Clear singleton to allow fresh instance
    TranscriptEncoder._instances = {}
    return TranscriptEncoder(nlp=nlp, vocab=vocab, rules=rules, patterns=patterns)


class TestTranscriptEncoderInit:
    def test_initialization(self, nlp, vocab, rules, patterns):
        TranscriptEncoder._instances = {}
        encoder = TranscriptEncoder(nlp=nlp, vocab=vocab, rules=rules, patterns=patterns)
        assert encoder._analyzer is not None
        assert encoder.analysis is None


class TestEncodeInteraction:
    def test_basic_interaction(self):
        call = CallInfo(
            call_id="123",
            type="SUPPORT",
            channel="voice",
            duration=10
        )
        result = TranscriptEncoder._encode_interaction(call)
        assert result == "[INTERACTION:SUPPORT:CHANNEL=VOICE]"

    def test_interaction_chat_channel(self):
        call = CallInfo(
            call_id="123",
            type="BILLING",
            channel="chat",
            duration=8
        )
        result = TranscriptEncoder._encode_interaction(call)
        assert result == "[INTERACTION:BILLING:CHANNEL=CHAT]"

    def test_interaction_email_channel(self):
        call = CallInfo(
            call_id="123",
            type="SUPPORT",
            channel="email",
            duration=4
        )
        result = TranscriptEncoder._encode_interaction(call)
        assert result == "[INTERACTION:SUPPORT:CHANNEL=EMAIL]"


class TestEncodeDuration:
    def test_duration_conversion(self):
        call = CallInfo(call_id="123", type="SUPPORT", channel="voice", duration=20)
        result = TranscriptEncoder._encode_duration(call)
        assert result == "[DURATION=10m]"

    def test_minimum_duration(self):
        call = CallInfo(call_id="123", type="SUPPORT", channel="voice", duration=1)
        result = TranscriptEncoder._encode_duration(call)
        assert result == "[DURATION=1m]"

    def test_no_duration(self):
        call = CallInfo(call_id="123", type="SUPPORT", channel="voice", duration=0)
        result = TranscriptEncoder._encode_duration(call)
        assert result is None


class TestEncodeLang:
    def test_lang_en(self):
        result = TranscriptEncoder._encode_lang("en")
        assert result == "[LANG=EN]"

    def test_lang_pt(self):
        result = TranscriptEncoder._encode_lang("pt")
        assert result == "[LANG=PT]"

    def test_lang_es(self):
        result = TranscriptEncoder._encode_lang("es")
        assert result == "[LANG=ES]"


class TestEncodeAgentActions:
    def test_single_action(self):
        actions = [Action(type="ACCOUNT_VERIFIED")]
        result = TranscriptEncoder._encode_agent_actions(actions)
        assert result == "[AGENT_ACTIONS:ACCOUNT_VERIFIED]"

    def test_multiple_actions(self):
        actions = [
            Action(type="ACCOUNT_VERIFIED"),
            Action(type="DIAGNOSTIC_PERFORMED"),
            Action(type="REFUND_INITIATED")
        ]
        result = TranscriptEncoder._encode_agent_actions(actions)
        assert result == "[AGENT_ACTIONS:ACCOUNT_VERIFIED→DIAGNOSTIC_PERFORMED→REFUND_INITIATED]"

    def test_action_chain_preserves_order(self):
        actions = [
            Action(type="ACCOUNT_VERIFIED"),
            Action(type="TROUBLESHOOT"),
            Action(type="DOCUMENTATION_UPDATED")
        ]
        result = TranscriptEncoder._encode_agent_actions(actions)
        assert result == "[AGENT_ACTIONS:ACCOUNT_VERIFIED→TROUBLESHOOT→DOCUMENTATION_UPDATED]"

    def test_two_actions(self):
        actions = [
            Action(type="REFUND_INITIATED"),
            Action(type="CUSTOMER_NOTIFIED")
        ]
        result = TranscriptEncoder._encode_agent_actions(actions)
        assert result == "[AGENT_ACTIONS:REFUND_INITIATED→CUSTOMER_NOTIFIED]"


class TestEncodeSystemActions:
    def test_single_system_action(self):
        result = TranscriptEncoder._encode_system_actions(["PAYMENT_RETRY_DETECTED"])
        assert result == "[SYSTEM_ACTIONS:PAYMENT_RETRY_DETECTED]"

    def test_multiple_system_actions(self):
        result = TranscriptEncoder._encode_system_actions(
            ["PAYMENT_RETRY_DETECTED", "NOTIFICATION_SENT"]
        )
        assert result == "[SYSTEM_ACTIONS:PAYMENT_RETRY_DETECTED→NOTIFICATION_SENT]"


class TestEncodeResolution:
    def test_resolved(self):
        resolution = Resolution(type="RESOLVED")
        result = TranscriptEncoder._encode_resolution(resolution)
        assert result == "[RESOLUTION:ISSUE_RESOLVED]"

    def test_pending(self):
        resolution = Resolution(type="PENDING")
        result = TranscriptEncoder._encode_resolution(resolution)
        assert result == "[RESOLUTION:PENDING]"

    def test_escalated(self):
        resolution = Resolution(type="ESCALATED")
        result = TranscriptEncoder._encode_resolution(resolution)
        assert result == "[RESOLUTION:ESCALATED]"

    def test_unknown_with_next_steps(self):
        resolution = Resolution(type="UNKNOWN", next_steps="callback tomorrow")
        result = TranscriptEncoder._encode_resolution(resolution)
        assert result == "[RESOLUTION:CALLBACK_TOMORROW]"

    def test_unknown_no_next_steps(self):
        resolution = Resolution(type="UNKNOWN")
        result = TranscriptEncoder._encode_resolution(resolution)
        assert result is None


class TestEncodeState:
    def test_resolved_state(self):
        resolution = Resolution(type="RESOLVED")
        state = ResolutionState(type="FULLY_RESOLVED")
        result = TranscriptEncoder._encode_state(resolution, state)
        assert result == "[STATE:RESOLVED]"

    def test_pending_state(self):
        resolution = Resolution(type="PENDING")
        state = ResolutionState(type="PENDING")
        result = TranscriptEncoder._encode_state(resolution, state)
        assert result == "[STATE:PENDING_SETTLEMENT]"

    def test_escalated_state(self):
        resolution = Resolution(type="ESCALATED")
        state = ResolutionState(type="ESCALATED")
        result = TranscriptEncoder._encode_state(resolution, state)
        assert result == "[STATE:ESCALATED]"

    def test_unresolved_state(self):
        resolution = Resolution(type="UNKNOWN")
        state = None
        result = TranscriptEncoder._encode_state(resolution, state)
        assert result == "[STATE:UNRESOLVED]"

    def test_pending_verification_state(self):
        resolution = Resolution(type="UNKNOWN")
        state = ResolutionState(type="RESOLVED_PENDING_VERIFICATION")
        result = TranscriptEncoder._encode_state(resolution, state)
        assert result == "[STATE:PENDING_CUSTOMER]"


class TestEncodeCommitments:
    def test_single_commitment_with_timeline(self):
        promises = [
            PromiseCommitment(
                type="REFUND_PROMISE",
                description="Refund in 3-5 days",
                timeline="3-5d",
                turn_index=5
            )
        ]
        result = TranscriptEncoder._encode_commitments(promises)
        assert len(result) == 1
        assert result[0] == "[COMMITMENT:REFUND_PROMISE_3-5d]"

    def test_commitment_with_amount_and_timeline(self):
        promises = [
            PromiseCommitment(
                type="CREDIT_PROMISE",
                description="Credit of $14.99",
                timeline="24h",
                amount="$14.99",
                turn_index=4
            )
        ]
        result = TranscriptEncoder._encode_commitments(promises)
        assert len(result) == 1
        assert result[0] == "[COMMITMENT:CREDIT_PROMISE_24h_$14.99]"

    def test_commitment_without_timeline(self):
        promises = [
            PromiseCommitment(
                type="CALLBACK",
                description="We'll call you back",
                turn_index=6
            )
        ]
        result = TranscriptEncoder._encode_commitments(promises)
        assert len(result) == 1
        assert result[0] == "[COMMITMENT:CALLBACK]"

    def test_multiple_commitments(self):
        promises = [
            PromiseCommitment(
                type="REFUND_PROMISE",
                description="Refund",
                timeline="3-5d",
                turn_index=5
            ),
            PromiseCommitment(
                type="FOLLOW_UP_EMAIL",
                description="Confirmation email",
                turn_index=6
            )
        ]
        result = TranscriptEncoder._encode_commitments(promises)
        assert len(result) == 2

    def test_empty_commitments(self):
        result = TranscriptEncoder._encode_commitments([])
        assert result == []


class TestEncodeArtifacts:
    def test_refund_reference_artifact(self):
        analysis = TranscriptAnalysis(
            call_info=CallInfo(call_id="1", type="SUPPORT", channel="voice", duration=5),
            customer=CustomerProfile(),
            turns=[Turn(speaker="customer", text="Hello", entities={})],
            issues=[],
            actions=[],
            resolution=Resolution(),
            sentiment_trajectory=SentimentTrajectory(),
            refund_reference=RefundReference(
                reference_number="RFD-908712",
                amount="$14.99"
            )
        )
        result = TranscriptEncoder._encode_artifacts(analysis)
        assert "[ARTIFACT:REFUND_REF=RFD-908712]" in result
        assert "[ARTIFACT:REFUND_AMT=$14.99]" in result

    def test_no_artifacts(self):
        analysis = TranscriptAnalysis(
            call_info=CallInfo(call_id="1", type="SUPPORT", channel="voice", duration=5),
            customer=CustomerProfile(),
            turns=[Turn(speaker="customer", text="Hello", entities={})],
            issues=[],
            actions=[],
            resolution=Resolution(),
            sentiment_trajectory=SentimentTrajectory()
        )
        result = TranscriptEncoder._encode_artifacts(analysis)
        assert result == []

    def test_identifier_artifacts(self):
        analysis = TranscriptAnalysis(
            call_info=CallInfo(call_id="1", type="SUPPORT", channel="voice", duration=5),
            customer=CustomerProfile(),
            turns=[
                Turn(
                    speaker="customer",
                    text="Order XYZ-123",
                    entities={"order_numbers": ["XYZ-123"]}
                )
            ],
            issues=[],
            actions=[],
            resolution=Resolution(),
            sentiment_trajectory=SentimentTrajectory()
        )
        result = TranscriptEncoder._encode_artifacts(analysis)
        assert "[ARTIFACT:ORDER_ID=XYZ-123]" in result


class TestEncodeSentiment:
    def test_simple_sentiment(self):
        sentiment = SentimentTrajectory(start="FRUSTRATED", end="SATISFIED")
        result = TranscriptEncoder._encode_sentiment(sentiment)
        assert result == "[SENTIMENT:FRUSTRATED→SATISFIED]"

    def test_sentiment_with_turning_points(self):
        sentiment = SentimentTrajectory(
            start="FRUSTRATED",
            end="SATISFIED",
            turning_points=[(3, "NEUTRAL"), (5, "SATISFIED")]
        )
        result = TranscriptEncoder._encode_sentiment(sentiment)
        assert "FRUSTRATED→NEUTRAL→SATISFIED" in result

    def test_sentiment_no_duplicate_emotions(self):
        sentiment = SentimentTrajectory(
            start="NEUTRAL",
            end="SATISFIED",
            turning_points=[(2, "NEUTRAL"), (3, "NEUTRAL"), (4, "SATISFIED")]
        )
        result = TranscriptEncoder._encode_sentiment(sentiment)
        assert result.count("NEUTRAL") == 1

    def test_sentiment_default_neutral(self):
        sentiment = SentimentTrajectory()
        result = TranscriptEncoder._encode_sentiment(sentiment)
        assert "NEUTRAL" in result


class TestTranscriptEncoderEncode:
    def test_encode_returns_clm_output(self, encoder):
        transcript = """Customer: Hi, I have a billing issue.
Agent: I'd be happy to help. Can you tell me more?
Customer: I was charged twice for my subscription.
Agent: I see. Let me look into that for you."""

        metadata = {"call_id": "TEST-001", "channel": "voice"}

        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)

        assert isinstance(result, CLMOutput)
        assert result.component == "TRANSCRIPT"
        assert result.original == transcript
        assert len(result.compressed) > 0

    def test_encode_metadata_structure(self, encoder):
        transcript = "Customer: Hello\nAgent: Hi there"
        metadata = {"call_id": "TEST-002"}

        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)

        assert "analysis" in result.metadata
        assert "original_length" in result.metadata
        assert "compressed_length" in result.metadata
        assert "verbs" in result.metadata
        assert "noun_chunks" in result.metadata
        assert "language" in result.metadata
        assert result.metadata["language"] == "en"
        assert result.metadata["schema_version"] == "2.0"

    def test_encode_preserves_call_id(self, encoder):
        transcript = "Customer: Hello\nAgent: Hi"
        metadata = {"call_id": "PRESERVE-THIS-ID"}

        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)

        assert result.metadata.get("call_id") == "PRESERVE-THIS-ID"

    def test_encode_compression_tokens(self, encoder):
        transcript = """Customer: Hi, I noticed an extra charge on my card.
Agent: I'm sorry to hear that. Let me look into it.
Customer: It's for $49.99 but I didn't order anything.
Agent: I found the issue. I'll process a refund right away.
Customer: Thank you so much!
Agent: You're welcome. Is there anything else?"""

        metadata = {"call_id": "TEST-003"}
        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)

        assert result.n_tokens > 0
        assert result.c_tokens > 0
        assert result.c_tokens < result.n_tokens

    def test_encode_has_numbers_detection(self, encoder):
        transcript = "Customer: I was charged $49.99\nAgent: Let me check order 12345"
        metadata = {}

        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)

        assert result.metadata["has_numbers"] is True

    def test_encode_has_urls_detection(self, encoder):
        transcript = "Customer: I saw this on https://example.com\nAgent: Thanks"
        metadata = {}

        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)

        assert result.metadata["has_urls"] is True

    def test_encode_no_urls(self, encoder):
        transcript = "Customer: Hello\nAgent: Hi there"
        metadata = {}

        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)

        assert result.metadata["has_urls"] is False

    def test_v2_format_tokens_present(self, encoder):
        transcript = """Customer: Hi, I noticed a duplicate charge on my account.
Agent: I apologize for the inconvenience. Let me look into that for you.
Customer: It's showing two charges of $29.99 on the same day.
Agent: I can see the duplicate charge. I'll process a refund immediately.
Customer: Great, how long will it take?
Agent: The refund should appear within 3-5 business days.
Customer: Thank you for your help!
Agent: You're welcome. Have a great day!"""

        metadata = {"call_id": "V2-001", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)

        # v2 tokens should be present
        assert "[INTERACTION:" in result.compressed
        assert "[LANG=EN]" in result.compressed
        assert "[DOMAIN:" in result.compressed
        assert "[CUSTOMER_INTENT:" in result.compressed
        assert "[STATE:" in result.compressed
        assert "[SENTIMENT:" in result.compressed

    def test_v2_no_legacy_tokens(self, encoder):
        transcript = """Customer: Hi, I have a billing issue.
Agent: Let me help. I've verified your account.
Customer: Thanks."""

        metadata = {"call_id": "V2-002"}
        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)

        # v1 tokens should NOT be present
        assert "[CALL:" not in result.compressed
        assert "[CUSTOMER:" not in result.compressed
        assert "[CONTACT:" not in result.compressed
        assert "[ISSUE:" not in result.compressed
        assert "[ACTION_CHAIN:" not in result.compressed
        assert "[RES_STATE:" not in result.compressed
        assert "[PROMISES:" not in result.compressed
        assert "[TIMELINE:" not in result.compressed


class TestTranscriptEncoderIntegration:
    """Full integration tests for transcript encoding"""

    def test_billing_dispute_transcript(self, encoder):
        transcript = """Customer: Hi, I noticed a duplicate charge on my account.
Agent: I apologize for the inconvenience. Let me look into that for you.
Customer: It's showing two charges of $29.99 on the same day.
Agent: I can see the duplicate charge. I'll process a refund immediately.
Customer: Great, how long will it take?
Agent: The refund should appear within 3-5 business days.
Customer: Thank you for your help!
Agent: You're welcome. Have a great day!"""

        metadata = {"call_id": "BILLING-001", "channel": "chat"}
        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)

        assert result.compression_ratio > 0
        assert "[INTERACTION:SUPPORT:CHANNEL=CHAT]" in result.compressed
        assert "[DOMAIN:BILLING]" in result.compressed
        assert "[SENTIMENT:" in result.compressed

    def test_technical_support_transcript(self, encoder):
        transcript = """Customer: My internet has been cutting out all day.
Agent: I'm sorry to hear that. Let me run some diagnostics.
Customer: It happens every few hours.
Agent: I see some signal issues. Let me reset your connection.
Customer: Okay, let's try that.
Agent: Done. Please check if it's working now.
Customer: Yes, it seems to be working. Thank you!"""

        metadata = {"call_id": "TECH-001", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)

        assert isinstance(result, CLMOutput)
        assert result.n_tokens > 0
        assert "[SENTIMENT:" in result.compressed
        assert "[INTERACTION:" in result.compressed

    def test_empty_metadata(self, encoder):
        transcript = "Customer: Hello\nAgent: Hi"
        result = encoder.encode(transcript=transcript, metadata={}, verbose=False)

        assert isinstance(result, CLMOutput)
        assert result.metadata.get("call_id") is None

    def test_full_v2_example(self, encoder):
        """Test the example from the v2 spec document."""
        transcript = """Customer: Hi, I'm calling about a duplicate charge on my subscription.
Agent: I'm sorry to hear that. Let me verify your account first.
Customer: Sure, my email is john@example.com.
Agent: Thank you. I've verified your account and I can see the duplicate charge.
Agent: I've run a diagnostic and confirmed the issue. I'll initiate a refund now.
Agent: Your refund reference is RFD-908712. It should appear within 3-5 business days.
Customer: Thank you so much for the quick help!
Agent: You're welcome! Is there anything else I can help with?"""

        metadata = {"call_id": "V2-EXAMPLE", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)

        compressed = result.compressed

        # Verify v2 structure
        assert "[INTERACTION:" in compressed
        assert "[DURATION=" in compressed
        assert "[LANG=EN]" in compressed
        assert "[DOMAIN:" in compressed
        assert "[CUSTOMER_INTENT:" in compressed
        assert "[STATE:" in compressed
        assert "[SENTIMENT:" in compressed
