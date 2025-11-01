import re
from collections import defaultdict
from typing import Optional, List, Tuple

import spacy
from . import (
    CallInfo, Issue, Action, Resolution,
    CustomerProfile, TranscriptAnalysis, Turn
)
from ...analyzers.intent_detector import IntentDetector
from .utils.named_entity import EntityExtractor
from .utils.sentiment_analyzer import SentimentAnalyzer
from .utils.temporal_analyzer import TemporalAnalyzer
from .vocabulary import TranscriptVocabulary
from ...analyzers.target import TargetExtractor


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

    def analyze(self, transcript: str, metadata: Optional[dict] = None) -> TranscriptAnalysis:
        """Run full transcript analysis pipeline"""
        metadata = metadata or {}

        turns = self._parse_turns(transcript)

        for turn in turns:
            turn.intent = self.intent_detector.get_primary_intent(
                self.intent_detector.detect(turn.text)
            )
            turn.targets = self.target_extractor.extract(turn.text)
            turn.sentiment, _ = self.sentiment_analyzer.analyze_turn(turn.text, turn.speaker)
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
            sentiment_trajectory=sentiment_trajectory
        )

    @staticmethod
    def _parse_turns(transcript: str) -> List[Turn]:
        """Split transcript into speaker turns"""
        turns = []
        for line in transcript.strip().split('\n'):
            if not line or ':' not in line:
                continue
            speaker, text = line.split(':', 1)
            speaker = speaker.strip().lower()
            if 'agent' in speaker:
                speaker = 'agent'
            elif 'customer' in speaker or 'caller' in speaker:
                speaker = 'customer'
            else:
                speaker = 'system'
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
        actions_dict: dict = {}
        for i, turn in enumerate(turns):
            if turn.speaker != 'agent':
                continue

            detected_actions = []
            text_lower = turn.text.lower()

            # NEW: Detect multiple possible actions in a single line
            for action_type, keywords in self.vocab.ACTION_TOKENS.items():
                if any(kw in text_lower for kw in keywords):
                    detected_actions.append(action_type)

            for action_type in detected_actions:
                result = self._determine_action_result(turns, i, turn)
                if action_type in ['REFUND', 'CREDIT', 'CHARGE', 'PAYMENT']:
                    amount, payment_method = self._extract_financial_details(turn)
                else:
                    amount = None
                    payment_method = None
                ref = self._extract_reference_number(turn)
                timeline = self._extract_timeline(turn.text.lower())

                attrs = {}
                if ref:
                    attrs['reference'] = ref
                if timeline:
                    attrs['timeline'] = timeline

                # Merge logic
                if action_type in actions_dict:
                    existing = actions_dict[action_type]
                    if result == 'COMPLETED':
                        existing.result = 'COMPLETED'
                    existing.attributes.update(attrs)
                else:
                    actions_dict[action_type] = Action(
                        type=action_type,
                        result=result,
                        amount=amount,
                        payment_method=payment_method,
                        attributes=attrs
                    )

        return list(actions_dict.values())

    def _extract_resolution(self, turns: List[Turn]) -> Resolution:
        """Resolution extraction with tiered keyword mapping"""
        for turn in reversed(turns[-6:]):
            if turn.speaker != 'agent':
                continue
            text = turn.text.lower()
            for res_type, keywords in self.vocab.RESOLUTION_TOKENS.items():
                if any(kw in text for kw in keywords):
                    timeline = self._extract_timeline(text)
                    return Resolution(type=res_type, timeline=timeline)
        return Resolution(type='UNKNOWN')

    @staticmethod
    def _extract_timeline(text: str) -> Optional[str]:
        """Improved timeline extraction"""
        if 'tomorrow' in text:
            return 'TOMORROW'
        if 'today' in text:
            return 'TODAY'
        if match := re.search(r'within (\d+)(?:-(\d+))?\s*(hour|day)', text):
            if match.group(2):
                return f"{match.group(1)}-{match.group(2)}d"
            return f"{match.group(1)}{'h' if 'hour' in match.group(3) else 'd'}"
        if match := re.search(r'(\d+)\s*[-–]\s*(\d+)\s*(?:business )?days?', text):
            return f"{match.group(1)}-{match.group(2)}d"
        if match := re.search(r'(\d+)\s*(?:business )?days?', text):
            return f"{match.group(1)}d"
        return None

    @staticmethod
    def _extract_reference_number(turn: Turn) -> Optional[str]:
        """Extract reference/confirmation numbers"""
        text = turn.text
        if match := re.search(r'\b([A-Z]{2,4})-(\d{4,})\b', text):
            return f"{match.group(1)}-{match.group(2)}"
        if match := re.search(r'(reference|confirmation) (?:number )?(is|#)? ?([A-Z0-9-]+)', text, re.IGNORECASE):
            return match.group(3)
        return None

    @staticmethod
    def _extract_financial_details(turn: Turn) -> tuple[Optional[str], Optional[str]]:
        """Extract amount and payment method from entities and text"""
        amount = (turn.entities.get('money', []) or [None])[0]
        text_lower = turn.text.lower()
        if 'paypal' in text_lower:
            method = 'PAYPAL'
        elif 'check' in text_lower:
            method = 'CHECK'
        elif 'credit card' in text_lower:
            method = 'CARD_CREDIT'
        elif 'account' in text_lower and 'credit' in text_lower:
            method = 'ACCOUNT_CREDIT'
        else:
            method = 'CARD_CREDIT'
        return amount, method

    def _extract_call_info(self, turns: list[Turn], metadata: dict) -> CallInfo:
        """Extract call metadata more compactly"""
        agent_name = metadata.get('agent')
        call_type = 'SUPPORT'
        full_text = ' '.join([t.text for t in turns]).lower()
        if any(word in full_text for word in [
            'upgrade', 'upgrading', 'plan', 'pricing', 'purchase',
            'buy', 'considering', 'interested in'
        ]):
            call_type = 'SALES'

        if not agent_name:
            # Check first 3 agent turns for NER-based name extraction
            for turn in (t for t in turns[:3] if t.speaker == 'agent'):
                for ent in self.nlp(turn.text).ents:
                    if ent.label_ == "PERSON":
                        agent_name = ent.text
                        break
                if agent_name:
                    break

            # Fallback: regex patterns
            if not agent_name:
                patterns = [
                    r'my name is (\w+)',
                    r"i'?m (\w+)",
                    r'this is (\w+)',
                    r'(\w+) from',
                    r'(\w+) here',
                ]
                agent_name = next(
                    (
                        match.group(1).title()
                        for turn in turns[:3]
                        if turn.speaker == 'agent'
                        for pattern in patterns
                        if (match := re.search(pattern, turn.text.lower()))
                    ),
                    None,
                )

        return CallInfo(
            call_id=metadata.get('call_id', 'unknown'),
            type=call_type,
            channel=metadata.get('channel', 'VOICE'),
            duration=len(turns),
            agent=agent_name,
        )

    @staticmethod
    def _extract_customer_profile(turns: list[Turn]) -> CustomerProfile:
        """Extract customer profile from turns in a cleaner, Pythonic way"""
        all_entities = defaultdict(list)
        for turn in turns:
            if turn.entities:
                for key, values in turn.entities.items():
                    all_entities[key].extend(values)

        # Extract customer name
        customer_name = next(
            (
                match.group(1)
                for turn in (t for t in turns if t.speaker == 'agent')
                for pattern in [
                r'\b(?:Thanks?|Thank you),\s+([A-Z][a-z]+)',
                r'\bcalling us,\s+([A-Z][a-z]+)',
                r'^([A-Z][a-z]+),\s+(?:let me|I can|give me)',
            ]
                if (match := re.search(pattern, turn.text))
            ),
            None,
        )

        # Build profile with defaults
        profile = CustomerProfile(
            name=customer_name,
            email=next(iter(all_entities.get('emails', [])), None),
            account=next(iter(all_entities.get('accounts', [])), None),
        )

        # Determine tier
        if plans := all_entities.get('plans'):
            plan = plans[0].lower()
            profile.tier = (
                'PREMIUM' if 'premium' in plan else
                'ENTERPRISE' if 'enterprise' in plan else
                'BASIC' if 'basic' in plan else
                'STANDARD'
            )

        # Address handling
        if addresses := all_entities.get('addresses'):
            profile.attributes = {'address': addresses[0]}

        return profile

    def _extract_issues(self, turns: list[Turn]) -> list[Issue]:
        """Extract issues with payment context separation"""
        customer_text = ' '.join(
            t.text for t in turns if t.speaker == 'customer'
        )

        issue_type = self.vocab.get_issue_token(customer_text)
        if not issue_type:
            return []

        temporal = self.temporal_extractor.extract(customer_text)
        severity = self._detect_severity(customer_text)

        disputed_amounts, cause, plan_change = [], None, None
        if issue_type in {'BILLING_DISPUTE', 'UNEXPECTED_CHARGE', 'REFUND_REQUEST', 'OVERCHARGE'}:
            disputed_amounts = self._extract_disputed_amounts(turns)
            cause, plan_change = self._detect_billing_cause(turns)

        return [
            Issue(
                type=issue_type,
                severity=severity,
                disputed_amounts=disputed_amounts,
                cause=cause,
                plan_change=plan_change,
                frequency=temporal.frequency,
                duration=temporal.duration,
                pattern=temporal.pattern,
                attributes={
                    'days': getattr(temporal, 'days', []),
                    'times': getattr(temporal, 'times', []),
                },
            )
        ]

    @staticmethod
    def _detect_severity(text: str) -> str:
        """Detect issue severity from text"""
        text_lower = text.lower()

        # High severity indicators
        high_severity = [
            'critical', 'urgent', 'emergency', 'completely down',
            'not working at all', 'can\'t work', 'losing money'
        ]
        if any(indicator in text_lower for indicator in high_severity):
            return 'HIGH'

        # Medium severity indicators
        medium_severity = [
            'frustrated', 'frustrating', 'annoying', 'work from home',
            'need it for work', 'important'
        ]
        if any(indicator in text_lower for indicator in medium_severity):
            return 'MEDIUM'

        return 'LOW'

    @staticmethod
    def _extract_disputed_amounts(turns: List[Turn]) -> List[str]:
        """
        Extract disputed amounts ONLY from customer turns mentioning the problem

        Returns list like: ["$14.99", "$16.99"]
        """
        disputed_amounts = []

        for turn in turns:
            if turn.speaker == 'customer':
                text_lower = turn.text.lower()

                # Check if customer is mentioning charges/billing
                problem_keywords = [
                    'charged', 'charge', 'bill', 'statement',
                    'saw', 'shows', 'billed', 'payment'
                ]

                if any(keyword in text_lower for keyword in problem_keywords):
                    # Extract money from this turn
                    money_amounts = turn.entities.get('money', [])
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
            if turn.speaker == 'agent':
                text_lower = turn.text.lower()

                # Enhanced pattern matching
                if 'duplicate' in text_lower or 'retried' in text_lower or 'processed twice' in text_lower:
                    cause = "DUPLICATE_PROCESSING"

                elif 'upgrade' in text_lower or 'upgraded' in text_lower:
                    cause = "MID_CYCLE_UPGRADE"

                    # Extract plan names
                    plan_patterns = [
                        r'from (\w+) to (\w+)',
                        r'(\w+) to (\w+) plan',
                        r'(\w+) plan.*(\w+) plan'
                    ]

                    for pattern in plan_patterns:
                        match = re.search(pattern, text_lower, re.IGNORECASE)
                        if match:
                            old_plan = match.group(1).upper()
                            new_plan = match.group(2).upper()
                            plan_change = f"{old_plan}→{new_plan}"
                            break

                elif 'downgrade' in text_lower or 'downgraded' in text_lower:
                    cause = "MID_CYCLE_DOWNGRADE"

                elif 'double' in text_lower and 'billing' in text_lower:
                    cause = "DOUBLE_BILLING"

                elif 'overlap' in text_lower:
                    cause = "BILLING_OVERLAP"

                elif 'error' in text_lower or 'mistake' in text_lower:
                    cause = "SYSTEM_ERROR"

                elif 'proration' in text_lower or 'prorated' in text_lower:
                    cause = "PRORATION_CONFUSION"

        return cause, plan_change

    @staticmethod
    def _determine_action_result(turns: list[Turn], action_index: int, action_turn: Turn) -> str:
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
            'submitted', 'processed', 'completed', 'filed',
            'applied', 'issued', 'sent', 'done',
            'just submitted', 'just processed', 'just filed',
            'already submitted', 'already processed'
        ]

        if any(keyword in text_lower for keyword in completion_keywords):
            return 'COMPLETED'

        # Check if action verb + "now" or "right now"
        action_now_patterns = [
            r'I\'?(?:ve|ll)\s+\w+\s+(?:the\s+)?\w+\s+now',  # "I've submitted the refund now"
            r'I\'?m\s+\w+ing\s+\w+\s+now',  # "I'm processing it now"
        ]

        for pattern in action_now_patterns:
            if re.search(pattern, text_lower):
                return 'COMPLETED'

        # Check following turns for confirmation
        following_turns = turns[action_index + 1:min(action_index + 3, len(turns))]

        for turn in following_turns:
            turn_text_lower = turn.text.lower()

            # Customer confirmation
            if turn.speaker == 'customer' and any(word in turn_text_lower for word in [
                'perfect', 'great', 'thank', 'appreciate', 'received', 'got it'
            ]):
                return 'COMPLETED'

            # Agent follow-up confirmation
            if turn.speaker == 'agent' and any(word in turn_text_lower for word in [
                'all set', 'you\'re all set', 'that\'s done', 'completed'
            ]):
                return 'COMPLETED'

        return 'PENDING'