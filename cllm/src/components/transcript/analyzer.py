import re
from typing import Optional
import spacy

from . import (
    CallInfo,
    Issue,
    Action,
    Resolution,
    CustomerProfile,
    TranscriptAnalysis,
    Turn,
)
from .utils.named_entity import EntityExtractor
from .utils.sentiment_analyzer import SentimentAnalyzer
from .utils.temporal_analyzer import TemporalAnalyzer
from .vocabulary import TranscriptVocabulary
from src.components.intent_detector import IntentDetector
from src.components.target_extractor import TargetExtractor
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
        self.entity_extractor = EntityExtractor()

    def analyze(
        self, transcript: str, metadata: Optional[dict] = None
    ) -> TranscriptAnalysis:
        metadata = metadata or {}
        turns = self._parse_turns(transcript)

        docs = list(self.nlp.pipe([t.text for t in turns])) if turns else []
        for turn, doc in zip(turns, docs):
            turn.doc = doc
            turn.intent = self.intent_detector.get_primary_intent(
                self.intent_detector.detect(turn.text)
            )
            turn.targets.append(self.target_extractor.extract(text=turn.text))
            turn.sentiment, _ = self.sentiment_analyzer.analyze_turn(
                turn.text, turn.speaker
            )
            turn.entities = self.entity_extractor.extract(turn.text)

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
        actions: dict = {}

        # We need indices for _determine_action_result; create indexable list
        indexed_turns = list(turns)

        for i, turn in enumerate(indexed_turns):
            if turn.speaker != "agent":
                continue

            action_type = self._detect_action_type(turn.text)
            if not action_type or action_type not in [
                "REFUND",
                "CREDIT",
                "TROUBLESHOOT",
                "ESCALATE",
                "REPLACE",
                "CHARGE",
                "PAYMENT",
            ]:
                continue

            result = self._determine_action_result(indexed_turns, i, turn)
            amount, method, attributes = self._extract_action_details(action_type, turn)

            if action_type in actions:
                existing = actions[action_type]
                if result == "COMPLETED":
                    existing.result = "COMPLETED"
                if attributes:
                    existing.attributes = existing.attributes or {}
                    existing.attributes.update(attributes)
                if amount and not existing.amount:
                    existing.amount = amount
                if method and not existing.payment_method:
                    existing.payment_method = method
            else:
                actions[action_type] = Action(
                    type=action_type,
                    result=result,
                    amount=amount,
                    payment_method=method,
                    attributes=attributes or {},
                )
        return list(actions.values())

    def _detect_action_type(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        best, longest = None, 0
        for action, keywords in self.vocab.ACTION_TOKENS.items():
            for kw in keywords:
                if kw in text_lower and len(kw) > longest:
                    best, longest = action, len(kw)
        return best

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
        """Extracts the resolution details from a list of turns.
        Args:
            turns: A list of turns.
        Returns:
            A Resolution object containing the extracted details.
        Examples:
            >>> _extract_resolution([Turn("agent", "The issue has been resolved.")])
            Resolution(type='RESOLVED', attributes={})
        """
        agent_turns = [t for t in turns if t.speaker == "agent"]
        recent = agent_turns[-5:] if agent_turns else []
        res_type, timeline, next_steps = "UNKNOWN", None, None

        for turn in reversed(recent):
            text = turn.text.lower()
            if self._match_any(
                text, ["submitted", "processed", "completed", "done", "issued", "sent"]
            ):
                res_type = "RESOLVED"
            elif self._match_any(
                text, ["resolved", "fixed", "solved", "approved", "payout"]
            ):
                res_type = "RESOLVED"
            elif self._match_any(text, ["replace", "replacement", "exchange"]):
                res_type, next_steps = "PENDING", "REPLACEMENT"
            elif self._match_any(text, ["escalate", "supervisor", "transfer"]):
                res_type = "ESCALATED"

            if res_type != "UNKNOWN":
                timeline = self._extract_timeline(text)
                break

        return Resolution(type=res_type, timeline=timeline, next_steps=next_steps)

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
        """
        Priority:
        1. Check current turn for completion keywords
        2. Check immediate following turns for confirmations
        3. Default to PENDING
        """
        text_lower = action_turn.text.lower()

        completion_keywords = [
            "submitted",
            "processed",
            "completed",
            "filed",
            "applied",
            "issued",
            "sent",
            "done",
            "just submitted",
            "just processed",
            "already submitted",
            "already processed",
        ]
        if any(k in text_lower for k in completion_keywords):
            return "COMPLETED"

        action_now_patterns = [
            r"(i('|’)ve|i have) (just )?(submitted|processed|filed)\b",
            r"i('?m| am) (processing|submitting|filing) (it|the|that)? (now)?\b",
        ]
        for pat in action_now_patterns:
            if re.search(pat, text_lower):
                return "COMPLETED"

        following_turns = turns[action_index + 1 : action_index + 3]
        for t in following_turns:
            tl = t.text.lower()
            if t.speaker == "customer" and any(
                word in tl
                for word in [
                    "perfect",
                    "great",
                    "thank",
                    "got it",
                    "received",
                    "appreciate",
                ]
            ):
                return "COMPLETED"
            if t.speaker == "agent" and any(
                word in tl
                for word in ["all set", "you're all set", "that's done", "completed"]
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

    def _extract_reference_number(self, turn: Turn) -> Optional[str]:
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

    @staticmethod
    def _get_issue_type(text: str) -> Optional[str]:
        if any(x in text for x in ["bill", "charge", "refund"]):
            return "BILLING_DISPUTE"
        if any(x in text for x in ["internet", "connection", "wifi"]):
            return "CONNECTIVITY"
        if any(x in text for x in ["slow", "speed"]):
            return "PERFORMANCE"
        return None

    @staticmethod
    def _detect_severity(text: str) -> str:
        text = text.lower()
        if any(
            x in text
            for x in [
                "critical",
                "urgent",
                "emergency",
                "not working at all",
                "can't work",
            ]
        ):
            return "HIGH"
        if any(
            x in text
            for x in ["frustrated", "annoying", "need it for work", "important"]
        ):
            return "MEDIUM"
        return "LOW"

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

    @staticmethod
    def _detect_billing_cause(turns: list[Turn]) -> tuple[Optional[str], Optional[str]]:
        """Detect the cause of a billing issue.

        Args:
            turns: List of turns in the conversation.

        Returns:
            A tuple containing the cause of the billing issue and the plan change.

        Examples:
            >>> _detect_billing_cause([Turn("agent", "What amount do you think is wrong?"), Turn("customer", "I think it's $100")])
            ('DUPLICATE_PROCESSING', None)
        """
        cause, plan_change = None, None
        for t in (t for t in turns if t.speaker == "agent"):
            text = t.text.lower()
            if any(x in text for x in ["duplicate", "processed twice", "retried"]):
                cause = "DUPLICATE_PROCESSING"
            elif "upgrade" in text:
                cause = "MID_CYCLE_UPGRADE"
                if match := re.search(r"from (\w+) to (\w+)", text):
                    plan_change = f"{match.group(1).upper()}→{match.group(2).upper()}"
            elif "downgrade" in text:
                cause = "MID_CYCLE_DOWNGRADE"
            elif "double" in text and "billing" in text:
                cause = "DOUBLE_BILLING"
            elif "overlap" in text:
                cause = "BILLING_OVERLAP"
            elif any(x in text for x in ["error", "mistake"]):
                cause = "SYSTEM_ERROR"
            elif any(x in text for x in ["proration", "prorated"]):
                cause = "PRORATION_CONFUSION"
        return cause, plan_change

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
