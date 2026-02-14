from clm_core.utils.vocabulary import BaseVocabulary
from clm_core.utils.parser_rules import BaseRules
from .en.vocabulary import ENVocabulary
from .en.rules import ENRules
from .es.vocabulary import ESVocabulary
from .es.rules import ESRules
from .pt.vocabulary import PTVocabulary
from .pt.rules import PTRules
from .fr.vocabulary import FRVocabulary
from .fr.rules import FRRules

vocab_map: dict[str, BaseVocabulary] = {
    "en": ENVocabulary(),
    "es": ESVocabulary(),
    "pt": PTVocabulary(),
    "fr": FRVocabulary(),
}

rules_map: dict[str, BaseRules] = {
    "en": ENRules(),
    "es": ESRules(),
    "pt": PTRules(),
    "fr": FRRules(),
}

# Lazy-initialized to avoid circular imports
# (TranscriptPatterns lives under clm_core.components.transcript)
_patterns_map = None


def _build_patterns_map():
    from clm_core.components.transcript.patterns import TranscriptPatterns
    from .en import patterns as en_pat
    from .es import patterns as es_pat
    from .pt import patterns as pt_pat
    from .fr import patterns as fr_pat

    def _build(mod):
        return TranscriptPatterns(
            resolution_keywords=mod.RESOLUTION_KEYWORDS,
            issue_type_keywords=mod.ISSUE_TYPE_KEYWORDS,
            severity_keywords=mod.SEVERITY_KEYWORDS,
            billing_cause_keywords=mod.BILLING_CAUSE_KEYWORDS,
            action_event_map=mod.ACTION_EVENT_MAP,
            action_completion_keywords=mod.ACTION_COMPLETION_KEYWORDS,
            action_completion_phrases=mod.ACTION_COMPLETION_PHRASES,
            action_now_patterns=mod.ACTION_NOW_PATTERNS,
            positive_customer_confirmations=mod.POSITIVE_CUSTOMER_CONFIRMATIONS,
            agent_confirmation_phrases=mod.AGENT_CONFIRMATION_PHRASES,
            issue_confirmation_map=mod.ISSUE_CONFIRMATION_MAP,
            explicit_only_actions=mod.EXPLICIT_ONLY_ACTIONS,
            explicit_action_phrases=mod.EXPLICIT_ACTION_PHRASES,
            technical_issue_map=mod.TECHNICAL_ISSUE_MAP,
            troubleshooting_actions=mod.TROUBLESHOOTING_ACTIONS,
            supported_action_types=mod.SUPPORTED_ACTION_TYPES,
            ner_address_abbreviations=mod.NER_ADDRESS_ABBREVIATIONS,
            emotion_keywords=mod.EMOTION_KEYWORDS,
            day_names=mod.DAY_NAMES,
            word_to_num=mod.WORD_TO_NUM,
            ner_domain_patterns=mod.NER_DOMAIN_PATTERNS,
            action_tokens=getattr(mod, "ACTION_TOKENS", {}),
            promise_commitment_tokens=getattr(mod, "PROMISE_COMMITMENT_TOKENS", {}),
            refund_status_tokens=getattr(mod, "REFUND_STATUS_TOKENS", {}),
            refund_method_tokens=getattr(mod, "REFUND_METHOD_TOKENS", {}),
            timeline_event_tokens=getattr(mod, "TIMELINE_EVENT_TOKENS", {}),
            resolution_state_tokens=getattr(mod, "RESOLUTION_STATE_TOKENS", {}),
            customer_satisfaction_tokens=getattr(
                mod, "CUSTOMER_SATISFACTION_TOKENS", {}
            ),
            follow_up_needed_tokens=getattr(mod, "FOLLOW_UP_NEEDED_TOKENS", {}),
            timeline_keywords=getattr(mod, "TIMELINE_KEYWORDS", {}),
            timeline_patterns=getattr(mod, "TIMELINE_PATTERNS", []),
            promise_confidence_strong=getattr(mod, "PROMISE_CONFIDENCE_STRONG", []),
            disputed_amount_keywords=getattr(mod, "DISPUTED_AMOUNT_KEYWORDS", []),
        )

    return {
        "en": _build(en_pat),
        "es": _build(es_pat),
        "pt": _build(pt_pat),
        "fr": _build(fr_pat),
    }


def get_patterns_map():
    global _patterns_map
    if _patterns_map is None:
        _patterns_map = _build_patterns_map()
    return _patterns_map


# For backwards-compatible dict-style access
class _PatternsMapProxy:
    def __getitem__(self, key):
        return get_patterns_map()[key]

    def __contains__(self, key):
        return key in get_patterns_map()

    def keys(self):
        return get_patterns_map().keys()


patterns_map = _PatternsMapProxy()

__all__ = ["vocab_map", "rules_map", "patterns_map"]
