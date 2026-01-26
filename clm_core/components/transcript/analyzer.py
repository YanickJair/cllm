import re
from typing import Optional
import spacy

from clm_core.dictionary.en.patterns import (
    SUPPORTED_ACTION_TYPES,
    ACTION_COMPLETION_KEYWORDS,
    ACTION_NOW_PATTERNS,
    ACTION_COMPLETION_PHRASES,
    POSITIVE_CUSTOMER_CONFIRMATIONS,
    AGENT_CONFIRMATION_PHRASES,
    RESOLUTION_KEYWORDS,
    ISSUE_TYPE_KEYWORDS,
    SEVERITY_KEYWORDS,
    BILLING_CAUSE_KEYWORDS, ISSUE_CONFIRMATION_MAP, ACTION_EVENT_MAP, EXPLICIT_ONLY_ACTIONS, EXPLICIT_ACTION_PHRASES,
    TECHNICAL_ISSUE_MAP, TROUBLESHOOTING_ACTIONS,
)
from . import (
    CallInfo,
    Issue,
    Action,
    Resolution,
    CustomerProfile,
    TranscriptAnalysis,
    Turn,
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
    ):
        self.nlp = nlp
        self.vocab = TranscriptVocabulary()
        self.intent_detector = IntentDetector(nlp=nlp, vocab=vocab)
        self.target_extractor = TargetExtractor(nlp, vocab=vocab, rules=rules)
        self.temporal_extractor = TemporalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.entity_extractor = EntityExtractor(nlp=nlp)

        # Pre-build reverse keyword indices for O(1) lookups
        self._issue_type_index = self._build_keyword_index(ISSUE_TYPE_KEYWORDS)
        self._severity_index = self._build_keyword_index(SEVERITY_KEYWORDS)
        self._resolution_index = self._build_keyword_index(RESOLUTION_KEYWORDS)
        self._billing_cause_index = self._build_keyword_index(BILLING_CAUSE_KEYWORDS)
        self._technical_issue_index = self._build_keyword_index(TECHNICAL_ISSUE_MAP)
        self._issue_confirmation_index = self._build_keyword_index(ISSUE_CONFIRMATION_MAP)
        self._troubleshooting_index = self._build_keyword_index(TROUBLESHOOTING_ACTIONS)
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
        # Sort by keyword length descending for greedy matching
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
        """
        pairs = []
        for raw_action, keywords in self.vocab.ACTION_TOKENS.items():
            if raw_action not in ACTION_EVENT_MAP:
                continue
            action_event = ACTION_EVENT_MAP[raw_action]
            is_explicit = action_event in EXPLICIT_ONLY_ACTIONS
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

        return TranscriptAnalysis(
            call_info=call_info,
            customer=customer,
            turns=turns,
            issues=issues,
            actions=actions,
            resolution=resolution,
            sentiment_trajectory=sentiment_trajectory,
        )

    @staticmethod
    def _parse_turns(transcript: str) -> list[Turn]:
        turns = []
        for line in transcript.strip().split("\n"):
            if not line or ":" not in line:
                continue
            speaker, text = line.split(":", 1)
            speaker = speaker.strip().lower()
            if "agent" in speaker:
                speaker = "agent"
            elif "customer" in speaker or "caller" in speaker:
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
                    actions[action_type] = Action(
                        type=action_type,
                        attributes={}
                    )

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
                phrases = EXPLICIT_ACTION_PHRASES.get(action_event, set())
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
                return Resolution(type=res_type, timeline=timeline, next_steps=next_steps)

        return Resolution(type="UNKNOWN", timeline=None, next_steps=None)

    @staticmethod
    def _match_any(text: str, keywords: list[str]) -> bool:
        return any(kw in text for kw in keywords)

    def _extract_timeline(self, text: str) -> Optional[str]:
        pattern = self.temporal_extractor.extract(text)
        if pattern and getattr(pattern, "duration", None):
            return str(pattern.duration).upper()
        if "tomorrow" in text.lower():
            return "TOMORROW"
        if "today" in text.lower():
            return "TODAY"
        if match := re.search(r"within\s+(\d+)\s*(hour|hours)", text, re.I):
            return f"{match.group(1)}h"
        if match := re.search(r"within\s+(\d+)\s*(day|days)", text, re.I):
            return f"{match.group(1)}d"
        return None

    @staticmethod
    def _determine_action_result(
        turns: list[Turn], action_index: int, action_turn: Turn
    ) -> str:
        text_lower = action_turn.text.lower()

        if any(
            k in text_lower
            for k in ACTION_COMPLETION_KEYWORDS | ACTION_COMPLETION_PHRASES
        ):
            return "COMPLETED"

        for pattern in ACTION_NOW_PATTERNS:
            if re.search(pattern, text_lower):
                return "COMPLETED"

        for t in turns[action_index + 1 : action_index + 3]:
            tl = t.text.lower()
            if t.speaker == "customer" and any(
                k in tl for k in POSITIVE_CUSTOMER_CONFIRMATIONS
            ):
                return "COMPLETED"
            if t.speaker == "agent" and any(
                k in tl for k in AGENT_CONFIRMATION_PHRASES
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

    @staticmethod
    def _extract_disputed_amounts(turns: list[Turn]) -> list[str]:
        """Extract disputed amounts from customer turns.

        Args:
            turns: List of turns.

        Returns:
            List of disputed amounts.
        Examples:
            >>> _extract_disputed_amounts([Turn("customer", "I think my bill is wrong"), Turn("agent", "What amount do you think is wrong?"), Turn("customer", "I think it's $100")])
            ['$100']
        """
        amounts = []
        for t in (t for t in turns if t.speaker == "customer"):
            if any(
                k in t.text.lower() for k in ["charge", "bill", "statement", "payment"]
            ):
                amounts.extend(getattr(t, "entities", {}).get("money", []))
        return list(dict.fromkeys(amounts))

    def _detect_billing_cause(self, turns: list[Turn]) -> tuple[Optional[str], Optional[str]]:
        for t in (t for t in turns if t.speaker == "agent"):
            text = t.text.lower()
            cause = self._lookup_category(text, self._billing_cause_index)
            if cause:
                plan_change = None
                if cause in {"MID_CYCLE_UPGRADE", "MID_CYCLE_DOWNGRADE"}:
                    if match := re.search(r"from (\w+) to (\w+)", text):
                        plan_change = f"{match.group(1).upper()}→{match.group(2).upper()}"
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

    @staticmethod
    def _detect_agent_name(turns: list[Turn]) -> Optional[str]:
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
                        return ent.text
            if match := re.search(
                r"(?:my name is|i'?m|this is)\s+([A-Z][a-z]+)", t.text, re.I
            ):
                return match.group(1)
        return None
