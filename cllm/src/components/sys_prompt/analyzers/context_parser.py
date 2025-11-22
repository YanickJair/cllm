import re
from spacy import Language
from src.components.sys_prompt._schemas import Context
from src.utils.parser_rules import Rules


class CTXEngine:
    def __init__(self, nlp: Language):
        self.nlp = nlp
        rules = Rules()
        self.compiled = rules.COMPILED

        self.ctx_patterns = {
            "LANGUAGE": [
                (r"\benglish\b", "ENGLISH"),
                (r"\bspanish\b", "SPANISH"),
                (r"\bfrench\b", "FRENCH"),
                (r"\bgerman\b", "GERMAN"),
                (r"\bchinese\b", "CHINESE"),
                (r"\bjapanese\b", "JAPANESE"),
            ],
            "REGION": [
                (r"\b(us|usa|american)\b", "US"),
                (r"\b(uk|british|england)\b", "UK"),
                (r"\b(europe|eu)\b", "EU"),
                (r"\b(apac|asia pacific)\b", "APAC"),
                (r"\bcanada|ca\b", "CA"),
            ],
            "PRIORITY": [
                (r"\burgent\b", "URGENT"),
                (r"\bpriority\b", "HIGH_PRIORITY"),
                (r"\basap\b", "URGENT"),
                (r"\bimmediately\b", "URGENT"),
            ],
            "SLA": [
                (r"\bwithin\s+(\d+)\s*(hours|hrs|h)\b", "SLA_HOURS"),
                (r"\brespond by\b", "SLA_DEADLINE"),
            ],
            "FORMAT": [
                (r"\bbullet(s)?\b", "BULLET_POINTS"),
                (r"\bnumbered\b", "NUMBERED_LIST"),
                (r"\btable\b", "TABLE"),
                (r"\bparagraph\b", "PARAGRAPH"),
            ]
        }

        self.compiled_ctx = {
            ctx: [(re.compile(p, re.I), val) for p, val in pairs]
            for ctx, pairs in self.ctx_patterns.items()
        }

    def parse_contexts(self, text: str) -> list[Context]:
        clean = text.strip()
        text_lower = clean.lower()
        if not self._has_ctx_intent(text_lower):
            return []
        doc = self.nlp(clean)

        contexts: list[Context] = []
        added_aspects = set()

        aud = self._match_single("audience", text_lower)
        if aud:
            contexts.append(Context(aspect="AUDIENCE", value=aud))
            added_aspects.add("AUDIENCE")

        length = self._match_single("length", text_lower)
        if length:
            contexts.append(Context(aspect="LENGTH", value=length))
            added_aspects.add("LENGTH")

        if "LENGTH" not in added_aspects:
            style = self._match_single("style", text_lower)
            if style:
                contexts.append(Context(aspect="STYLE", value=style))
                added_aspects.add("STYLE")

        tone = self._match_single("tone", text_lower)
        if tone:
            contexts.append(Context(aspect="TONE", value=tone))
            added_aspects.add("TONE")

        for aspect, patterns in self.compiled_ctx.items():
            for pat, value in patterns:
                match = pat.search(text_lower)
                if match:
                    contexts.append(Context(aspect=aspect, value=value))
                    break  # 1 match per category

        if "AUDIENCE" not in added_aspects:
            if doc[0].text.lower() == "as" and len(doc) > 2:
                nxt = doc[2].text.lower()
                if nxt in ("manager", "developer", "engineer", "analyst"):
                    contexts.append(Context(aspect="AUDIENCE", value="BUSINESS"))

        unique = []
        seen = set()
        for ctx in contexts:
            key = (ctx.aspect, ctx.value)
            if key not in seen:
                unique.append(ctx)
                seen.add(key)

        return unique

    def _has_ctx_intent(self, text: str) -> bool:
        has_ctx_intent = any(
            kw in text
            for kw in [
                "write", "give", "provide", "explain", "describe",
                "summarize", "make it", "in a", "as a", "keep it",
                "brief", "short", "long", "detailed", "simple", "concise"
            ]
        )

        # Disable CTX if prompt looks like system template / scoring rubric
        if any(marker in text for marker in [
            "output format", "{", "}", "criteria", "scoring", "qa_", "compliance", "policy adherence"
        ]):
            has_ctx_intent = False
        return has_ctx_intent

    def _match_single(self, category: str, text_lower: str):
        matches = [
            (m, span, val)
            for (pat, val) in self.compiled[category]
            for m, span, val in [self._match_any(text_lower, pat, val)]
            if m
        ]
        if not matches:
            return None

        # longest match wins (most specific)
        matches.sort(key=lambda x: x[1][1] - x[1][0], reverse=True)
        return matches[0][2]

    def _match_any(self, text_lower, pat, value):
        m = pat.search(text_lower)
        if m:
            return m.group(0), m.span(), value
        return None, None, None

class ContextParser:
    """
    Unified entrypoint that:
    1. Extracts CTX from text (ContextParser)
    2. Compresses CTX into final token (ContextCompressor)
    """

    def __init__(self, nlp: Language):
        self._engine = CTXEngine(nlp)

    def parse(self, text: str) -> list[Context]:
        return self._engine.parse_contexts(text)