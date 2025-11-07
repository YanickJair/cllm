import re
from typing import Optional, List, Tuple

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
from src.components.sys_prompt.analyzers import IntentDetector
from .utils.named_entity import EntityExtractor
from .utils.sentiment_analyzer import SentimentAnalyzer
from .utils.temporal_analyzer import TemporalAnalyzer
from .vocabulary import TranscriptVocabulary
from src.components.sys_prompt.analyzers import TargetExtractor


class TranscriptAnalyzer:
    """
    Analyzes transcripts using existing CLLM components

    Philosophy: Reuse IntentDetector, TargetExtractor
    Add transcript-specific logic on top
    """

    def __init__(self, nlp: spacy.Language):
        self.nlp = nlp
        self.vocab = TranscriptVocabulary()

        self.intent_detector = IntentDetector(nlp)
        self.target_extractor = TargetExtractor(nlp)
        self.temporal_extractor = TemporalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.entity_extractor = EntityExtractor(nlp)

    def analyze(
        self, transcript: str, metadata: Optional[dict] = None
    ) -> TranscriptAnalysis:
        """Run full transcript analysis pipeline"""
        metadata = metadata or {}

        turns = self._parse_turns(transcript)

        for turn in turns:
            turn.intent = self.intent_detector.get_primary_intent(
                self.intent_detector.detect(turn.text)
            )
            turn.targets = self.target_extractor.extract(turn.text)
            turn.sentiment, _ = self.sentiment_analyzer.analyze_turn(
                turn.text, turn.speaker
            )
            turn.entities = self.entity_extractor.extract(turn.text)

        # Higher-level inferences
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
    def _parse_turns(transcript: str) -> List[Turn]:
        """Split transcript into speaker turns"""
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

    def _mock_get_action_type(self, text: str) -> Optional[str]:
        """Detect probable action type from agent text"""
        text_lower = text.lower()
        best_match = None
        longest_kw = 0
        for action, keywords in self.vocab.ACTION_TOKENS.items():
            for kw in keywords:
                if kw in text_lower and len(kw) > longest_kw:
                    best_match = action
                    longest_kw = len(kw)
        return best_match

    def _extract_actions(self, turns: List[Turn]) -> List[Action]:
        """Enhanced multi-action extraction with deduplication and merging"""
        actions_dict = {}  # Deduplicate by type

        for i, turn in enumerate(turns):
            if turn.speaker != "agent":
                continue

            # Get action type from your vocabulary
            action_type = self._mock_get_action_type(turn.text)

            if not action_type:
                continue

            # Filter: only keep essential actions
            if action_type not in [
                "REFUND",
                "CREDIT",
                "TROUBLESHOOT",
                "ESCALATE",
                "REPLACE",
            ]:
                continue

            # Determine result status for THIS turn
            result = self._determine_action_result(turns, i, turn)

            # Extract information from THIS turn
            attributes_new = {}
            amount_new = None
            payment_method_new = None

            # Only extract financial details for money-related actions
            if action_type in ["REFUND", "CREDIT", "CHARGE", "PAYMENT"]:
                amount_new, payment_method_new = self._extract_financial_details(turn)

                # Extract reference number
                reference = self._extract_reference_number(turn)
                if reference:
                    attributes_new["reference"] = reference

                # Extract timeline
                timeline = self._extract_timeline(turn.text)
                if timeline:
                    attributes_new["timeline"] = timeline

            # SMART MERGE: If action already exists, merge information
            if action_type in actions_dict:
                existing = actions_dict[action_type]

                # Keep COMPLETED status if found (upgrade from PENDING)
                if result == "COMPLETED":
                    existing.result = "COMPLETED"

                # Merge attributes (keeps both reference and timeline)
                if attributes_new:
                    if not existing.attributes:
                        existing.attributes = {}
                    existing.attributes.update(attributes_new)

                # Update amount/method if found
                if amount_new and not existing.amount:
                    existing.amount = amount_new
                if payment_method_new and not existing.payment_method:
                    existing.payment_method = payment_method_new

            else:
                # Create new action
                action = Action(
                    type=action_type,
                    result=result,
                    amount=amount_new,
                    payment_method=payment_method_new,
                    attributes=attributes_new if attributes_new else {},
                )

                actions_dict[action_type] = action

        return list(actions_dict.values())

    def _extract_resolution(self, turns: List) -> Resolution:
        """
        Enhanced resolution extraction with better pattern matching

        Priority:
        1. Explicit completion (submitted, processed, completed)
        2. Resolution keywords (resolved, fixed)
        3. Approved/payout keywords
        4. Pending indicators (scheduled, tomorrow)
        """
        agent_turns = [t for t in turns if t.speaker == "agent"]
        last_agent_turns = agent_turns[-5:]  # Check last 5 turns

        resolution_type = "UNKNOWN"
        timeline = None
        next_steps = None

        for turn in reversed(last_agent_turns):
            text_lower = turn.text.lower()

            # Pattern 1: Explicit completion - HIGHEST PRIORITY
            completion_keywords = [
                "submitted",
                "processed",
                "completed",
                "done",
                "applied",
                "issued",
                "sent",
                "filed",
                "i've submitted",
            ]
            if any(word in text_lower for word in completion_keywords):
                resolution_type = "RESOLVED"
                timeline = self._extract_timeline(text_lower)
                break

            # Pattern 2: Explicit resolution
            if any(word in text_lower for word in ["resolved", "fixed", "solved"]):
                resolution_type = "RESOLVED"
                timeline = self._extract_timeline(text_lower)
                break

            # Pattern 3: Approved/Payout
            if any(word in text_lower for word in ["approved", "payout"]):
                resolution_type = "RESOLVED"
                timeline = self._extract_timeline(text_lower)
                break

            # Pattern 4: Replacement/Exchange scheduled
            if any(
                word in text_lower for word in ["replace", "replacement", "exchange"]
            ):
                resolution_type = "PENDING"
                timeline = self._extract_timeline(text_lower)
                next_steps = "REPLACEMENT"
                break

            # Pattern 5: Escalated/Transferred
            if any(
                word in text_lower for word in ["escalate", "transfer", "supervisor"]
            ):
                resolution_type = "ESCALATED"
                break

        return Resolution(
            type=resolution_type, timeline=timeline, next_steps=next_steps
        )

    @staticmethod
    def _extract_timeline(text: str) -> Optional[str]:
        """Improved timeline extraction"""
        if "tomorrow" in text:
            return "TOMORROW"
        if "today" in text:
            return "TODAY"
        if match := re.search(r"within (\d+)(?:-(\d+))?\s*(hour|day)", text):
            if match.group(2):
                return f"{match.group(1)}-{match.group(2)}d"
            return f"{match.group(1)}{'h' if 'hour' in match.group(3) else 'd'}"
        if match := re.search(r"(\d+)\s*[-–]\s*(\d+)\s*(?:business )?days?", text):
            return f"{match.group(1)}-{match.group(2)}d"
        if match := re.search(r"(\d+)\s*(?:business )?days?", text):
            return f"{match.group(1)}d"
        return None

    @staticmethod
    def _extract_reference_number(turn: Turn) -> Optional[str]:
        """Extract reference/confirmation numbers"""
        text = turn.text
        if match := re.search(r"\b([A-Z]{2,4})-(\d{4,})\b", text):
            return f"{match.group(1)}-{match.group(2)}"
        if match := re.search(
            r"(reference|confirmation) (?:number )?(is|#)? ?([A-Z0-9-]+)",
            text,
            re.IGNORECASE,
        ):
            return match.group(3)
        return None

    @staticmethod
    def _extract_financial_details(turn: Turn) -> tuple[Optional[str], Optional[str]]:
        """Extract amount and payment method from entities and text"""
        amount = (turn.entities.get("money", []) or [None])[0]
        text_lower = turn.text.lower()
        if "paypal" in text_lower:
            method = "PAYPAL"
        elif "check" in text_lower:
            method = "CHECK"
        elif "credit card" in text_lower:
            method = "CARD_CREDIT"
        elif "account" in text_lower and "credit" in text_lower:
            method = "ACCOUNT_CREDIT"
        else:
            method = "CARD_CREDIT"
        return amount, method

    def _extract_call_info(self, turns: list[Turn], metadata: dict) -> CallInfo:
        """Extract call metadata more compactly"""
        agent_name = metadata.get("agent")
        call_type = "SUPPORT"
        full_text = " ".join([t.text for t in turns]).lower()
        if any(
            word in full_text
            for word in [
                "upgrade",
                "upgrading",
                "plan",
                "pricing",
                "purchase",
                "buy",
                "considering",
                "interested in",
            ]
        ):
            call_type = "SALES"

        if not agent_name:
            # Check first 3 agent turns for NER-based name extraction
            for turn in (t for t in turns[:3] if t.speaker == "agent"):
                for ent in self.nlp(turn.text).ents:
                    if ent.label_ == "PERSON":
                        agent_name = ent.text
                        break
                if agent_name:
                    break

            # Fallback: regex patterns
            if not agent_name:
                patterns = [
                    r"my name is (\w+)",
                    r"i'?m (\w+)",
                    r"this is (\w+)",
                    r"(\w+) from",
                    r"(\w+) here",
                ]
                agent_name = next(
                    (
                        match.group(1).title()
                        for turn in turns[:3]
                        if turn.speaker == "agent"
                        for pattern in patterns
                        if (match := re.search(pattern, turn.text.lower()))
                    ),
                    None,
                )

        return CallInfo(
            call_id=metadata.get("call_id", "unknown"),
            type=call_type,
            channel=metadata.get("channel", "VOICE"),
            duration=len(turns),
            agent=agent_name,
        )

    def _extract_customer_profile(self, turns: list[Turn]) -> CustomerProfile:
        """Extract customer profile from turns in a cleaner, Pythonic way"""
        profile = CustomerProfile()

        # Extract customer name
        customer_name = self._extract_customer_name(turns)
        if customer_name:
            profile.name = customer_name

        # Extract other details from entities
        for turn in turns:
            if hasattr(turn, "entities") and turn.entities:
                # Email
                emails = turn.entities.get("emails", [])
                if emails:
                    if not profile.attributes:
                        profile.attributes = {}
                    profile.attributes["email"] = emails[0]

                # Account
                accounts = turn.entities.get("accounts", [])
                if accounts and not profile.account:
                    profile.account = accounts[0]

                # Tier from plan mentions
                plans = turn.entities.get("plans", [])
                if plans and not profile.tier:
                    plan = plans[0].lower()
                    if "premium" in plan:
                        profile.tier = "PREMIUM"
                    elif "enterprise" in plan:
                        profile.tier = "ENTERPRISE"
                    elif "basic" in plan:
                        profile.tier = "BASIC"
                    else:
                        profile.tier = "STANDARD"

        return profile

    def _extract_customer_name(self, turns: List) -> Optional[str]:
        """
        Extract customer name from agent addressing them

        Patterns:
        - "Thanks, NAME"
        - "Thank you, NAME"
        - Extract from email (name.something@)
        """
        for turn in turns:
            if turn.speaker == "agent":
                text = turn.text

                # Pattern 1: "Thanks, NAME" or "Thank you, NAME"
                match = re.search(r"[Tt]hank[s]?,\s+([A-Z][a-z]+)", text)
                if match:
                    name = match.group(1)
                    # Filter common false positives
                    if name.lower() not in ["you", "for", "the", "so", "very"]:
                        return name

                # Pattern 2: Extract from email (melissa.jordan@ → Melissa)
                match = re.search(r"([a-z]+)\.[a-z]+@", text.lower())
                if match:
                    return match.group(1).title()

        return None

    def _extract_issues(self, turns: list[Turn]) -> list[Issue]:
        """Extract issues with payment context separation"""
        issues = []

        # Combine all customer text
        customer_text = " ".join(
            [turn.text for turn in turns if turn.speaker == "customer"]
        )

        # Get issue type from your vocabulary
        issue_type = self._get_issue_type(customer_text)

        if issue_type:
            # Detect severity
            severity = self._detect_severity(customer_text)

            # For billing issues, detect cause
            cause = None
            plan_change = None
            disputed_amounts = []

            if issue_type in ["BILLING_DISPUTE", "UNEXPECTED_CHARGE", "REFUND_REQUEST"]:
                cause, plan_change = self._detect_billing_cause(turns)
                disputed_amounts = self._extract_disputed_amounts(turns)

            # Extract temporal pattern (but don't include if empty)
            temporal_days = self._extract_temporal_days(customer_text)

            issue = Issue(
                type=issue_type,
                severity=severity,
                cause=cause,
                plan_change=plan_change,
                disputed_amounts=disputed_amounts,
                attributes={},
            )

            # Only add DAYS if actually present
            if temporal_days and len(temporal_days) > 0:
                issue.attributes["days"] = temporal_days

            issues.append(issue)

        return issues

    def _get_issue_type(self, text: str) -> Optional[str]:
        """Get issue type - replace with your vocab.get_issue_token()"""
        text_lower = text.lower()

        if "bill" in text_lower or "charge" in text_lower or "refund" in text_lower:
            return "BILLING_DISPUTE"
        elif (
            "internet" in text_lower
            or "connection" in text_lower
            or "wifi" in text_lower
        ):
            return "CONNECTIVITY"
        elif "slow" in text_lower or "speed" in text_lower:
            return "PERFORMANCE"

        return None

    def _extract_temporal_days(self, text: str) -> List[str]:
        """Extract days from text"""
        days = []
        day_patterns = {
            "monday": "MON",
            "tuesday": "TUE",
            "wednesday": "WED",
            "thursday": "THU",
            "friday": "FRI",
            "saturday": "SAT",
            "sunday": "SUN",
        }

        text_lower = text.lower()
        for day_name, day_abbr in day_patterns.items():
            if day_name in text_lower:
                days.append(day_abbr)

        return days

    @staticmethod
    def _detect_severity(text: str) -> str:
        """Detect issue severity from text"""
        text_lower = text.lower()

        # High severity indicators
        high_severity = [
            "critical",
            "urgent",
            "emergency",
            "completely down",
            "not working at all",
            "can't work",
            "losing money",
        ]
        if any(indicator in text_lower for indicator in high_severity):
            return "HIGH"

        # Medium severity indicators
        medium_severity = [
            "frustrated",
            "frustrating",
            "annoying",
            "work from home",
            "need it for work",
            "important",
        ]
        if any(indicator in text_lower for indicator in medium_severity):
            return "MEDIUM"

        return "LOW"

    @staticmethod
    def _extract_disputed_amounts(turns: List[Turn]) -> List[str]:
        """
        Extract disputed amounts ONLY from customer turns mentioning the problem

        Returns list like: ["$14.99", "$16.99"]
        """
        disputed_amounts = []

        for turn in turns:
            if turn.speaker == "customer":
                text_lower = turn.text.lower()

                # Check if customer is mentioning charges/billing
                problem_keywords = [
                    "charged",
                    "charge",
                    "bill",
                    "statement",
                    "saw",
                    "shows",
                    "billed",
                    "payment",
                ]

                if any(keyword in text_lower for keyword in problem_keywords):
                    # Extract money from this turn
                    money_amounts = turn.entities.get("money", [])
                    disputed_amounts.extend(money_amounts)

        # Deduplicate while preserving order
        seen = set()
        unique_amounts = []
        for amount in disputed_amounts:
            if amount not in seen:
                seen.add(amount)
                unique_amounts.append(amount)

        return unique_amounts

    @staticmethod
    def _detect_billing_cause(turns: List[Turn]) -> Tuple[Optional[str], Optional[str]]:
        """
        Detect root cause and plan change from agent explanation

        Returns: (cause, plan_change)
        """
        cause = None
        plan_change = None

        for turn in turns:
            if turn.speaker == "agent":
                text_lower = turn.text.lower()

                # Enhanced pattern matching
                if (
                    "duplicate" in text_lower
                    or "retried" in text_lower
                    or "processed twice" in text_lower
                ):
                    cause = "DUPLICATE_PROCESSING"

                elif "upgrade" in text_lower or "upgraded" in text_lower:
                    cause = "MID_CYCLE_UPGRADE"

                    # Extract plan names
                    plan_patterns = [
                        r"from (\w+) to (\w+)",
                        r"(\w+) to (\w+) plan",
                        r"(\w+) plan.*(\w+) plan",
                    ]

                    for pattern in plan_patterns:
                        match = re.search(pattern, text_lower, re.IGNORECASE)
                        if match:
                            old_plan = match.group(1).upper()
                            new_plan = match.group(2).upper()
                            plan_change = f"{old_plan}→{new_plan}"
                            break

                elif "downgrade" in text_lower or "downgraded" in text_lower:
                    cause = "MID_CYCLE_DOWNGRADE"

                elif "double" in text_lower and "billing" in text_lower:
                    cause = "DOUBLE_BILLING"

                elif "overlap" in text_lower:
                    cause = "BILLING_OVERLAP"

                elif "error" in text_lower or "mistake" in text_lower:
                    cause = "SYSTEM_ERROR"

                elif "proration" in text_lower or "prorated" in text_lower:
                    cause = "PRORATION_CONFUSION"

        return cause, plan_change

    @staticmethod
    def _determine_action_result(
        turns: list[Turn], action_index: int, action_turn: Turn
    ) -> str:
        """
        Enhanced action result detection

        Priority:
        1. Check current turn for completion keywords
        2. Check following turns for confirmation
        3. Default to PENDING
        """
        text_lower = action_turn.text.lower()

        # HIGH PRIORITY: Explicit completion in current turn
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
            "just filed",
            "already submitted",
            "already processed",
        ]

        if any(keyword in text_lower for keyword in completion_keywords):
            return "COMPLETED"

        # Check if action verb + "now" or "right now"
        action_now_patterns = [
            r"I\'?(?:ve|ll)\s+\w+\s+(?:the\s+)?\w+\s+now",  # "I've submitted the refund now"
            r"I\'?m\s+\w+ing\s+\w+\s+now",  # "I'm processing it now"
        ]

        for pattern in action_now_patterns:
            if re.search(pattern, text_lower):
                return "COMPLETED"

        # Check following turns for confirmation
        following_turns = turns[action_index + 1 : min(action_index + 3, len(turns))]

        for turn in following_turns:
            turn_text_lower = turn.text.lower()

            # Customer confirmation
            if turn.speaker == "customer" and any(
                word in turn_text_lower
                for word in [
                    "perfect",
                    "great",
                    "thank",
                    "appreciate",
                    "received",
                    "got it",
                ]
            ):
                return "COMPLETED"

            # Agent follow-up confirmation
            if turn.speaker == "agent" and any(
                word in turn_text_lower
                for word in ["all set", "you're all set", "that's done", "completed"]
            ):
                return "COMPLETED"

        return "PENDING"
