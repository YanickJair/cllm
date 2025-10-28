# transcript_encoder.py - NEW file
from typing import Optional

from src.components.transcript import Resolution, SentimentTrajectory, CallInfo, CustomerProfile, Issue, Action, \
    TranscriptAnalysis
from src.core.tokenizer import CLLMTokenizer


class TranscriptEncoder:
    """
    Encodes transcript analysis into compressed tokens

    Philosophy: Extends CLLMTokenizer format: [CALL:metadata][ISSUE:details][ACTION:details][RESOLUTION:details]
    """

    def encode(self, analysis: TranscriptAnalysis, verbose: bool = False) -> str:
        """
        Encode transcript analysis to compressed format

        Format Design:
        [CALL:type:key=value:...]
        [CUSTOMER:key=value:...]
        [ISSUE:type:key=value:...]
        [ACTION:type:key=value:...]
        [RESOLUTION:type:key=value:...]
        [SENTIMENT:start→end]
        """
        tokens = []

        # 1. Call info
        call_token = self._encode_call_info(analysis.call_info)
        tokens.append(call_token)
        if verbose:
            print(f"Call: {call_token}")

        # 2. Customer profile
        customer_token = self._encode_customer(analysis.customer)
        tokens.append(customer_token)
        if verbose:
            print(f"Customer: {customer_token}")

        # 3. Issues (with full temporal details)
        for issue in analysis.issues:
            issue_token = self._encode_issue(issue)
            tokens.append(issue_token)
            if verbose:
                print(f"Issue: {issue_token}")

        # 4. Actions
        for action in analysis.actions:
            action_token = self._encode_action(action)
            tokens.append(action_token)
            if verbose:
                print(f"Action: {action_token}")

        # 5. Resolution
        resolution_token = self._encode_resolution(analysis.resolution)
        tokens.append(resolution_token)
        if verbose:
            print(f"Resolution: {resolution_token}")

        # 6. Sentiment trajectory
        sentiment_token = self._encode_sentiment(analysis.sentiment_trajectory)
        tokens.append(sentiment_token)
        if verbose:
            print(f"Sentiment: {sentiment_token}")

        identifiers = self._encode_identifiers(analysis)
        if identifiers:
            tokens.append(identifiers)

        return ' '.join(tokens)

    def _encode_call_info(self, call: CallInfo) -> str:
        """
        Encode call metadata

        Format: [CALL:TYPE:ATTR=VALUE:...]
        Example: [CALL:SUPPORT:AGENT=Sarah:DURATION=8m]
        """
        parts = ['CALL', call.type]

        if call.agent:
            parts.append(f"AGENT={call.agent}")

        if call.duration:
            # Convert turns to approximate minutes (assume 2 turns/minute)
            minutes = max(1, call.duration // 2)
            parts.append(f"DURATION={minutes}m")

        if call.channel:
            parts.append(f"CHANNEL={call.channel}")

        return f"[{':'.join(parts)}]"

    def _encode_customer(self, customer: CustomerProfile) -> str:
        """
        Encode customer profile

        Format: [CUSTOMER:ATTR=VALUE:...]
        Example: [CUSTOMER:ACCOUNT=847-392-1045:TIER=PREMIUM:ADDRESS=123_Main_St]
        """
        parts = ['CUSTOMER']

        if customer.account:
            parts.append(f"ACCOUNT={customer.account}")

        if customer.tier:
            parts.append(f"TIER={customer.tier}")

        if customer.tenure:
            parts.append(f"TENURE={customer.tenure}")

        # Add address if present
        if customer.attributes and 'address' in customer.attributes:
            # Compress address: "123 Main Street" → "123_Main_St"
            address = customer.attributes['address']
            address_compressed = self._compress_address(address)
            parts.append(f"ADDRESS={address_compressed}")

        return f"[{':'.join(parts)}]"

    def _encode_issue(self, issue: Issue) -> str:
        """
        Encode issue with full temporal details

        Format: [ISSUE:TYPE:ATTR=VALUE:...]
        Example: [ISSUE:INTERNET_OUTAGE:SEVERITY=MEDIUM:FREQ=3x_daily:DURATION=3d:PATTERN=9am+1pm+6pm:DAYS=MON+TUE+WED]
        """
        parts = ['ISSUE', issue.type]

        if issue.type in ['BILLING_DISPUTE', 'UNEXPECTED_CHARGE', 'REFUND_REQUEST']:
            if issue.attributes and 'money' in issue.attributes:
                amounts = issue.attributes['money']
                if amounts:
                    parts.append(f"AMOUNTS={'+'.join(amounts)}")

        # Severity
        if issue.severity:
            parts.append(f"SEVERITY={issue.severity}")

        # Frequency
        if issue.frequency:
            parts.append(f"FREQ={issue.frequency}")

        # Duration
        if issue.duration:
            parts.append(f"DURATION={issue.duration}")

        # Pattern (times)
        if issue.pattern:
            parts.append(f"PATTERN={issue.pattern}")

        # Days (if available in attributes)
        if issue.attributes and 'days' in issue.attributes:
            days = issue.attributes['days']
            if days:
                days_str = '+'.join(days)
                parts.append(f"DAYS={days_str}")

        # Impact
        if issue.impact:
            parts.append(f"IMPACT={issue.impact}")

        return f"[{':'.join(parts)}]"

    def _encode_action(self, action: Action) -> str:
        """
        Encode action

        Format: [ACTION:TYPE:ATTR=VALUE:...]
        Example: [ACTION:TROUBLESHOOT:RESULT=PENDING]
        """
        parts = ['ACTION', action.type]

        if action.step:
            parts.append(f"STEP={action.step}")

        if action.result:
            parts.append(f"RESULT={action.result}")

        return f"[{':'.join(parts)}]"

    def _encode_resolution(self, resolution: Resolution) -> str:
        """
        Encode resolution

        Format: [RESOLUTION:TYPE:ATTR=VALUE:...]
        Example: [RESOLUTION:PENDING:TIMELINE=24h:TICKET=TK12345]
        """
        parts = ['RESOLUTION', resolution.type]

        if resolution.timeline:
            parts.append(f"TIMELINE={resolution.timeline}")

        if resolution.ticket_id:
            parts.append(f"TICKET={resolution.ticket_id}")

        if resolution.next_steps:
            # Compress next steps
            steps_compressed = resolution.next_steps.replace(' ', '_')
            parts.append(f"NEXT={steps_compressed}")

        return f"[{':'.join(parts)}]"

    def _encode_sentiment(self, sentiment: SentimentTrajectory) -> str:
        """
        Encode sentiment trajectory

        Format: [SENTIMENT:START→END]
        Example: [SENTIMENT:FRUSTRATED→SATISFIED]

        With turning points: [SENTIMENT:FRUSTRATED→NEUTRAL→SATISFIED]
        """
        if not sentiment.turning_points:
            return f"[SENTIMENT:{sentiment.start}→{sentiment.end}]"

        # Build trajectory with turning points
        trajectory = [sentiment.start]
        for _, emotion in sentiment.turning_points:
            if emotion != trajectory[-1]:
                trajectory.append(emotion)

        # Ensure end state is included
        if trajectory[-1] != sentiment.end:
            trajectory.append(sentiment.end)

        trajectory_str = '→'.join(trajectory)
        return f"[SENTIMENT:{trajectory_str}]"

    def _compress_address(self, address: str) -> str:
        """
        Compress address

        Examples:
        - "123 Main Street" → "123_Main_St"
        - "456 Oak Avenue" → "456_Oak_Ave"
        """
        # Replace spaces with underscores
        compressed = address.replace(' ', '_')

        # Abbreviate common words
        abbreviations = {
            'Street': 'St',
            'Avenue': 'Ave',
            'Road': 'Rd',
            'Drive': 'Dr',
            'Lane': 'Ln',
            'Boulevard': 'Blvd',
            'Court': 'Ct',
            'Place': 'Pl'
        }

        for full, abbrev in abbreviations.items():
            compressed = compressed.replace(full, abbrev)

        return compressed

    def _encode_identifiers(self, analysis: TranscriptAnalysis) -> Optional[str]:
        """Encode tracking numbers, claim numbers, product models"""

        # Collect all identifiers from all turns
        tracking_numbers = []
        claim_numbers = []
        product_models = []

        for turn in analysis.turns:
            if turn.entities:
                tracking_numbers.extend(turn.entities.get('tracking_numbers', []))
                claim_numbers.extend(turn.entities.get('claim_numbers', []))
                product_models.extend(turn.entities.get('product_models', []))

        # Deduplicate
        tracking_numbers = list(set(tracking_numbers))
        claim_numbers = list(set(claim_numbers))
        product_models = list(set(product_models))

        # Build identifier token
        parts = []

        if tracking_numbers:
            parts.append(f"TRACKING={','.join(tracking_numbers)}")

        if claim_numbers:
            parts.append(f"CLAIM={','.join(claim_numbers)}")

        if product_models:
            parts.append(f"PRODUCT={','.join(product_models)}")

        if not parts:
            return None

        return f"[ID:{':'.join(parts)}]"