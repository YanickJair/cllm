"""
Utility functions for target extraction
"""

import re
from typing import Optional


def extract_number(text: str, pattern: str) -> Optional[int]:
    """Extract a number from text using a pattern"""
    match = re.search(pattern, text.lower())
    return int(match.group(1)) if match else None


def clean_text(text: str) -> str:
    """Basic text cleaning"""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def contains_any(text: str, keywords: list[str]) -> bool:
    """Check if text contains any of the keywords"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)