import pytest
from unittest.mock import MagicMock, patch

from clm_core.components.thread_encoder.encoder import ThreadEncoder
from clm_core.components.thread_encoder import (
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
    """English thread_encoder patterns"""
    from clm_core.dictionary import patterns_map
    return patterns_map["en"]


@pytest.fixture
def encoder(nlp, vocab, rules, patterns):
    """Create encoder instance, clearing singleton"""
    # Clear singleton to allow fresh instance
    ThreadEncoder._instances = {}
    return ThreadEncoder(nlp=nlp, vocab=vocab, rules=rules, patterns=patterns)


class TestTranscriptEncoderInit:
    def test_initialization(self, nlp, vocab, rules, patterns):
        ThreadEncoder._instances = {}
        encoder = ThreadEncoder(nlp=nlp, vocab=vocab, rules=rules, patterns=patterns)
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
        result = ThreadEncoder._encode_interaction(call)
        assert result == "[INTERACTION:SUPPORT:CHANNEL=VOICE]"

    def test_interaction_chat_channel(self):
        call = CallInfo(
            call_id="123",
            type="BILLING",
            channel="chat",
            duration=8
        )
        result = ThreadEncoder._encode_interaction(call)
        assert result == "[INTERACTION:BILLING:CHANNEL=CHAT]"

    def test_interaction_email_channel(self):
        call = CallInfo(
            call_id="123",
            type="SUPPORT",
            channel="email",
            duration=4
        )
        result = ThreadEncoder._encode_interaction(call)
        assert result == "[INTERACTION:SUPPORT:CHANNEL=EMAIL]"


class TestEncodeDuration:
    def test_duration_conversion(self):
        call = CallInfo(call_id="123", type="SUPPORT", channel="voice", duration=20)
        result = ThreadEncoder._encode_duration(call)
        assert result == "[DURATION=10m]"

    def test_minimum_duration(self):
        call = CallInfo(call_id="123", type="SUPPORT", channel="voice", duration=1)
        result = ThreadEncoder._encode_duration(call)
        assert result == "[DURATION=1m]"

    def test_no_duration(self):
        call = CallInfo(call_id="123", type="SUPPORT", channel="voice", duration=0)
        result = ThreadEncoder._encode_duration(call)
        assert result is None


class TestEncodeLang:
    def test_lang_en(self):
        result = ThreadEncoder._encode_lang("en")
        assert result == "[LANG=EN]"

    def test_lang_pt(self):
        result = ThreadEncoder._encode_lang("pt")
        assert result == "[LANG=PT]"

    def test_lang_es(self):
        result = ThreadEncoder._encode_lang("es")
        assert result == "[LANG=ES]"


class TestEncodeAgentActions:
    def test_single_action(self):
        actions = [Action(type="ACCOUNT_VERIFIED")]
        result = ThreadEncoder._encode_agent_actions(actions)
        assert result == "[AGENT_ACTIONS:ACCOUNT_VERIFIED]"

    def test_multiple_actions(self):
        actions = [
            Action(type="ACCOUNT_VERIFIED"),
            Action(type="DIAGNOSTIC_PERFORMED"),
            Action(type="REFUND_INITIATED")
        ]
        result = ThreadEncoder._encode_agent_actions(actions)
        assert result == "[AGENT_ACTIONS:ACCOUNT_VERIFIED→DIAGNOSTIC_PERFORMED→REFUND_INITIATED]"

    def test_action_chain_preserves_order(self):
        actions = [
            Action(type="ACCOUNT_VERIFIED"),
            Action(type="TROUBLESHOOT"),
            Action(type="DOCUMENTATION_UPDATED")
        ]
        result = ThreadEncoder._encode_agent_actions(actions)
        assert result == "[AGENT_ACTIONS:ACCOUNT_VERIFIED→TROUBLESHOOT→DOCUMENTATION_UPDATED]"

    def test_two_actions(self):
        actions = [
            Action(type="REFUND_INITIATED"),
            Action(type="CUSTOMER_NOTIFIED")
        ]
        result = ThreadEncoder._encode_agent_actions(actions)
        assert result == "[AGENT_ACTIONS:REFUND_INITIATED→CUSTOMER_NOTIFIED]"


class TestEncodeSystemActions:
    def test_single_system_action(self):
        result = ThreadEncoder._encode_system_actions(["PAYMENT_RETRY_DETECTED"])
        assert result == "[SYSTEM_ACTIONS:PAYMENT_RETRY_DETECTED]"

    def test_multiple_system_actions(self):
        result = ThreadEncoder._encode_system_actions(
            ["PAYMENT_RETRY_DETECTED", "NOTIFICATION_SENT"]
        )
        assert result == "[SYSTEM_ACTIONS:PAYMENT_RETRY_DETECTED→NOTIFICATION_SENT]"


class TestEncodeResolution:
    def test_resolved(self):
        resolution = Resolution(type="RESOLVED")
        result = ThreadEncoder._encode_resolution(resolution)
        assert result == "[RESOLUTION:ISSUE_RESOLVED]"

    def test_pending(self):
        resolution = Resolution(type="PENDING")
        result = ThreadEncoder._encode_resolution(resolution)
        assert result == "[RESOLUTION:PENDING]"

    def test_escalated(self):
        resolution = Resolution(type="ESCALATED")
        result = ThreadEncoder._encode_resolution(resolution)
        assert result == "[RESOLUTION:ESCALATED]"

    def test_unknown_with_next_steps(self):
        resolution = Resolution(type="UNKNOWN", next_steps="callback tomorrow")
        result = ThreadEncoder._encode_resolution(resolution)
        assert result == "[RESOLUTION:CALLBACK_TOMORROW]"

    def test_unknown_no_next_steps(self):
        resolution = Resolution(type="UNKNOWN")
        result = ThreadEncoder._encode_resolution(resolution)
        assert result is None


class TestEncodeState:
    def test_resolved_state(self):
        resolution = Resolution(type="RESOLVED")
        state = ResolutionState(type="FULLY_RESOLVED")
        result = ThreadEncoder._encode_state(resolution, state)
        assert result == "[STATE:RESOLVED]"

    def test_pending_state(self):
        resolution = Resolution(type="PENDING")
        state = ResolutionState(type="PENDING")
        result = ThreadEncoder._encode_state(resolution, state)
        assert result == "[STATE:PENDING_CUSTOMER]"

    def test_escalated_state(self):
        resolution = Resolution(type="ESCALATED")
        state = ResolutionState(type="ESCALATED")
        result = ThreadEncoder._encode_state(resolution, state)
        assert result == "[STATE:ESCALATED]"

    def test_unresolved_state(self):
        resolution = Resolution(type="UNKNOWN")
        state = None
        result = ThreadEncoder._encode_state(resolution, state)
        assert result == "[STATE:UNRESOLVED]"

    def test_pending_verification_state(self):
        resolution = Resolution(type="UNKNOWN")
        state = ResolutionState(type="RESOLVED_PENDING_VERIFICATION")
        result = ThreadEncoder._encode_state(resolution, state)
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
        result = ThreadEncoder._encode_commitments(promises)
        assert len(result) == 1
        assert result[0] == "[COMMITMENT:REFUND_3-5_BUSINESS_DAYS]"

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
        result = ThreadEncoder._encode_commitments(promises)
        assert len(result) == 1
        assert result[0] == "[COMMITMENT:CREDIT_WITHIN_24_HOURS_$14.99]"

    def test_commitment_without_timeline(self):
        promises = [
            PromiseCommitment(
                type="CALLBACK",
                description="We'll call you back",
                turn_index=6
            )
        ]
        result = ThreadEncoder._encode_commitments(promises)
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
        result = ThreadEncoder._encode_commitments(promises)
        assert len(result) == 2

    def test_empty_commitments(self):
        result = ThreadEncoder._encode_commitments([])
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
        result = ThreadEncoder._encode_artifacts(analysis)
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
        result = ThreadEncoder._encode_artifacts(analysis)
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
        result = ThreadEncoder._encode_artifacts(analysis)
        assert "[ARTIFACT:ORDER_ID=XYZ-123]" in result


class TestEncodeSentiment:
    def test_simple_sentiment(self):
        sentiment = SentimentTrajectory(start="FRUSTRATED", end="SATISFIED")
        result = ThreadEncoder._encode_sentiment(sentiment)
        assert result == "[SENTIMENT:FRUSTRATED→SATISFIED]"

    def test_sentiment_with_turning_points(self):
        sentiment = SentimentTrajectory(
            start="FRUSTRATED",
            end="SATISFIED",
            turning_points=[(3, "NEUTRAL"), (5, "SATISFIED")]
        )
        result = ThreadEncoder._encode_sentiment(sentiment)
        assert "FRUSTRATED→NEUTRAL→SATISFIED" in result

    def test_sentiment_no_duplicate_emotions(self):
        sentiment = SentimentTrajectory(
            start="NEUTRAL",
            end="SATISFIED",
            turning_points=[(2, "NEUTRAL"), (3, "NEUTRAL"), (4, "SATISFIED")]
        )
        result = ThreadEncoder._encode_sentiment(sentiment)
        assert result.count("NEUTRAL") == 1

    def test_sentiment_default_neutral(self):
        sentiment = SentimentTrajectory()
        result = ThreadEncoder._encode_sentiment(sentiment)
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
        assert result.component == "THREAD_ENCODER"
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
    """Full integration tests for thread_encoder encoding"""

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


class TestV2Improvements:
    """Tests for the v2 improvements identified in the review."""

    def test_name_change_domain_is_account(self, encoder):
        """Example 1 from review: Name change should be DOMAIN=ACCOUNT, not BILLING."""
        transcript = """Customer: Hi Sophia, I recently changed my last name after getting married, and I'd like to update it on my account. But when I tried to edit my profile, it said the field is locked.
Agent: Congratulations on your marriage! And sure, I can help you with that. May I have your account email and the name as it currently appears?
Customer: It's emily.reed@example.com, and it still shows as Emily Reed. I'd like to change it to Emily Carter.
Agent: Got it. Thank you, Emily. For name changes, we just need to verify your identity before updating the record. I'll send a quick verification code to your registered email.
Customer: Okay, I see it — the code is 542819.
Agent: Perfect, verified. I've updated your account name to Emily Carter. It may take about 30 minutes for the change to show across all systems.
Customer: Great, that was fast. Do I need to update my billing details separately?
Agent: Good question — the billing name will automatically sync, but if your payment method is under a different name, you might need to update that manually in your payment settings.
Customer: Got it. And just to confirm, my login credentials stay the same, right?
Agent: Yes, nothing changes with your login. Only your display and billing name are updated.
Customer: Awesome. Thanks for walking me through this.
Agent: My pleasure, Emily — or should I say Mrs. Carter now! Congratulations again, and is there anything else I can assist you with today?
Customer: Haha, that's all. Thanks, Sophia!
Agent: You're very welcome. Have a wonderful day!"""

        metadata = {"call_id": "REVIEW-001", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)
        compressed = result.compressed

        assert "[DOMAIN:ACCOUNT]" in compressed
        assert "[CUSTOMER_INTENT:REQUEST_PROFILE_UPDATE]" in compressed
        assert "[CONTEXT:EMAIL_PROVIDED]" in compressed

    def test_refund_escalation_domain_billing(self, encoder):
        """Example 2 from review: Refund escalation with case number and delay."""
        transcript = """Customer: Hi, I'm honestly pretty frustrated right now. This is the third time I've called about the same issue — my refund still hasn't come through, even though it was approved last week.
Agent: I'm really sorry to hear that. Let's get this sorted once and for all. May I have your case number or the email linked to your account?
Customer: It's jason.miller@example.com and the case number is 22091.
Agent: Thanks, Jason. Give me a moment... alright, I can see that your refund was approved on the 10th but hasn't been processed yet due to a pending review flag. That shouldn't have happened.
Customer: Yeah, that's exactly what the last agent said. I've been waiting 12 days already.
Agent: Completely understandable, and I apologize for the delay. What I'm going to do right now is escalate this directly to our billing supervisor. They'll have the authority to override the pending status and release the refund immediately.
Customer: That's all I've been asking for. Can you guarantee it'll be done today?
Agent: Once I mark it as a high-priority escalation, it'll move to the top of the queue. Typically, these are processed within a few hours.
Customer: Alright, but I really need confirmation this time.
Agent: Absolutely. I'm creating the escalation now... okay, your escalation ticket number is ESC-45390. I've also added my name to the notes so the supervisor knows this was personally verified.
Customer: That's good to hear. I just want closure on this.
Agent: Totally understandable. You'll receive an email update by the end of the day confirming the refund transfer.
Customer: Alright, I appreciate your help, Daniel. You've been much more responsive than the last person.
Agent: Thank you for saying that, Jason. I'll keep an eye on your case and personally follow up to ensure it's resolved.
Customer: Appreciate that. Hopefully this is the last call I need to make.
Agent: I hope so too. Thanks for your patience — you'll hear from us shortly with confirmation."""

        metadata = {"call_id": "REVIEW-002", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)
        compressed = result.compressed

        assert "[DOMAIN:BILLING]" in compressed
        assert "[CUSTOMER_INTENT:REQUEST_REFUND_STATUS]" in compressed
        assert "[CONTEXT:EMAIL_PROVIDED]" in compressed
        # Should capture the case number
        assert "[CONTEXT:CASE_ID_PROVIDED]" in compressed
        # Should capture the delay
        assert "DELAY_12_DAYS" in compressed
        # Escalation should be in actions
        assert "ESCALATION_CREATED" in compressed
        # ESC-45390 should be captured as artifact
        assert "ESC-45390" in compressed

    def test_replacement_headset_domain_fulfillment(self, encoder):
        """Example 3 from review: Replacement headset should be DOMAIN=FULFILLMENT."""
        transcript = """Customer: Hi Nina, I called last week about a defective Bluetooth headset I ordered. I was told a replacement would be shipped, but I haven't received any update yet.
Agent: Hi there, I'm sorry for the delay. Let's check what's happening. Could you please share your order number?
Customer: Sure, it's 7730219.
Agent: Thanks. One moment... okay, I see that the replacement order was created last Friday, but the warehouse hadn't assigned a tracking number yet. That's why you haven't received a shipping notification.
Customer: Ah, that makes sense. Is there any delay on your end?
Agent: A slight one — the headset model you ordered just came back into stock yesterday, so the replacement should go out today. I can prioritize your order so it ships in the next batch.
Customer: I'd really appreciate that. I've been using a backup headset that keeps cutting out.
Agent: Understood! I've just flagged it for same-day dispatch. You'll get an email with the tracking ID within a few hours.
Customer: Great. Once I receive the new one, do I need to return the defective item?
Agent: Yes, please. We'll send a prepaid return label in the box. Just pack the old headset and drop it at any postal point within 10 days.
Customer: Got it. Thanks for clearing that up.
Agent: You're welcome! I'll follow up tomorrow to make sure the replacement is in transit.
Customer: Awesome, thanks Nina.
Agent: Anytime! Hope you get to enjoy the new headset soon."""

        metadata = {"call_id": "REVIEW-003", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)
        compressed = result.compressed

        assert "[DOMAIN:FULFILLMENT]" in compressed
        assert "[CUSTOMER_INTENT:FOLLOWUP_REPLACEMENT_STATUS]" in compressed
        # Should NOT be RESOLVED since physical shipment is pending
        assert "[STATE:RESOLVED]" not in compressed
        # Should detect follow-up commitment
        assert "FOLLOWUP" in compressed

    def test_unclassified_domain_fallback(self, encoder):
        """When no domain can be determined, should return UNCLASSIFIED instead of BILLING."""
        transcript = """Customer: Hello, I have a question.
Agent: Sure, how can I help you today?
Customer: I was wondering about something.
Agent: Of course, go ahead."""

        metadata = {"call_id": "UNCLASS-001"}
        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)
        compressed = result.compressed

        assert "[DOMAIN:UNCLASSIFIED]" in compressed
        assert "[DOMAIN:BILLING]" not in compressed

    def test_resolution_from_actions(self):
        """Resolution should be derived from the last significant agent action."""
        resolution = Resolution(type="RESOLVED")
        actions = [
            Action(type="ACCOUNT_VERIFIED"),
            Action(type="REFUND_INITIATED"),
        ]
        result = ThreadEncoder._encode_resolution(resolution, actions)
        assert result == "[RESOLUTION:REFUND_INITIATED]"

    def test_resolution_from_profile_update(self):
        """Profile update action should produce PROFILE_UPDATED resolution."""
        resolution = Resolution(type="RESOLVED")
        actions = [
            Action(type="IDENTITY_VERIFIED"),
            Action(type="PROFILE_UPDATED"),
        ]
        result = ThreadEncoder._encode_resolution(resolution, actions)
        assert result == "[RESOLUTION:PROFILE_UPDATED]"

    def test_resolution_fallback_no_actions(self):
        """Without actions, should fall back to resolution type mapping."""
        resolution = Resolution(type="RESOLVED")
        result = ThreadEncoder._encode_resolution(resolution, actions=[])
        assert result == "[RESOLUTION:ISSUE_RESOLVED]"

    def test_state_pending_processing_on_escalation(self):
        """Escalation + billing context should produce ESCALATED.

        The escalation team is handling the issue; the customer is not pending
        any action, so PENDING_CUSTOMER would be misleading.
        """
        resolution = Resolution(type="PENDING")
        state = ResolutionState(type="PENDING")
        actions = [
            Action(type="CASE_REVIEWED"),
            Action(type="ESCALATION_CREATED"),
        ]
        result = ThreadEncoder._encode_state(
            resolution, state, actions=actions, domain="BILLING"
        )
        assert result == "[STATE:ESCALATED]"

    def test_state_pending_shipment(self):
        """Physical shipment context should produce PENDING_SHIPMENT."""
        resolution = Resolution(type="PENDING")
        state = ResolutionState(type="PENDING")
        actions = [
            Action(type="ORDER_STATUS_CHECKED"),
            Action(type="PRIORITY_DISPATCH_FLAGGED"),
        ]
        result = ThreadEncoder._encode_state(
            resolution, state, actions=actions, domain="FULFILLMENT"
        )
        assert result == "[STATE:PENDING_SHIPMENT]"

    def test_state_pending_engineering_fix(self):
        """Technical escalation should produce PENDING_ENGINEERING."""
        resolution = Resolution(type="ESCALATED")
        state = ResolutionState(type="ESCALATED")
        actions = [
            Action(type="LOGS_REVIEWED"),
            Action(type="ESCALATION_CREATED"),
        ]
        result = ThreadEncoder._encode_state(
            resolution, state, actions=actions, domain="TECHNICAL"
        )
        assert result == "[STATE:PENDING_ENGINEERING]"

    def test_commitment_gold_format_refund(self):
        """Commitment should use gold-style format."""
        promises = [
            PromiseCommitment(
                type="REFUND_PROMISE",
                description="Refund in 3-5 business days",
                timeline="3-5d",
                turn_index=5,
            )
        ]
        result = ThreadEncoder._encode_commitments(promises)
        assert result[0] == "[COMMITMENT:REFUND_3-5_BUSINESS_DAYS]"

    def test_commitment_gold_format_followup(self):
        """FOLLOWUP commitment should produce clean label."""
        promises = [
            PromiseCommitment(
                type="FOLLOWUP",
                description="I'll follow up tomorrow",
                timeline="TOMORROW",
                turn_index=8,
            )
        ]
        result = ThreadEncoder._encode_commitments(promises)
        assert result[0] == "[COMMITMENT:FOLLOWUP_TOMORROW]"

    def test_commitment_gold_format_email(self):
        """Confirmation email commitment should produce clean label."""
        promises = [
            PromiseCommitment(
                type="CONFIRMATION_EMAIL",
                description="You'll receive a confirmation email",
                timeline="TODAY",
                turn_index=6,
            )
        ]
        result = ThreadEncoder._encode_commitments(promises)
        assert result[0] == "[COMMITMENT:CONFIRMATION_EMAIL_TODAY]"

    def test_service_outage_resolved_no_false_positive_actions(self, encoder):
        """Service outage resolved on the call — no false-positive actions."""
        transcript = """Agent: Hi, this is Isabella, senior support specialist. I'm picking up your case that was escalated earlier today about a service outage. I understand you've been trying to get this resolved for over a week?
Customer: Yes, finally! I've called three times. Our business relies on your platform, and it's been offline since last Thursday.
Agent: I can imagine how frustrating that must be. I have your account pulled up now. I see multiple tickets tied to your service ID, and one marked as high-priority from this morning.
Customer: Yeah, but nothing's changed. Every agent keeps saying it's being worked on.
Agent: You're right, and I apologize for the delays. I just checked with the infrastructure team before joining this call — they identified a corrupted configuration file that's been preventing your system from restarting.
Customer: So what does that mean for me? How long until it's fixed?
Agent: The good news is that the engineering team has already replaced the corrupted instance, and your service is in the process of rebooting right now. I can see logs showing recovery steps happening in real time.
Customer: Okay, that's promising. I just want to be sure it actually works this time.
Agent: Absolutely. Let's stay on the line for a few minutes while I confirm the reboot status... alright, I'm now seeing the connection restored on our side. Can you refresh your dashboard?
Customer: Yep... and it's back! Finally! I can see everything online again.
Agent: Wonderful. I'll monitor your account for the next few hours to ensure it remains stable. I'll also extend your current billing cycle by five days to compensate for the downtime.
Customer: Wow, thank you, Isabella. That's really appreciated. You've been the first person to actually fix this.
Agent: I'm glad we could turn it around. I know it's been a long week — thank you for your patience.
Customer: You've been great. Thanks again.
Agent: You're very welcome. Have a better rest of your week!"""

        metadata = {"call_id": "OUTAGE-001", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)
        compressed = result.compressed

        # Domain should be TECHNICAL (service outage)
        assert "[DOMAIN:TECHNICAL]" in compressed

        # Should NOT have false-positive actions
        assert "ESCALATION_CREATED" not in compressed  # was escalated EARLIER, not now
        assert "REPLACEMENT_ORDERED" not in compressed  # replaced a config file, not product
        assert "TRIAL_ACTIVATED" not in compressed       # no trial
        assert "REFUND_INITIATED" not in compressed      # compensate != refund

        # Customer mentions agent name "Isabella" — should NOT be NAME_PROVIDED
        assert "NAME_PROVIDED" not in compressed

        # Should have ACCOUNT_LOOKUP (agent pulled up account)
        assert "ACCOUNT_LOOKUP" in compressed

    def test_agent_fallback_for_issue_and_domain(self, encoder):
        """When customer turns don't contain issue keywords, fall back to agent turns."""
        transcript = """Customer: Hi, I need some help please.
Agent: Hi, this is Aisha from technical support. I understand you're having trouble with your cloud storage syncing.
Customer: Yes, exactly. It's been really frustrating.
Agent: Let me check the logs and see what's going on.
Agent: I found the issue — there's a token error in your sync configuration. I'm escalating this to our engineering team.
Customer: Okay, thank you."""

        metadata = {"call_id": "AGENT-FALLBACK-001", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata, verbose=False)
        compressed = result.compressed

        # Domain should be TECHNICAL (from agent mentioning sync)
        assert "[DOMAIN:TECHNICAL]" in compressed
        # Should not be UNCLASSIFIED since agent stated the issue
        assert "[DOMAIN:UNCLASSIFIED]" not in compressed


class TestThreadFixes:
    """Tests for fixes described in Thread-Fixes.md."""

    def test_business_pro_upgrade_interaction_trigger(self, encoder):
        """Transcript 1: SALES call with plan upgrade consideration."""
        transcript = """Customer: Hi Laura, I'm considering upgrading to your Business Pro plan, but I wanted to know if it includes advanced analytics features.
Agent: Great question! The Business Pro plan does include analytics, but there are a few levels to it. Can I ask how you plan to use the data — mostly for tracking sales, or customer engagement?
Customer: Mostly engagement. We want to track activity per user, response times, and conversion metrics.
Agent: Perfect, that's exactly what the advanced analytics module covers. You'd get access to dashboards that show detailed engagement stats by user segment, plus export options for CSV and API access.
Customer: Sounds good. Does that come standard or as an add-on?
Agent: It's included in the Business Pro plan. The only add-on you might consider is the predictive insights module, which uses machine learning to forecast trends.
Customer: Interesting — what's the cost for that?
Agent: It's an additional $30 a month per account. But if you're upgrading before the end of the quarter, you'd qualify for a 20% discount for the first six months.
Customer: That's tempting. Can I try it before committing?
Agent: Yes, we offer a 14-day trial for the predictive module. I can activate that trial for you right after the call.
Customer: Please do. This helps a lot.
Agent: Done! You'll receive a confirmation email shortly with setup instructions.
Customer: Awesome, thank you Laura.
Agent: My pleasure! Feel free to reach out anytime if you need help exploring the analytics dashboard."""

        metadata = {"call_id": "T1", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata)
        compressed = result.compressed

        assert "[INTERACTION_TRIGGER:REQUEST_PLAN_UPGRADE]" in compressed
        assert "TRIAL_ACTIVATED" in compressed
        # $30 add-on should be flagged as EXTRA_CHARGE
        assert "AMT=$30/EXTRA_CHARGE" in compressed

    def test_refund_escalation_trigger(self, encoder):
        """Transcript 2: Refund still hasn't come through should trigger REFUND_NOT_RECEIVED."""
        transcript = """Customer: Hi, I'm honestly pretty frustrated right now. This is the third time I've called about the same issue — my refund still hasn't come through, even though it was approved last week.
Agent: I'm really sorry to hear that. Let's get this sorted once and for all. May I have your case number or the email linked to your account?
Customer: It's jason.miller@example.com and the case number is 22091.
Agent: Thanks, Jason. Give me a moment... alright, I can see that your refund was approved on the 10th but hasn't been processed yet due to a pending review flag. That shouldn't have happened.
Customer: Yeah, that's exactly what the last agent said. I've been waiting 12 days already.
Agent: Completely understandable, and I apologize for the delay. What I'm going to do right now is escalate this directly to our billing supervisor. They'll have the authority to override the pending status and release the refund immediately.
Customer: That's all I've been asking for. Can you guarantee it'll be done today?
Agent: Once I mark it as a high-priority escalation, it'll move to the top of the queue. Typically, these are processed within a few hours.
Customer: Alright, but I really need confirmation this time.
Agent: Absolutely. I'm creating the escalation now... okay, your escalation ticket number is ESC-45390. I've also added my name to the notes so the supervisor knows this was personally verified.
Customer: That's good to hear. I just want closure on this.
Agent: Totally understandable. You'll receive an email update by the end of the day confirming the refund transfer.
Customer: Alright, I appreciate your help, Daniel. You've been much more responsive than the last person.
Agent: Thank you for saying that, Jason. I'll keep an eye on your case and personally follow up to ensure it's resolved.
Customer: Appreciate that. Hopefully this is the last call I need to make.
Agent: I hope so too. Thanks for your patience — you'll hear from us shortly with confirmation."""

        metadata = {"call_id": "T2", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata)
        compressed = result.compressed

        assert "[INTERACTION_TRIGGER:REFUND_NOT_RECEIVED]" in compressed
        # Escalation must not produce a RESOLVED state
        assert "[STATE:RESOLVED]" not in compressed
        assert "[STATE:ESCALATED]" in compressed
        # Resolution should reflect escalation, not a settled outcome
        assert "[RESOLUTION:ESCALATED]" in compressed

    def test_replacement_tracking_trigger(self, encoder):
        """Transcript 3: Haven't received any update should trigger TRACKING_NOT_ASSIGNED."""
        transcript = """Customer: Hi Nina, I called last week about a defective Bluetooth headset I ordered. I was told a replacement would be shipped, but I haven't received any update yet.
Agent: Hi there, I'm sorry for the delay. Let's check what's happening. Could you please share your order number?
Customer: Sure, it's 7730219.
Agent: Thanks. One moment... okay, I see that the replacement order was created last Friday, but the warehouse hadn't assigned a tracking number yet. That's why you haven't received a shipping notification.
Customer: Ah, that makes sense. Is there any delay on your end?
Agent: A slight one — the headset model you ordered just came back into stock yesterday, so the replacement should go out today. I can prioritize your order so it ships in the next batch.
Customer: I'd really appreciate that. I've been using a backup headset that keeps cutting out.
Agent: Understood! I've just flagged it for same-day dispatch. You'll get an email with the tracking ID within a few hours.
Customer: Great. Once I receive the new one, do I need to return the defective item?
Agent: Yes, please. We'll send a prepaid return label in the box. Just pack the old headset and drop it at any postal point within 10 days.
Customer: Got it. Thanks for clearing that up.
Agent: You're welcome! I'll follow up tomorrow to make sure the replacement is in transit.
Customer: Awesome, thanks Nina.
Agent: Anytime! Hope you get to enjoy the new headset soon."""

        metadata = {"call_id": "T3", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata)
        compressed = result.compressed

        assert "[INTERACTION_TRIGGER:TRACKING_NOT_ASSIGNED]" in compressed

    def test_unexpected_fee_trigger(self, encoder):
        """Transcript 5: Unexpected service fee should trigger UNEXPECTED_CHARGE."""
        transcript = """Agent: Hello, this is Leo with billing support. How can I help you today?
Customer: Hi Leo, I just noticed a $20 service fee on my bill that I wasn't expecting. I've been a customer for over three years and never had that before.
Agent: Thanks for bringing that up. Let me take a look at your account details to find out what triggered that fee. May I have your account email?
Customer: Sure, it's andrea.peters@example.com.
Agent: Alright, give me a moment... okay, I see the fee you mentioned. It's a reactivation charge from when your payment was processed three days late last month.
Customer: Oh, but I thought the grace period was five days.
Agent: You're absolutely right — it used to be five days, but our policy changed in July. It's now a three-day grace period. However, I do see you've had a perfect payment record before this, so I can waive it as a one-time courtesy.
Customer: That would be great, I really appreciate it.
Agent: No problem. I've just reversed the charge. You'll see a $20 credit applied within the next 24 hours, and your updated invoice will reflect that.
Customer: Perfect. Can you send me a confirmation email too?
Agent: Of course. I'll include the refund reference number — BCR-55209 — in that email.
Customer: Thank you so much, Leo. That clears everything up.
Agent: My pleasure, Andrea. Glad we could fix it quickly!"""

        metadata = {"call_id": "T5", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata)
        compressed = result.compressed

        assert "[INTERACTION_TRIGGER:UNEXPECTED_CHARGE]" in compressed
        assert "[STATE:RESOLVED]" in compressed
        # $20 fee and $20 credit should be captured
        assert "AMT=$20/FEE" in compressed or "AMT=$20/CREDIT" in compressed

    def test_plan_upgrade_trigger_and_action(self, encoder):
        """Transcript 6: Upgrade to Premium should trigger REQUEST_PLAN_UPGRADE and PLAN_UPGRADED."""
        transcript = """Agent: Good afternoon, this is Chloe from customer care. How can I assist you today?
Customer: Hi Chloe, I'm currently on the Starter plan, and I'm thinking of upgrading to Premium. Can you tell me what's different?
Agent: Absolutely. The Premium plan gives you access to unlimited projects, advanced analytics, and priority support. You also get integration options for CRMs like Salesforce and HubSpot.
Customer: That sounds useful. Does it include team collaboration tools too?
Agent: Yes, it does. You'll get real-time editing, version history, and role-based permissions for team members.
Customer: Nice. How much is it per month?
Agent: The Premium plan is $49 a month, or $480 if you choose annual billing — which saves you about $108 per year.
Customer: Hmm, not bad. If I upgrade mid-cycle, do I get billed immediately?
Agent: You'd only pay the prorated difference for the remaining days in your billing period. The upgrade takes effect right away.
Customer: Great, that's transparent. Can I switch back if it's not what I expected?
Agent: Yes, you can downgrade anytime before your next renewal, and the system automatically adjusts your credits.
Customer: Perfect. Go ahead and upgrade me, then.
Agent: Done! Your account is now on the Premium plan. You'll receive a confirmation email with all the new features highlighted.
Customer: That was quick. Thanks for the great service.
Agent: Always happy to help! Enjoy your upgraded plan."""

        metadata = {"call_id": "T6", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata)
        compressed = result.compressed

        assert "[INTERACTION_TRIGGER:REQUEST_PLAN_UPGRADE]" in compressed
        assert "PLAN_UPGRADED" in compressed

    def test_service_disruption_trigger(self, encoder):
        """Transcript 8: Service been offline should trigger SERVICE_DISRUPTION."""
        transcript = """Agent: Hi, this is Isabella, senior support specialist. I'm picking up your case that was escalated earlier today about a service outage. I understand you've been trying to get this resolved for over a week?
Customer: Yes, finally! I've called three times. Our business relies on your platform, and it's been offline since last Thursday.
Agent: I can imagine how frustrating that must be. I have your account pulled up now. I see multiple tickets tied to your service ID, and one marked as high-priority from this morning.
Customer: Yeah, but nothing's changed. Every agent keeps saying it's being worked on.
Agent: You're right, and I apologize for the delays. I just checked with the infrastructure team before joining this call — they identified a corrupted configuration file that's been preventing your system from restarting.
Customer: So what does that mean for me? How long until it's fixed?
Agent: The good news is that the engineering team has already replaced the corrupted instance, and your service is in the process of rebooting right now. I can see logs showing recovery steps happening in real time.
Customer: Okay, that's promising. I just want to be sure it actually works this time.
Agent: Absolutely. Let's stay on the line for a few minutes while I confirm the reboot status... alright, I'm now seeing the connection restored on our side. Can you refresh your dashboard?
Customer: Yep... and it's back! Finally! I can see everything online again.
Agent: Wonderful. I'll monitor your account for the next few hours to ensure it remains stable. I'll also extend your current billing cycle by five days to compensate for the downtime.
Customer: Wow, thank you, Isabella. That's really appreciated. You've been the first person to actually fix this.
Agent: I'm glad we could turn it around. I know it's been a long week — thank you for your patience.
Customer: You've been great. Thanks again.
Agent: You're very welcome. Have a better rest of your week!"""

        metadata = {"call_id": "T8", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata)
        compressed = result.compressed

        assert "[INTERACTION_TRIGGER:SERVICE_DISRUPTION]" in compressed

    def test_escalated_resolution_no_resolved_contradiction(self):
        """ESCALATED + RESOLVED simultaneously is not allowed."""
        resolution = Resolution(type="RESOLVED")
        actions = [
            Action(type="FEE_REVIEWED"),
            Action(type="ESCALATION_CREATED"),
            Action(type="FEE_WAIVED"),
        ]
        result = ThreadEncoder._encode_resolution(resolution, actions)
        # Even though FEE_WAIVED is a definitive action, escalation takes precedence
        assert result == "[RESOLUTION:ESCALATED]"

    def test_escalated_with_service_restored_resolves(self):
        """Escalation followed by SERVICE_RESTORED should produce SERVICE_RESTORED resolution."""
        resolution = Resolution(type="RESOLVED")
        actions = [
            Action(type="ESCALATION_CREATED"),
            Action(type="LOGS_REVIEWED"),
            Action(type="SERVICE_RESTORED"),
        ]
        result = ThreadEncoder._encode_resolution(resolution, actions)
        assert result == "[RESOLUTION:SERVICE_RESTORED]"

    def test_extraction_confidence_fields_present(self, encoder):
        """TranscriptAnalysis must include extraction_confidence and requires_review."""
        transcript = """Customer: I need help with my account.
Agent: Sure, I can help you. What seems to be the issue?
Customer: My login isn't working.
Agent: Let me look into that for you."""

        metadata = {"call_id": "CONF-001", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata)
        analysis_dict = result.metadata["analysis"]
        assert "extraction_confidence" in analysis_dict
        assert "requires_review" in analysis_dict
        confidence = float(analysis_dict["extraction_confidence"])
        assert 0.0 <= confidence <= 1.0
        assert analysis_dict["requires_review"] in ("True", "False")

    def test_trial_activated_state_is_trial_active(self):
        """TRIAL_ACTIVATED action must produce STATE:TRIAL_ACTIVE, not STATE:RESOLVED."""
        resolution = Resolution(type="RESOLVED")
        actions = [
            Action(type="PLAN_FEATURES_EXPLAINED"),
            Action(type="TRIAL_ACTIVATED"),
        ]
        result = ThreadEncoder._encode_state(
            resolution, None, actions=actions
        )
        assert result == "[STATE:TRIAL_ACTIVE]"

    def test_plan_upgraded_state_is_upgraded(self):
        """PLAN_UPGRADED action must produce STATE:UPGRADED, not STATE:RESOLVED."""
        resolution = Resolution(type="RESOLVED")
        actions = [
            Action(type="PLAN_FEATURES_EXPLAINED"),
            Action(type="PLAN_UPGRADED"),
        ]
        result = ThreadEncoder._encode_state(
            resolution, None, actions=actions
        )
        assert result == "[STATE:UPGRADED]"

    def test_sales_upgrade_no_billing_dispute(self, encoder):
        """Premium upgrade SALES call must not produce [ISSUE:BILLING_DISPUTE] from pricing info."""
        transcript = """Agent: Good afternoon, this is Chloe from customer care. How can I assist you today?
Customer: Hi Chloe, I'm currently on the Starter plan, and I'm thinking of upgrading to Premium. Can you tell me what's different?
Agent: Absolutely. The Premium plan gives you access to unlimited projects, advanced analytics, and priority support.
Customer: How much is it per month?
Agent: The Premium plan is $49 a month, or $480 if you choose annual billing.
Customer: Perfect. Go ahead and upgrade me, then.
Agent: Done! Your account is now on the Premium plan. You'll receive a confirmation email with all the new features highlighted."""

        metadata = {"call_id": "SALES-01", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata)
        compressed = result.compressed

        assert "BILLING_DISPUTE" not in compressed
        assert "PLAN_UPGRADED" in compressed
        assert "[STATE:UPGRADED]" in compressed

    def test_requires_review_sales_without_monetization(self, encoder):
        """SALES call where agent only explains but takes no monetization action must require review."""
        transcript = """Customer: I'm interested in upgrading my account to the premium tier.
Agent: Sure, I can tell you about our premium features. The premium plan includes advanced analytics and priority support.
Customer: Thanks for the information.
Agent: Let me know if you have any other questions."""

        metadata = {"call_id": "SALES-02", "channel": "voice"}
        result = encoder.encode(transcript=transcript, metadata=metadata)
        analysis_dict = result.metadata["analysis"]
        assert analysis_dict["requires_review"] == "True"
