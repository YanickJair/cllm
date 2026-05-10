import re
from typing import Optional, Annotated

from annotated_doc import Doc
from thread_encoder.components.sys_prompt import Target


def extract_number(
    text: Annotated[str, Doc("Input text to search for a numeric match.")],
    pattern: Annotated[
        str,
        Doc("Regex pattern with a capture group that matches the digit(s) to extract."),
    ],
) -> Optional[int]:
    """Extract a number from text using a pattern."""
    match = re.search(pattern, text.lower())
    return int(match.group(1)) if match else None


def clean_text(
    text: Annotated[
        str,
        Doc("Text to clean by collapsing consecutive whitespace into a single space."),
    ],
) -> str:
    """Basic text cleaning."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_target_token(
    t: Annotated[
        Target, Doc("The Target object to serialize into a compact token string.")
    ],
    omit_default_domain: Annotated[
        bool,
        Doc(
            "When True, the DOMAIN attribute is omitted if it equals the default domain for the token type."
        ),
    ] = True,
) -> str:
    """
    Build compact TARGET token string:
      [TARGET:<TOKEN>[:DOMAIN=...][:K=V...]]

    - omit_default_domain: if True and domain equals default for token, skip printing DOMAIN
    """

    token = (t.token or "UNKNOWN").upper()
    parts = [f"TARGET:{token}"]

    domain = (t.domain or "").upper() if getattr(t, "domain", None) else None
    if domain:
        from .target_normalizer import TargetNormalizer

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


def contains_any(
    text: Annotated[str, Doc("Input text to search.")],
    keywords: Annotated[
        list[str],
        Doc(
            "List of keyword strings to look for (case-insensitive comparison against lowercased text)."
        ),
    ],
) -> bool:
    """Check if text contains any of the keywords."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)
