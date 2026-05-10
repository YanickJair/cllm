import re
from typing import Annotated, Literal, Optional
from annotated_doc import Doc

from spacy import Language
from thread_encoder.components.thread_encoder.analyzer import TranscriptAnalyzer
from thread_encoder.components.thread_encoder.free_form.splitter import (
    detect_format,
    split_free_form,
)
from thread_encoder.components.thread_encoder.patterns import TranscriptPatterns
from thread_encoder.types import ThreadConfig

from . import (
    Action,
    CallInfo,
    ThreadOutput,
    Resolution,
    SentimentTrajectory,
    TranscriptAnalysis,
    ResolutionState,
    PromiseCommitment,
    Turn,
)
from thread_encoder.utils.singleton import SingletonMeta
from ...utils.parser_rules import BaseRules
from ...utils.vocabulary import BaseVocabulary

COMPONENT = "THREAD_ENCODER"
CLM_SCHEMA_VERSION = "2.0"

# Generic diagnostic actions that do not change system state and add no signal.
# These are excluded from the AGENT_ACTIONS token to reduce noise and token overhead.
_INFORMATIONAL_ACTIONS = frozenset({
    "TROUBLESHOOT",
    "DIAGNOSTIC_PERFORMED",
    "TROUBLESHOOTING_PERFORMED",
})


class ThreadEncoder(metaclass=SingletonMeta):
    """
    Encodes thread_encoder analysis into CLM Thread Encoder Schema v2 compressed tokens.

    v2 Format:
    [INTERACTION:SUPPORT:CHANNEL=VOICE]
    [DURATION=6m]
    [LANG=EN]
    [DOMAIN:BILLING]
    [SERVICE:SUBSCRIPTION]
    [CUSTOMER_INTENT:REPORT_DUPLICATE_CHARGE]
    [CUSTOMER_INTENTS:PRIMARY=REQUEST_SHIPMENT_STATUS;SECONDARY=DISPUTE_SERVICE_FEE]
    [INTERACTION_TRIGGER:FIELD_LOCKED]
    [CONTEXT:EMAIL_PROVIDED]
    [AGENT_ACTIONS:ACCOUNT_VERIFIED→DIAGNOSTIC_PERFORMED→REFUND_INITIATED]
    [SYSTEM_ACTIONS:PAYMENT_RETRY_DETECTED]
    [RESOLUTION:REFUND_ISSUED]
    [STATE:RESOLVED|ESCALATED|PENDING_SHIPMENT|PENDING_ENGINEERING|PENDING_CUSTOMER]
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
        config: ThreadConfig,
        lang: str = "en",
    ):
        self._patterns = patterns
        self._lang = lang
        self._analyzer = TranscriptAnalyzer(
            nlp=nlp,
            vocab=vocab,
            rules=rules,
            patterns=patterns,
            redaction_pattern=config.redaction_pattern,
        )
        self._config = config
        self.analysis: TranscriptAnalysis | None = None

    def encode(
        self,
        *,
        thread: Annotated[
            str,
            Doc("""
            Original Thread input to compress. It can be a Transcript or a Free-Form text like
            Email, Slack Threads, etc.
            """),
        ],
        metadata: Annotated[
            dict,
            Doc("""
            Thread's metadata. It can include channel, Id, etc.
            """),
        ],
        verbose: Annotated[
            bool,
            Doc("""
            A flag that enables verbose output.

            Defaults to False.
            """),
        ] = False,
        thread_format: Annotated[
            Literal["auto", "turns", "free_form"],
            Doc("""
            Controls how the transcript is parsed before analysis.

            - `"auto"` — heuristic detection: if ≥50% of non-empty lines carry a
              recognized speaker prefix the input is treated as `"turns"`, otherwise
              as `"free_form"`.
            - `"turns"` — expects the canonical `"Speaker: text"` line format.
            - `"free_form"` — unstructured text (emails, SMS, raw notes). The encoder
              splits on blank lines (paragraph mode) or falls back to line-by-line,
              then runs the full analysis pipeline with all turns attributed to the
              customer role.

            The resolved value is stored in `result.metadata["transcript_format"]`.
            """),
        ] = "auto",
    ) -> ThreadOutput:
        """
        Encode thread_encoder analysis to CLM Thread Schema v2 format.

        The encoder works as a pipeline with multiple layers for each Token:
        - The analyzer function is the first in the pipeline.
        - It tries to normalize the thread interaction (Define Channel, etc.)
        - Tries to estimate the duration of the thread interaction
        - The encode_lang function tries to predict the language of the thread interaction
        """
        resolved_format = thread_format
        if thread_format == "auto":
            resolved_format = self._detect_format(thread)
            print(f"Resolved format: {resolved_format}")

        pre_built_turns = None
        if resolved_format == "free_form":
            pre_built_turns = self._split_free_form(thread)

        self.analysis = self._analyzer.analyze(thread, metadata, turns=pre_built_turns)

        tokens = []

        interaction_token = self._encode_interaction(self.analysis.call_info)
        tokens.append(interaction_token)
        if verbose:
            print(f"Interaction: {interaction_token}")

        if self._config.estimate_thread_duration:
            duration_token = self._encode_duration(self.analysis.call_info)
            if duration_token:
                tokens.append(duration_token)
                if verbose:
                    print(f"Duration: {duration_token}")

        if self._config.detect_lang:
            lang_token = self._encode_lang(self._lang)
            tokens.append(lang_token)
            if verbose:
                print(f"Lang: {lang_token}")

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

        if self.analysis.customer_intent and self.analysis.secondary_intent:
            intent_token = (
                f"[CUSTOMER_INTENTS:PRIMARY={self.analysis.customer_intent}"
                f";SECONDARY={self.analysis.secondary_intent}]"
            )
            tokens.append(intent_token)
            if verbose:
                print(f"Customer Intents: {intent_token}")
        elif self.analysis.customer_intent:
            intent_token = f"[CUSTOMER_INTENT:{self.analysis.customer_intent}]"
            tokens.append(intent_token)
            if verbose:
                print(f"Customer Intent: {intent_token}")

        if self.analysis.trigger_cause:
            trigger_token = f"[INTERACTION_TRIGGER:{self.analysis.trigger_cause}]"
            tokens.append(trigger_token)
            if verbose:
                print(f"Trigger: {trigger_token}")

        for ctx in self.analysis.context_provided:
            if self._config.include_ctx_values:
                value = self.analysis.context_values.get(ctx)
                ctx_token = f"[CONTEXT:{ctx}:{value}]" if value else f"[CONTEXT:{ctx}]"
            else:
                ctx_token = f"[CONTEXT:{ctx}]"
            tokens.append(ctx_token)
            if verbose:
                print(f"Context: {ctx_token}")

        for redacted in self.analysis.redacted_fields:
            r_token = f"[CONTEXT:{redacted}]"
            tokens.append(r_token)
            if verbose:
                print(f"Redacted: {r_token}")

        state_changing_actions = [
            a for a in self.analysis.actions if a.type not in _INFORMATIONAL_ACTIONS
        ]
        if state_changing_actions:
            agent_actions_token = self._encode_agent_actions(state_changing_actions)
            tokens.append(agent_actions_token)
            if verbose:
                print(f"Agent Actions: {agent_actions_token}")

        if self.analysis.system_actions:
            sys_token = self._encode_system_actions(self.analysis.system_actions)
            tokens.append(sys_token)
            if verbose:
                print(f"System Actions: {sys_token}")

        resolution_token = self._encode_resolution(
            self.analysis.resolution, self.analysis.actions
        )
        if resolution_token:
            tokens.append(resolution_token)
            if verbose:
                print(f"Resolution: {resolution_token}")

        state_token = self._encode_state(
            self.analysis.resolution,
            self.analysis.resolution_state,
            actions=self.analysis.actions,
            domain=self.analysis.domain,
            issues=self.analysis.issues,
        )
        tokens.append(state_token)
        if verbose:
            print(f"State: {state_token}")

        if self.analysis.promises:
            for commitment_token in self._encode_commitments(self.analysis.promises):
                tokens.append(commitment_token)
                if verbose:
                    print(f"Commitment: {commitment_token}")

        artifact_tokens = self._encode_artifacts(self.analysis)
        for artifact_token in artifact_tokens:
            tokens.append(artifact_token)
            if verbose:
                print(f"Artifact: {artifact_token}")

        sentiment_token = self._encode_sentiment(self.analysis.sentiment_trajectory)
        tokens.append(sentiment_token)
        if verbose:
            print(f"Sentiment: {sentiment_token}")

        compressed = " ".join(tokens)

        verbs = []
        noun_chunks = []
        for turn in self.analysis.turns:
            if turn.doc:
                verbs.extend(token.lemma_ for token in turn.doc if token.pos_ == "VERB")
                noun_chunks.extend(chunk.text for chunk in turn.doc.noun_chunks)

        return ThreadOutput(
            compressed=compressed,
            original=thread,
            component=COMPONENT,
            metadata={
                **metadata,
                "analysis": self.analysis.to_dict(),
                "compressed_tokens": compressed,
                "original_length": len(thread),
                "compressed_length": len(compressed),
                "verbs": verbs,
                "noun_chunks": noun_chunks,
                "language": self._lang,
                "schema_version": CLM_SCHEMA_VERSION,
                "has_numbers": bool(re.search(r"\d", thread)),
                "has_urls": bool(re.search(r"https?://", thread)),
                "transcript_format": resolved_format,
            },
        )

    def _detect_format(self, transcript: str) -> str:
        """Return 'turns' if >=50% of non-empty lines have a recognized speaker prefix."""
        return detect_format(transcript, self._analyzer.patterns)

    def _split_free_form(self, text: str) -> list[Turn]:
        """Split unstructured text into turns with speaker='unknown'."""
        return split_free_form(text)

    @classmethod
    def to_recoder(cls):
        pass

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

    _RESOLUTION_MAP = {
        "RESOLVED": "ISSUE_RESOLVED",
        "PENDING": "PENDING",
        "ESCALATED": "ESCALATED",
        "UNKNOWN": None,
        "UNRESOLVED": None,
        "CANCELLED": "CANCELLED",
    }

    # Actions that represent a specific resolution outcome
    _ACTION_TO_RESOLUTION = {
        "REFUND_INITIATED": "REFUND_INITIATED",
        "PROFILE_UPDATED": "PROFILE_UPDATED",
        "ESCALATION_CREATED": "ESCALATED",
        "PLAN_UPGRADED": "PLAN_UPGRADED",
        "ADDON_ACTIVATED": "ADDON_ACTIVATED",
        "DISCOUNT_APPLIED": "DISCOUNT_APPLIED",
        "SERVICE_RESTORED": "SERVICE_RESTORED",
        "SUBSCRIPTION_PAUSED": "SUBSCRIPTION_PAUSED",
        "TRIAL_ACTIVATED": "TRIAL_ACTIVATED",
        "FEE_WAIVED": "FEE_REVERSED",
        "CREDIT_APPLIED": "CREDIT_APPLIED",
        "PASSWORD_RESET": "LOGIN_RESTORED",
        "REPLACEMENT_ORDERED": "REPLACEMENT_CONFIRMED",
        "DUPLICATE_PAYMENT_CONFIRMED": "REFUND_INITIATED",
        "ACCOUNT_VERIFIED": None,
        "DIAGNOSTIC_PERFORMED": None,
        "ACCOUNT_LOOKUP": None,
        "CASE_REVIEWED": None,
        "LOGS_REVIEWED": None,
        "FEE_REVIEWED": None,
        "ORDER_STATUS_CHECKED": None,
    }

    @classmethod
    def _encode_resolution(
        cls, resolution: Resolution, actions: Optional[list] = None
    ) -> Optional[str]:
        """
        Encode resolution outcome.

        Derives resolution from agent actions when possible (the last significant action
        IS the resolution). Falls back to resolution type mapping.

        State consistency guarantees:
        - ESCALATED + RESOLVED cannot coexist: when ESCALATION_CREATED is present, the
          resolution reflects the escalation outcome, not earlier agent actions.
        - Exception: if SERVICE_RESTORED follows escalation, the service was fixed.

        Format: [RESOLUTION:REFUND_INITIATED]
        """
        actions = actions or []
        action_types_set = {a.type for a in actions}
        has_escalation = "ESCALATION_CREATED" in action_types_set

        # Cancellation deflection: agent made a retention offer and customer did not cancel
        if (
            "RETENTION_OFFER" in action_types_set
            and "SERVICE_CANCELLED" not in action_types_set
        ):
            return "[RESOLUTION:CANCELLATION_DEFLECTED]"

        # When escalated but service was subsequently restored, the escalation resolved
        if has_escalation and "SERVICE_RESTORED" in action_types_set:
            return "[RESOLUTION:SERVICE_RESTORED]"

        # Escalation takes precedence — do not emit a resolved outcome while escalated.
        # RESOLVED + ESCALATED simultaneously is a contradiction.
        if has_escalation:
            return "[RESOLUTION:ESCALATED]"

        # Try to derive resolution from the last significant agent action
        for action in reversed(actions):
            action_res = cls._ACTION_TO_RESOLUTION.get(action.type)
            if action_res is not None:
                return f"[RESOLUTION:{action_res}]"

        res_type = cls._RESOLUTION_MAP.get(resolution.type)
        if res_type:
            return f"[RESOLUTION:{res_type}]"

        # Try to derive from next_steps
        if resolution.next_steps:
            steps = resolution.next_steps.upper().replace(" ", "_")
            return f"[RESOLUTION:{steps}]"

        return None

    # Canonical state set: RESOLVED, ESCALATED, PENDING_SHIPMENT,
    # PENDING_ENGINEERING, PENDING_CUSTOMER (+ UNRESOLVED as fallback)
    _STATE_MAP = {
        "FULLY_RESOLVED": "RESOLVED",
        "PARTIALLY_RESOLVED": "RESOLVED",
        "RESOLVED": "RESOLVED",
        "RESOLVED_PENDING_VERIFICATION": "PENDING_CUSTOMER",
        "PENDING": "PENDING_CUSTOMER",
        "ESCALATED": "ESCALATED",
        "UNRESOLVED": "UNRESOLVED",
        "UNKNOWN": "UNRESOLVED",
    }

    @classmethod
    def _encode_state(
        cls,
        resolution: Resolution,
        resolution_state: Optional[ResolutionState],
        actions: Optional[list] = None,
        domain: Optional[str] = None,
        issues: Optional[list] = None,
    ) -> str:
        """
        Encode authoritative interaction state (mutually exclusive).

        Canonical finite state set:
        - RESOLVED
        - ESCALATED
        - PENDING_SHIPMENT  (physical delivery pending)
        - PENDING_ENGINEERING  (technical/engineering fix pending)
        - PENDING_CUSTOMER  (waiting on customer action, refund processing, etc.)
        - UNRESOLVED  (fallback when no clear resolution path)

        Format: [STATE:RESOLVED]
        """
        actions = actions or []
        action_types = {a.type for a in actions}

        # Determine base state
        base_state = None
        if resolution_state and resolution_state.type != "UNKNOWN":
            base_state = cls._STATE_MAP.get(resolution_state.type, "UNRESOLVED")
        elif resolution.type == "RESOLVED":
            base_state = "RESOLVED"
        elif resolution.type == "PENDING":
            base_state = "PENDING_CUSTOMER"
        elif resolution.type == "ESCALATED":
            base_state = "ESCALATED"
        elif resolution.type == "CANCELLED":
            base_state = "RESOLVED"
        else:
            base_state = "UNRESOLVED"

        # Hard state machine rules
        has_physical_shipment = any(
            a in action_types
            for a in ("REPLACEMENT_ORDERED", "PRIORITY_DISPATCH_FLAGGED")
        )
        has_refund = any(
            a in action_types
            for a in (
                "REFUND_INITIATED",
                "CREDIT_APPLIED",
                "DUPLICATE_PAYMENT_CONFIRMED",
            )
        )
        has_escalation = "ESCALATION_CREATED" in action_types
        has_paused = (
            "SUBSCRIPTION_PAUSED" in action_types
            and "SERVICE_CANCELLED" not in action_types
        )

        # Paused subscription — account is in a frozen state, not pending customer action
        if has_paused:
            return "[STATE:PAUSED]"

        # Trial activation — account is in a trial state, not RESOLVED
        if "TRIAL_ACTIVATED" in action_types and not has_escalation:
            return "[STATE:TRIAL_ACTIVE]"

        # Plan/addon upgrade — account is in UPGRADED state, not RESOLVED
        if (
            "PLAN_UPGRADED" in action_types or "ADDON_ACTIVATED" in action_types
        ) and not has_escalation:
            return "[STATE:UPGRADED]"

        # Physical shipment pending → PENDING_SHIPMENT (not RESOLVED)
        if has_physical_shipment and base_state == "RESOLVED":
            base_state = "PENDING_SHIPMENT"

        # Refund processing → PENDING_CUSTOMER (not RESOLVED)
        if has_refund and base_state == "RESOLVED":
            base_state = "PENDING_CUSTOMER"

        # Actions that definitively resolve an issue on the agent's side —
        # the customer has nothing left to do, so PENDING_CUSTOMER is wrong.
        _DEFINITIVE_RESOLUTION_ACTIONS = {
            "PASSWORD_RESET",
            "FEE_WAIVED",
            "SERVICE_RESTORED",
        }

        # Escalation always takes precedence over derived PENDING_CUSTOMER /
        # UNRESOLVED states — the escalation team is working on it.
        if base_state == "ESCALATED" or has_escalation:
            if domain == "TECHNICAL" or any(
                a in action_types for a in ("LOGS_REVIEWED",)
            ):
                return "[STATE:PENDING_ENGINEERING]"
            # Escalation is handling the refund — customer is not pending any
            # action; the billing team is.  Use ESCALATED, not PENDING_CUSTOMER.
            return "[STATE:ESCALATED]"

        # Contextual sub-states for PENDING_CUSTOMER (only reached when no
        # active escalation).
        if base_state == "PENDING_CUSTOMER":
            if has_physical_shipment:
                return "[STATE:PENDING_SHIPMENT]"
            # If the issue was definitively resolved by a specific action
            # (e.g. password reset, fee waived) the state is RESOLVED, not
            # PENDING_CUSTOMER.  The follow-up email promise does NOT make the
            # outcome pending from the customer's perspective.
            if action_types & _DEFINITIVE_RESOLUTION_ACTIONS:
                return "[STATE:RESOLVED]"
            # Outage or technical issue with dispatched technicians / pending fix
            # — the engineering team is pending, not the customer.
            if domain == "TECHNICAL":
                return "[STATE:PENDING_ENGINEERING]"
            # Refund processing waits on the bank — PENDING_REFUND is more
            # precise than PENDING_CUSTOMER and satisfies state-machine semantics:
            # REFUND_INITIATED ≠ RESOLVED.
            if has_refund:
                return "[STATE:PENDING_REFUND]"
            return "[STATE:PENDING_CUSTOMER]"

        # Outage/restoration context
        if domain == "TECHNICAL" and base_state == "UNRESOLVED":
            if any(a in action_types for a in ("SERVICE_RESTORED",)):
                return "[STATE:RESOLVED]"
            return "[STATE:PENDING_ENGINEERING]"

        # Delivery/fulfillment context
        if domain == "FULFILLMENT" and base_state == "UNRESOLVED":
            return "[STATE:PENDING_SHIPMENT]"

        return f"[STATE:{base_state}]"

    @staticmethod
    def _encode_commitments(promises: list[PromiseCommitment]) -> list[str]:
        """
        Encode commitments from promises.

        Gold-style format examples:
        - [COMMITMENT:REFUND_3-5_BUSINESS_DAYS]
        - [COMMITMENT:CONFIRMATION_EMAIL_TODAY]
        - [COMMITMENT:FOLLOWUP_TOMORROW]
        - [COMMITMENT:TRACKING_WITHIN_HOURS]
        """
        # Map promise types to shorter commitment labels
        _TYPE_MAP = {
            "REFUND_PROMISE": "REFUND",
            "CREDIT_PROMISE": "CREDIT",
            "DELIVERY_PROMISE": "DELIVERY",
            "CALLBACK": "CALLBACK",
            "FOLLOW_UP_EMAIL": "CONFIRMATION_EMAIL",
            "CONFIRMATION_EMAIL": "CONFIRMATION_EMAIL",
            "FOLLOWUP": "FOLLOWUP",
            "MONITORING": "MONITORING",
            "TECHNICIAN_VISIT": "TECHNICIAN_VISIT",
            "RESOLUTION_PROMISE": "RESOLUTION",
            "BILLING_EXTENSION": "BILLING_EXTENSION",
            "PAUSE_EXPIRY_REMINDER": "PAUSE_EXPIRY_REMINDER",
        }

        # Commitment types where timeline is omitted (the timing is inherently future/contextual)
        # MONITORING is operational and open-ended; PAUSE_EXPIRY_REMINDER has no fixed date.
        _NO_TIMELINE_TYPES = {"PAUSE_EXPIRY_REMINDER", "MONITORING"}

        # Map timeline shorthand to gold-style
        _TIMELINE_MAP = {
            "3-5d": "3-5_BUSINESS_DAYS",
            "1-3d": "1-3_BUSINESS_DAYS",
            "24h": "WITHIN_24_HOURS",
            "48h": "WITHIN_48_HOURS",
            "TODAY": "TODAY",
            "TOMORROW": "TOMORROW",
        }

        tokens = []
        seen: set[str] = set()
        for p in promises:
            label = _TYPE_MAP.get(p.type, p.type)
            parts = [label]
            if p.timeline and p.type not in _NO_TIMELINE_TYPES:
                timeline_norm = p.timeline.lower()
                # Try original case first (for "TODAY", "TOMORROW"), then lowercase
                timeline_str = _TIMELINE_MAP.get(
                    p.timeline, _TIMELINE_MAP.get(timeline_norm, timeline_norm)
                )
                # Expand compact shorthands: "5d" → "5_DAYS", "3h" → "3_HOURS"
                if re.match(r"^\d+d$", timeline_str):
                    timeline_str = f"{timeline_str[:-1]}_DAYS"
                elif re.match(r"^\d+h$", timeline_str):
                    timeline_str = f"{timeline_str[:-1]}_HOURS"
                parts.append(timeline_str)
            if p.amount:
                parts.append(p.amount)
            commitment_str = "_".join(parts)
            if commitment_str not in seen:
                seen.add(commitment_str)
                tokens.append(f"[COMMITMENT:{commitment_str}]")
        return tokens

    # Pattern that looks like a reference/ticket/escalation ID (e.g. RFD-908712, ESC-45390)
    _REF_ID_PATTERN = re.compile(r"^[A-Z]{2,5}-\d{3,}$")

    @classmethod
    def _encode_artifacts(cls, analysis: TranscriptAnalysis) -> list[str]:
        """
        Encode structured identifiers as artifacts.

        Format: [ARTIFACT:REFUND_REF=RFD-908712]
        Format: [ARTIFACT:AMT=$2.99/EXTRA_CHARGE]
        Format: [ARTIFACT:BILLING_EXTENSION=5_DAYS]
        """
        artifacts = []

        # Monetary amounts with reason
        for amt in analysis.amounts:
            if amt.reason:
                artifacts.append(f"[ARTIFACT:AMT={amt.amount}/{amt.reason}]")

        # Billing extension duration artifact
        for promise in analysis.promises:
            if promise.type == "BILLING_EXTENSION" and promise.timeline:
                tl = promise.timeline
                if re.match(r"^\d+d$", tl):
                    artifact_val = f"{tl[:-1]}_DAYS"
                elif re.match(r"^\d+h$", tl):
                    artifact_val = f"{tl[:-1]}_HOURS"
                else:
                    artifact_val = tl.upper()
                artifacts.append(f"[ARTIFACT:BILLING_EXTENSION={artifact_val}]")

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
            "escalation_ids": "ESCALATION_ID",
        }

        collected: dict[str, list[str]] = {key: [] for key in identifiers}

        for turn in analysis.turns:
            if turn.entities:
                for key in identifiers:
                    collected[key].extend(turn.entities.get(key, []))

        # Already-encoded reference numbers (avoid duplication across artifact types)
        encoded_refs: set[str] = set()
        if analysis.refund_reference and analysis.refund_reference.reference_number:
            encoded_refs.add(analysis.refund_reference.reference_number)

        for key, artifact_type in identifiers.items():
            unique_values = list(set(collected[key]))
            for val in unique_values:
                # Skip values that look like reference/ticket IDs when encoding
                # as PRODUCT_ID — entity extractors sometimes mis-classify them.
                if artifact_type == "PRODUCT_ID" and cls._REF_ID_PATTERN.match(val):
                    continue
                # Skip if this value was already encoded as REFUND_REF
                if val in encoded_refs:
                    continue
                artifacts.append(f"[ARTIFACT:{artifact_type}={val}]")

        return artifacts

    _VALID_SENTIMENTS = frozenset(
        {
            "NEUTRAL",
            "SATISFIED",
            "GRATEFUL",
            "FRUSTRATED",
            "ANGRY",
            "DISAPPOINTED",
            "CONFUSED",
            "RELIEVED",
            "IMPATIENT",
            "HOPEFUL",
            "CALM",
            "WORRIED",
        }
    )

    @classmethod
    def _normalize_sentiment(cls, s: str) -> str:
        """Normalize sentiment to a valid canonical label.

        Handles malformed values like 'GRATEFUL_POSITIVE' → 'GRATEFUL'.
        """
        if not s:
            return "NEUTRAL"
        upper = s.upper()
        if upper in cls._VALID_SENTIMENTS:
            return upper
        for valid in cls._VALID_SENTIMENTS:
            if upper.startswith(valid):
                return valid
        return upper

    @classmethod
    def _encode_sentiment(cls, sentiment: SentimentTrajectory) -> str:
        """
        Encode sentiment trajectory.

        Format: [SENTIMENT:NEUTRAL→GRATEFUL]
        Prevents regressions: once a sentiment appears in the trajectory it
        is not appended again (e.g. NEUTRAL→SATISFIED→GRATEFUL→SATISFIED
        becomes NEUTRAL→SATISFIED→GRATEFUL).
        """
        start = cls._normalize_sentiment(sentiment.start or "NEUTRAL")
        end = cls._normalize_sentiment(sentiment.end or "NEUTRAL")

        if not sentiment.turning_points:
            if start == end:
                return f"[SENTIMENT:{start}]"
            return f"[SENTIMENT:{start}→{end}]"

        trajectory = [start]
        seen = {start}
        for _, emotion in sentiment.turning_points:
            emotion = cls._normalize_sentiment(emotion)
            if emotion != trajectory[-1] and emotion not in seen:
                seen.add(emotion)
                trajectory.append(emotion)

        # Append end only if it differs from the last label and hasn't appeared
        if trajectory[-1] != end and end not in seen:
            trajectory.append(end)

        trajectory_str = "→".join(trajectory)
        return f"[SENTIMENT:{trajectory_str}]"
