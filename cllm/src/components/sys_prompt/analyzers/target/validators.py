import re
from typing import Optional

from src.components.sys_prompt import Target


class TargetValidator:
    """Validates, deduplicates, and merges target objects"""

    # Specificity by DOMAIN → determines which token is more appropriate
    DOMAIN_SPECIFICITY = {
        "SUPPORT":     ["CALL", "AGENT", "MESSAGE", "SYSTEM", "CONTENT"],
        "TECHNICAL":   ["CODE", "STACKTRACE", "SYSTEM", "CONTENT"],
        "DOCUMENT":    ["DOCUMENT", "CONTENT", "SYSTEM"],
        "BUSINESS":    ["REPORT", "CONTENT", "SYSTEM"],
        # fallback
        "DEFAULT":     ["CALL", "MESSAGE", "SYSTEM", "CONTENT"],
    }

    def __init__(self):
        self.topic_cleaner = TopicCleaner()

    def deduplicate(self, targets: list[Target]) -> list[Target]:
        if not targets:
            return targets

        # Remove exact duplicates
        seen = set()
        unique = []
        for t in targets:
            sig = (t.token, tuple(sorted((t.attributes or {}).items())))
            if sig not in seen:
                seen.add(sig)
                unique.append(t)

        if len(unique) <= 1:
            return unique

        # Group by semantic identity: same DOMAIN + same CONTEXT (if present)
        groups = {}
        for t in unique:
            domain = (t.domain or "").upper()
            ctx = (t.attributes or {}).get("CONTEXT", "").upper()
            groups.setdefault((domain, ctx), []).append(t)

        final_targets = []

        # For each group → choose the best target
        for (domain, ctx), group in groups.items():

            if len(group) == 1:
                final_targets.append(group[0])
                continue

            specificity = self.DOMAIN_SPECIFICITY.get(domain, self.DOMAIN_SPECIFICITY["DEFAULT"])
            group_sorted = sorted(
                group,
                key=lambda t: specificity.index(t.token) if t.token in specificity else 999
            )

            winner = group_sorted[0]

            merged_attributes = winner.attributes.copy() if winner.attributes else {}
            for t in group_sorted[1:]:
                if t.attributes:
                    for k, v in t.attributes.items():
                        if k not in merged_attributes:
                            merged_attributes[k] = v

            winner.attributes = merged_attributes
            final_targets.append(winner)

        return final_targets[:2]


class TopicCleaner:
    """Cleans and validates TOPIC attributes"""

    def clean(self, topic: str) -> Optional[str]:
        """Clean topic string"""
        if not topic:
            return None

        # Remove demonstratives
        topic = re.sub(r'\b(this|that|these|those)\b', '', topic, flags=re.IGNORECASE)

        # Remove articles
        topic = re.sub(r'^(the|a|an)\s+', '', topic, flags=re.IGNORECASE)

        # Remove pronouns
        topic = re.sub(r'^(i|we|you|they)\s+', '', topic, flags=re.IGNORECASE)

        # Remove verbs
        action_verbs = ['reduce', 'increase', 'improve', 'explain', 'describe']
        for verb in action_verbs:
            topic = re.sub(rf'\b{verb}\b', '', topic, flags=re.IGNORECASE)

        # Clean up spaces
        topic = re.sub(r'\s+', ' ', topic).strip()

        return topic if topic and len(topic) > 1 else None

    def trim(self, topic: str) -> str:
        """Trim topic to prevent greediness (max 4 words)"""
        if not topic:
            return topic

        words = topic.split()

        # Stop at prepositions
        stop_words = ['in', 'with', 'for', 'and', 'or']
        trimmed_words = []
        for word in words:
            if word.lower() in stop_words:
                break
            trimmed_words.append(word)

        # Max 4 words
        if len(trimmed_words) > 4:
            trimmed_words = trimmed_words[:4]

        return ' '.join(trimmed_words)

    def validate(self, topic: str) -> Optional[str]:
        """Validate topic quality"""
        if not topic:
            return None

        topic_upper = topic.upper()

        # Reject demonstratives
        if topic_upper in ['THIS', 'THAT', 'IT', 'THE']:
            return None

        # Reject if starts with THIS_
        if topic_upper.startswith('THIS_'):
            topic = re.sub(r'^THIS_', '', topic, flags=re.IGNORECASE)
            if not topic or len(topic) < 2:
                return None

        # Reject if too short
        if len(topic) < 2:
            return None

        return topic