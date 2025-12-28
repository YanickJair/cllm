import re
from typing import Optional

from clm_core.components.sys_prompt import Target
from .target_normalizer import TargetNormalizer


def build_target_token(t: Target, omit_default_domain: bool = True) -> str:
    """
    Build compact TARGET token string:
      [TARGET:<TOKEN>[:DOMAIN=...][:K=V...]]

    - omit_default_domain: if True and domain equals default for token, skip printing DOMAIN
    """

    token = (t.token or "UNKNOWN").upper()
    parts = [f"TARGET:{token}"]

    domain = (t.domain or "").upper() if getattr(t, "domain", None) else None
    if domain:
        default_map = TargetNormalizer.DEFAULT_DOMAIN_MAP
        default_domain = default_map.get(token)

        if (
            not omit_default_domain
            or (default_domain is None)
            or (domain != default_domain)
        ):
            parts.append(f"DOMAIN={domain}")

    attrs = t.attributes or {}
    for k in sorted(attrs.keys()):
        v = attrs[k]
        if isinstance(v, (dict, list)):
            v_str = str(v)
        else:
            v_str = str(v)
        parts.append(f"{k}={v_str}")

    return f"[{':'.join(parts)}]"


class TargetValidator:
    """Validates, deduplicates, and merges target objects"""

    # Specificity by DOMAIN → determines which token is more appropriate
    DOMAIN_SPECIFICITY = {
        "SUPPORT": ["CALL", "AGENT", "MESSAGE", "SYSTEM", "CONTENT"],
        "TECHNICAL": ["CODE", "STACKTRACE", "SYSTEM", "CONTENT"],
        "DOCUMENT": ["DOCUMENT", "CONTENT", "SYSTEM"],
        "BUSINESS": ["REPORT", "CONTENT", "SYSTEM"],
        # fallback
        "DEFAULT": ["CALL", "MESSAGE", "SYSTEM", "CONTENT"],
    }
    TARGET_HIERARCHY = {
        "CALL": ["TRANSCRIPT", "DOCUMENT", "PROCEDURE"],
        "MEETING": ["TRANSCRIPT", "DOCUMENT"],
        "EMAIL": ["DOCUMENT"],
        "CODE": ["DOCUMENT"],
    }

    def __init__(self):
        self.topic_cleaner = TopicCleaner()
        self.normalizer = TargetNormalizer()

    @staticmethod
    def _is_generic_token(token: str) -> bool:
        return token.upper() in {
            "CONCEPT",
            "ANSWER",
            "CONTENT",
            "DOCUMENT",
            "DATA",
            "ITEMS",
            "RESULT",
            "SYSTEM",
        }

    def deduplicate(self, targets: list[Target]) -> list[Target]:
        """
        Clean duplicates and normalize targets.
        Rules:
          - Remove exact duplicates by (token + sorted attributes)
          - Normalize attributes (TargetNormalizer)
          - Prefer specific tokens over generic ones (keep specific if present)
          - Limit to 2 targets max (preserve order of priority)
        """
        if not targets:
            return targets

        normalized = [self.normalizer.normalize(t) for t in targets]

        seen = set()
        unique_targets: list[Target] = []
        for t in normalized:
            sig_attrs = tuple(
                sorted((k, str(v)) for k, v in (t.attributes or {}).items())
            )
            sig = (t.token, t.domain or "", sig_attrs)
            if sig not in seen:
                seen.add(sig)
                unique_targets.append(t)

        has_specific = any(not self._is_generic_token(t.token) for t in unique_targets)
        if has_specific:
            unique_targets = [
                t for t in unique_targets if not self._is_generic_token(t.token)
            ]

        # If more than 2 remain, attempt to pick the most informative:
        # criteria: more attributes > fewer attributes; presence of domain preferred.
        if len(unique_targets) > 2:
            sorted_targets = sorted(
                unique_targets,
                key=lambda x: (len(x.attributes or {}), 1 if x.domain else 0),
                reverse=True,
            )
            unique_targets = sorted_targets[:2]

        tokens_present = {t.token: t for t in unique_targets}
        final_targets = unique_targets.copy()

        for strong, weak_list in self.TARGET_HIERARCHY.items():
            if strong in tokens_present:
                strong_t = tokens_present[strong]
                for weak in weak_list:
                    if weak in tokens_present:
                        weak_t = tokens_present[weak]

                        for k, v in (weak_t.attributes or {}).items():
                            if k not in strong_t.attributes:
                                strong_t.attributes[k] = v

                        if not strong_t.domain and weak_t.domain:
                            strong_t.domain = weak_t.domain

                        final_targets = [t for t in final_targets if t.token != weak]
        return final_targets

    @staticmethod
    def serialize_targets(target: Target, omit_default_domain: bool = True) -> str:
        """
        Convenience: convert normalized targets to compact strings.
        """
        return build_target_token(target, omit_default_domain=omit_default_domain)


class TopicCleaner:
    """Cleans and validates TOPIC attributes"""

    def clean(self, topic: str) -> Optional[str]:
        """Clean topic string"""
        if not topic:
            return None

        # Remove demonstratives
        topic = re.sub(r"\b(this|that|these|those)\b", "", topic, flags=re.IGNORECASE)

        # Remove articles
        topic = re.sub(r"^(the|a|an)\s+", "", topic, flags=re.IGNORECASE)

        # Remove pronouns
        topic = re.sub(r"^(i|we|you|they)\s+", "", topic, flags=re.IGNORECASE)

        # Remove verbs
        action_verbs = ["reduce", "increase", "improve", "explain", "describe"]
        for verb in action_verbs:
            topic = re.sub(rf"\b{verb}\b", "", topic, flags=re.IGNORECASE)

        # Clean up spaces
        topic = re.sub(r"\s+", " ", topic).strip()

        return topic if topic and len(topic) > 1 else None

    def trim(self, topic: str) -> str:
        """Trim topic to prevent greediness (max 4 words)"""
        if not topic:
            return topic

        words = topic.split()

        # Stop at prepositions
        stop_words = ["in", "with", "for", "and", "or"]
        trimmed_words = []
        for word in words:
            if word.lower() in stop_words:
                break
            trimmed_words.append(word)

        # Max 4 words
        if len(trimmed_words) > 4:
            trimmed_words = trimmed_words[:4]

        return " ".join(trimmed_words)

    def validate(self, topic: str) -> Optional[str]:
        """Validate topic quality"""
        if not topic:
            return None

        topic_upper = topic.upper()

        # Reject demonstratives
        if topic_upper in ["THIS", "THAT", "IT", "THE"]:
            return None

        # Reject if starts with THIS_
        if topic_upper.startswith("THIS_"):
            topic = re.sub(r"^THIS_", "", topic, flags=re.IGNORECASE)
            if not topic or len(topic) < 2:
                return None

        # Reject if too short
        if len(topic) < 2:
            return None

        return topic
