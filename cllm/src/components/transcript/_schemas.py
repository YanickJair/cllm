from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from spacy.tokens import Doc
from src.components.sys_prompt import Intent, Target


class Turn(BaseModel):
    """Single turn in conversation"""

    speaker: str  # "agent", "customer", "system"
    text: str
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
    type: str  # SUPPORT, SALES, BILLING
    channel: str  # VOICE, CHAT, EMAIL
    duration: int  # minutes
    agent: Optional[str] = None
    timestamp: Optional[datetime] = None


class Issue(BaseModel):
    """Customer issue"""

    type: str  # INTERNET_OUTAGE, BILLING_DISPUTE, etc.
    disputed_amounts: list[str] = Field(default_factory=list)
    cause: Optional[str] = None
    plan_change: Optional[str] = None
    severity: Optional[str] = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    frequency: Optional[str] = None  # ONCE, DAILY, etc.
    duration: Optional[str] = None  # "3d", "1week"
    pattern: Optional[str] = None  # "9am+1pm+6pm"
    impact: Optional[str] = None  # WORK_FROM_HOME, etc.
    attributes: dict = Field(default_factory=dict)


class Action(BaseModel):
    """Action taken by agent"""

    type: str  # TROUBLESHOOT, ESCALATE, etc.
    step: Optional[str] = None
    result: Optional[str] = "PENDING"  # SUCCESS, FAILED, TEMP_FIX
    timestamp: Optional[float] = None
    attributes: dict = Field(default_factory=dict)
    amount: Optional[str] = None
    payment_method: Optional[str] = None


class Resolution(BaseModel):
    """How conversation resolved"""

    type: str = "UNKNOWN"  # RESOLVED, PENDING, ESCALATED, etc.
    status: Optional[str] = None
    timeline: Optional[str] = None  # "24h", "3-5_days"
    next_steps: Optional[str] = None
    ticket_id: Optional[str] = None


class SentimentTrajectory(BaseModel):
    """Sentiment across conversation"""

    start: str  # FRUSTRATED, ANGRY, etc.
    end: str
    turning_points: list[tuple[int, str]] = Field(
        default_factory=list
    )  # (turn_number, sentiment)
    intensity: Optional[float] = None


class CustomerProfile(BaseModel):
    """Customer information"""

    account: Optional[str] = None
    tier: Optional[str] = None  # FREE, BASIC, PREMIUM, ENTERPRISE
    tenure: Optional[str] = None  # "5yr"
    lifetime_value: Optional[float] = None
    churn_risk: Optional[str] = None  # LOW, MEDIUM, HIGH
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

    days: list[str] | None = None # ["monday", "tuesday"]
    times: list[str] | None = None # ["9am", "1pm", "6pm"]
    duration: str | None = None # "3d"
    frequency: str | None = None  # "3x_daily"
    pattern: str | None = None # "9am+1pm+6pm"
