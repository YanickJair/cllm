from typing import Annotated

from annotated_doc import Doc

from clm_core.components.thread_encoder import Turn
from clm_core.components.thread_encoder.patterns import TranscriptPatterns


def detect_format(
    transcript: Annotated[
        str,
        Doc("""
        Raw transcript or free-form text to classify.

        The function examines each non-empty line for a recognized speaker prefix
        (`"Agent:"`, `"Customer:"`, etc.) derived from the active language patterns.
        If at least 50% of lines carry such a prefix the transcript is classified as
        `"turns"`; otherwise it is classified as `"free_form"`. An empty string always
        returns `"free_form"`.
        """),
    ],
    patterns: Annotated[
        TranscriptPatterns,
        Doc("""
        Language-specific patterns used to derive the set of recognized speaker labels.

        `patterns.agent_speaker_labels` and `patterns.customer_speaker_labels` are
        combined to form the label set. Falls back to `["agent"]` / `["customer"]`
        when either attribute is empty.
        """),
    ],
) -> str:
    """Classify a transcript as `'turns'` or `'free_form'`.

    Returns `'turns'` when at least 50% of non-empty lines carry a recognized
    speaker prefix, `'free_form'` otherwise.
    """
    lines = [l for l in transcript.strip().splitlines() if l.strip()]
    if not lines:
        return "free_form"
    agent_labels = patterns.agent_speaker_labels or ["agent"]
    customer_labels = patterns.customer_speaker_labels or ["customer"]
    all_labels = agent_labels + customer_labels

    def is_labeled(line: str) -> bool:
        if ":" not in line:
            return False
        prefix = line.split(":", 1)[0].strip().lower()
        return any(label in prefix for label in all_labels)

    labeled = sum(1 for l in lines if is_labeled(l))
    return "turns" if labeled / len(lines) >= 0.5 else "free_form"


def split_free_form(
    text: Annotated[
        str,
        Doc("""
        Unstructured text to split into turns.

        Blank-line-separated paragraphs are preferred as chunk boundaries. When the
        text contains no blank lines (only one paragraph), the function falls back to
        splitting on individual lines. Empty lines and whitespace-only lines are
        excluded from the output.
        """),
    ],
) -> list[Turn]:
    """Split unstructured text into a list of `Turn` objects.

    Each chunk becomes a `Turn` with `speaker='unknown'`. The caller is responsible
    for normalizing speaker roles before passing turns to the analyzer.
    """
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    if len(chunks) <= 1:
        chunks = [l.strip() for l in text.splitlines() if l.strip()]
    return [Turn(speaker="unknown", text=chunk) for chunk in chunks]
