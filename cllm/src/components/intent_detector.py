import re
from typing import List, Optional
from spacy import Language
from spacy.tokens import Doc
from src.utils.vocabulary import BaseVocabulary
from src.components.sys_prompt import Intent


class IntentDetector:
    """
    High-precision, generic REQ detector.
    Features:
        - Robust synonym detection
        - Root verb fallback
        - Multi-REQ only if "and" is explicitly used
        - Strict RANK trigger (prevents false positives)
        - spaCy lemma matching
        - Supports multi-word synonyms
    """

    def __init__(self, nlp: Language, vocab: BaseVocabulary):
        self.nlp = nlp
        self.vocab = vocab
        self.syn_index = self._build_reverse_index()

    def _build_reverse_index(self):
        index = {}
        for action, synonyms in self.vocab.REQ_TOKENS.items():
            for syn in synonyms:
                syn = syn.lower().strip()
                index[syn] = action
        return index

    def detect(self, text: str, context: str = "") -> List[Intent]:
        text_lower = text.lower().strip()
        doc = self.nlp(text_lower)

        multi = self._detect_multiple_explicit(text_lower, doc)
        if multi:
            return multi

        direct = self._detect_direct_synonym(text_lower, doc)
        if direct:
            return [direct]

        imp = self._detect_imperative(doc)
        if imp:
            return [imp]

        root_req = self._detect_root_based(doc)
        if root_req:
            return [root_req]

        q = self.vocab.get_question_req(text=text_lower)
        if q:
            return [Intent(token=q, confidence=0.7, trigger_word="question")]

        return []

    def _detect_multiple_explicit(self, text_lower: str, doc: Doc):
        """
        Detect multiple REQs only when user explicitly writes multiple actions with 'and'.
        Returns a list of unique Intent objects (no repeated tokens), preserving first-seen order.
        Examples:
          "analyze and summarize" -> [ANALYZE, SUMMARIZE]
          "analyze and assess"   -> [ANALYZE]  (assess maps to ANALYZE)
        """
        parts = [
            p.strip() for p in re.split(r"\s+and\s+|\s*,\s*", text_lower) if p.strip()
        ]
        if len(parts) < 2:
            return None

        seen_tokens = set()
        unique_intents = []

        for part in parts:
            part_doc = self.nlp(part)

            req = self._detect_direct_synonym(part, part_doc)
            if not req:
                req = self._detect_imperative(part_doc) or self._detect_root_based(
                    part_doc
                )

            if not req:
                continue

            if req.token not in seen_tokens:
                seen_tokens.add(req.token)
                unique_intents.append(req)

        return unique_intents if len(unique_intents) >= 2 else None

    def _detect_direct_synonym(self, text_lower: str, doc):
        """
        Three-stage matching:
            1. Multi-word phrase match
            2. Lemma match via spaCy tokens
            3. Whole-word regex match
        """

        for syn, action in self.syn_index.items():
            if " " in syn and syn in text_lower:
                if action == "FORMAT":
                    if self._should_ignore_format(doc, text_lower):
                        continue
                if action == "RANK" and not self._explicit_rank(text_lower):
                    continue
                return Intent(token=action, confidence=1.0, trigger_word=syn)

        for tok in doc:
            lemma = tok.lemma_.lower()
            if lemma in self.syn_index:
                action = self.syn_index[lemma]
                if action == "FORMAT" and self._should_ignore_format(doc, text_lower):
                    continue
                if action == "RANK" and not self._explicit_rank(text_lower):
                    continue
                return Intent(token=action, confidence=0.95, trigger_word=tok.text)

        for syn, action in self.syn_index.items():
            if " " not in syn:
                if re.search(rf"\b{re.escape(syn)}\b", text_lower):
                    if action == "FORMAT" and self._should_ignore_format(
                        doc, text_lower
                    ):
                        continue
                    if action == "RANK" and not self._explicit_rank(text_lower):
                        continue
                    return Intent(token=action, confidence=0.9, trigger_word=syn)
        return None

    def _detect_imperative(self, doc):
        first = doc[0]
        if first.pos_ == "VERB" or "VerbForm=Imp" in first.morph:
            lemma = first.lemma_.lower()
            if lemma in self.syn_index:
                action = self.syn_index[lemma]
                if action == "RANK":
                    if not self._explicit_rank(doc.text.lower()):
                        return None
                return Intent(token=action, confidence=0.92, trigger_word=first.text)
        return None

    def _detect_root_based(self, doc):
        root = next((t for t in doc if t.dep_ == "ROOT"), None)
        if not root:
            return None

        lemma = root.lemma_.lower()
        if lemma in self.syn_index:
            action = self.syn_index[lemma]
            if action == "RANK" and not self._explicit_rank(doc.text.lower()):
                return None
            return Intent(token=action, confidence=0.88, trigger_word=root.text)

        return None

    def _explicit_rank(self, text_lower: str) -> bool:
        return any(trg in text_lower for trg in self.vocab.rank_triggers)

    @staticmethod
    def get_primary_intent(intents: List[Intent]) -> Optional[Intent]:
        return intents[0] if intents else None

    @staticmethod
    def _is_action_usage(tok):
        """
        A word like 'format' or 'structure' appears in many non-action contexts.
        This function ensures FORMAT is only triggered when used as an actual verb.

        :param tok: The spaCy token object.
        :return: True if the token is an action usage, False otherwise.
        """
        if tok.pos_ == "VERB":
            return True

        if tok.pos_ in {"NOUN", "ADJ"}:
            return False
        return True

    def _should_ignore_format(self, doc: Doc, text_lower: str) -> bool:
        """
        FORMAT should only trigger when used as an actual verb.
        This checks whether 'format' or FORMAT synonyms appear as noun/adj descriptors.

        :param doc: The spaCy document object.
        :param text_lower: The lowercased text of the document.
        :return: True if FORMAT should be ignored, False otherwise.

        Examples:
        - "format the data" should trigger FORMAT
        - "the formatted data" should not trigger FORMAT
        """
        format_synonyms = self.vocab.REQ_TOKENS.get("FORMAT", [])

        for tok in doc:
            if tok.lemma_.lower() in format_synonyms:
                if tok.pos_ != "VERB":
                    return True
        return False
