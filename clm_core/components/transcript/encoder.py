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
CLM_SCHEMA_VERSION = "2.0"


class TranscriptEncoder(metaclass=SingletonMeta):
    """
    Encodes transcript analysis into CLM Transcript Schema v2 compressed tokens.

    v2 Format:
    [INTERACTION:SUPPORT:CHANNEL=VOICE]
    [DURATION=6m]
    [LANG=EN]
    [DOMAIN:BILLING]
    [SERVICE:SUBSCRIPTION]
    [CUSTOMER_INTENT:REPORT_DUPLICATE_CHARGE]
    [CONTEXT:EMAIL_PROVIDED]
    [AGENT_ACTIONS:ACCOUNT_VERIFIED→DIAGNOSTIC_PERFORMED→REFUND_INITIATED]
    [SYSTEM_ACTIONS:PAYMENT_RETRY_DETECTED]
    [RESOLUTION:REFUND_ISSUED]
    [STATE:RESOLVED]
    [COMMITMENT:REFUND_3-5_DAYS]
    [ARTIFACT:REFUND_REF=RFD-908712]
    [SENTIMENT:NEUTRAL→GRATEFUL]
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
        Encode transcript analysis to CLM Transcript Schema v2 format.
        """
        self.analysis = self._analyzer.analyze(transcript, metadata)

        tokens = []

        # 1. Interaction metadata
        interaction_token = self._encode_interaction(self.analysis.call_info)
        tokens.append(interaction_token)
        if verbose:
            print(f"Interaction: {interaction_token}")

        duration_token = self._encode_duration(self.analysis.call_info)
        if duration_token:
            tokens.append(duration_token)
            if verbose:
                print(f"Duration: {duration_token}")

        lang_token = self._encode_lang(self._lang)
        tokens.append(lang_token)
        if verbose:
            print(f"Lang: {lang_token}")

        # 2. Domain context
        if self.analysis.domain:
            domain_token = f"[DOMAIN:{self.analysis.domain}]"
            tokens.append(domain_token)
            if verbose:
                print(f"Domain: {domain_token}")

        if self.analysis.service:
            service_token = f"[SERVICE:{self.analysis.service}]"
            tokens.append(service_token)
            if verbose:
                print(f"Service: {service_token}")

        # 3. Customer intent (mandatory)
        if self.analysis.customer_intent:
            intent_token = f"[CUSTOMER_INTENT:{self.analysis.customer_intent}]"
            tokens.append(intent_token)
            if verbose:
                print(f"Customer Intent: {intent_token}")

        if self.analysis.secondary_intent:
            secondary_token = (
                f"[CUSTOMER_INTENT:{self.analysis.secondary_intent}]"
            )
            tokens.append(secondary_token)
            if verbose:
                print(f"Secondary Intent: {secondary_token}")

        # 4. Context provided by customer
        for ctx in self.analysis.context_provided:
            ctx_token = f"[CONTEXT:{ctx}]"
            tokens.append(ctx_token)
            if verbose:
                print(f"Context: {ctx_token}")

        # 5. Agent actions
        if self.analysis.actions:
            agent_actions_token = self._encode_agent_actions(self.analysis.actions)
            tokens.append(agent_actions_token)
            if verbose:
                print(f"Agent Actions: {agent_actions_token}")

        # 6. System actions (optional)
        if self.analysis.system_actions:
            sys_token = self._encode_system_actions(self.analysis.system_actions)
            tokens.append(sys_token)
            if verbose:
                print(f"System Actions: {sys_token}")

        # 7. Resolution
        resolution_token = self._encode_resolution(self.analysis.resolution)
        if resolution_token:
            tokens.append(resolution_token)
            if verbose:
                print(f"Resolution: {resolution_token}")

        # 8. State (mutually exclusive)
        state_token = self._encode_state(
            self.analysis.resolution, self.analysis.resolution_state
        )
        tokens.append(state_token)
        if verbose:
            print(f"State: {state_token}")

        # 9. Commitments
        if self.analysis.promises:
            for commitment_token in self._encode_commitments(self.analysis.promises):
                tokens.append(commitment_token)
                if verbose:
                    print(f"Commitment: {commitment_token}")

        # 10. Artifacts
        artifact_tokens = self._encode_artifacts(self.analysis)
        for artifact_token in artifact_tokens:
            tokens.append(artifact_token)
            if verbose:
                print(f"Artifact: {artifact_token}")

        # 11. Sentiment
        sentiment_token = self._encode_sentiment(self.analysis.sentiment_trajectory)
        tokens.append(sentiment_token)
        if verbose:
            print(f"Sentiment: {sentiment_token}")

        compressed = " ".join(tokens)

        # Extract verbs and noun_chunks from already-processed turn docs
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
                "schema_version": CLM_SCHEMA_VERSION,
                "has_numbers": bool(re.search(r"\d", transcript)),
                "has_urls": bool(re.search(r"https?://", transcript)),
            },
        )

    # ============================================================
    # v2 encoding methods
    # ============================================================

    @staticmethod
    def _encode_interaction(call: CallInfo) -> str:
        """
        Encode interaction metadata.

        Format: [INTERACTION:SUPPORT:CHANNEL=VOICE]
        """
        channel = call.channel.upper() if call.channel else "VOICE"
        return f"[INTERACTION:{call.type}:CHANNEL={channel}]"

    @staticmethod
    def _encode_duration(call: CallInfo) -> Optional[str]:
        """
        Encode duration.
        Convert turns to approximate minutes (assume 2 turns/minute).

        Format: [DURATION=6m]
        """
        if call.duration:
            minutes = max(1, call.duration // 2)
            return f"[DURATION={minutes}m]"
        return None

    @staticmethod
    def _encode_lang(lang: str) -> str:
        """
        Encode language metadata.

        Format: [LANG=EN]
        """
        return f"[LANG={lang.upper()}]"

    @staticmethod
    def _encode_agent_actions(actions: list[Action]) -> str:
        """
        Encode agent actions as a chain joined by →

        Format: [AGENT_ACTIONS:TYPE1→TYPE2→TYPE3→...]
        Example: [AGENT_ACTIONS:ACCOUNT_VERIFIED→DIAGNOSTIC_PERFORMED→REFUND_INITIATED]
        """
        action_types = [action.type for action in actions]
        chain = "→".join(action_types)
        return f"[AGENT_ACTIONS:{chain}]"

    @staticmethod
    def _encode_system_actions(system_actions: list[str]) -> str:
        """
        Encode system actions.

        Format: [SYSTEM_ACTIONS:ACTION1→ACTION2]
        """
        chain = "→".join(system_actions)
        return f"[SYSTEM_ACTIONS:{chain}]"

    # Maps resolution types and actions to v2 resolution descriptions
    _RESOLUTION_MAP = {
        "RESOLVED": "ISSUE_RESOLVED",
        "PENDING": "PENDING",
        "ESCALATED": "ESCALATED",
        "UNKNOWN": None,
        "UNRESOLVED": None,
        "CANCELLED": "CANCELLED",
    }

    @classmethod
    def _encode_resolution(cls, resolution: Resolution) -> Optional[str]:
        """
        Encode resolution outcome.

        Format: [RESOLUTION:REFUND_ISSUED]
        """
        res_type = cls._RESOLUTION_MAP.get(resolution.type)
        if res_type:
            return f"[RESOLUTION:{res_type}]"

        # Try to derive from next_steps
        if resolution.next_steps:
            steps = resolution.next_steps.upper().replace(" ", "_")
            return f"[RESOLUTION:{steps}]"

        return None

    # Maps resolution state types to v2 STATE values
    _STATE_MAP = {
        "FULLY_RESOLVED": "RESOLVED",
        "PARTIALLY_RESOLVED": "RESOLVED",
        "RESOLVED": "RESOLVED",
        "RESOLVED_PENDING_VERIFICATION": "PENDING_CUSTOMER",
        "PENDING": "PENDING_SETTLEMENT",
        "ESCALATED": "ESCALATED",
        "UNRESOLVED": "UNRESOLVED",
        "UNKNOWN": "UNRESOLVED",
    }

    @classmethod
    def _encode_state(
        cls, resolution: Resolution, resolution_state: Optional[ResolutionState]
    ) -> str:
        """
        Encode authoritative interaction state (mutually exclusive).

        Format: [STATE:RESOLVED]
        """
        # Prefer resolution_state if available (more granular)
        if resolution_state and resolution_state.type != "UNKNOWN":
            state = cls._STATE_MAP.get(resolution_state.type, "UNRESOLVED")
            return f"[STATE:{state}]"

        # Fall back to resolution type
        if resolution.type == "RESOLVED":
            return "[STATE:RESOLVED]"
        elif resolution.type == "PENDING":
            return "[STATE:PENDING_SETTLEMENT]"
        elif resolution.type == "ESCALATED":
            return "[STATE:ESCALATED]"
        elif resolution.type == "CANCELLED":
            return "[STATE:RESOLVED]"

        return "[STATE:UNRESOLVED]"

    @staticmethod
    def _encode_commitments(promises: list[PromiseCommitment]) -> list[str]:
        """
        Encode commitments from promises.

        Format: [COMMITMENT:REFUND_3-5_DAYS]
        """
        tokens = []
        for p in promises:
            parts = [p.type]
            if p.timeline:
                parts.append(p.timeline)
            if p.amount:
                parts.append(p.amount)
            commitment_str = "_".join(parts)
            tokens.append(f"[COMMITMENT:{commitment_str}]")
        return tokens

    @staticmethod
    def _encode_artifacts(analysis: TranscriptAnalysis) -> list[str]:
        """
        Encode structured identifiers as artifacts.

        Format: [ARTIFACT:REFUND_REF=RFD-908712]
        """
        artifacts = []

        # Refund reference
        if analysis.refund_reference:
            ref = analysis.refund_reference
            if ref.reference_number:
                artifacts.append(f"[ARTIFACT:REFUND_REF={ref.reference_number}]")
            if ref.amount:
                artifacts.append(f"[ARTIFACT:REFUND_AMT={ref.amount}]")

        # Identifiers from turns
        identifiers = {
            "tracking_numbers": "TRACKING_ID",
            "claim_numbers": "CLAIM_ID",
            "product_models": "PRODUCT_ID",
            "order_numbers": "ORDER_ID",
            "ticket_numbers": "TICKET_ID",
            "case_numbers": "CASE_ID",
        }

        collected: dict[str, list[str]] = {key: [] for key in identifiers}

        for turn in analysis.turns:
            if turn.entities:
                for key in identifiers:
                    collected[key].extend(turn.entities.get(key, []))

        for key, artifact_type in identifiers.items():
            unique_values = list(set(collected[key]))
            for val in unique_values:
                artifacts.append(f"[ARTIFACT:{artifact_type}={val}]")

        return artifacts

    @staticmethod
    def _encode_sentiment(sentiment: SentimentTrajectory) -> str:
        """
        Encode sentiment trajectory.

        Format: [SENTIMENT:NEUTRAL→GRATEFUL]
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
