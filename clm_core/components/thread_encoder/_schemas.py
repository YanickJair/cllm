from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from spacy.tokens import Doc
from clm_core.components.sys_prompt import Intent, Target


class Turn(BaseModel):
    """Single turn in conversation"""

    speaker: str = Field(..., description="agent, customer, system")
    text: str = Field(..., description="text of the turn")
    timestamp: Optional[float] = None
    intent: Optional[Intent] = None
    targets: list[Target] = Field(default_factory=list)
    sentiment: Optional[str] = None
    entities: dict = Field(default_factory=dict)
    doc: Optional[Doc] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CallInfo(BaseModel):
    """Call metadata"""

    call_id: str
    type: str = Field(..., description="type of call: SUPPORT, SALES, BILLING, etc.")
    channel: str = Field(..., description="channel of call: VOICE, CHAT, EMAIL")
    duration: int = Field(..., description="duration of call in minutes")
    agent: Optional[str] = None
    timestamp: Optional[datetime] = None


class Issue(BaseModel):
    """Customer issue"""

    type: str = Field(
        ..., description="type of issue: INTERNET_OUTAGE, BILLING_DISPUTE, etc."
    )
    disputed_amounts: list[str] = Field(default_factory=list)
    cause: Optional[str] = None
    plan_change: Optional[str] = None
    severity: Optional[str] = Field(
        default="LOW", description="severity of issue: LOW, MEDIUM, HIGH, CRITICAL"
    )
    frequency: Optional[str] = Field(
        default=None, description="frequency of issue: ONCE, DAILY, etc."
    )
    duration: Optional[str] = Field(
        default=None, description="duration of issue: '3d', '1week'"
    )
    pattern: Optional[str] = Field(
        default=None, description="pattern of issue: '9am+1pm+6pm'"
    )
    impact: Optional[str] = Field(
        default=None, description="impact of issue: WORK_FROM_HOME, etc."
    )
    attributes: dict = Field(default_factory=dict)


class Action(BaseModel):
    """Action taken by agent"""

    type: str = Field(..., description="type of action: TROUBLESHOOT, ESCALATE, etc.")
    step: Optional[str] = None
    result: Optional[str] = Field(
        default="PENDING", description="result of action: SUCCESS, FAILED, TEMP_FIX"
    )
    timestamp: Optional[float] = None
    attributes: dict = Field(default_factory=dict)
    amount: Optional[str] = None
    payment_method: Optional[str] = None


class Resolution(BaseModel):
    """How conversation resolved"""

    type: str = Field(
        default="UNKNOWN",
        description="type of resolution: RESOLVED, PENDING, ESCALATED, etc.",
    )
    status: Optional[str] = None
    timeline: Optional[str] = Field(
        default=None, description="timeline of resolution: '24h', '3-5_days'"
    )
    next_steps: Optional[str] = None
    ticket_id: Optional[str] = None


class SentimentTrajectory(BaseModel):
    """Sentiment across conversation"""

    start: Optional[str] = Field(
        default="NEUTRAL",
        description="start sentiment: 'NEUTRAL', 'POSITIVE', 'NEGATIVE'",
    )
    end: Optional[str] = Field(
        default="NEUTRAL",
        description="end sentiment: 'NEUTRAL', 'POSITIVE', 'NEGATIVE'",
    )
    turning_points: list[tuple[int, str]] = Field(
        default_factory=list, description="turning points: [(turn_number, sentiment)]"
    )
    intensity: Optional[float] = None


class CustomerProfile(BaseModel):
    """Customer information"""

    account: Optional[str] = None
    tier: Optional[str] = Field(
        default=None,
        description="customer tier: 'FREE', 'BASIC', 'PREMIUM', 'ENTERPRISE'",
    )
    tenure: Optional[str] = Field(default=None, description="customer tenure: '5yr'")
    lifetime_value: Optional[float] = None
    churn_risk: Optional[str] = Field(
        default=None, description="churn risk: 'LOW', 'MEDIUM', 'HIGH'"
    )
    attributes: Optional[dict] = None
    name: Optional[str] = Field(default=None, description="Customer's name")
    email: Optional[str] = Field(default=None, description="Customer's email")


class ResolutionState(BaseModel):
    """Enhanced resolution state with granularity"""

    type: str = Field(
        default="UNKNOWN",
        description="FULLY_RESOLVED, PARTIALLY_RESOLVED, PENDING, ESCALATED, UNRESOLVED",
    )
    completeness: Optional[str] = Field(
        default=None,
        description="FULL, PARTIAL, NONE - how much of issue was addressed",
    )
    customer_satisfaction: Optional[str] = Field(
        default=None, description="SATISFIED, NEUTRAL, DISSATISFIED"
    )
    follow_up_needed: bool = Field(
        default=False, description="Whether follow-up is required"
    )
    follow_up_reason: Optional[str] = Field(
        default=None,
        description="PENDING_ACTION, VERIFICATION_NEEDED, SCHEDULED_CALLBACK",
    )


class RefundReference(BaseModel):
    """Case-dependent refund information for billing/refund cases"""

    reference_number: Optional[str] = Field(
        default=None, description="Refund reference ID"
    )
    amount: Optional[str] = Field(default=None, description="Refund amount like $14.99")
    method: Optional[str] = Field(
        default=None, description="CARD_CREDIT, ACCOUNT_CREDIT, CHECK, PAYPAL"
    )
    status: Optional[str] = Field(
        default=None, description="INITIATED, PROCESSING, COMPLETED, PENDING_APPROVAL"
    )
    timeline: Optional[str] = Field(
        default=None, description="Expected timeline: 3-5_DAYS, 24h, IMMEDIATE"
    )
    original_transaction_id: Optional[str] = Field(
        default=None, description="Original transaction being refunded"
    )


class TimelineEvent(BaseModel):
    """Single event in conversation timeline"""

    event_type: str = Field(
        ..., description="ISSUE_RAISED, ACTION_TAKEN, RESOLUTION_PROPOSED, etc."
    )
    description: Optional[str] = Field(
        default=None, description="Brief description of event"
    )
    turn_index: int = Field(..., description="Turn index where event occurred")
    timestamp: Optional[float] = Field(
        default=None, description="Relative timestamp if available"
    )
    actor: str = Field(
        default="agent", description="Who triggered: agent, customer, system"
    )


class ConversationTimeline(BaseModel):
    """Timeline of key events in conversation"""

    events: list[TimelineEvent] = Field(
        default_factory=list, description="Ordered list of events"
    )
    first_issue_turn: Optional[int] = Field(
        default=None, description="Turn index when issue was first raised"
    )
    first_resolution_turn: Optional[int] = Field(
        default=None, description="Turn index when resolution was first proposed"
    )
    time_to_first_action: Optional[int] = Field(
        default=None, description="Turns between issue and first action"
    )
    time_to_resolution: Optional[int] = Field(
        default=None, description="Turns between issue and resolution"
    )


class PromiseCommitment(BaseModel):
    """Agent promise/commitment to customer"""

    type: str = Field(
        ...,
        description="CALLBACK, FOLLOW_UP_EMAIL, TECHNICIAN_VISIT, CREDIT_PROMISE, etc.",
    )
    description: str = Field(..., description="What was promised")
    timeline: Optional[str] = Field(
        default=None, description="When promised: 24h, MONDAY, 3-5_DAYS"
    )
    amount: Optional[str] = Field(
        default=None, description="Amount if applicable (credit/refund)"
    )
    turn_index: int = Field(..., description="Turn where promise was made")
    confidence: float = Field(default=0.8, description="Detection confidence 0.0-1.0")


class MonetaryAmount(BaseModel):
    """Monetary amount extracted from a conversation turn"""

    amount: str = Field(..., description="Amount string e.g. '$2.99'")
    reason: Optional[str] = Field(
        default=None,
        description="Reason category: REFUND, CHARGE, FEE, CREDIT, EXTRA_CHARGE, DUPLICATE_CHARGE, DISCOUNT",
    )
    speaker: str = Field(..., description="Who mentioned the amount: customer, agent, system")
    turn_index: int = Field(..., description="Index of the turn where amount appeared")


class TranscriptAnalysis(BaseModel):
    """Complete thread_encoder analysis"""

    call_info: CallInfo = Field(..., description="Transcript metadata information")
    customer: CustomerProfile = Field(..., description="Customer profile information")
    turns: list[Turn] = Field(..., description="Turns information (Agent/Customer)")
    issues: list[Issue] = Field(..., description="Issues information")
    actions: list[Action] = Field(
        ..., description="Actions performed by the agent during the conversation"
    )
    resolution: Resolution = Field(
        ..., description="Resolution detected during the conversation"
    )
    sentiment_trajectory: SentimentTrajectory = Field(
        ..., description="Sentiment trajectory information"
    )
    resolution_state: Optional[ResolutionState] = Field(
        default=None, description="Enhanced resolution state"
    )
    refund_reference: Optional[RefundReference] = Field(
        default=None, description="Refund details (only for billing/refund cases)"
    )
    timeline: Optional[ConversationTimeline] = Field(
        default=None, description="Timeline of key events"
    )
    promises: list[PromiseCommitment] = Field(
        default_factory=list, description="Agent promises/commitments"
    )

    # v2 schema fields — amounts and redacted fields
    amounts: list[MonetaryAmount] = Field(
        default_factory=list,
        description="All monetary amounts extracted from all turns with their reason",
    )
    redacted_fields: list[str] = Field(
        default_factory=list,
        description="Detected redacted field types: EMAIL_REDACTED, PHONE_REDACTED, etc.",
    )

    domain: Optional[str] = Field(
        default=None,
        description="Domain classification: BILLING, AUTHENTICATION, BOOKINGS, API, PERFORMANCE, etc.",
    )
    service: Optional[str] = Field(
        default=None,
        description="Service area: SUBSCRIPTION, HOST_STAY, PAYMENT, DASHBOARD, EXPORTS, etc.",
    )
    customer_intent: Optional[str] = Field(
        default=None,
        description="Primary customer intent derived from customer utterances",
    )
    secondary_intent: Optional[str] = Field(
        default=None,
        description="Optional secondary customer intent",
    )
    trigger_cause: Optional[str] = Field(
        default=None,
        description="Why the issue happened: the trigger/cause that prompted the customer to contact support (e.g. FIELD_LOCKED, MISSING_DELIVERY)",
    )
    context_provided: list[str] = Field(
        default_factory=list,
        description="Context provided by customer without PII: EMAIL_PROVIDED, BOOKING_ID_PROVIDED, etc.",
    )
    system_actions: list[str] = Field(
        default_factory=list,
        description="Automated system-level events: PAYMENT_RETRY_DETECTED, etc.",
    )

    def to_dict(self):
        return {k: str(v) for k, v in self.model_dump().items()}


class TranscriptCompressionResult(BaseModel):
    """Transcript compression result"""

    original: str
    compressed: str
    analysis: TranscriptAnalysis
    compression_ratio: float
    information_preserved: float
    metadata: dict


class TemporalPattern(BaseModel):
    """Represents extracted temporal information"""

    days: Optional[list[str]] = Field(default=None, description="days of the week")
    times: Optional[list[str]] = Field(default=None, description="times of day")
    duration: Optional[str] = Field(default=None, description="duration")
    frequency: Optional[str] = Field(default=None, description="frequency: 33x day")
    pattern: Optional[str] = Field(default=None, description="pattern")
    resolved_date: Optional[str] = Field(
        default=None, description="Resolved ISO date e.g. '2026-02-24'"
    )
