import re
from typing import Optional

from spacy import Language
from clm_core.components.transcript.analyzer import TranscriptAnalyzer

from clm_core.dictionary.en.patterns import NER_ADDRESS_ABBREVIATIONS

from . import (
    Action,
    CallInfo,
    CustomerProfile,
    Issue,
    Resolution,
    SentimentTrajectory,
    TranscriptAnalysis,
    Turn,
)
from clm_core.utils.singleton import SingletonMeta
from clm_core.types import CLMOutput
from ...utils.parser_rules import BaseRules
from ...utils.vocabulary import BaseVocabulary

COMPONENT = "TRANSCRIPT"


class TranscriptEncoder(metaclass=SingletonMeta):
    """
    Encodes transcript analysis into compressed tokens

    Philosophy: Extends CLLMTokenizer format: [CALL:metadata][ISSUE:details][ACTION:details][RESOLUTION:details]
    """

    def __init__(self, nlp: Language, vocab: BaseVocabulary, rules: BaseRules):
        self._nlp = nlp
        self._analyzer = TranscriptAnalyzer(nlp=nlp, vocab=vocab, rules=rules)
        self.analysis: TranscriptAnalysis | None = None

    def encode(
        self, *, transcript: str, metadata: dict, verbose: bool = False
    ) -> CLMOutput:
        """
        Encode transcript analysis to compressed format

        Format Design:
        [CALL:type:key=value:...]
        [CUSTOMER:key=value:...]
        [ID:key=value:...]
        [CONTACT:key=value:...]
        [ISSUE:type:key=value:...]
        [ACTION:type:key=value:...]
        [RESOLUTION:type:key=value:...]
        [SENTIMENT:start→end]
        """
        self.analysis = self._analyzer.analyze(transcript, metadata)

        tokens = []

        call_token = self._encode_call_info(self.analysis.call_info)
        tokens.append(call_token)
        if verbose:
            print(f"Call: {call_token}")

        customer_token = self._encode_customer(self.analysis.customer)
        tokens.append(customer_token)
        if verbose:
            print(f"Customer: {customer_token}")

        identifiers = self._encode_identifiers(self.analysis)
        if identifiers:
            tokens.append(identifiers)
            if verbose:
                print(f"Identifiers: {identifiers}")

        contact = self._encode_contact_info(self.analysis)
        if contact:
            tokens.append(contact)
            if verbose:
                print(f"Contact: {contact}")

        for issue in self.analysis.issues:
            issue_token = self._encode_issue(issue, self.analysis.turns)
            tokens.append(issue_token)
            if verbose:
                print(f"Issue: {issue_token}")

        for action in self.analysis.actions:
            action_token = self._encode_action(action)
            tokens.append(action_token)
            if verbose:
                print(f"Action: {action_token}")

        resolution_token = self._encode_resolution(self.analysis.resolution)
        tokens.append(resolution_token)
        if verbose:
            print(f"Resolution: {resolution_token}")

        sentiment_token = self._encode_sentiment(self.analysis.sentiment_trajectory)
        tokens.append(sentiment_token)
        if verbose:
            print(f"Sentiment: {sentiment_token}")

        compressed = " ".join(tokens)
        doc = self._nlp(transcript)

        return CLMOutput(
            compressed=compressed,
            original=transcript,
            component=COMPONENT,
            metadata={
                **metadata,
                "original_length": len(transcript),
                "compressed_length": len(compressed),
                "verbs": [token.lemma_ for token in doc if token.pos_ == "VERB"],
                "noun_chunks": [chunk.text for chunk in doc.noun_chunks],
                "language": "en",
                "has_numbers": bool(re.search(r"\d", transcript)),
                "has_urls": bool(re.search(r"https?://", transcript)),
            },
        )

    @staticmethod
    def _encode_call_info(call: CallInfo) -> str:
        """
        Encode call metadata.
        Convert turns to approximate minutes (assume 2 turns/minute)

        Format: [CALL:TYPE:ATTR=VALUE:...]
        Example: [CALL:SUPPORT:AGENT=Sarah:DURATION=8m]
        """
        parts = ["CALL", call.type]

        if call.agent:
            parts.append(f"AGENT={call.agent}")

        if call.duration:
            minutes = max(1, call.duration // 2)
            parts.append(f"DURATION={minutes}m")

        if call.channel:
            parts.append(f"CHANNEL={call.channel}")

        return f"[{':'.join(parts)}]"

    def _encode_customer(self, customer: CustomerProfile) -> str:
        """
        Encode customer profile based on found information: contact, attributes, etc.

        Format: [CUSTOMER:ATTR=VALUE:...]
        Example: [CUSTOMER:ACCOUNT=847-392-1045:TIER=PREMIUM:ADDRESS=123_Main_St]
        """
        parts = ["CUSTOMER"]

        if customer.account:
            parts.append(f"ACCOUNT={customer.account}")

        if customer.tier:
            parts.append(f"TIER={customer.tier}")

        if customer.tenure:
            parts.append(f"TENURE={customer.tenure}")

        if customer.attributes and "address" in customer.attributes:
            address = customer.attributes["address"]
            address_compressed = self._compress_address(address)
            parts.append(f"ADDRESS={address_compressed}")

        if customer.attributes and "organization" in customer.attributes:
            org = customer.attributes["organization"]
            org_compressed = org.replace(" ", "_")
            parts.append(f"ORG={org_compressed}")

        if customer.attributes and "location" in customer.attributes:
            location = customer.attributes["location"]
            parts.append(f"LOCATION={location}")

        return f"[{':'.join(parts)}]"

    @staticmethod
    def _encode_identifiers(analysis: TranscriptAnalysis) -> Optional[str]:
        """
        Encode all identifiers in one token. Identifiers can be order number, product number etc.

        Format: [ID:TYPE=value:TYPE=value:...]
        Example: [ID:TRACKING=PL-7294008:PRODUCT=HP-300A]

        Supported identifier types:
        - TRACKING: Tracking numbers
        - CLAIM: Claim numbers
        - PRODUCT: Product models
        - ORDER: Order numbers
        - TICKET: Ticket numbers
        - CASE: Case numbers
        """

        identifiers: dict = {
            "tracking_numbers": [],
            "claim_numbers": [],
            "product_models": [],
            "order_numbers": [],
            "ticket_numbers": [],
            "case_numbers": [],
        }

        for turn in analysis.turns:
            if turn.entities:
                for key in identifiers:
                    identifiers[key].extend(turn.entities.get(key, []))

        for key in identifiers:
            identifiers[key] = list(set(identifiers[key]))

        parts = []
        match identifiers:
            case "tracking_numbers":
                parts.append(f"TRACKING={','.join(identifiers['tracking_numbers'])}")
            case "claim_numbers":
                parts.append(f"CLAIM={','.join(identifiers['claim_numbers'])}")
            case "product_models":
                parts.append(f"PRODUCT={','.join(identifiers['product_models'])}")
            case "order_numbers":
                parts.append(f"ORDER={','.join(identifiers['order_numbers'])}")
            case "ticket_numbers":
                parts.append(f"TICKET={','.join(identifiers['ticket_numbers'])}")
            case "case_numbers":
                parts.append(f"CASE={','.join(identifiers['case_numbers'])}")
            case _:
                print("No identifier found")

        if not parts:
            return None

        return f"[ID:{':'.join(parts)}]"

    @staticmethod
    def _encode_contact_info(analysis: TranscriptAnalysis) -> Optional[str]:
        """
        Encode contact information

        Format: [CONTACT:TYPE=value:...]
        Example: [CONTACT:EMAIL=user@example.com:PHONE=555-123-4567]
        """

        emails = []
        phone_numbers = []

        for turn in analysis.turns:
            if turn.entities:
                emails.extend(turn.entities.get("emails", []))
                phone_numbers.extend(turn.entities.get("phone_numbers", []))

        emails = list(set(emails))
        phone_numbers = list(set(phone_numbers))

        parts = []
        if emails:
            parts.append(f"EMAIL={','.join(emails)}")

        if phone_numbers:
            parts.append(f"PHONE={','.join(phone_numbers)}")

        if not parts:
            return None

        return f"[CONTACT:{':'.join(parts)}]"

    @staticmethod
    def _encode_issue(issue: Issue, turns: list[Turn]) -> str:
        """
        Encode issue with full temporal details and money amounts

        Format: [ISSUE:TYPE:ATTR=VALUE:...]
        Example: [ISSUE:INTERNET_OUTAGE:SEVERITY=MEDIUM:FREQ=3x_daily:DURATION=3d:PATTERN=9am+1pm+6pm:DAYS=MON+TUE+WED]
        Example: [ISSUE:BILLING_DISPUTE:SEVERITY=LOW:AMOUNTS=$14.99+$16.99]
        """
        parts = ["ISSUE", issue.type]

        if issue.type in [
            "BILLING_DISPUTE",
            "UNEXPECTED_CHARGE",
            "REFUND_REQUEST",
            "OVERCHARGE",
        ]:
            for turn in turns:
                if len(turn.entities.get("money", [])) > 0:
                    amounts = "+".join(turn.entities.get("money", []))
                    parts.append(f"AMOUNTS={amounts}")

        if issue.severity:
            parts.append(f"SEVERITY={issue.severity}")

        if issue.frequency:
            parts.append(f"FREQ={issue.frequency}")

        if issue.duration:
            parts.append(f"DURATION={issue.duration}")

        if issue.pattern:
            parts.append(f"PATTERN={issue.pattern}")

        if issue.attributes and "days" in issue.attributes:
            days = issue.attributes["days"]
            if days and len(days) > 0:  # Only if not empty
                days_str = "+".join(days)
                parts.append(f"DAYS={days_str}")

        if issue.impact:
            parts.append(f"IMPACT={issue.impact}")

        return f"[{':'.join(parts)}]"

    @staticmethod
    def _encode_action(action: Action) -> str:
        """
        Encode action with financial details

        Format: [ACTION:TYPE:ATTR=VALUE:...]
        Example: [ACTION:TROUBLESHOOT:RESULT=PENDING]
        Example: [ACTION:REFUND:REFERENCE=RFD-908712:TIMELINE=3-5d:RESULT=COMPLETED]
        Example: [ACTION:CREDIT:AMOUNT=$10:METHOD=ACCOUNT_CREDIT:RESULT=APPLIED]
        """
        parts = ["ACTION", action.type]

        if action.step:
            parts.append(f"STEP={action.step}")

        if (
            action.attributes
            and "reference" in action.attributes
            and action.attributes["reference"]
        ):
            parts.append(f"REFERENCE={action.attributes['reference']}")

        if (
            action.attributes
            and "timeline" in action.attributes
            and action.attributes["timeline"]
        ):
            parts.append(f"TIMELINE={action.attributes['timeline']}")

        if action.amount:
            parts.append(f"AMOUNT={action.amount}")

        if action.payment_method:
            parts.append(f"METHOD={action.payment_method}")

        if action.result:
            parts.append(f"RESULT={action.result}")

        return f"[{':'.join(parts)}]"

    @staticmethod
    def _encode_resolution(resolution: Resolution) -> str:
        """
        Encode resolution

        Format: [RESOLUTION:TYPE:ATTR=VALUE:...]
        Example: [RESOLUTION:PENDING:TIMELINE=24h:TICKET=TK12345]
        Example: [RESOLUTION:RESOLVED:TIMELINE=3d]
        """
        parts = ["RESOLUTION", resolution.type]

        if resolution.timeline:
            parts.append(f"TIMELINE={resolution.timeline}")

        if resolution.ticket_id:
            parts.append(f"TICKET={resolution.ticket_id}")

        if resolution.next_steps:
            steps_compressed = resolution.next_steps.replace(" ", "_")
            parts.append(f"NEXT={steps_compressed}")

        return f"[{':'.join(parts)}]"

    @staticmethod
    def _encode_sentiment(sentiment: SentimentTrajectory) -> str:
        """
        Encode sentiment trajectory

        Args:
            sentiment (SentimentTrajectory): The sentiment trajectory to encode.

        Returns:
            str: The encoded sentiment trajectory.

        Example:
            Format: [SENTIMENT:START→END]
            Example: [SENTIMENT:FRUSTRATED→SATISFIED]
            With turning points: [SENTIMENT:FRUSTRATED→NEUTRAL→SATISFIED]
        """
        checked_sentiment = set()
        if not sentiment.turning_points:
            return f"[SENTIMENT:{sentiment.start}→{sentiment.end}]"

        trajectory = [sentiment.start]
        for _, emotion in sentiment.turning_points:
            if emotion != trajectory[-1] and emotion not in checked_sentiment:
                checked_sentiment.add(emotion)
                trajectory.append(emotion)

        if trajectory[-1] != sentiment.end and sentiment.end is not None:
            trajectory.append(sentiment.end)

        trajectory_str = "→".join(trajectory)
        return f"[SENTIMENT:{trajectory_str}]"

    @staticmethod
    def _compress_address(address: str) -> str:
        """
        Compress address

        Args:
            address (str): The address to compress.

        Returns:
            str: The compressed address.

        Examples:
        - "123 Main Street" → "123_Main_St"
        - "456 Oak Avenue" → "456_Oak_Ave"
        - "41 Riverbend Lane" → "41_Riverbend_Ln"
        """
        compressed = address.replace(" ", "_")

        for full, abbrev in NER_ADDRESS_ABBREVIATIONS.items():
            compressed = compressed.replace(full, abbrev)

        return compressed
