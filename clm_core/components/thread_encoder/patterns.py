"""
TranscriptPatterns dataclass — bundles every language-specific constant
needed by the thread_encoder analyzer and encoder into a single object.
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

    # Speaker label detection
    agent_speaker_labels: list[str] = field(default_factory=list)
    customer_speaker_labels: list[str] = field(default_factory=list)

    # Amount reason context mapping: list of (keyword, reason_code) tuples
    amount_reason_context: list[tuple] = field(default_factory=list)

    # Billing period context: checked against a narrow (30-char) suffix window
    # after each monetary amount to capture MONTH/YEAR pricing reason codes.
    billing_period_context: list[tuple] = field(default_factory=list)

    # Redacted field context mapping: list of (keyword, field_token) tuples
    redacted_field_context: list[tuple] = field(default_factory=list)

    # Call type detection
    call_type_sales_keywords: list[str] = field(default_factory=list)

    # Name extraction patterns (regex strings)
    name_intro_patterns: list[str] = field(default_factory=list)
    name_thanks_patterns: list[str] = field(default_factory=list)
    name_change_patterns: list[str] = field(default_factory=list)
    agent_name_patterns: list[str] = field(default_factory=list)

    # Delay context words (for DELAY_N_DAYS context detection)
    delay_context_words: list[str] = field(default_factory=list)

    # Extra commitment patterns: dict of commitment_type -> list of phrases
    extra_commitment_patterns: dict[str, list[str]] = field(default_factory=dict)

    # Promise timeline patterns: list of (regex, format_string) tuples
    promise_timeline_patterns: list[tuple] = field(default_factory=list)
