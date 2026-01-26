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
def encoder(nlp, vocab, rules):
    """Create encoder instance, clearing singleton"""
    # Clear singleton to allow fresh instance
    TranscriptEncoder._instances = {}
    return TranscriptEncoder(nlp=nlp, vocab=vocab, rules=rules)


class TestTranscriptEncoderInit:
    def test_initialization(self, nlp, vocab, rules):
        TranscriptEncoder._instances = {}
        encoder = TranscriptEncoder(nlp=nlp, vocab=vocab, rules=rules)
        assert encoder._analyzer is not None
        assert encoder.analysis is None


class TestEncodeCallInfo:
    def test_basic_call_info(self):
        call = CallInfo(
            call_id="123",
            type="SUPPORT",
            channel="voice",
            duration=10
        )
        result = TranscriptEncoder._encode_call_info(call)
        assert result == "[CALL:SUPPORT:DURATION=5m:CHANNEL=voice]"

    def test_call_info_with_agent(self):
        call = CallInfo(
            call_id="123",
            type="SUPPORT",
            channel="voice",
            duration=10,
            agent="Sarah"
        )
        result = TranscriptEncoder._encode_call_info(call)
        assert "AGENT=Sarah" in result
        assert result.startswith("[CALL:SUPPORT")

    def test_call_info_with_channel(self):
        call = CallInfo(
            call_id="123",
            type="BILLING",
            channel="chat",
            duration=8
        )
        result = TranscriptEncoder._encode_call_info(call)
        assert "CHANNEL=chat" in result

    def test_call_info_duration_conversion(self):
        # Duration is in turns, converted to minutes (turns / 2)
        call = CallInfo(
            call_id="123",
            type="SUPPORT",
            channel="voice",
            duration=20  # 20 turns = 10 minutes
        )
        result = TranscriptEncoder._encode_call_info(call)
        assert "DURATION=10m" in result

    def test_call_info_minimum_duration(self):
        call = CallInfo(
            call_id="123",
            type="SUPPORT",
            channel="voice",
            duration=1  # 1 turn = minimum 1 minute
        )
        result = TranscriptEncoder._encode_call_info(call)
        assert "DURATION=1m" in result


class TestEncodeCustomer:
    def test_basic_customer(self, encoder):
        customer = CustomerProfile()
        result = encoder._encode_customer(customer)
        assert result == "[CUSTOMER]"

    def test_customer_with_account(self, encoder):
        customer = CustomerProfile(account="847-392-1045")
        result = encoder._encode_customer(customer)
        assert "ACCOUNT=847-392-1045" in result

    def test_customer_with_tier(self, encoder):
        customer = CustomerProfile(tier="PREMIUM")
        result = encoder._encode_customer(customer)
        assert "TIER=PREMIUM" in result

    def test_customer_with_tenure(self, encoder):
        customer = CustomerProfile(tenure="5yr")
        result = encoder._encode_customer(customer)
        assert "TENURE=5yr" in result

    def test_customer_with_address(self, encoder):
        customer = CustomerProfile(
            attributes={"address": "123 Main Street"}
        )
        result = encoder._encode_customer(customer)
        assert "ADDRESS=" in result

    def test_customer_with_organization(self, encoder):
        customer = CustomerProfile(
            attributes={"organization": "Acme Corp"}
        )
        result = encoder._encode_customer(customer)
        assert "ORG=Acme_Corp" in result

    def test_customer_with_location(self, encoder):
        customer = CustomerProfile(
            attributes={"location": "New York"}
        )
        result = encoder._encode_customer(customer)
        assert "LOCATION=New York" in result

    def test_customer_full_profile(self, encoder):
        customer = CustomerProfile(
            account="123456",
            tier="ENTERPRISE",
            tenure="10yr",
            attributes={
                "address": "456 Oak Avenue",
                "organization": "Big Company"
            }
        )
        result = encoder._encode_customer(customer)
        assert "ACCOUNT=123456" in result
        assert "TIER=ENTERPRISE" in result
        assert "TENURE=10yr" in result
        assert "ADDRESS=" in result
        assert "ORG=Big_Company" in result


class TestEncodeIssue:
    def test_basic_issue(self):
        issue = Issue(type="INTERNET_OUTAGE")
        result = TranscriptEncoder._encode_issue(issue, [])
        assert result == "[ISSUE:INTERNET_OUTAGE:SEVERITY=LOW]"

    def test_issue_with_severity(self):
        issue = Issue(type="BILLING_DISPUTE", severity="HIGH")
        result = TranscriptEncoder._encode_issue(issue, [])
        assert "SEVERITY=HIGH" in result

    def test_issue_with_frequency(self):
        issue = Issue(type="INTERNET_OUTAGE", frequency="3x_daily")
        result = TranscriptEncoder._encode_issue(issue, [])
        assert "FREQ=3x_daily" in result

    def test_issue_with_duration(self):
        issue = Issue(type="SERVICE_INTERRUPTION", duration="3d")
        result = TranscriptEncoder._encode_issue(issue, [])
        assert "DURATION=3d" in result

    def test_issue_with_pattern(self):
        issue = Issue(type="INTERNET_OUTAGE", pattern="9am+1pm+6pm")
        result = TranscriptEncoder._encode_issue(issue, [])
        assert "PATTERN=9am+1pm+6pm" in result

    def test_issue_with_days(self):
        issue = Issue(
            type="INTERNET_OUTAGE",
            attributes={"days": ["MON", "TUE", "WED"]}
        )
        result = TranscriptEncoder._encode_issue(issue, [])
        assert "DAYS=MON+TUE+WED" in result

    def test_issue_with_impact(self):
        issue = Issue(type="INTERNET_OUTAGE", impact="WORK_FROM_HOME")
        result = TranscriptEncoder._encode_issue(issue, [])
        assert "IMPACT=WORK_FROM_HOME" in result

    def test_billing_issue_with_amounts(self):
        issue = Issue(type="BILLING_DISPUTE")
        turns = [
            Turn(
                speaker="customer",
                text="I was charged $14.99",
                entities={"money": ["$14.99", "$16.99"]}
            )
        ]
        result = TranscriptEncoder._encode_issue(issue, turns)
        assert "AMOUNTS=$14.99+$16.99" in result


class TestEncodeActionChain:
    def test_single_action(self):
        actions = [Action(type="TROUBLESHOOT")]
        result = TranscriptEncoder._encode_action_chain(actions)
        assert result == "[ACTION_CHAIN:TROUBLESHOOT]"

    def test_multiple_actions(self):
        actions = [
            Action(type="TROUBLESHOOT"),
            Action(type="ACCOUNT_VERIFIED"),
            Action(type="REFUND_PROCESSED")
        ]
        result = TranscriptEncoder._encode_action_chain(actions)
        assert result == "[ACTION_CHAIN:TROUBLESHOOT→ACCOUNT_VERIFIED→REFUND_PROCESSED]"

    def test_action_chain_preserves_order(self):
        actions = [
            Action(type="ACCOUNT_VERIFIED"),
            Action(type="TROUBLESHOOT"),
            Action(type="DOCUMENTATION_UPDATED")
        ]
        result = TranscriptEncoder._encode_action_chain(actions)
        assert result == "[ACTION_CHAIN:ACCOUNT_VERIFIED→TROUBLESHOOT→DOCUMENTATION_UPDATED]"

    def test_two_actions(self):
        actions = [
            Action(type="REFUND"),
            Action(type="CREDIT")
        ]
        result = TranscriptEncoder._encode_action_chain(actions)
        assert result == "[ACTION_CHAIN:REFUND→CREDIT]"


class TestEncodeResolution:
    def test_basic_resolution(self):
        resolution = Resolution(type="RESOLVED")
        result = TranscriptEncoder._encode_resolution(resolution)
        assert result == "[RESOLUTION:RESOLVED]"

    def test_resolution_with_timeline(self):
        resolution = Resolution(type="PENDING", timeline="24h")
        result = TranscriptEncoder._encode_resolution(resolution)
        assert "TIMELINE=24h" in result

    def test_resolution_with_ticket(self):
        resolution = Resolution(type="ESCALATED", ticket_id="TK12345")
        result = TranscriptEncoder._encode_resolution(resolution)
        assert "TICKET=TK12345" in result

    def test_resolution_with_next_steps(self):
        resolution = Resolution(type="PENDING", next_steps="callback tomorrow")
        result = TranscriptEncoder._encode_resolution(resolution)
        assert "NEXT=callback_tomorrow" in result

    def test_resolution_full(self):
        resolution = Resolution(
            type="PENDING",
            timeline="48h",
            ticket_id="TK-999",
            next_steps="await confirmation"
        )
        result = TranscriptEncoder._encode_resolution(resolution)
        assert "RESOLUTION:PENDING" in result
        assert "TIMELINE=48h" in result
        assert "TICKET=TK-999" in result
        assert "NEXT=await_confirmation" in result


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
        # Should not have duplicate NEUTRAL
        assert result.count("NEUTRAL") == 1

    def test_sentiment_default_neutral(self):
        sentiment = SentimentTrajectory()
        result = TranscriptEncoder._encode_sentiment(sentiment)
        assert "NEUTRAL" in result


class TestCompressAddress:
    def test_basic_address(self):
        result = TranscriptEncoder._compress_address("123 Main Street")
        assert result == "123_Main_St"

    def test_address_with_avenue(self):
        result = TranscriptEncoder._compress_address("456 Oak Avenue")
        assert result == "456_Oak_Ave"

    def test_address_with_lane(self):
        result = TranscriptEncoder._compress_address("41 Riverbend Lane")
        assert result == "41_Riverbend_Ln"

    def test_address_with_drive(self):
        result = TranscriptEncoder._compress_address("789 Sunset Drive")
        assert result == "789_Sunset_Dr"


class TestEncodeContactInfo:
    def test_no_contact_info(self):
        analysis = TranscriptAnalysis(
            call_info=CallInfo(call_id="1", type="SUPPORT", channel="voice", duration=5),
            customer=CustomerProfile(),
            turns=[Turn(speaker="customer", text="Hello", entities={})],
            issues=[],
            actions=[],
            resolution=Resolution(),
            sentiment_trajectory=SentimentTrajectory()
        )
        result = TranscriptEncoder._encode_contact_info(analysis)
        assert result is None

    def test_with_email(self):
        analysis = TranscriptAnalysis(
            call_info=CallInfo(call_id="1", type="SUPPORT", channel="voice", duration=5),
            customer=CustomerProfile(),
            turns=[
                Turn(
                    speaker="customer",
                    text="My email is test@example.com",
                    entities={"emails": ["test@example.com"]}
                )
            ],
            issues=[],
            actions=[],
            resolution=Resolution(),
            sentiment_trajectory=SentimentTrajectory()
        )
        result = TranscriptEncoder._encode_contact_info(analysis)
        assert result is not None
        assert "EMAIL=test@example.com" in result

    def test_with_phone(self):
        analysis = TranscriptAnalysis(
            call_info=CallInfo(call_id="1", type="SUPPORT", channel="voice", duration=5),
            customer=CustomerProfile(),
            turns=[
                Turn(
                    speaker="customer",
                    text="Call me at 555-123-4567",
                    entities={"phone_numbers": ["555-123-4567"]}
                )
            ],
            issues=[],
            actions=[],
            resolution=Resolution(),
            sentiment_trajectory=SentimentTrajectory()
        )
        result = TranscriptEncoder._encode_contact_info(analysis)
        assert result is not None
        assert "PHONE=555-123-4567" in result

    def test_with_both(self):
        analysis = TranscriptAnalysis(
            call_info=CallInfo(call_id="1", type="SUPPORT", channel="voice", duration=5),
            customer=CustomerProfile(),
            turns=[
                Turn(
                    speaker="customer",
                    text="Contact me",
                    entities={
                        "emails": ["user@test.com"],
                        "phone_numbers": ["123-456-7890"]
                    }
                )
            ],
            issues=[],
            actions=[],
            resolution=Resolution(),
            sentiment_trajectory=SentimentTrajectory()
        )
        result = TranscriptEncoder._encode_contact_info(analysis)
        assert "EMAIL=user@test.com" in result
        assert "PHONE=123-456-7890" in result


class TestEncodeIdentifiers:
    def test_no_identifiers(self):
        analysis = TranscriptAnalysis(
            call_info=CallInfo(call_id="1", type="SUPPORT", channel="voice", duration=5),
            customer=CustomerProfile(),
            turns=[Turn(speaker="customer", text="Hello", entities={})],
            issues=[],
            actions=[],
            resolution=Resolution(),
            sentiment_trajectory=SentimentTrajectory()
        )
        result = TranscriptEncoder._encode_identifiers(analysis)
        assert result is None


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
        # Compression should reduce tokens
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

        # Should have compression
        assert result.compression_ratio > 0
        # Should mention billing-related tokens
        compressed_lower = result.compressed.lower()
        assert "call" in compressed_lower or "support" in compressed_lower

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
        assert "SENTIMENT" in result.compressed

    def test_empty_metadata(self, encoder):
        transcript = "Customer: Hello\nAgent: Hi"
        result = encoder.encode(transcript=transcript, metadata={}, verbose=False)

        assert isinstance(result, CLMOutput)
        assert result.metadata.get("call_id") is None
