import re
from spacy import Language


class DomainDetector:
    """
    Determines the domain of a user query using:
    - spaCy semantic cues
    - noun chunks
    - verb lemmas
    - keyword patterns
    - fallback heuristics

    Output:
        (domain: str, confidence: float)
    """

    DOMAIN_KEYWORDS = {
        "SUPPORT": [
            "ticket", "case", "customer", "support", "call", "complaint",
            "csr", "agent", "caller", "chat", "inquiry", "troubleshoot"
        ],
        "TECHNICAL": [
            "bug", "error", "stacktrace", "exception", "api", "server",
            "log", "debug", "traceback", "crash", "deployment", "backend"
        ],
        "DOCUMENT": [
            "document", "article", "manual", "guide", "doc", "writeup",
            "transcript", "notes", "summary", "instructions"
        ],
        "BUSINESS": [
            "report", "briefing", "analysis", "executive", "management",
            "dashboard", "kpi", "roi", "funnel", "quarterly", "presentation"
        ],
        "LEGAL": [
            "contract", "policy", "compliance", "gdpr", "clause", "lawyer",
            "agreement", "terms", "privacy"
        ],
        "FINANCE": [
            "invoice", "billing", "payment", "transaction", "refund",
            "expense", "balance", "statement", "amount"
        ],
        "SECURITY": [
            "breach", "risk", "threat", "alert", "malware", "phishing",
            "permissions", "access control", "audit"
        ],
        "MEDICAL": [
            "patient", "diagnosis", "prescription", "clinical", "chart",
            "symptoms", "treatment", "doctor"
        ],
        "SALES": [
            "lead", "crm", "opportunity", "pipeline", "account manager",
            "prospect", "deal", "quote"
        ],
        "EDUCATION": [
            "lesson", "curriculum", "teacher", "student", "training",
            "course", "learning"
        ],
    }

    DOMAIN_REGEX = {
        "SUPPORT": r"\b(call|ticket|csr|customer|support|helpdesk)\b",
        "TECHNICAL": r"\b(error|bug|crash|stacktrace|api|debug|server|exception)\b",
        "DOCUMENT": r"\b(document|article|manual|writeup|transcript)\b",
        "BUSINESS": r"\b(report|executive|analysis|kpi|dashboard)\b",
        "LEGAL": r"\b(contract|policy|compliance|clause|gdpr)\b",
        "FINANCE": r"\b(invoice|billing|payment|refund|transaction)\b",
        "SECURITY": r"\b(breach|threat|risk|malware|audit)\b",
        "MEDICAL": r"\b(patient|clinical|diagnosis|treatment)\b",
        "SALES": r"\b(lead|crm|opportunity|prospect)\b",
        "EDUCATION": r"\b(lesson|teacher|student|curriculum)\b",
    }

    # domain priority for tie-breaking
    PRIORITY = [
        "SUPPORT",
        "TECHNICAL",
        "FINANCE",
        "SECURITY",
        "LEGAL",
        "BUSINESS",
        "DOCUMENT",
        "SALES",
        "EDUCATION",
        "MEDICAL",
    ]

    def __init__(self, nlp: Language):
        self.nlp = nlp

    def detect(self, text: str) -> tuple[str, float]:
        """
        Returns (domain, confidence).
        """

        clean = text.strip().lower()
        doc = self.nlp(clean)

        kw_scores = self._score_keyword_matches(clean)
        rg_scores = self._score_regex(clean)
        sem_scores = self._score_semantic(doc)
        final_scores = self._merge_scores(kw_scores, rg_scores, sem_scores)
        domain, confidence = self._pick_best(final_scores)

        return domain, confidence

    def _score_keyword_matches(self, text: str) -> dict:
        scores = {domain: 0 for domain in self.DOMAIN_KEYWORDS}
        for domain, words in self.DOMAIN_KEYWORDS.items():
            for w in words:
                if w in text:
                    scores[domain] += 1
        return scores

    def _score_regex(self, text: str) -> dict:
        scores = {domain: 0 for domain in self.DOMAIN_REGEX}
        for domain, pattern in self.DOMAIN_REGEX.items():
            if re.search(pattern, text):
                scores[domain] += 2   # regex → higher weight
        return scores

    def _score_semantic(self, doc) -> dict:
        scores = {domain: 0.0 for domain in self.DOMAIN_KEYWORDS}

        # Noun chunks
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            for domain, words in self.DOMAIN_KEYWORDS.items():
                if any(w in chunk_text for w in words):
                    scores[domain] += 1.5

        # Verb lemmas
        for tok in doc:
            if tok.pos_ == "VERB":
                lemma = tok.lemma_.lower()
                if lemma in {"debug", "fix", "deploy", "compile"}:
                    scores["TECHNICAL"] += 1.5
                if lemma in {"refund", "pay", "charge"}:
                    scores["FINANCE"] += 1.5
                if lemma in {"escalate", "assist"}:
                    scores["SUPPORT"] += 1.5

        return scores

    @staticmethod
    def _merge_scores(*score_dicts):
        merged = {}
        for d in score_dicts:
            for domain, score in d.items():
                merged[domain] = merged.get(domain, 0) + score
        return merged

    def _pick_best(self, scores: dict) -> tuple[str, float]:
        # If all zero → default
        if all(score == 0 for score in scores.values()):
            return "DEFAULT", 0.0

        # Find max score
        highest = max(scores.values())
        candidates = [d for d, s in scores.items() if s == highest]

        # If multiple → tie-break by PRIORITY order
        if len(candidates) > 1:
            for dom in self.PRIORITY:
                if dom in candidates:
                    return dom, highest
            return candidates[0], highest  # fallback

        return candidates[0], highest
