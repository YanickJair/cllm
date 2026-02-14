import re
from typing import Optional

from spacy import Language
from clm_core.components.transcript.analyzer import TranscriptAnalyzer
from clm_core.components.transcript.patterns import TranscriptPatterns

from . import (
    Action,
    CallInfo,
    CustomerProfile,
    Issue,
    Resolution,
    SentimentTrajectory,
    TranscriptAnalysis,
    Turn,
    ResolutionState,
    RefundReference,
    ConversationTimeline,
    PromiseCommitment,
)
from clm_core.utils.singleton import SingletonMeta
from clm_core.types import CLMOutput
from ...utils.parser_rules import BaseRules
from ...utils.vocabulary import BaseVocabulary

COMPONENT = "TRANSCRIPT"


class TranscriptEncoder(metaclass=SingletonMeta):
    """
    Encodes transcript analysis into compressed tokens

    Philosophy: Extends CLLMTokenizer format: [CALL:metadata][ISSUE:details][ACTION_CHAIN:action1→action2→...][RESOLUTION:details]
    """

    def __init__(
        self,
        nlp: Language,
        vocab: BaseVocabulary,
        rules: BaseRules,
        patterns: TranscriptPatterns,
        lang: str = "en",
    ):
        self._patterns = patterns
        self._lang = lang
        self._analyzer = TranscriptAnalyzer(
            nlp=nlp,
            vocab=vocab,
            rules=rules,
            patterns=patterns,
        )
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
        [ACTION_CHAIN:type1→type2→type3→...]
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

        if self.analysis.actions:
            action_chain_token = self._encode_action_chain(self.analysis.actions)
            tokens.append(action_chain_token)
            if verbose:
                print(f"Action Chain: {action_chain_token}")

        # Resolution logic: avoid showing both UNKNOWN and a clear state
        resolution = self.analysis.resolution
        resolution_state = self.analysis.resolution_state

        has_clear_state = resolution_state and resolution_state.type not in (
            "UNKNOWN",
            "UNRESOLVED",
        )

        if resolution.type == "UNKNOWN" and has_clear_state:
            res_state_token = self._encode_resolution_state(resolution_state)
            tokens.append(res_state_token)
            if verbose:
                print(f"Resolution State: {res_state_token}")
        elif resolution.type == "UNKNOWN":
            resolution_token = self._encode_resolution(resolution)
            tokens.append(resolution_token)
            if verbose:
                print(f"Resolution: {resolution_token}")
        else:
            resolution_token = self._encode_resolution(resolution)
            tokens.append(resolution_token)
            if verbose:
                print(f"Resolution: {resolution_token}")

            if resolution_state:
                res_state_token = self._encode_resolution_state(resolution_state)
                tokens.append(res_state_token)
                if verbose:
                    print(f"Resolution State: {res_state_token}")

        if self.analysis.refund_reference:
            refund_token = self._encode_refund_reference(self.analysis.refund_reference)
            if refund_token:
                tokens.append(refund_token)
                if verbose:
                    print(f"Refund: {refund_token}")

        if self.analysis.timeline:
            timeline_token = self._encode_timeline(self.analysis.timeline)
            if timeline_token:
                tokens.append(timeline_token)
                if verbose:
                    print(f"Timeline: {timeline_token}")

        if self.analysis.promises:
            promises_token = self._encode_promises(self.analysis.promises)
            if promises_token:
                tokens.append(promises_token)
                if verbose:
                    print(f"Promises: {promises_token}")

        sentiment_token = self._encode_sentiment(self.analysis.sentiment_trajectory)
        tokens.append(sentiment_token)
        if verbose:
            print(f"Sentiment: {sentiment_token}")

        compressed = " ".join(tokens)

        # Extract verbs and noun_chunks from already-processed turn docs (avoid re-processing)
        verbs = []
        noun_chunks = []
        for turn in self.analysis.turns:
            if turn.doc:
                verbs.extend(token.lemma_ for token in turn.doc if token.pos_ == "VERB")
                noun_chunks.extend(chunk.text for chunk in turn.doc.noun_chunks)

        return CLMOutput(
            compressed=compressed,
            original=transcript,
            component=COMPONENT,
            metadata={
                **metadata,
                "analysis": self.analysis.to_dict(),
                "original_length": len(transcript),
                "compressed_length": len(compressed),
                "verbs": verbs,
                "noun_chunks": noun_chunks,
                "language": self._lang,
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

        if issue.cause:
            parts.append(f"CAUSE={issue.cause}")

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
    def _encode_action_chain(actions: list[Action]) -> str:
        """
        Encode actions as a chain joined by →

        Format: [ACTION_CHAIN:TYPE1→TYPE2→TYPE3→...]
        Example: [ACTION_CHAIN:TROUBLESHOOTING_PERFORMED→ACCOUNT_VERIFIED→REFUND_PROCESSED]
        """
        action_types = [action.type for action in actions]
        chain = "→".join(action_types)
        return f"[ACTION_CHAIN:{chain}]"

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

    def _compress_address(self, address: str) -> str:
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

        for full, abbrev in self._patterns.ner_address_abbreviations.items():
            compressed = compressed.replace(full, abbrev)

        return compressed

    # ============================================================
    # Case-dependent feature encoding methods
    # ============================================================

    @staticmethod
    def _encode_resolution_state(state: ResolutionState) -> str:
        """
        Encode enhanced resolution state

        Format: [RES_STATE:TYPE:ATTR=VALUE:...]
        Example: [RES_STATE:FULLY_RESOLVED:CSAT=SATISFIED]
        Example: [RES_STATE:PENDING:FOLLOW_UP=YES:REASON=VERIFICATION_NEEDED]
        """
        parts = ["RES_STATE", state.type]

        if state.completeness and state.completeness != "UNKNOWN":
            parts.append(f"COMPLETENESS={state.completeness}")

        if state.customer_satisfaction:
            parts.append(f"CSAT={state.customer_satisfaction}")

        if state.follow_up_needed:
            parts.append("FOLLOW_UP=YES")
            if state.follow_up_reason:
                parts.append(f"REASON={state.follow_up_reason}")

        return f"[{':'.join(parts)}]"

    @staticmethod
    def _encode_refund_reference(refund: RefundReference) -> Optional[str]:
        """
        Encode refund reference (case-dependent)

        Format: [REFUND:ATTR=VALUE:...]
        Example: [REFUND:REF=RFD-908712:AMT=$14.99:METHOD=CARD_CREDIT:STATUS=INITIATED:TIMELINE=3-5d]
        """
        if not refund:
            return None

        parts = ["REFUND"]

        if refund.reference_number:
            parts.append(f"REF={refund.reference_number}")

        if refund.amount:
            parts.append(f"AMT={refund.amount}")

        if refund.method:
            parts.append(f"METHOD={refund.method}")

        if refund.status:
            parts.append(f"STATUS={refund.status}")

        if refund.timeline:
            parts.append(f"TIMELINE={refund.timeline}")

        if refund.original_transaction_id:
            parts.append(f"ORIG_TXN={refund.original_transaction_id}")

        if len(parts) == 1:  # Only "REFUND" with no attributes
            return None

        return f"[{':'.join(parts)}]"

    @staticmethod
    def _encode_timeline(timeline: ConversationTimeline) -> Optional[str]:
        """
        Encode conversation timeline

        Format: [TIMELINE:EVENT1→EVENT2→EVENT3:METRICS]
        Example: [TIMELINE:ISSUE_RAISED→INVESTIGATION→ACTION_TAKEN→RESOLVED:TTR=5:TTFA=2]
        """
        if not timeline or not timeline.events:
            return None

        # Compress events to just types (limit to 8 events)
        event_chain = "→".join(e.event_type for e in timeline.events[:8])

        parts = ["TIMELINE", event_chain]

        if timeline.time_to_resolution is not None:
            parts.append(f"TTR={timeline.time_to_resolution}")

        if timeline.time_to_first_action is not None:
            parts.append(f"TTFA={timeline.time_to_first_action}")

        return f"[{':'.join(parts)}]"

    @staticmethod
    def _encode_promises(promises: list[PromiseCommitment]) -> Optional[str]:
        """
        Encode agent promises

        Format: [PROMISES:TYPE1(TIMELINE):TYPE2(AMT):...]
        Example: [PROMISES:CALLBACK(24h):REFUND_PROMISE($14.99,3-5d):TECHNICIAN_VISIT(MONDAY)]
        """
        if not promises:
            return None

        promise_parts = []
        for p in promises:
            details = []
            if p.amount:
                details.append(p.amount)
            if p.timeline:
                details.append(p.timeline)

            if details:
                promise_parts.append(f"{p.type}({','.join(details)})")
            else:
                promise_parts.append(p.type)

        return f"[PROMISES:{':'.join(promise_parts)}]"
