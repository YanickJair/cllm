import re
from spacy import Language

from clm_core.utils.parser_rules import BaseRules
from clm_core.utils.vocabulary import BaseVocabulary


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

    def __init__(self, *, nlp: Language, vocab: BaseVocabulary, rules: BaseRules):
        self.nlp = nlp
        self._vocab = vocab
        self._rules = rules

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
        scores = dict.fromkeys(self._vocab.domain_candidates, 0)
        for domain, words in self._vocab.domain_candidates.items():
            for w in words:
                if w in text:
                    scores[domain] += 1
        return scores

    def _score_regex(self, text: str) -> dict:
        scores = dict.fromkeys(self._rules.DOMAIN_REGEX, 0)
        for domain, pattern in self._rules.DOMAIN_REGEX.items():
            if re.search(pattern, text):
                scores[domain] += 2
        return scores

    def _score_semantic(self, doc) -> dict:
        scores = dict.fromkeys(self._vocab.domain_candidates, 0.0)

        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            for domain, words in self._vocab.domain_candidates.items():
                if any(w in chunk_text for w in words):
                    scores[domain] += 1.5

        return self._assign_semantic_score(doc, scores)

    def _assign_semantic_score(self, doc, scores: dict) -> dict:
        for tok in doc:
            if tok.pos_ == "VERB":
                lemma = tok.lemma_.lower()
                if lemma in self._vocab.default_technical_lemmas:
                    scores["TECHNICAL"] += 1.5
                if lemma in self._vocab.default_finance_lemmas:
                    scores["FINANCE"] += 1.5
                if lemma in self._vocab.default_support_lemmas:
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
        if all(score == 0 for score in scores.values()):
            return "DEFAULT", 0.0

        highest = max(scores.values())
        candidates = [d for d, s in scores.items() if s == highest]

        if len(candidates) > 1:
            for dom in self._vocab.domains_priority:
                if dom in candidates:
                    return dom, highest
            return candidates[0], highest

        return candidates[0], highest
