from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime

from src.core import Intent, Target


@dataclass
class Turn:
    """Single turn in conversation"""
    speaker: str  # "agent", "customer", "system"
    text: str
    timestamp: Optional[float] = None
    intent: Optional[Intent] = None
    targets: list[Target] = field(default_factory=list)
    sentiment: Optional[str] = None
    entities: dict = field(default_factory=dict)


@dataclass
class CallInfo:
    """Call metadata"""
    call_id: str
    type: str  # SUPPORT, SALES, BILLING
    channel: str  # VOICE, CHAT, EMAIL
    duration: int  # minutes
    agent: Optional[str] = None
    timestamp: Optional[datetime] = None


@dataclass
class Issue:
    """Customer issue"""
    type: str  # INTERNET_OUTAGE, BILLING_DISPUTE, etc.
    disputed_amounts: list[str] = field(default_factory=list)
    cause: Optional[str] = None
    plan_change: Optional[str] = None
    severity: Optional[str] = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    frequency: Optional[str] = None  # ONCE, DAILY, etc.
    duration: Optional[str] = None  # "3d", "1week"
    pattern: Optional[str] = None  # "9am+1pm+6pm"
    impact: Optional[str] = None  # WORK_FROM_HOME, etc.
    attributes: dict = field(default_factory=dict)


@dataclass
class Action:
    """Action taken by agent"""
    type: str  # TROUBLESHOOT, ESCALATE, etc.
    step: Optional[str] = None
    result: Optional[str] = "PENDING"  # SUCCESS, FAILED, TEMP_FIX
    timestamp: Optional[float] = None
    attributes: dict = field(default_factory=dict)
    amount: Optional[str] = None
    payment_method: Optional[str] = None


@dataclass
class Resolution:
    """How conversation resolved"""
    type: str  = "UNKNOWN" # RESOLVED, PENDING, ESCALATED, etc.
    status: Optional[str] = None
    timeline: Optional[str] = None  # "24h", "3-5_days"
    next_steps: Optional[str] = None
    ticket_id: Optional[str] = None


@dataclass
class SentimentTrajectory:
    """Sentiment across conversation"""
    start: str  # FRUSTRATED, ANGRY, etc.
    end: str
    turning_points: list[tuple[int, str]] = field(default_factory=list)  # (turn_number, sentiment)
    intensity: Optional[float] = None


@dataclass
class CustomerProfile:
    """Customer information"""
    account: Optional[str] = None
    tier: Optional[str] = None  # FREE, BASIC, PREMIUM, ENTERPRISE
    tenure: Optional[str] = None  # "5yr"
    lifetime_value: Optional[float] = None
    churn_risk: Optional[str] = None  # LOW, MEDIUM, HIGH
    attributes: Optional[dict] = None
    name: str | None = None
    email: str | None = None


@dataclass
class TranscriptAnalysis:
    """Complete transcript analysis"""
    call_info: CallInfo
    customer: CustomerProfile
    turns: list[Turn]
    issues: list[Issue]
    actions: list[Action]
    resolution: Resolution
    sentiment_trajectory: SentimentTrajectory

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass
class TranscriptCompressionResult:
    """Transcript compression result"""
    original: str
    compressed: str
    analysis: TranscriptAnalysis
    compression_ratio: float
    information_preserved: float
    metadata: dict

@dataclass
class TemporalPattern:
    """Represents extracted temporal information"""
    days: list[str]  # ["monday", "tuesday"]
    times: list[str]  # ["9am", "1pm", "6pm"]
    duration: str  # "3d"
    frequency: str  # "3x_daily"
    pattern: str  # "9am+1pm+6pm"