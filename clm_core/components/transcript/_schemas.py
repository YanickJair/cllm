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
    name: str | None = None
    email: str | None = None


class TranscriptAnalysis(BaseModel):
    """Complete transcript analysis"""

    call_info: CallInfo
    customer: CustomerProfile
    turns: list[Turn]
    issues: list[Issue]
    actions: list[Action]
    resolution: Resolution
    sentiment_trajectory: SentimentTrajectory

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

    days: list[str] | None = Field(default=None, description="days of the week")
    times: list[str] | None = Field(default=None, description="times of day")
    duration: str | None = Field(default=None, description="duration")
    frequency: str | None = Field(default=None, description="frequency: 33x day")
    pattern: str | None = Field(default=None, description="pattern")
