"""
CLM-driven action matcher.

Given a turn and a catalog of actions (each with a structured `match` block),
this script encodes the turn through CLM and scores each catalog entry
deterministically — no LLM call needed for the routine case.

The catalog schema mirrors what CLM already produces:
  domain, service, customerIntent, supportTrigger, turnTypes

Callers own the catalog; CLM owns the signal extraction.

The `__main__` demo simulates a live call: turns accumulate one at a time
(customer and agent alternating), and CLM re-encodes the transcript so far
after each new line — the same way a real-time agent-assist tool would see
the conversation build up rather than analyzing isolated one-liners.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import contextlib
import io
import os
import sys

from clm_core import CLMConfig, CLMEncoder
from clm_core.components.thread_encoder.turn_classifier.classifier import TurnClassifier
from clm_core.types import TurnType


@contextlib.contextmanager
def _quiet():
    """Suppress all output (stdout + stderr at the fd level) so that
    pretty_loguru's file-descriptor writes don't bleed into script output.
    Flushes Python's I/O buffers before and after the redirect so buffered
    content doesn't escape through the restored fd."""
    sys.stdout.flush()
    sys.stderr.flush()
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    saved = {1: os.dup(1), 2: os.dup(2)}
    os.dup2(devnull_fd, 1)
    os.dup2(devnull_fd, 2)
    try:
        yield
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        os.dup2(saved[1], 1)
        os.dup2(saved[2], 2)
        for fd in (devnull_fd, saved[1], saved[2]):
            os.close(fd)


# ---------------------------------------------------------------------------
# Scoring weights
# ---------------------------------------------------------------------------
_WEIGHTS = {
    "domain": 3,
    "customerIntent": 3,
    "supportTrigger": 2,
    "service": 2,
    "turnType": 1,
}

# Minimum score to include a candidate.
#   3 = domain OR intent alone (high recall, broad triage)
#   5 = domain AND intent must both match (recommended default)
DEFAULT_THRESHOLD = 3

# Minimum number of distinct CLM field types that must match.
# Prevents a single high-weight field (e.g. domain=BILLING alone) from
# flooding results with loosely related actions.
DEFAULT_MIN_FIELD_TYPES = 2


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------
@dataclass
class MatchResult:
    action_id: str
    title: str
    score: int
    matched_fields: list[str]


@dataclass
class TurnSignal:
    """Fields extracted by CLM from a single turn."""
    domain: str | None = None
    service: str | None = None
    customer_intent: str | None = None
    support_trigger: str | None = None
    turn_type: TurnType | None = None
    turn_confidence: float = 0.0

    @property
    def has_semantic_signal(self) -> bool:
        """True when CLM produced at least one non-trivial semantic field."""
        return any([
            self.domain and self.domain != "UNCLASSIFIED",
            self.service,
            self.customer_intent,
            self.support_trigger,
        ])


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------
def extract_signal(
    transcript: str,
    latest_turn_text: str,
    encoder: CLMEncoder,
) -> TurnSignal:
    """Extract the CLM signal for a transcript-so-far in a live conversation.

    `transcript` is the full "Speaker: text" history accumulated up to and
    including the newest line — domain/service/intent/trigger are derived
    from that whole context, matching how CLM behaves against a growing
    call rather than an isolated sentence.

    `latest_turn_text` (the newest line's raw text, no speaker prefix) is
    classified separately for turn_type, since that signal describes what
    is happening *right now* in the call, not the conversation as a whole.
    """
    out = encoder.ts_encoder.encode(
        thread=transcript, is_turn=False, thread_format="turns", metadata={}
    )
    d = out.to_dict()

    # Turn type: call the classifier directly so the encoder's conservative
    # reporting threshold (0.6) does not suppress supporting signals here.
    # Any non-NEUTRAL result is used; the +1 weight keeps it from overriding
    # strong semantic matches.
    turn_type: TurnType | None = None
    turn_confidence = 0.0
    clf: TurnClassifier = encoder.ts_encoder._turn_classifier
    raw_tt, raw_conf = clf.classify(latest_turn_text)
    if raw_tt != TurnType.NEUTRAL and raw_conf > 0.0:
        turn_type = raw_tt
        turn_confidence = raw_conf

    domain = d.get("domain")
    if domain == "UNCLASSIFIED":
        domain = None

    return TurnSignal(
        domain=domain,
        service=d.get("service"),
        customer_intent=d.get("customerIntent"),
        support_trigger=d.get("supportTrigger"),
        turn_type=turn_type,
        turn_confidence=turn_confidence,
    )


def score_action(
    signal: TurnSignal,
    action: dict,
    threshold: int,
    min_field_types: int,
) -> tuple[int, list[str]] | None:
    """
    Returns (score, matched_fields) when the action qualifies, else None.

    Adaptive threshold: when CLM produced no semantic signal (domain, intent,
    trigger, service all absent), the classifier turn_type is the only signal
    available. In that case a single turnType match is enough to qualify —
    the caller's catalog controls which turn types map to which action.
    """
    m = action.get("match", {})
    score = 0
    matched: list[str] = []

    if signal.domain and signal.domain in m.get("domain", []):
        score += _WEIGHTS["domain"]
        matched.append(f"domain={signal.domain}")

    if signal.customer_intent and signal.customer_intent in m.get("customerIntent", []):
        score += _WEIGHTS["customerIntent"]
        matched.append(f"customerIntent={signal.customer_intent}")

    if signal.support_trigger and signal.support_trigger in m.get("supportTrigger", []):
        score += _WEIGHTS["supportTrigger"]
        matched.append(f"supportTrigger={signal.support_trigger}")

    if signal.service and signal.service in m.get("service", []):
        score += _WEIGHTS["service"]
        matched.append(f"service={signal.service}")

    turn_type_matched = (
        signal.turn_type is not None
        and signal.turn_type.value in m.get("turnTypes", [])
    )
    if turn_type_matched:
        score += _WEIGHTS["turnType"]
        matched.append(f"turnType={signal.turn_type.value} ({signal.turn_confidence:.0%})")

    # When CLM has no semantic signal, any turn_type match qualifies by itself.
    # When it does, apply the normal threshold and min-field-types guard.
    if not signal.has_semantic_signal:
        if not turn_type_matched:
            return None
    else:
        if score < threshold:
            return None
        if len(matched) < min_field_types:
            return None

    return score, matched


def match_actions(
    transcript: str,
    latest_turn_text: str,
    catalog: list[dict],
    encoder: CLMEncoder,
    threshold: int = DEFAULT_THRESHOLD,
    min_field_types: int = DEFAULT_MIN_FIELD_TYPES,
) -> tuple[TurnSignal, list[MatchResult]]:
    signal = extract_signal(transcript, latest_turn_text, encoder)
    results: list[MatchResult] = []

    for action in catalog:
        outcome = score_action(signal, action, threshold, min_field_types)
        if outcome is not None:
            score, matched_fields = outcome
            results.append(MatchResult(
                action_id=action["id"],
                title=action["title"],
                score=score,
                matched_fields=matched_fields,
            ))

    results.sort(key=lambda r: (r.score, len(r.matched_fields)), reverse=True)
    return signal, results


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
def display(
    step: int,
    total: int,
    speaker: str,
    turn_text: str,
    signal: TurnSignal,
    results: list[MatchResult],
) -> None:
    tt_str = (
        f"{signal.turn_type.value} ({signal.turn_confidence:.0%})"
        if signal.turn_type else "—"
    )
    print(f"\n{'─' * 72}")
    print(f"  [{step}/{total}] {speaker:<8}: {turn_text}")
    print(
        f"  CLM (so far) : domain={signal.domain or '—'}  "
        f"intent={signal.customer_intent or '—'}  "
        f"trigger={signal.support_trigger or '—'}  "
        f"service={signal.service or '—'}"
    )
    print(f"  TurnType     : {tt_str}")
    print(f"{'─' * 72}")

    if not results:
        print("  → No match — catalog gap or LLM fallback candidate\n")
        return

    for i, r in enumerate(results):
        tag = "★" if i == 0 else f"{i + 1}"
        print(f"  [{tag}] score={r.score}  {r.action_id}: {r.title}")
        print(f"      ↳ {', '.join(r.matched_fields)}")
    print()


# ---------------------------------------------------------------------------
# Sample catalog
# ---------------------------------------------------------------------------
SAMPLE_CATALOG: list[dict] = [
    {
        "id": "ACT-001",
        "title": "Billing Issue Resolution",
        "description": "Resolve billing disputes, duplicate charges, or refund requests.",
        "match": {
            "domain": ["BILLING"],
            "service": ["PAYMENT", "SUBSCRIPTION"],
            "customerIntent": [
                "REPORT_DUPLICATE_CHARGE",
                "DISPUTE_CHARGE",
                "REQUEST_REFUND",
                "BILLING_ERROR",
                "REPORT_BILLING_ISSUE",
            ],
            "supportTrigger": ["DUPLICATE_CHARGE", "OVERCHARGE", "WRONG_AMOUNT"],
            "turnTypes": ["COMPLAINT", "DEMAND", "REQUEST", "PROBLEM_DESCRIPTION"],
        },
    },
    {
        "id": "ACT-002",
        "title": "Account Verification",
        "description": "Verify customer identity before making account changes.",
        "match": {
            "domain": ["ACCOUNT", "AUTHENTICATION", "SECURITY"],
            "service": ["ACCOUNT_MANAGEMENT", "LOGIN", "PROFILE"],
            "customerIntent": [
                "VERIFY_IDENTITY",
                "UPDATE_ACCOUNT",
                "ACCOUNT_ISSUE",
                "RESET_PASSWORD",
                "LOGIN_ISSUE",
            ],
            "supportTrigger": [
                "LOGIN_FAILURE",
                "ACCOUNT_LOCKED",
                "IDENTITY_CHANGE",
                "SYSTEM_ERROR",
                "AUTHENTICATION_FAILURE",
            ],
            "turnTypes": ["REQUEST", "INQUIRY", "PROBLEM_DESCRIPTION"],
        },
    },
    {
        "id": "ACT-003",
        "title": "Cancellation Retention",
        "description": "Engage retention offer when customer signals intent to cancel.",
        "match": {
            "domain": ["BILLING", "ACCOUNT", "SUBSCRIPTION"],
            "service": ["SUBSCRIPTION", "PLAN"],
            "customerIntent": [
                "CANCEL_SUBSCRIPTION",
                "DOWNGRADE_PLAN",
                "REQUEST_CANCELLATION",
            ],
            "supportTrigger": ["CHURN_RISK", "CANCELLATION_REQUEST"],
            "turnTypes": ["THREAT", "CHURN", "RETENTION_RISK"],
        },
    },
    {
        "id": "ACT-004",
        "title": "Onboarding Assistance",
        "description": "Guide new customers through initial setup and first use.",
        "match": {
            "domain": ["ACCOUNT", "PRODUCT"],
            "service": ["ONBOARDING", "SETUP", "ACCOUNT_MANAGEMENT"],
            "customerIntent": [
                "GET_STARTED",
                "SETUP_ACCOUNT",
                "LEARN_PRODUCT",
                "FIRST_LOGIN",
            ],
            "supportTrigger": ["NEW_CUSTOMER", "FIRST_LOGIN", "SETUP_INCOMPLETE"],
            "turnTypes": ["ONBOARDING", "GUIDE", "INQUIRY"],
        },
    },
    {
        "id": "ACT-005",
        "title": "Technical Support",
        "description": "Diagnose and resolve technical or connectivity issues.",
        "match": {
            "domain": ["TECHNICAL", "CONNECTIVITY", "PERFORMANCE"],
            "service": ["API", "NETWORK", "PLATFORM"],
            "customerIntent": [
                "REPORT_OUTAGE",
                "REPORT_ERROR",
                "FIX_CONNECTIVITY",
                "PERFORMANCE_ISSUE",
            ],
            "supportTrigger": [
                "SERVICE_OUTAGE",
                "CONNECTION_FAILURE",
                "ERROR_RATE_HIGH",
            ],
            "turnTypes": ["COMPLAINT", "PROBLEM_DESCRIPTION", "REQUEST"],
        },
    },
    {
        "id": "ACT-006",
        "title": "Complaint Escalation",
        "description": "Escalate to a supervisor when the customer expresses strong dissatisfaction.",
        "match": {
            "domain": ["BILLING", "TECHNICAL", "ACCOUNT", "SERVICE"],
            "service": ["PAYMENT", "SUBSCRIPTION", "SUPPORT"],
            "customerIntent": [],
            "supportTrigger": [],
            "turnTypes": ["THREAT", "DEMAND", "REPETITION", "CONTRADICTION"],
        },
    },
    {
        "id": "ACT-007",
        "title": "Refund Processing",
        "description": "Initiate or follow up on a refund for a verified erroneous charge.",
        "match": {
            "domain": ["BILLING", "FULFILLMENT"],
            "service": ["PAYMENT"],
            "customerIntent": [
                "REQUEST_REFUND",
                "REPORT_DUPLICATE_CHARGE",
                "DISPUTE_CHARGE",
                "FOLLOWUP_REPLACEMENT_STATUS",
                "FOLLOWUP_REFUND_STATUS",
            ],
            "supportTrigger": [
                "DUPLICATE_CHARGE",
                "OVERCHARGE",
                "WRONG_AMOUNT",
                "UNAUTHORIZED_CHARGE",
            ],
            "turnTypes": ["REQUEST", "DEMAND", "PROBLEM_DESCRIPTION"],
        },
    },
    {
        "id": "ACT-008",
        "title": "Sales Opportunity Follow-up",
        "description": "Engage a customer expressing interest in buying or upgrading a product; surface pricing/availability and route to sales for a next-best-action.",
        "match": {
            "domain": ["PRODUCT"],
            "service": ["SALES", "CATALOG"],
            "customerIntent": [
                "EXPRESS_PURCHASE_INTEREST",
                "REQUEST_TRIAL",
                "REQUEST_PLAN_UPGRADE",
                "EVALUATE_PLAN_UPGRADE",
            ],
            "supportTrigger": [],
            "turnTypes": ["STATEMENT", "INQUIRY", "PURCHASE_INTENT"],
        },
    },
    {
        "id": "ACT-009",
        "title": "Greet & Identify Caller",
        "description": "Open the interaction: greet the caller back and ask for the information needed to verify who they are before proceeding.",
        "match": {
            "domain": [],
            "service": [],
            "customerIntent": [],
            "supportTrigger": [],
            "turnTypes": ["GREETING", "INTRODUCTION"],
        },
    },
    {
        "id": "ACT-010",
        "title": "Wrap-up & Confirm Resolution",
        "description": "Customer signaled they're ending the call; confirm everything is resolved, summarize the outcome, and close out courteously.",
        "match": {
            "domain": [],
            "service": [],
            "customerIntent": [],
            "supportTrigger": [],
            "turnTypes": ["CLOSING"],
        },
    },
]


# ---------------------------------------------------------------------------
# Sample live conversations
# ---------------------------------------------------------------------------
# Each scenario is a single call, turn by turn — (speaker, text) pairs. The
# demo below feeds a scenario's turns in one at a time, re-encoding the
# transcript accumulated so far after every line — mirroring how a live call
# would be analyzed as it happens rather than as isolated one-off utterances.
CONVERSATIONS: dict[str, list[tuple[str, str]]] = {
    "Billing — Duplicate Charge": [
        ("Customer", "Hi, this is Sarah calling about my account."),
        ("Agent", "Hi Sarah, thanks for calling in. Can I get your account email to pull things up?"),
        ("Customer", "Sure, it's sarah@example.com. I noticed my account was charged twice this month — one on the 2nd and another on the 3rd."),
        ("Agent", "I'm sorry about that, let me take a look... yes, I can see the duplicate charge on the 3rd."),
        ("Customer", "Okay good, because I need this fixed immediately, it's really frustrating."),
        ("Agent", "Completely understandable. I've gone ahead and initiated a refund for the duplicate charge."),
        ("Customer", "Thank you, how long will the refund take to show up?"),
        ("Agent", "You should see it back on your card within 3-5 business days."),
        ("Customer", "Great, thanks so much for your help today, take care, goodbye!"),
    ],
    "Technical Support — Service Outage": [
        ("Customer", "Hi, I'm having a really frustrating problem with my internet connection."),
        ("Agent", "Sorry to hear that, can you tell me more about what's happening?"),
        ("Customer", "It's a complete outage, the service has been down since this morning."),
        ("Agent", "I can see there's a reported outage in your area, let me check the status for you."),
        ("Customer", "This is really impacting our work, when will it be fixed?"),
        ("Agent", "Our engineers are already working on restoring connectivity."),
        ("Customer", "Okay, thank you for the update."),
    ],
    "Account Security — Unauthorized Access": [
        ("Customer", "Hi, this is Marcus, I need help with my account."),
        ("Agent", "Sure Marcus, what's going on?"),
        ("Customer", "I got an email saying someone signed into my account from a different location, and it wasn't me."),
        ("Agent", "That's concerning, let's secure your account right away."),
        ("Customer", "Okay, my email is marcus@example.com."),
        ("Agent", "Thanks, I've verified your identity and locked down the account."),
        ("Customer", "Great, thank you so much for catching that."),
    ],
    "Cancellation & Retention — Price Increase": [
        ("Customer", "Hi, I want to cancel my subscription right now."),
        ("Agent", "I'm sorry to hear that, can I ask what's prompting the cancellation?"),
        ("Customer", "The price went up and honestly it's just not worth it anymore."),
        ("Agent", "I understand. Before you go, I can offer you 20% off for the next six months."),
        ("Customer", "Hmm, that's actually pretty good, let's do that instead."),
        ("Agent", "Great, I've applied the discount and your subscription will continue."),
    ],
    "Onboarding — New Customer": [
        ("Customer", "Hi, I just signed up and I have no idea how to get started."),
        ("Agent", "Welcome aboard! I'd be happy to walk you through the setup."),
        ("Customer", "That would be great, this is my first time using something like this."),
        ("Agent", "No problem, let's start by setting up your profile."),
        ("Customer", "Okay sounds good, thank you."),
    ],
    "Sales Opportunity — Plan Upgrade Interest": [
        ("Customer", "Hi, I saw the new premium plan online and I'm thinking about upgrading."),
        ("Agent", "That's great to hear! What features are you most interested in?"),
        ("Customer", "I'm curious about the analytics features, what does the plan include?"),
        ("Agent", "The premium plan includes advanced analytics, priority support, and more storage."),
        ("Customer", "That sounds good, I might go ahead and upgrade."),
    ],
}

if __name__ == "__main__":
    # Initialise encoder (loads NLP model, wires up pretty_loguru) silently.
    with _quiet():
        cfg = CLMConfig(lang="en")
        encoder = CLMEncoder(cfg=cfg)
        _ = encoder.ts_encoder

    print("\nCLM Action Matcher — live conversation simulation")
    print(f"Threshold ≥ {DEFAULT_THRESHOLD}  |  Min field types: {DEFAULT_MIN_FIELD_TYPES}")
    print("Weights: domain/intent=3, trigger/service=2, turnType=1")

    for scenario, conversation in CONVERSATIONS.items():
        print(f"\n{'=' * 72}")
        print(f"  SCENARIO: {scenario}")
        print(f"{'=' * 72}")

        total = len(conversation)
        lines: list[str] = []
        for step, (speaker, text) in enumerate(conversation, start=1):
            lines.append(f"{speaker}: {text}")
            transcript_so_far = "\n".join(lines)

            with _quiet():
                signal, results = match_actions(transcript_so_far, text, SAMPLE_CATALOG, encoder)
            display(step, total, speaker, text, signal, results)
