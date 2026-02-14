"""
TranscriptPatterns dataclass — bundles every language-specific constant
needed by the transcript analyzer and encoder into a single object.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TranscriptPatterns:
    # Resolution / issue / severity keyword dicts
    resolution_keywords: dict[str, set] = field(default_factory=dict)
    issue_type_keywords: dict[str, set] = field(default_factory=dict)
    severity_keywords: dict[str, set] = field(default_factory=dict)
    billing_cause_keywords: dict[str, set] = field(default_factory=dict)

    # Action-related
    action_event_map: dict[str, str] = field(default_factory=dict)
    action_completion_keywords: set = field(default_factory=set)
    action_completion_phrases: set = field(default_factory=set)
    action_now_patterns: list[str] = field(default_factory=list)

    # Confirmation
    positive_customer_confirmations: set = field(default_factory=set)
    agent_confirmation_phrases: set = field(default_factory=set)
    issue_confirmation_map: dict[str, set] = field(default_factory=dict)

    # Explicit actions
    explicit_only_actions: set = field(default_factory=set)
    explicit_action_phrases: dict[str, set] = field(default_factory=dict)

    # Technical / troubleshooting
    technical_issue_map: dict[str, list] = field(default_factory=dict)
    troubleshooting_actions: dict[str, set] = field(default_factory=dict)

    # Supported action types
    supported_action_types: set = field(default_factory=set)

    # NER address abbreviations (used by encoder)
    ner_address_abbreviations: dict[str, str] = field(default_factory=dict)

    # Emotion keywords (used by sentiment analyzer)
    emotion_keywords: dict = field(default_factory=dict)

    # Temporal (used by temporal analyzer)
    day_names: dict[str, str] = field(default_factory=dict)
    word_to_num: dict[str, int] = field(default_factory=dict)

    # NER domain patterns (used by entity extractor)
    ner_domain_patterns: dict[str, list] = field(default_factory=dict)

    # Language-specific vocabulary tokens (override English defaults in TranscriptVocabulary)
    action_tokens: dict[str, list[str]] = field(default_factory=dict)
    promise_commitment_tokens: dict[str, list[str]] = field(default_factory=dict)
    refund_status_tokens: dict[str, list[str]] = field(default_factory=dict)
    refund_method_tokens: dict[str, list[str]] = field(default_factory=dict)
    timeline_event_tokens: dict[str, list[str]] = field(default_factory=dict)
    resolution_state_tokens: dict[str, list[str]] = field(default_factory=dict)
    customer_satisfaction_tokens: dict[str, list[str]] = field(default_factory=dict)
    follow_up_needed_tokens: dict[str, list[str]] = field(default_factory=dict)
    timeline_keywords: dict[str, str] = field(default_factory=dict)
    timeline_patterns: list[tuple[str, str]] = field(default_factory=list)
    promise_confidence_strong: list[str] = field(default_factory=list)
    disputed_amount_keywords: list[str] = field(default_factory=list)
