import re
from typing import Optional

from clm_core.components.sys_prompt import Target


def extract_number(text: str, pattern: str) -> Optional[int]:
    """Extract a number from text using a pattern"""
    match = re.search(pattern, text.lower())
    return int(match.group(1)) if match else None


def clean_text(text: str) -> str:
    """Basic text cleaning"""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_target_token(t: Target, omit_default_domain: bool = True) -> str:
    """
    Build compact TARGET token string:
      [TARGET:<TOKEN>[:DOMAIN=...][:K=V...]]

    - omit_default_domain: if True and domain equals default for token, skip printing DOMAIN
    """

    token = (t.token or "UNKNOWN").upper()
    parts = [f"TARGET:{token}"]

    # Domain
    domain = (t.domain or "").upper() if getattr(t, "domain", None) else None
    if domain:
        from .target_normalizer import TargetNormalizer

        default_map = TargetNormalizer.DEFAULT_DOMAIN_MAP
        default_domain = default_map.get(token)
        # include domain only if not default or omit_default_domain == False
        if (
            not omit_default_domain
            or (default_domain is None)
            or (domain != default_domain)
        ):
            parts.append(f"DOMAIN={domain}")

    # Attributes (already normalized)
    attrs = t.attributes or {}
    # deterministic order
    for k in sorted(attrs.keys()):
        v = attrs[k]
        # flatten values to string; if dict/list keep a concise repr
        if isinstance(v, (dict, list)):
            v_str = str(v)
        else:
            v_str = str(v)
        parts.append(f"{k}={v_str}")

    return f"[{':'.join(parts)}]"


def contains_any(text: str, keywords: list[str]) -> bool:
    """Check if text contains any of the keywords"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)
