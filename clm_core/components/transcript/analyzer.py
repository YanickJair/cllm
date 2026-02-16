import re
from typing import Optional
import spacy

from .patterns import TranscriptPatterns
from . import (
    CallInfo,
    Issue,
    Action,
    Resolution,
    CustomerProfile,
    TranscriptAnalysis,
    Turn,
    ResolutionState,
    RefundReference,
    TimelineEvent,
    ConversationTimeline,
    PromiseCommitment,
)
from .vocabulary import TranscriptVocabulary
from clm_core.components.intent_detector import IntentDetector
from clm_core.components.target_extractor import TargetExtractor
from .utils.named_entity import EntityExtractor
from .utils.sentiment_analyzer import SentimentAnalyzer
from .utils.temporal_analyzer import TemporalAnalyzer
from ...utils.parser_rules import BaseRules
from ...utils.vocabulary import BaseVocabulary


class TranscriptAnalyzer:
    def __init__(
        self,
        nlp: spacy.Language,
        vocab: BaseVocabulary,
        rules: BaseRules,
        patterns: TranscriptPatterns,
    ):
        self.nlp = nlp
        self.patterns = patterns
        self.vocab = TranscriptVocabulary()
        self.intent_detector = IntentDetector(nlp=nlp, vocab=vocab)
        self.target_extractor = TargetExtractor(nlp, vocab=vocab, rules=rules)
        self.temporal_extractor = TemporalAnalyzer(
            nlp=nlp,
            day_names=patterns.day_names,
            word_to_num=patterns.word_to_num,
        )
        self.sentiment_analyzer = SentimentAnalyzer(
            emotion_keywords=patterns.emotion_keywords,
        )
        self.entity_extractor = EntityExtractor(
            nlp=nlp,
            ner_domain_patterns=patterns.ner_domain_patterns,
        )

        self._issue_type_index = self._build_keyword_index(patterns.issue_type_keywords)
        self._severity_index = self._build_keyword_index(patterns.severity_keywords)
        self._resolution_index = self._build_keyword_index(patterns.resolution_keywords)
        self._billing_cause_index = self._build_keyword_index(
            patterns.billing_cause_keywords
        )
        self._technical_issue_index = self._build_keyword_index(
            patterns.technical_issue_map
        )
        self._issue_confirmation_index = self._build_keyword_index(
            patterns.issue_confirmation_map
        )
        self._troubleshooting_index = self._build_keyword_index(
            patterns.troubleshooting_actions
        )
        self._action_tokens_index = self._build_action_tokens_index()

    @staticmethod
    def _build_keyword_index(keyword_dict: dict) -> list[tuple[str, str]]:
        """Build a flat list of (keyword, category) tuples sorted by keyword length desc.

        Longer keywords are checked first to match phrases like 'processed twice'
        before single words like 'twice'.
        """
        pairs = []
        for category, keywords in keyword_dict.items():
            for kw in keywords:
                pairs.append((kw.lower() if isinstance(kw, str) else kw, category))
        pairs.sort(key=lambda x: len(x[0]), reverse=True)
        return pairs

    @staticmethod
    def _lookup_category(text: str, index: list[tuple[str, str]]) -> Optional[str]:
        """Fast lookup using pre-built index. Returns first matching category."""
        for keyword, category in index:
            if keyword in text:
                return category
        return None

    @staticmethod
    def _lookup_all_categories(text: str, index: list[tuple[str, str]]) -> list[str]:
        """Fast lookup returning all matching categories (deduplicated, order preserved)."""
        seen = set()
        result = []
        for keyword, category in index:
            if keyword in text and category not in seen:
                seen.add(category)
                result.append(category)
        return result

    def _build_action_tokens_index(self) -> list[tuple[str, str, bool]]:
        """Build index for ACTION_TOKENS with explicit-only flag.

        Returns list of (keyword, action_event, is_explicit_only) tuples.
        Merges language-specific patterns.action_tokens with vocab defaults.
        """
        pairs = []
        # Merge: start with vocab defaults, then layer pattern overrides
        merged: dict[str, list[str]] = {}
        for raw_action, keywords in self.vocab.ACTION_TOKENS.items():
            merged[raw_action] = list(keywords)
        for raw_action, keywords in self.patterns.action_tokens.items():
            merged.setdefault(raw_action, []).extend(keywords)

        for raw_action, keywords in merged.items():
            if raw_action not in self.patterns.action_event_map:
                continue
            action_event = self.patterns.action_event_map[raw_action]
            is_explicit = action_event in self.patterns.explicit_only_actions
            for kw in keywords:
                pairs.append((kw.lower(), action_event, is_explicit))
        pairs.sort(key=lambda x: len(x[0]), reverse=True)
        return pairs

    def analyze(
        self, transcript: str, metadata: Optional[dict] = None
    ) -> TranscriptAnalysis:
        metadata = metadata or {}
        turns = self._parse_turns(transcript)

        docs = list(self.nlp.pipe([t.text for t in turns])) if turns else []
        for turn, doc in zip(turns, docs):
            turn.doc = doc
            turn.intent = self.intent_detector.get_primary_intent(
                self.intent_detector.detect(turn.text, doc=doc)
            )
            turn.targets.append(self.target_extractor.extract(text=turn.text, doc=doc))
            turn.sentiment, _ = self.sentiment_analyzer.analyze_turn(
                turn.text, turn.speaker
            )
            turn.entities = self.entity_extractor.extract(turn.text, doc=doc)

        call_info = self._extract_call_info(turns, metadata)
        customer = self._extract_customer_profile(turns)
        issues = self._extract_issues(turns)
        actions = self._extract_actions(turns)
        resolution = self._extract_resolution(turns)
        sentiment_trajectory = self.sentiment_analyzer.track_trajectory(turns)
        resolution_state = self._extract_resolution_state(turns, resolution)
        refund_reference = self._extract_refund_reference(turns, issues, actions)
        timeline = self._extract_conversation_timeline(turns)
        promises = self._extract_promises(turns)

        # v2 schema extractions
        domain = self._extract_domain(call_info, issues)
        service = self._extract_service(issues, turns)
        customer_intent, secondary_intent = self._extract_customer_intent(
            issues, turns
        )
        context_provided = self._extract_context_provided(turns)
        system_actions = self._extract_system_actions(turns)

        return TranscriptAnalysis(
            call_info=call_info,
            customer=customer,
            turns=turns,
            issues=issues,
            actions=actions,
            resolution=resolution,
            sentiment_trajectory=sentiment_trajectory,
            resolution_state=resolution_state,
            refund_reference=refund_reference,
            timeline=timeline,
            promises=promises,
            domain=domain,
            service=service,
            customer_intent=customer_intent,
            secondary_intent=secondary_intent,
            context_provided=context_provided,
            system_actions=system_actions,
        )

    @staticmethod
    def _parse_turns(transcript: str) -> list[Turn]:
        turns = []
        for line in transcript.strip().split("\n"):
            if not line or ":" not in line:
                continue
            speaker, text = line.split(":", 1)
            speaker = speaker.strip().lower()
            if "agent" in speaker or "agente" in speaker:
                speaker = "agent"
            elif any(x in speaker for x in ("customer", "caller", "cliente", "client")):
                speaker = "customer"
            else:
                speaker = "system"
            turns.append(Turn(speaker=speaker, text=text.strip()))
        return turns

    def _extract_actions(self, turns: list[Turn]) -> list[Action]:
        """
        Extract canonical, atomic ACTION EVENTS from agent turns.

        Each Action represents a confirmed fact (event),
        not a derived outcome or result.
        """
        actions: dict[str, Action] = {}

        for turn in turns:
            if turn.speaker != "agent":
                continue

            text = turn.text

            action_events = self._detect_action_events(text)
            if not action_events:
                continue

            for action_type in action_events:
                if action_type not in actions:
                    actions[action_type] = Action(type=action_type, attributes={})

                action = actions[action_type]

                if "REFUND" in action_type or "ESCALATION" in action_type:
                    if ref := self._extract_reference_number(turn):
                        action.attributes["reference"] = ref

                if "REFUND" in action_type or "CREDIT" in action_type:
                    amount, method = self._extract_financial_details(turn)
                    if amount:
                        action.attributes.setdefault("amount", amount)
                    if method:
                        action.attributes.setdefault("payment_method", method)

        return list(actions.values())

    def _detect_action_events(self, text: str) -> list[str]:
        text_lower = text.lower()
        seen = set()
        events = []

        for kw, category in self._issue_confirmation_index:
            if kw in text_lower and category not in seen:
                seen.add(category)
                events.append(category)

        for kw, category in self._troubleshooting_index:
            if kw in text_lower and category not in seen:
                seen.add(category)
                events.append(category)

        for kw, action_event, is_explicit in self._action_tokens_index:
            if action_event in seen:
                continue
            if kw not in text_lower:
                continue
            if is_explicit:
                phrases = self.patterns.explicit_action_phrases.get(action_event, set())
                if not any(p in text_lower for p in phrases):
                    continue
            seen.add(action_event)
            events.append(action_event)

        return events

    def _detect_technical_issue_detail(self, text: str) -> Optional[str]:
        return self._lookup_category(text.lower(), self._technical_issue_index)

    def _extract_action_details(self, action_type: str, turn: Turn):
        amount, method = None, None
        attributes = {}
        if action_type in ["REFUND", "CREDIT", "CHARGE", "PAYMENT"]:
            amount, method = self._extract_financial_details(turn)
            if ref := self._extract_reference_number(turn):
                attributes["reference"] = ref
            if timeline := self._extract_timeline(turn.text):
                attributes["timeline"] = timeline
        return amount, method, attributes

    def _extract_resolution(self, turns: list[Turn]) -> Resolution:
        agent_turns = [t for t in turns if t.speaker == "agent"]
        recent = agent_turns[-5:] if agent_turns else []

        for turn in reversed(recent):
            text = turn.text.lower()
            key = self._lookup_category(text, self._resolution_index)
            if key:
                if key == "PENDING_REPLACEMENT":
                    res_type = "PENDING"
                    next_steps = "REPLACEMENT"
                else:
                    res_type = key
                    next_steps = None
                timeline = self._extract_timeline(text)
                return Resolution(
                    type=res_type, timeline=timeline, next_steps=next_steps
                )

        return Resolution(type="UNKNOWN", timeline=None, next_steps=None)

    @staticmethod
    def _match_any(text: str, keywords: list[str]) -> bool:
        return any(kw in text for kw in keywords)

    def _extract_timeline(self, text: str) -> Optional[str]:
        text_lower = text.lower()

        # Language-specific timeline patterns first (more specific, e.g. "3 a 5 días hábiles")
        for regex, fmt in self.patterns.timeline_patterns:
            if match := re.search(regex, text_lower, re.I):
                groups = match.groups()
                return fmt.format(*groups)

        # Temporal extractor (duration inference)
        pattern = self.temporal_extractor.extract(text)
        if pattern and getattr(pattern, "duration", None):
            return str(pattern.duration).upper()

        # Language-specific timeline keywords
        timeline_kw = self.patterns.timeline_keywords or {}
        for kw, value in timeline_kw.items():
            if kw in text_lower:
                return value

        # English defaults
        if "tomorrow" in text_lower:
            return "TOMORROW"
        if "today" in text_lower:
            return "TODAY"
        if match := re.search(r"within\s+(\d+)\s*(hour|hours)", text, re.I):
            return f"{match.group(1)}h"
        if match := re.search(r"within\s+(\d+)\s*(day|days)", text, re.I):
            return f"{match.group(1)}d"
        return None

    def _determine_action_result(
        self, turns: list[Turn], action_index: int, action_turn: Turn
    ) -> str:
        text_lower = action_turn.text.lower()

        if any(
            k in text_lower
            for k in self.patterns.action_completion_keywords
            | self.patterns.action_completion_phrases
        ):
            return "COMPLETED"

        for pattern in self.patterns.action_now_patterns:
            if re.search(pattern, text_lower):
                return "COMPLETED"

        for t in turns[action_index + 1 : action_index + 3]:
            tl = t.text.lower()
            if t.speaker == "customer" and any(
                k in tl for k in self.patterns.positive_customer_confirmations
            ):
                return "COMPLETED"
            if t.speaker == "agent" and any(
                k in tl for k in self.patterns.agent_confirmation_phrases
            ):
                return "COMPLETED"
        return "PENDING"

    @staticmethod
    def _extract_financial_details(turn: Turn) -> tuple[Optional[str], Optional[str]]:
        """
        Prefer using named entities from turn.entities if present; otherwise fallback to regex heuristics.
        Returns (amount, payment_method)
        """
        amount = None
        method = None
        ents = getattr(turn, "entities", {}) or {}

        money_candidates = ents.get("money") or ents.get("money_amounts") or []
        if money_candidates:
            amount = money_candidates[0]

        if not amount:
            if m := re.search(r"\$\s?([\d,]+(?:\.\d{1,2})?)", turn.text):
                amount = f"${m.group(1)}"

        text_lower = turn.text.lower()
        if "paypal" in text_lower:
            method = "PAYPAL"
        elif "check" in text_lower:
            method = "CHECK"
        elif "credit card" in text_lower or "card" in text_lower:
            method = "CARD_CREDIT"
        elif (
            "account credit" in text_lower
            or "account" in text_lower
            and "credit" in text_lower
        ):
            method = "ACCOUNT_CREDIT"
        return amount, method

    @staticmethod
    def _extract_reference_number(turn: Turn) -> Optional[str]:
        """
        Extracts reference numbers like:
         - RFD-908712
         - ESC-45390
         - "reference number is RFD-..." or "confirmation #12345"
        """
        text = turn.text
        if m := re.search(r"\b([A-Z]{2,5}-\d{3,})\b", text):
            return m.group(0)

        if m := re.search(
            r"(?:reference|confirmation|ref)[^\w]{0,6}#?\s*([A-Z0-9-]{4,30})",
            text,
            re.I,
        ):
            return m.group(1)

        if m := re.search(
            r"(?:id|ticket|case|order)[^\w]{0,6}#?\s*([A-Z0-9-]{3,30})", text, re.I
        ):
            return m.group(1)

        return None

    def _extract_customer_profile(self, turns: list[Turn]) -> CustomerProfile:
        """Extract the customer's profile from the conversation.

        Args:
            turns: List of turns in the conversation.

        Returns:
            The customer's profile if found, otherwise None.
        Examples:
            >>> analyzer = TranscriptAnalyzer()
            >>> turns = [
            ...     Turn(speaker="customer", text="I have a problem with my account."),
            ...     Turn(speaker="agent", text="What seems to be the issue?"),
            ...     Turn(speaker="customer", text="I'm not getting my bill."),
            ... ]
            >>> analyzer._extract_customer_profile(turns)
            CustomerProfile(name='John', account='12345', tier='STANDARD')
        """
        profile = CustomerProfile()
        profile.name = self._extract_customer_name(turns)

        for t in turns:
            ents = getattr(t, "entities", {}) or {}
            if emails := ents.get("emails"):
                profile.attributes = profile.attributes or {}
                profile.attributes["email"] = emails[0]
            if accounts := ents.get("accounts") or ents.get("account_numbers"):
                profile.account = profile.account or accounts[0]
            if plans := ents.get("plans"):
                profile.tier = profile.tier or self._map_plan_to_tier(plans[0])

        return profile

    @staticmethod
    def _map_plan_to_tier(plan: str) -> str:
        """Map a plan to a tier.

        Args:
            plan: The plan name.

        Returns:
            The tier corresponding to the plan.
        Examples:
            >>> analyzer = TranscriptAnalyzer()
            >>> analyzer._map_plan_to_tier("Premium")
            'PREMIUM'
        """
        plan = plan.lower()
        if "premium" in plan:
            return "PREMIUM"
        if "enterprise" in plan:
            return "ENTERPRISE"
        if "basic" in plan:
            return "BASIC"
        return "STANDARD"

    @staticmethod
    def _extract_customer_name(turns: list[Turn]) -> Optional[str]:
        """Extract the customer's name from the conversation.

        Args:
            turns: List of turns in the conversation.

        Returns:
            The customer's name if found, otherwise None.
        Examples:
            >>> analyzer = TranscriptAnalyzer()
            >>> turns = [
            ...     Turn(speaker="customer", text="I have a problem with my account."),
            ...     Turn(speaker="agent", text="What seems to be the issue?"),
            ...     Turn(speaker="customer", text="I'm not getting my bill."),
            ... ]
            >>> analyzer._extract_customer_name(turns)
            'John'
        """
        for t in turns[:3]:
            if t.speaker == "agent":
                doc = t.doc
                if doc:
                    for ent in doc.ents:
                        if ent.label_ == "PERSON":
                            return ent.text
                if match := re.search(
                    r"(?:my name is|i'?m|this is)\s+([A-Z][a-z]+)", t.text, re.I
                ):
                    return match.group(1).title()
                if match := re.search(r"thank(?:s| you),\s+([A-Z][a-z]+)", t.text):
                    return match.group(1)
        for t in turns:
            ents = getattr(t, "entities", {}) or {}
            emails = ents.get("emails") or []
            if emails:
                local_part = emails[0].split("@")[0]
                if "." in local_part:
                    return local_part.split(".")[0].title()
        return None

    def _extract_issues(self, turns: list[Turn]) -> list[Issue]:
        """Extract issues from a list of turns.

        Args:
            turns: List of turns in the conversation.

        Returns:
            A list of issues extracted from the conversation.
        Examples:
            >>> analyzer = TranscriptAnalyzer()
            >>> turns = [
            ...     Turn(speaker="customer", text="I have a problem with my account."),
            ...     Turn(speaker="agent", text="What seems to be the issue?"),
            ...     Turn(speaker="customer", text="I'm not getting my bill."),
            ... ]
            >>> analyzer._extract_issues(turns)
            [Issue(type="ACCOUNT_ISSUE", severity="LOW", cause="BILLING_DISPUTE", plan_change=None, amounts=[], days=[])]
        """
        customer_text = " ".join(
            t.text for t in turns if t.speaker == "customer"
        ).lower()
        issue_type = self._get_issue_type(customer_text)
        if not issue_type:
            return []

        severity = self._detect_severity(customer_text)
        cause, plan_change = None, None
        amounts = []

        if issue_type in ["BILLING_DISPUTE", "UNEXPECTED_CHARGE", "REFUND_REQUEST"]:
            cause, plan_change = self._detect_billing_cause(turns)
            amounts = self._extract_disputed_amounts(turns)

        days = self.temporal_extractor.extract(customer_text).days or []
        attrs = {"days": days} if days else {}
        if issue_type in {"CONNECTIVITY", "TECHNICAL"}:
            cause = self._detect_technical_issue_detail(customer_text)
            return [
                Issue(
                    type=issue_type,
                    severity=severity,
                    cause=cause,
                    attributes=attrs,
                )
            ]

        return [
            Issue(
                type=issue_type,
                severity=severity,
                cause=cause,
                plan_change=plan_change,
                disputed_amounts=amounts,
                attributes=attrs,
            )
        ]

    def _get_issue_type(self, text: str) -> Optional[str]:
        return self._lookup_category(text, self._issue_type_index)

    def _detect_severity(self, text: str) -> str:
        return self._lookup_category(text.lower(), self._severity_index) or "LOW"

    def _extract_disputed_amounts(self, turns: list[Turn]) -> list[str]:
        """Extract disputed amounts from customer turns.

        Args:
            turns: List of turns.

        Returns:
            List of disputed amounts.
        Examples:
            >>> _extract_disputed_amounts([Turn("customer", "I think my bill is wrong"), Turn("agent", "What amount do you think is wrong?"), Turn("customer", "I think it's $100")])
            ['$100']
        """
        en_keywords = ["charge", "bill", "statement", "payment"]
        keywords = en_keywords + (self.patterns.disputed_amount_keywords or [])
        amounts = []
        for t in (t for t in turns if t.speaker == "customer"):
            if any(k in t.text.lower() for k in keywords):
                amounts.extend(getattr(t, "entities", {}).get("money", []))
        return list(dict.fromkeys(amounts))

    def _detect_billing_cause(
        self, turns: list[Turn]
    ) -> tuple[Optional[str], Optional[str]]:
        for t in (t for t in turns if t.speaker == "agent"):
            text = t.text.lower()
            cause = self._lookup_category(text, self._billing_cause_index)
            if cause:
                plan_change = None
                if cause in {"MID_CYCLE_UPGRADE", "MID_CYCLE_DOWNGRADE"}:
                    if match := re.search(r"from (\w+) to (\w+)", text):
                        plan_change = (
                            f"{match.group(1).upper()}→{match.group(2).upper()}"
                        )
                return cause, plan_change
        return None, None

    def _extract_call_info(self, turns: list[Turn], metadata: dict) -> CallInfo:
        """
        Extracts call information from the transcript.

        Args:
            turns: List of turns in the transcript.
            metadata: Metadata associated with the call.

        Returns:
            CallInfo object containing extracted information.
        """
        agent_name = metadata.get("agent") or self._detect_agent_name(turns)
        full_text = " ".join(t.text.lower() for t in turns)
        call_type = (
            "SALES"
            if any(
                x in full_text for x in ["upgrade", "pricing", "buy", "interested in"]
            )
            else "SUPPORT"
        )
        return CallInfo(
            call_id=metadata.get("call_id", "unknown"),
            type=call_type,
            channel=metadata.get("channel", "VOICE"),
            duration=len(turns),
            agent=agent_name,
        )

    # Common words that should not be extracted as agent names
    _NAME_BLACKLIST = {
        "sorry",
        "happy",
        "glad",
        "pleased",
        "here",
        "calling",
        "able",
        "going",
        "looking",
        "checking",
        "helping",
        "available",
        "ready",
        "sure",
        "certain",
        "afraid",
        "delighted",
        "excited",
        "thrilled",
    }

    @classmethod
    def _detect_agent_name(cls, turns: list[Turn]) -> Optional[str]:
        """Detects the agent's name from the transcript.
        We will find the agent's name by looking for a PERSON entity
        in the text or by matching a pattern.

        Args:
            turns: List of turns in the transcript.

        Returns:
            The detected agent's name or None if not found.

        Examples:
            >>> _detect_agent_name([Turn("agent", "Hello, my name is John.")])
            'John'
        """
        for t in (t for t in turns[:3] if t.speaker == "agent"):
            doc = getattr(t, "doc", None)
            if doc:
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        name = ent.text.lower()
                        if name not in cls._NAME_BLACKLIST:
                            return ent.text
            if match := re.search(
                r"(?:my name is|this is)\s+([A-Z][a-z]+)", t.text, re.I
            ):
                candidate = match.group(1)
                if candidate.lower() not in cls._NAME_BLACKLIST:
                    return candidate
        return None

    def _extract_resolution_state(
        self, turns: list[Turn], resolution: Resolution
    ) -> ResolutionState:
        """Extract enhanced resolution state with granularity."""
        agent_turns = [t for t in turns if t.speaker == "agent"]
        customer_turns = [t for t in turns if t.speaker == "customer"]

        completeness = self._detect_resolution_completeness(agent_turns)
        customer_satisfaction = self._derive_customer_satisfaction(customer_turns)
        follow_up_needed, follow_up_reason = self._detect_follow_up_needed(agent_turns)
        resolution_type = self._map_resolution_to_state(
            resolution.type, completeness, follow_up_needed, customer_satisfaction
        )

        return ResolutionState(
            type=resolution_type,
            completeness=completeness,
            customer_satisfaction=customer_satisfaction,
            follow_up_needed=follow_up_needed,
            follow_up_reason=follow_up_reason,
        )

    def _detect_resolution_completeness(self, agent_turns: list[Turn]) -> Optional[str]:
        """Detect if resolution was full, partial, or none."""
        recent = agent_turns[-5:] if agent_turns else []
        text = " ".join(t.text.lower() for t in recent)

        tokens = (
            self.patterns.resolution_state_tokens or self.vocab.RESOLUTION_STATE_TOKENS
        )
        for state, keywords in tokens.items():
            if any(kw in text for kw in keywords):
                if state == "FULLY_RESOLVED":
                    return "FULL"
                elif state == "PARTIALLY_RESOLVED":
                    return "PARTIAL"
        return None

    def _derive_customer_satisfaction(
        self, customer_turns: list[Turn]
    ) -> Optional[str]:
        """Derive satisfaction from final customer turns."""
        if not customer_turns:
            return None

        final_turns = customer_turns[-3:]
        text = " ".join(t.text.lower() for t in final_turns)

        tokens = (
            self.patterns.customer_satisfaction_tokens
            or self.vocab.CUSTOMER_SATISFACTION_TOKENS
        )
        for satisfaction, keywords in tokens.items():
            if any(kw in text for kw in keywords):
                return satisfaction

        if final_turns:
            final_sentiment = final_turns[-1].sentiment
            if final_sentiment in ["SATISFIED", "GRATEFUL", "RELIEVED"]:
                return "SATISFIED"
            elif final_sentiment in ["FRUSTRATED", "ANGRY", "DISAPPOINTED"]:
                return "DISSATISFIED"

        return "NEUTRAL"

    def _detect_follow_up_needed(
        self, agent_turns: list[Turn]
    ) -> tuple[bool, Optional[str]]:
        """Detect if follow-up is needed and why."""
        recent = agent_turns[-3:] if agent_turns else []
        text = " ".join(t.text.lower() for t in recent)

        tokens = (
            self.patterns.follow_up_needed_tokens or self.vocab.FOLLOW_UP_NEEDED_TOKENS
        )
        for reason, keywords in tokens.items():
            if any(kw in text for kw in keywords):
                return True, reason

        return False, None

    @staticmethod
    def _map_resolution_to_state(
        resolution_type: str,
        completeness: Optional[str],
        follow_up_needed: bool,
        customer_satisfaction: Optional[str] = None,
    ) -> str:
        """Map resolution to granular state, considering customer satisfaction."""
        if resolution_type == "RESOLVED":
            if completeness == "FULL" and not follow_up_needed:
                return "FULLY_RESOLVED"
            elif completeness == "PARTIAL":
                return "PARTIALLY_RESOLVED"
            else:
                return "RESOLVED_PENDING_VERIFICATION"
        elif resolution_type == "PENDING":
            return "PENDING"
        elif resolution_type == "ESCALATED":
            return "ESCALATED"
        else:
            # If resolution is UNKNOWN but customer is satisfied, infer resolution
            if customer_satisfaction == "SATISFIED":
                if completeness == "FULL":
                    return "FULLY_RESOLVED"
                return "RESOLVED"
            elif customer_satisfaction == "NEUTRAL":
                return "RESOLVED_PENDING_VERIFICATION"
            return "UNRESOLVED"

    def _extract_refund_reference(
        self, turns: list[Turn], issues: list[Issue], actions: list[Action]
    ) -> Optional[RefundReference]:
        """Extract refund details for billing/refund cases (case-dependent)."""
        issue_types = [i.type for i in issues]
        is_refund_case = any(
            it in issue_types
            for it in [
                "BILLING_DISPUTE",
                "REFUND_REQUEST",
                "DUPLICATE_CHARGE",
                "UNEXPECTED_CHARGE",
                "MISSING_REFUND",
            ]
        )

        has_refund_action = any(
            "REFUND" in a.type or "CREDIT" in a.type for a in actions
        )

        if not is_refund_case and not has_refund_action:
            return None

        refund = RefundReference()

        for turn in turns:
            if turn.speaker != "agent":
                continue

            text = turn.text
            text_lower = text.lower()

            if not refund.reference_number:
                refund.reference_number = self._extract_refund_reference_number(text)

            if not refund.amount:
                amount, _ = self._extract_financial_details(turn)
                refund.amount = amount

            if not refund.method:
                refund.method = self._detect_refund_method(text_lower)

            if not refund.status:
                refund.status = self._detect_refund_status(text_lower)

            if not refund.timeline:
                refund.timeline = self._extract_timeline(text_lower)

        # Also pull from action attributes
        for action in actions:
            if "REFUND" in action.type or "CREDIT" in action.type:
                if not refund.reference_number and "reference" in action.attributes:
                    refund.reference_number = action.attributes["reference"]
                if not refund.amount and action.amount:
                    refund.amount = action.amount
                if not refund.method and action.payment_method:
                    refund.method = action.payment_method

        # Only return if we have meaningful data
        if any([refund.reference_number, refund.amount, refund.status]):
            return refund

        return None

    @staticmethod
    def _extract_refund_reference_number(text: str) -> Optional[str]:
        """Extract refund-specific reference numbers."""
        patterns = [
            r"\bRFD-?\d{5,10}\b",
            r"\bREF-?\d{5,10}\b",
            r"\bCRD-?\d{5,10}\b",
            r"refund\s*(?:number|id|#)?\s*[:=]?\s*([A-Z0-9-]{5,15})",
        ]

        for pattern in patterns:
            if match := re.search(pattern, text, re.I):
                return match.group(0) if match.lastindex is None else match.group(1)

        return None

    def _detect_refund_method(self, text: str) -> Optional[str]:
        """Detect refund method from text."""
        tokens = self.patterns.refund_method_tokens or self.vocab.REFUND_METHOD_TOKENS
        for method, keywords in tokens.items():
            if any(kw in text for kw in keywords):
                return method
        return None

    def _detect_refund_status(self, text: str) -> Optional[str]:
        """Detect refund status from text."""
        tokens = self.patterns.refund_status_tokens or self.vocab.REFUND_STATUS_TOKENS
        for status, keywords in tokens.items():
            if any(kw in text for kw in keywords):
                return status
        return None

    def _extract_conversation_timeline(self, turns: list[Turn]) -> ConversationTimeline:
        """Extract conversation timeline with key events."""
        events = []
        first_issue_turn = None
        first_resolution_turn = None

        for idx, turn in enumerate(turns):
            text_lower = turn.text.lower()

            event_type = self._detect_timeline_event_type(text_lower, turn.speaker)

            if event_type:
                event = TimelineEvent(
                    event_type=event_type,
                    description=self._summarize_event(turn.text, event_type),
                    turn_index=idx,
                    timestamp=turn.timestamp,
                    actor=turn.speaker,
                )
                events.append(event)

                if event_type == "ISSUE_RAISED" and first_issue_turn is None:
                    first_issue_turn = idx
                elif (
                    event_type in ["RESOLUTION_PROPOSED", "ACTION_TAKEN"]
                    and first_resolution_turn is None
                ):
                    first_resolution_turn = idx

        time_to_first_action = None
        time_to_resolution = None

        if first_issue_turn is not None:
            first_action = next(
                (e.turn_index for e in events if e.event_type == "ACTION_TAKEN"), None
            )
            if first_action is not None:
                time_to_first_action = first_action - first_issue_turn

            if first_resolution_turn is not None:
                time_to_resolution = first_resolution_turn - first_issue_turn

        return ConversationTimeline(
            events=events,
            first_issue_turn=first_issue_turn,
            first_resolution_turn=first_resolution_turn,
            time_to_first_action=time_to_first_action,
            time_to_resolution=time_to_resolution,
        )

    def _detect_timeline_event_type(self, text: str, speaker: str) -> Optional[str]:
        """Detect timeline event type from turn text."""
        tokens = self.patterns.timeline_event_tokens or self.vocab.TIMELINE_EVENT_TOKENS
        for event_type, keywords in tokens.items():
            # Issue raised typically by customer
            if event_type == "ISSUE_RAISED" and speaker != "customer":
                continue
            # Most other events by agent
            if (
                event_type
                in ["ACTION_TAKEN", "RESOLUTION_PROPOSED", "INVESTIGATION_STARTED"]
                and speaker != "agent"
            ):
                continue

            if any(kw in text for kw in keywords):
                return event_type

        return None

    @staticmethod
    def _summarize_event(text: str, event_type: str) -> str:
        """Create brief summary of event."""
        sentences = text.split(".")
        summary = sentences[0] if sentences else text
        return summary[:100].strip()

    def _extract_promises(self, turns: list[Turn]) -> list[PromiseCommitment]:
        """Extract agent promises and commitments (case-dependent)."""
        promises = []

        for idx, turn in enumerate(turns):
            if turn.speaker != "agent":
                continue

            text = turn.text
            text_lower = text.lower()

            tokens = (
                self.patterns.promise_commitment_tokens
                or self.vocab.PROMISE_COMMITMENT_TOKENS
            )
            for promise_type, keywords in tokens.items():
                matching_keyword = next(
                    (kw for kw in keywords if kw in text_lower), None
                )

                if matching_keyword:
                    timeline = self._extract_promise_timeline(text_lower)
                    amount = None

                    if promise_type in ["CREDIT_PROMISE", "REFUND_PROMISE"]:
                        amount, _ = self._extract_financial_details(turn)

                    confidence = self._calculate_promise_confidence(
                        text_lower, promise_type
                    )

                    promise = PromiseCommitment(
                        type=promise_type,
                        description=self._extract_promise_description(
                            text, matching_keyword
                        ),
                        timeline=timeline,
                        amount=amount,
                        turn_index=idx,
                        confidence=confidence,
                    )
                    promises.append(promise)

        return self._dedupe_promises(promises)

    def _extract_promise_timeline(self, text: str) -> Optional[str]:
        """Extract timeline from promise text."""
        timeline = self._extract_timeline(text)
        if timeline:
            return timeline

        en_patterns = [
            (r"within (\d+) hours?", lambda m: f"{m.group(1)}h"),
            (r"within (\d+) days?", lambda m: f"{m.group(1)}d"),
            (
                r"by (monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
                lambda m: m.group(1).upper(),
            ),
            (r"next (week|month)", lambda m: f"NEXT_{m.group(1).upper()}"),
            (
                r"in the next (\d+[-\s]?\d*) ?(business )?days?",
                lambda m: f"{m.group(1).strip()}d",
            ),
        ]

        for pattern, formatter in en_patterns:
            if match := re.search(pattern, text, re.I):
                return formatter(match)

        # Language-specific day names for "by <day>" pattern
        if self.patterns.day_names:
            day_alts = "|".join(re.escape(d) for d in self.patterns.day_names)
            if match := re.search(rf"(?:para el|antes del)\s+({day_alts})", text, re.I):
                return self.patterns.day_names.get(
                    match.group(1).lower(), match.group(1).upper()
                )

        return None

    def _calculate_promise_confidence(self, text: str, promise_type: str) -> float:
        """Calculate confidence in promise detection."""
        confidence = 0.6

        strong_indicators = ["will", "going to", "i'll", "we'll", "definitely"]
        if self.patterns.promise_confidence_strong:
            strong_indicators = (
                strong_indicators + self.patterns.promise_confidence_strong
            )
        if any(ind in text for ind in strong_indicators):
            confidence += 0.2

        timeline_re = r"within|by|before|tomorrow|today|\d+ (day|hour)"
        if self.patterns.timeline_keywords:
            kw_alts = "|".join(re.escape(k) for k in self.patterns.timeline_keywords)
            timeline_re = rf"{timeline_re}|{kw_alts}"
        if re.search(timeline_re, text, re.I):
            confidence += 0.1

        if promise_type in ["CREDIT_PROMISE", "REFUND_PROMISE"]:
            if "$" in text or re.search(r"\d+\.?\d*", text):
                confidence += 0.1

        return min(confidence, 1.0)

    @staticmethod
    def _extract_promise_description(text: str, keyword: str) -> str:
        """Extract the promise description around the keyword."""
        sentences = text.split(".")
        for sentence in sentences:
            if keyword in sentence.lower():
                return sentence.strip()[:150]
        return text[:150]

    @staticmethod
    def _dedupe_promises(promises: list[PromiseCommitment]) -> list[PromiseCommitment]:
        """Remove duplicate promises of the same type."""
        seen_types = set()
        unique = []
        for p in promises:
            key = (p.type, p.amount, p.timeline)
            if key not in seen_types:
                seen_types.add(key)
                unique.append(p)
        return unique

    # ============================================================
    # v2 schema extraction methods
    # ============================================================

    # Maps issue types to v2 DOMAIN values
    _ISSUE_TO_DOMAIN = {
        "BILLING_DISPUTE": "BILLING",
        "DUPLICATE_CHARGE": "BILLING",
        "PAYMENT_FAILED": "BILLING",
        "MISSING_REFUND": "BILLING",
        "INVALID_COUPON": "BILLING",
        "CREDIT_CARD_UPDATE": "BILLING",
        "AUTO_RENEWAL_ISSUE": "BILLING",
        "CARD_DECLINED": "BILLING",
        "UNAUTHORIZED_TRANSACTION": "BILLING",
        "MISSING_STATEMENT": "BILLING",
        "INVOICE_REQUEST": "BILLING",
        "REFUND_DELAY": "BILLING",
        "UNEXPECTED_CHARGE": "BILLING",
        "OVERCHARGE": "BILLING",
        "PREMIUM_PAYMENT_ISSUE": "BILLING",
        "LOGIN_FAILURE": "AUTHENTICATION",
        "AUTHENTICATION_ERROR": "AUTHENTICATION",
        "ACCOUNT_LOCKED": "AUTHENTICATION",
        "ACCOUNT_HACKED": "AUTHENTICATION",
        "KYC_VERIFICATION": "AUTHENTICATION",
        "ACCOUNT_CREATION_ERROR": "AUTHENTICATION",
        "INTERNET_OUTAGE": "PERFORMANCE",
        "SLOW_INTERNET": "PERFORMANCE",
        "SERVER_DOWN": "PERFORMANCE",
        "APP_CRASH": "PERFORMANCE",
        "OVERHEATING_DEVICE": "PERFORMANCE",
        "CONNECTIVITY": "PERFORMANCE",
        "PERFORMANCE": "PERFORMANCE",
        "WIFI_ISSUE": "PERFORMANCE",
        "DELIVERY_DELAY": "LOGISTICS",
        "LOST_PACKAGE": "LOGISTICS",
        "DAMAGED_PACKAGE": "LOGISTICS",
        "WRONG_ITEM": "LOGISTICS",
        "TRACKING_ISSUE": "LOGISTICS",
        "CUSTOMS_HOLD": "LOGISTICS",
        "PRODUCT_NOT_RECEIVED": "LOGISTICS",
        "ADDRESS_CHANGE": "LOGISTICS",
        "WAREHOUSE_DELAY": "LOGISTICS",
        "OUT_OF_STOCK": "LOGISTICS",
        "PREORDER_DELAY": "LOGISTICS",
        "API_ERROR": "API",
        "REPORTING_ISSUE": "API",
        "DATA_EXPORT_ERROR": "API",
        "EMAIL_INTEGRATION_ISSUE": "API",
        "ACCOUNT_SYNC_ERROR": "API",
        "APPOINTMENT_RESCHEDULE": "BOOKINGS",
        "RETURN_REQUEST": "RETURNS",
        "EXCHANGE_REQUEST": "RETURNS",
        "RETURN_REFUSED": "RETURNS",
        "EXPIRED_RETURN_WINDOW": "RETURNS",
        "ORDER_CANCELLATION": "RETURNS",
        "SUBSCRIPTION_CANCELLATION": "ACCOUNT_MANAGEMENT",
        "PLAN_UPGRADE": "ACCOUNT_MANAGEMENT",
        "PLAN_DOWNGRADE": "ACCOUNT_MANAGEMENT",
        "PROFILE_UPDATE": "ACCOUNT_MANAGEMENT",
        "DATA_PRIVACY_REQUEST": "ACCOUNT_MANAGEMENT",
        "MULTIPLE_ACCOUNTS": "ACCOUNT_MANAGEMENT",
    }

    # Maps call type to domain fallback
    _CALL_TYPE_TO_DOMAIN = {
        "BILLING": "BILLING",
        "TECHNICAL": "PERFORMANCE",
        "SALES": "SALES",
        "SUPPORT": "SUPPORT",
        "RETENTION": "RETENTION",
        "LOGISTICS": "LOGISTICS",
        "ACCOUNT_MANAGEMENT": "ACCOUNT_MANAGEMENT",
        "FEEDBACK": "FEEDBACK",
        "RETURNS": "RETURNS",
    }

    @classmethod
    def _extract_domain(
        cls, call_info: CallInfo, issues: list[Issue]
    ) -> Optional[str]:
        """Extract v2 DOMAIN from issues and call info."""
        if issues:
            issue_type = issues[0].type
            if issue_type in cls._ISSUE_TO_DOMAIN:
                return cls._ISSUE_TO_DOMAIN[issue_type]
        return cls._CALL_TYPE_TO_DOMAIN.get(call_info.type, "SUPPORT")

    # Maps issue types to v2 SERVICE values
    _ISSUE_TO_SERVICE = {
        "SUBSCRIPTION_CANCELLATION": "SUBSCRIPTION",
        "PLAN_UPGRADE": "SUBSCRIPTION",
        "PLAN_DOWNGRADE": "SUBSCRIPTION",
        "AUTO_RENEWAL_ISSUE": "SUBSCRIPTION",
        "SUBSCRIPTION_RENEWAL_ISSUE": "SUBSCRIPTION",
        "PAYMENT_FAILED": "PAYMENT",
        "CREDIT_CARD_UPDATE": "PAYMENT",
        "CARD_DECLINED": "PAYMENT",
        "UNAUTHORIZED_TRANSACTION": "PAYMENT",
        "MISSING_STATEMENT": "PAYMENT",
        "PREMIUM_PAYMENT_ISSUE": "PAYMENT",
        "BILLING_DISPUTE": "PAYMENT",
        "DUPLICATE_CHARGE": "PAYMENT",
        "MISSING_REFUND": "PAYMENT",
        "REPORTING_ISSUE": "DASHBOARD",
        "DATA_EXPORT_ERROR": "EXPORTS",
        "API_ERROR": "API",
        "DELIVERY_DELAY": "DELIVERY",
        "LOST_PACKAGE": "DELIVERY",
        "DAMAGED_PACKAGE": "DELIVERY",
        "TRACKING_ISSUE": "DELIVERY",
    }

    @classmethod
    def _extract_service(
        cls, issues: list[Issue], turns: list[Turn]
    ) -> Optional[str]:
        """Extract v2 SERVICE from issues."""
        if issues:
            issue_type = issues[0].type
            if issue_type in cls._ISSUE_TO_SERVICE:
                return cls._ISSUE_TO_SERVICE[issue_type]
        return None

    # Maps issue types to v2 CUSTOMER_INTENT
    _ISSUE_TO_INTENT = {
        "BILLING_DISPUTE": "REPORT_BILLING_ISSUE",
        "DUPLICATE_CHARGE": "REPORT_DUPLICATE_CHARGE",
        "PAYMENT_FAILED": "REPORT_PAYMENT_FAILURE",
        "MISSING_REFUND": "REQUEST_REFUND_STATUS",
        "REFUND_DELAY": "REQUEST_REFUND_STATUS",
        "REFUND_REQUEST": "REQUEST_REFUND",
        "UNEXPECTED_CHARGE": "REPORT_UNEXPECTED_CHARGE",
        "OVERCHARGE": "REPORT_OVERCHARGE",
        "LOGIN_FAILURE": "REPORT_LOGIN_ISSUE",
        "AUTHENTICATION_ERROR": "REPORT_AUTH_ERROR",
        "ACCOUNT_LOCKED": "ACCOUNT_UNLOCK",
        "ACCOUNT_HACKED": "REPORT_SECURITY_BREACH",
        "INTERNET_OUTAGE": "REPORT_OUTAGE",
        "SLOW_INTERNET": "REPORT_SLOW_PERFORMANCE",
        "SERVER_DOWN": "REPORT_OUTAGE",
        "CONNECTIVITY": "REPORT_CONNECTIVITY_ISSUE",
        "WIFI_ISSUE": "REPORT_CONNECTIVITY_ISSUE",
        "DELIVERY_DELAY": "REPORT_DELIVERY_DELAY",
        "LOST_PACKAGE": "REPORT_LOST_PACKAGE",
        "DAMAGED_PACKAGE": "REPORT_DAMAGED_ITEM",
        "WRONG_ITEM": "REPORT_WRONG_ITEM",
        "SUBSCRIPTION_CANCELLATION": "CANCEL_SUBSCRIPTION",
        "PLAN_UPGRADE": "REQUEST_PLAN_CHANGE",
        "PLAN_DOWNGRADE": "REQUEST_PLAN_CHANGE",
        "RETURN_REQUEST": "REQUEST_RETURN",
        "EXCHANGE_REQUEST": "REQUEST_EXCHANGE",
        "ORDER_CANCELLATION": "CANCEL_ORDER",
        "PRODUCT_DEFECT": "REPORT_DEFECTIVE_PRODUCT",
        "FEATURE_NOT_WORKING": "FEATURE_INQUIRY",
        "PROFILE_UPDATE": "REQUEST_PROFILE_UPDATE",
        "DATA_PRIVACY_REQUEST": "REQUEST_DATA_DELETION",
        "ESCALATION_REQUEST": "REQUEST_ESCALATION",
        "APPOINTMENT_RESCHEDULE": "CANCEL_BOOKING",
        "APP_CRASH": "REPORT_APP_ISSUE",
        "TRACKING_ISSUE": "REQUEST_TRACKING_UPDATE",
        "INVOICE_REQUEST": "REQUEST_INVOICE",
        "CREDIT_CARD_UPDATE": "REQUEST_PAYMENT_UPDATE",
    }

    @classmethod
    def _extract_customer_intent(
        cls, issues: list[Issue], turns: list[Turn]
    ) -> tuple[Optional[str], Optional[str]]:
        """Extract v2 CUSTOMER_INTENT from issues and customer turns.

        Returns (primary_intent, secondary_intent).
        """
        primary = None
        secondary = None

        if issues:
            primary = cls._ISSUE_TO_INTENT.get(issues[0].type)
            if len(issues) > 1:
                secondary = cls._ISSUE_TO_INTENT.get(issues[1].type)

        # Fallback: try to derive intent from customer text keywords
        if not primary:
            customer_text = " ".join(
                t.text.lower() for t in turns if t.speaker == "customer"
            )
            if any(w in customer_text for w in ["refund", "money back", "reimburse"]):
                primary = "REQUEST_REFUND"
            elif any(w in customer_text for w in ["cancel", "terminate", "stop"]):
                primary = "CANCEL_SUBSCRIPTION"
            elif any(w in customer_text for w in ["unlock", "locked out", "can't log"]):
                primary = "ACCOUNT_UNLOCK"
            elif any(w in customer_text for w in ["how do", "how does", "what is"]):
                primary = "FEATURE_INQUIRY"
            elif any(
                w in customer_text
                for w in ["not working", "broken", "issue", "problem"]
            ):
                primary = "REPORT_ISSUE"

        return primary, secondary

    @staticmethod
    def _extract_context_provided(turns: list[Turn]) -> list[str]:
        """Extract v2 CONTEXT tokens indicating what information the customer provided.

        Returns fact-of-information without leaking PII.
        """
        context = []
        seen = set()

        for turn in turns:
            if turn.speaker != "customer":
                continue
            ents = getattr(turn, "entities", {}) or {}

            if ents.get("emails") and "EMAIL_PROVIDED" not in seen:
                context.append("EMAIL_PROVIDED")
                seen.add("EMAIL_PROVIDED")

            if ents.get("phone_numbers") and "PHONE_PROVIDED" not in seen:
                context.append("PHONE_PROVIDED")
                seen.add("PHONE_PROVIDED")

            if (
                ents.get("account_numbers") or ents.get("accounts")
            ) and "ACCOUNT_ID_PROVIDED" not in seen:
                context.append("ACCOUNT_ID_PROVIDED")
                seen.add("ACCOUNT_ID_PROVIDED")

            if ents.get("order_numbers") and "ORDER_ID_PROVIDED" not in seen:
                context.append("ORDER_ID_PROVIDED")
                seen.add("ORDER_ID_PROVIDED")

            if ents.get("tracking_numbers") and "TRACKING_ID_PROVIDED" not in seen:
                context.append("TRACKING_ID_PROVIDED")
                seen.add("TRACKING_ID_PROVIDED")

            if ents.get("money") and "PAYMENT_AMOUNT_PROVIDED" not in seen:
                context.append("PAYMENT_AMOUNT_PROVIDED")
                seen.add("PAYMENT_AMOUNT_PROVIDED")

            if ents.get("ticket_numbers") and "TICKET_ID_PROVIDED" not in seen:
                context.append("TICKET_ID_PROVIDED")
                seen.add("TICKET_ID_PROVIDED")

            if ents.get("case_numbers") and "CASE_ID_PROVIDED" not in seen:
                context.append("CASE_ID_PROVIDED")
                seen.add("CASE_ID_PROVIDED")

            if ents.get("product_models") and "PRODUCT_ID_PROVIDED" not in seen:
                context.append("PRODUCT_ID_PROVIDED")
                seen.add("PRODUCT_ID_PROVIDED")

        return context

    # System action keyword patterns
    _SYSTEM_ACTION_KEYWORDS = {
        "PAYMENT_RETRY_DETECTED": [
            "payment retry",
            "auto-retry",
            "automatic retry",
            "system retried",
        ],
        "AUTO_ESCALATION_TRIGGERED": [
            "auto-escalated",
            "automatically escalated",
            "system escalated",
        ],
        "SLA_BREACH_DETECTED": [
            "sla breach",
            "sla violation",
            "exceeded sla",
        ],
        "FRAUD_ALERT_TRIGGERED": [
            "fraud alert",
            "fraud detected",
            "suspicious activity",
        ],
        "ACCOUNT_AUTO_LOCKED": [
            "account automatically locked",
            "auto-locked",
            "system locked",
        ],
        "NOTIFICATION_SENT": [
            "notification sent",
            "automated email",
            "system notification",
        ],
    }

    @classmethod
    def _extract_system_actions(cls, turns: list[Turn]) -> list[str]:
        """Extract v2 SYSTEM_ACTIONS from system turns and agent references."""
        actions = []
        seen = set()

        system_text = " ".join(
            t.text.lower()
            for t in turns
            if t.speaker in ("system", "agent")
        )

        for action, keywords in cls._SYSTEM_ACTION_KEYWORDS.items():
            if action not in seen and any(kw in system_text for kw in keywords):
                actions.append(action)
                seen.add(action)

        return actions
