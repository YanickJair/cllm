import re
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

    def analyze(self, transcript: str, metadata: dict = None) -> TranscriptAnalysis:
        """Analyze transcript with enhanced extraction"""

        if metadata is None:
            metadata = {}

        # Step 1: Parse turns
        turns = self._parse_turns(transcript)

        # Step 2: Analyze each turn
        for turn in turns:
            # Use existing IntentDetector
            intents = self.intent_detector.detect(turn.text)
            turn.intent = self.intent_detector.get_primary_intent(intents)

            # Use existing TargetExtractor
            turn.targets = self.target_extractor.extract(turn.text)

            # Enhanced: Sentiment with context
            turn.sentiment, _ = self.sentiment_analyzer.analyze_turn(
                turn.text,
                turn.speaker
            )

            # Enhanced: Entities
            turn.entities = self.entity_extractor.extract(turn.text)

        # Step 3: Extract conversation-level elements
        call_info = self._extract_call_info(turns, metadata)
        customer = self._extract_customer_profile(turns)
        issues = self._extract_issues_enhanced(turns)
        actions = self._extract_actions_enhanced(turns)  # Enhanced version
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
    def _parse_turns(transcript: str) -> list[Turn]:
        """Parse transcript into turns"""
        turns = []
        lines = transcript.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if ':' in line:
                speaker, text = line.split(':', 1)
                speaker = speaker.strip().lower()

                # Normalize speaker
                if 'agent' in speaker or 'rep' in speaker:
                    speaker = 'agent'
                elif 'customer' in speaker or 'caller' in speaker or 'user' in speaker:
                    speaker = 'customer'
                else:
                    speaker = 'system'

                turns.append(Turn(
                    speaker=speaker,
                    text=text.strip()
                ))

        return turns

    def _extract_issues_enhanced(self, turns: list[Turn]) -> list[Issue]:
        """Extract issues with payment context separation"""
        issues = []

        # Combine all customer text for context
        customer_text = ' '.join([
            turn.text for turn in turns if turn.speaker == 'customer'
        ])

        # Detect issue type
        issue_type = self.vocab.get_issue_token(customer_text)

        if issue_type:
            # Extract temporal pattern
            temporal = self.temporal_extractor.extract(customer_text)

            # Detect severity
            severity = self._detect_severity(customer_text)

            # NEW: Extract payment context for billing issues
            disputed_amounts = []
            cause = None
            plan_change = None

            if issue_type in ['BILLING_DISPUTE', 'UNEXPECTED_CHARGE', 'REFUND_REQUEST', 'OVERCHARGE']:
                # Extract disputed amounts ONLY from customer turns
                disputed_amounts = self._extract_disputed_amounts(turns)

                # Detect cause and plan change from agent explanation
                cause, plan_change = self._detect_billing_cause(turns)

            issue = Issue(
                type=issue_type,
                severity=severity,
                disputed_amounts=disputed_amounts,
                cause=cause,
                plan_change=plan_change,
                frequency=temporal.frequency,
                duration=temporal.duration,
                pattern=temporal.pattern,
                attributes={
                    'days': temporal.days,
                    'times': temporal.times
                }
            )
            issues.append(issue)

        return issues

    def _extract_disputed_amounts(self, turns: List[Turn]) -> List[str]:
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

    def _detect_billing_cause(self, turns: List[Turn]) -> Tuple[Optional[str], Optional[str]]:
        """
        Detect root cause and plan change from agent explanation

        Returns: (cause, plan_change)
        Example: ("MID_CYCLE_UPGRADE", "STANDARD→PREMIUM")
        """
        cause = None
        plan_change = None

        for turn in turns:
            if turn.speaker == 'agent':
                text_lower = turn.text.lower()

                # Detect plan upgrade/downgrade
                if 'upgrade' in text_lower or 'upgraded' in text_lower:
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

                elif 'double' in text_lower or 'twice' in text_lower:
                    cause = "DOUBLE_BILLING"

                elif 'overlap' in text_lower:
                    cause = "BILLING_OVERLAP"

                elif 'error' in text_lower or 'mistake' in text_lower:
                    cause = "SYSTEM_ERROR"

                elif 'proration' in text_lower or 'prorated' in text_lower:
                    cause = "PRORATION_CONFUSION"

        return cause, plan_change

    @staticmethod
    def _extract_customer_profile(turns: list[Turn]) -> CustomerProfile:
        """Extract customer profile from turns"""
        profile = CustomerProfile()

        # Collect all entities from all turns
        all_entities = {
            'accounts': [],
            'addresses': [],
            'plans': []
        }

        for turn in turns:
            if turn.entities:
                for key in all_entities:
                    if key in turn.entities:
                        all_entities[key].extend(turn.entities[key])

        # Extract account
        if all_entities['accounts']:
            profile.account = all_entities['accounts'][0]

        # Extract tier from plan
        if all_entities['plans']:
            plan = all_entities['plans'][0].lower()
            if 'premium' in plan:
                profile.tier = 'PREMIUM'
            elif 'enterprise' in plan:
                profile.tier = 'ENTERPRISE'
            elif 'basic' in plan:
                profile.tier = 'BASIC'
            else:
                profile.tier = 'STANDARD'

        # Store address
        if all_entities['addresses']:
            if profile.attributes is None:
                profile.attributes = {}
            profile.attributes['address'] = all_entities['addresses'][0]

        return profile

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

    def _extract_call_info(self, turns: list[Turn], metadata: dict) -> CallInfo:
        """Extract call metadata"""

        # Extract agent name from first agent turn
        agent_name = None
        if 'agent' in metadata and metadata['agent']:
            agent_name = metadata['agent']
        else:
            for turn in turns[:3]:
                if turn.speaker == 'agent':
                    doc = self.nlp(turn.text)
                    for ent in doc.ents:
                        if ent.label_ == "PERSON":
                            agent_name = ent.text
                            break
                if agent_name:
                    break

            if not agent_name:
                # Regex as fallback
                agent_patterns = [
                    r'my name is (\w+)',  # "My name is Jason"
                    r"i'?m (\w+)",  # "I'm Maria" or "Im Raj"
                    r'this is (\w+)',  # "This is Anita"
                    r'(\w+) from',  # "Jason from support"
                    r'(\w+) here',  # "Michael here"
                ]
                for turn in turns[:3]:  # Check first 3 turns
                    if turn.speaker == 'agent':
                        text_lower = turn.text.lower()

                        for pattern in agent_patterns:
                            match = re.search(pattern, text_lower)
                            if match:
                                agent_name = match.group(1).title()
                                break

                        if agent_name:
                            break

        return CallInfo(
            call_id=metadata.get('call_id', 'unknown'),
            type=metadata.get('type', 'SUPPORT'),
            channel=metadata.get('channel', 'VOICE'),
            duration=len(turns),
            agent=agent_name
        )

    def _extract_actions_enhanced(self, turns: list[Turn]) -> list[Action]:
        """
        Extract actions with financial details

        NEW: Populates amount and payment_method for REFUND/CREDIT actions
        """
        actions = []

        for i, turn in enumerate(turns):
            if turn.speaker == 'agent':
                action_type = self.vocab.get_action_token(turn.text)
                if action_type:
                    result = self._determine_action_result(turns, i)

                    # NEW: Extract financial details for REFUND/CREDIT actions
                    amount = None
                    payment_method = None

                    if action_type in ['REFUND', 'CREDIT', 'CHARGE', 'PAYMENT']:
                        amount, payment_method = self._extract_financial_details(turn)

                    actions.append(Action(
                        type=action_type,
                        result=result,
                        amount=amount,
                        payment_method=payment_method
                    ))

        return actions

    @staticmethod
    def _extract_financial_details(turn: Turn) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract amount and payment method from agent turn

        Returns: (amount, payment_method)
        Example: ("$12.00", "CARD_CREDIT")
        """
        amount = None
        payment_method = None

        # Extract amount
        money_amounts = turn.entities.get('money', [])
        if money_amounts:
            amount = money_amounts[0]  # Take first amount mentioned

        # Detect payment method
        text_lower = turn.text.lower()

        if 'card' in text_lower or 'credit card' in text_lower:
            payment_method = "CARD_CREDIT"
        elif 'account' in text_lower and 'credit' in text_lower:
            payment_method = "ACCOUNT_CREDIT"
        elif 'check' in text_lower or 'cheque' in text_lower:
            payment_method = "CHECK"
        elif 'paypal' in text_lower:
            payment_method = "PAYPAL"
        elif 'balance' in text_lower:
            payment_method = "BALANCE_CREDIT"
        else:
            # Default for refunds
            payment_method = "CARD_CREDIT"

        return amount, payment_method

    def _extract_resolution(self, turns: list[Turn]) -> Resolution:
        """Extract resolution"""
        agent_turns = [t for t in turns if t.speaker == 'agent']
        last_agent_turns = agent_turns[-4:]

        resolution_type = 'UNKNOWN'
        timeline = None
        next_steps = None

        for turn in reversed(last_agent_turns):
            text_lower = turn.text.lower()

            # Pattern 1: Explicit resolution
            if any(word in text_lower for word in ['resolved', 'fixed', 'solved', 'working now']):
                resolution_type = 'RESOLVED'
                break

            # Pattern 2: Approved/Payout (insurance, refund)
            if any(word in text_lower for word in ['approved', 'payout', 'refund processed', 'credit', 'refund']):
                resolution_type = 'RESOLVED'
                # Extract timeline
                timeline = self._extract_timeline(text_lower)
                break

            # Pattern 3: Replacement/Exchange scheduled
            if any(word in text_lower for word in ['replace', 'replacement', 'exchange']):
                resolution_type = 'PENDING'
                # Look for timeline: "within 24 hours", "tomorrow"
                timeline = self._extract_timeline(text_lower)
                next_steps = 'REPLACEMENT'
                break

            # Pattern 4: Delivery scheduled
            if any(word in text_lower for word in ['prioritized', 'scheduled', 'tomorrow', 'today']):
                resolution_type = 'PENDING'
                timeline = self._extract_timeline(text_lower)
                break

            # Pattern 5: Escalated/Transferred
            if any(word in text_lower for word in ['escalate', 'transfer', 'supervisor']):
                resolution_type = 'ESCALATED'
                break

        return Resolution(
            type=resolution_type,
            timeline=timeline,
            next_steps=next_steps
        )

    def _extract_timeline(self, text: str) -> Optional[str]:
        """Extract timeline from text"""

        # Pattern 1: "within X hours/days"
        match = re.search(r'within (\d+)\s*(hour|day|business day)s?', text)
        if match:
            num = match.group(1)
            unit = 'h' if 'hour' in match.group(2) else 'd'
            return f"{num}{unit}"

        # Pattern 2: "tomorrow"
        if 'tomorrow' in text:
            return 'TOMORROW'

        # Pattern 3: "today"
        if 'today' in text:
            return 'TODAY'

        # Pattern 4: "X business days"
        match = re.search(r'(\d+)\s*business days?', text)
        if match:
            return f"{match.group(1)}d"

        return None

    @staticmethod
    def _determine_action_result(turns: list[Turn], action_index: int) -> str:
        """Determine action result"""
        following = turns[action_index + 1:action_index + 4]

        for turn in following:
            text_lower = turn.text.lower()
            if any(word in text_lower for word in ['worked', 'fixed', 'resolved', 'processed', 'applied']):
                return 'COMPLETED'
            elif any(word in text_lower for word in ['didn\'t work', 'failed', 'still']):
                return 'FAILED'

        return 'PENDING'