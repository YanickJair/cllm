# transcript_encoder.py - NEW file
from typing import Optional

from . import Resolution, SentimentTrajectory, CallInfo, CustomerProfile, Issue, Action, \
    TranscriptAnalysis, Turn


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
        [ID:key=value:...]                          ← NEW: All identifiers in one token
        [CONTACT:key=value:...]                     ← NEW: Contact information
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

        # 3. Identifiers (tracking, claim, product, order, ticket, case)
        identifiers = self._encode_identifiers(analysis)
        if identifiers:
            tokens.append(identifiers)
            if verbose:
                print(f"Identifiers: {identifiers}")

        # 4. Contact info (email, phone)
        contact = self._encode_contact_info(analysis)
        if contact:
            tokens.append(contact)
            if verbose:
                print(f"Contact: {contact}")

        # 5. Issues (with full temporal details and money)
        for issue in analysis.issues:
            issue_token = self._encode_issue(issue, analysis.turns)
            tokens.append(issue_token)
            if verbose:
                print(f"Issue: {issue_token}")

        # 6. Actions (with amounts for refunds)
        for action in analysis.actions:
            action_token = self._encode_action(action)
            tokens.append(action_token)
            if verbose:
                print(f"Action: {action_token}")

        # 7. Resolution
        resolution_token = self._encode_resolution(analysis.resolution)
        tokens.append(resolution_token)
        if verbose:
            print(f"Resolution: {resolution_token}")

        # 8. Sentiment trajectory
        sentiment_token = self._encode_sentiment(analysis.sentiment_trajectory)
        tokens.append(sentiment_token)
        if verbose:
            print(f"Sentiment: {sentiment_token}")

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

        # Add organization if present
        if customer.attributes and 'organization' in customer.attributes:
            org = customer.attributes['organization']
            # Compress organization name
            org_compressed = org.replace(' ', '_')
            parts.append(f"ORG={org_compressed}")

        # Add location if present
        if customer.attributes and 'location' in customer.attributes:
            location = customer.attributes['location']
            parts.append(f"LOCATION={location}")

        return f"[{':'.join(parts)}]"

    def _encode_identifiers(self, analysis: TranscriptAnalysis) -> Optional[str]:
        """
        Encode all identifiers in one token

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

        # Collect all identifiers from all turns
        identifiers: dict = {
            'tracking_numbers': [],
            'claim_numbers': [],
            'product_models': [],
            'order_numbers': [],
            'ticket_numbers': [],
            'case_numbers': []

        }

        for turn in analysis.turns:
            if turn.entities:
                for key in identifiers:
                    identifiers[key].extend(turn.entities.get(key, []))

        # Deduplicate all
        for key in identifiers:
            identifiers[key] = list(set(identifiers[key]))

        # Build identifier token
        parts = []

        if identifiers['tracking_numbers']:
            # Join multiple with comma (rare but possible)
            parts.append(f"TRACKING={','.join(identifiers['tracking_numbers'])}")

        if identifiers['claim_numbers']:
            parts.append(f"CLAIM={','.join(identifiers['claim_numbers'])}")

        if identifiers['product_models']:
            parts.append(f"PRODUCT={','.join(identifiers['product_models'])}")

        if identifiers['order_numbers']:
            parts.append(f"ORDER={','.join(identifiers['order_numbers'])}")

        if identifiers['ticket_numbers']:
            parts.append(f"TICKET={','.join(identifiers['ticket_numbers'])}")

        if identifiers['case_numbers']:
            parts.append(f"CASE={','.join(identifiers['case_numbers'])}")

        if not parts:
            return None

        return f"[ID:{':'.join(parts)}]"

    def _encode_contact_info(self, analysis: TranscriptAnalysis) -> Optional[str]:
        """
        Encode contact information

        Format: [CONTACT:TYPE=value:...]
        Example: [CONTACT:EMAIL=user@example.com:PHONE=555-123-4567]
        """

        # Collect contact info from all turns
        emails = []
        phone_numbers = []

        for turn in analysis.turns:
            if turn.entities:
                emails.extend(turn.entities.get('emails', []))
                phone_numbers.extend(turn.entities.get('phone_numbers', []))

        # Deduplicate
        emails = list(set(emails))
        phone_numbers = list(set(phone_numbers))

        # Build contact token
        parts = []

        if emails:
            # Usually just one email, but support multiple
            parts.append(f"EMAIL={','.join(emails)}")

        if phone_numbers:
            parts.append(f"PHONE={','.join(phone_numbers)}")

        if not parts:
            return None

        return f"[CONTACT:{':'.join(parts)}]"

    def _encode_issue(self, issue: Issue, turns: list[Turn]) -> str:
        """
        Encode issue with full temporal details and money amounts

        Format: [ISSUE:TYPE:ATTR=VALUE:...]
        Example: [ISSUE:INTERNET_OUTAGE:SEVERITY=MEDIUM:FREQ=3x_daily:DURATION=3d:PATTERN=9am+1pm+6pm:DAYS=MON+TUE+WED]
        Example: [ISSUE:BILLING_DISPUTE:SEVERITY=LOW:AMOUNTS=$14.99+$16.99]
        """
        parts = ['ISSUE', issue.type]

        # Money amounts for billing issues
        if issue.type in ['BILLING_DISPUTE', 'UNEXPECTED_CHARGE', 'REFUND_REQUEST', 'OVERCHARGE']:
            for turn in turns:
                if len(turn.entities.get('money', [])) > 0:
                    amounts = '+'.join(turn.entities.get('money', []))
                    parts.append(f"AMOUNTS={amounts}")

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
            if days and len(days) > 0:  # Only if not empty
                days_str = '+'.join(days)
                parts.append(f"DAYS={days_str}")

        # Impact
        if issue.impact:
            parts.append(f"IMPACT={issue.impact}")

        return f"[{':'.join(parts)}]"

    def _encode_action(self, action: Action) -> str:
        """
        Encode action with financial details

        Format: [ACTION:TYPE:ATTR=VALUE:...]
        Example: [ACTION:TROUBLESHOOT:RESULT=PENDING]
        Example: [ACTION:REFUND:REFERENCE=RFD-908712:TIMELINE=3-5d:RESULT=COMPLETED]
        Example: [ACTION:CREDIT:AMOUNT=$10:METHOD=ACCOUNT_CREDIT:RESULT=APPLIED]
        """
        parts = ['ACTION', action.type]

        if action.step:
            parts.append(f"STEP={action.step}")

        # Add reference number if present
        if action.attributes and 'reference' in action.attributes and action.attributes['reference']:
            parts.append(f"REFERENCE={action.attributes['reference']}")

        # Add timeline if present
        if action.attributes and 'timeline' in action.attributes and action.attributes['timeline']:
            parts.append(f"TIMELINE={action.attributes['timeline']}")

        # Add amount for financial actions
        if action.amount:
            parts.append(f"AMOUNT={action.amount}")

        # Add payment method
        if action.payment_method:
            parts.append(f"METHOD={action.payment_method}")

        if action.result:
            parts.append(f"RESULT={action.result}")

        return f"[{':'.join(parts)}]"

    def _encode_resolution(self, resolution: Resolution) -> str:
        """
        Encode resolution

        Format: [RESOLUTION:TYPE:ATTR=VALUE:...]
        Example: [RESOLUTION:PENDING:TIMELINE=24h:TICKET=TK12345]
        Example: [RESOLUTION:RESOLVED:TIMELINE=3d]
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
        - "41 Riverbend Lane" → "41_Riverbend_Ln"
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