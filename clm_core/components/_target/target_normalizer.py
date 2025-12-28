from typing import Dict, Set, List
from clm_core.components.sys_prompt import Target


class TargetNormalizer:
    """
    Normalizes OR aggregates multiple extracted Target objects.

    If passed a single Target -> behaves like before.
    If passed a list of Targets -> merges them, picks a primary, normalizes.
    """

    PRIORITY = [
        "TRANSCRIPT",
        "CALL",
        "MEETING",
        "TICKET",
        "EMAIL",
        "REPORT",
        "DOCUMENT",
        "CODE",
        "DATA",
        "QUERY",
        "CONTENT",
        "ITEMS",
        "RESULT",
        "ANSWER",
        "CONCEPT",
    ]

    ALLOWED: Dict[str, Set[str]] = {
        "CALL": {"DURATION", "LANG"},
        "TRANSCRIPT": {"DURATION", "PARTICIPANTS"},
        "EMAIL": {"PRIORITY"},
        "DATA": {"FORMAT", "SIZE", "ROWS"},
        "CODE": {"LANG", "FILE_TYPE"},
        "DOCUMENT": {"SUBJECT"},
        "CONTENT": {"SUBJECT", "FORMAT"},
        "TICKET": {"STATUS", "ISSUE", "PRIORITY"},
        "CONCEPT": {"TOPIC"},
        "ANSWER": set(),
        "ITEMS": {"SUBJECT"},
        "RESULT": {"TYPE"},
        "QUERY": {"LANG", "FORMAT"},
    }

    BANNED = {"CONTEXT", "TOPIC_HINT", "RAW", "FORMAT_HINT", "CTX", "REQ"}

    DEFAULT_DOMAIN_MAP = {
        "CALL": "SUPPORT",
        "TICKET": "SUPPORT",
    }

    def normalize_many(self, targets: List[Target]) -> Target:
        """Entry point: accepts many Targets and returns exactly one or None."""
        if not targets:
            return None

        primary = self._pick_primary(targets)

        merged_attrs = dict(primary.attributes or {})

        for t in targets:
            if t is primary:
                continue
            for k, v in (t.attributes or {}).items():
                if k not in merged_attrs:
                    merged_attrs[k] = v

        domains = {t.domain for t in targets if t.domain}
        primary.domain = primary.domain or (domains.pop() if domains else None)

        if "DOMAIN" in merged_attrs:
            merged_attrs.pop("DOMAIN")

        primary.attributes = merged_attrs
        return self.normalize(primary)

    def normalize(self, t: Target) -> Target:
        """
        Backwards-compatible: normalize a SINGLE Target.
        Called internally after merging.
        """

        token = (t.token or "").upper().strip()
        t.token = token

        if isinstance(t.domain, str) and t.domain:
            t.domain = t.domain.upper().strip()
        else:
            t.domain = None

        raw_attrs = t.attributes or {}
        cleaned = {}
        if t.domain:
            cleaned["DOMAIN"] = t.domain.upper()

        allowed = self.ALLOWED.get(token, set())

        for k, v in raw_attrs.items():
            if not k:
                continue
            kuk = k.upper().strip()

            if kuk in self.BANNED:
                continue

            if isinstance(v, str) and v.upper().strip() == token:
                continue

            if allowed and kuk not in allowed:
                continue

            cleaned[kuk] = v

        t.attributes = cleaned
        return t

    def _pick_primary(self, targets: List[Target]) -> Target:
        """
        Select the best target according to PRIORITY list.
        """

        def score(target: Target):
            try:
                return self.PRIORITY.index(target.token.upper())
            except ValueError:
                return 999

        return sorted(targets, key=score)[0]
