"""
CLM-driven action matcher.

Given a turn and a catalog of actions (each with a structured `match` block),
this script encodes the turn through CLM and scores each catalog entry
deterministically — no LLM call needed for the routine case.

The catalog schema mirrors what CLM already produces:
  domain, service, customerIntent, supportTrigger, turnTypes

Callers own the catalog; CLM owns the signal extraction.
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
def extract_signal(turn_text: str, encoder: CLMEncoder) -> TurnSignal:
    out = encoder.ts_encoder.encode(thread=turn_text, is_turn=False, metadata={})
    d = out.to_dict()

    # Turn type: call the classifier directly so the encoder's conservative
    # reporting threshold (0.6) does not suppress supporting signals here.
    # Any non-NEUTRAL result is used; the +1 weight keeps it from overriding
    # strong semantic matches.
    turn_type: TurnType | None = None
    turn_confidence = 0.0
    clf: TurnClassifier = encoder.ts_encoder._turn_classifier
    raw_tt, raw_conf = clf.classify(turn_text)
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
    turn_text: str,
    catalog: list[dict],
    encoder: CLMEncoder,
    threshold: int = DEFAULT_THRESHOLD,
    min_field_types: int = DEFAULT_MIN_FIELD_TYPES,
) -> tuple[TurnSignal, list[MatchResult]]:
    signal = extract_signal(turn_text, encoder)
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
def display(turn_text: str, signal: TurnSignal, results: list[MatchResult]) -> None:
    tt_str = (
        f"{signal.turn_type.value} ({signal.turn_confidence:.0%})"
        if signal.turn_type else "—"
    )
    print(f"\n{'─' * 72}")
    print(f"  Turn   : {turn_text}")
    print(
        f"  CLM    : domain={signal.domain or '—'}  "
        f"intent={signal.customer_intent or '—'}  "
        f"trigger={signal.support_trigger or '—'}  "
        f"service={signal.service or '—'}"
    )
    print(f"  TurnType: {tt_str}")
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
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Initialise encoder (loads NLP model, wires up pretty_loguru) silently.
    with _quiet():
        cfg = CLMConfig(lang="en")
        encoder = CLMEncoder(cfg=cfg)
        _ = encoder.ts_encoder

    turns = [
        # Semantic signal dominant
        "I noticed my account was charged twice this month — one on the 2nd and another on the 3rd.",
        "I'm calling to complain about a duplicated charge on my account. I need this fixed immediately.",
        # Classifier signal dominant (CLM can't classify domain/intent)
        "I just signed up and I have no idea how to get started, can you walk me through it?",
        "I'm thinking of leaving. This isn't really what I expected.",
        # Mixed
        "I want to cancel my subscription right now, this service is terrible.",
        "Why can't I log into my account? I keep getting an error message.",
        "Your agent promised me a refund two weeks ago and I still haven't received anything.",
        "I saw that thing online, the new iPhone. I was thinking about buying it maybe",
        # Turn-type dominant: opening/closing pleasantries
        "Hi, this is Sarah calling about my order.",
        "Thanks so much for your help today, take care, goodbye!",
    ]

    print("\nCLM Action Matcher")
    print(f"Threshold ≥ {DEFAULT_THRESHOLD}  |  Min field types: {DEFAULT_MIN_FIELD_TYPES}")
    print("Weights: domain/intent=3, trigger/service=2, turnType=1")

    for turn in turns:
        with _quiet():
            signal, results = match_actions(turn, SAMPLE_CATALOG, encoder)
        display(turn, signal, results)
