import re
from spacy import Language
from clm_core.utils.vocabulary import BaseVocabulary
from clm_core.components.sys_prompt import (
    Intent,
    VOCAB_SIGNAL_MAP,
    REQ,
    Signal,
    Artifact,
)


class _SPECDetector:
    """
    SPEC extraction is conservative by design; expand only in response to real misses.
    """

    # High-precision explicit artifact extraction.
    # Intentionally conservative to avoid SPEC pollution.
    EXPLICIT_OUTPUT_PATTERNS = [
        re.compile(
            r"(?:generate|return|provide|output|produce)\s+(?:a|an|the)?\s*([a-zA-Z_ ]{2,40})",
            re.IGNORECASE,
        )
    ]
    # Non-domain specs represent format or mathematical shape,
    # never primary domain artifacts.
    NON_DOMAIN_SPECS = {
        "JSON_OBJECT",
        "JSON_SCHEMA",
        "PROBABILITY_DISTRIBUTION",
    }
    SPEC_KEYWORDS = {
        "BETTING_ODDS": ["odds", "betting", "bookmaker"],
        "FORECAST": ["forecast", "projection"],
        "SUMMARY": ["summary", "recap", "overview"],
        "REPORT": ["report", "analysis document"],
        "SUPPORT_RESPONSE": ["support", "ticket", "issue", "incident"],
        "TROUBLESHOOTING_GUIDE": ["troubleshoot", "troubleshooting", "steps"],
    }
    # Artifact-driven specs are only valid when REQ matches
    # the artifact's epistemic intent.
    ARTIFACT_TO_SPEC = {
        Artifact.VALIDATION: "VALIDATION_RESULT",
        Artifact.DECISION: "RECOMMENDATION",
    }
    SPEC_ONTOLOGY = {
        "SUPPORT_RESPONSE",
        "TROUBLESHOOTING_GUIDE",
        "BETTING_ODDS",
        "PROBABILITY_DISTRIBUTION",
        "FORECAST",
        "REPORT",
        "SUMMARY",
        "RECOMMENDATION",
        "RANKING",
        "JSON_OBJECT",
        "JSON_SCHEMA",
        "FIELDS",
        "ENTITIES",
        "VALIDATION_RESULT",
    }

    def _extract_explicit_spec(self, text: str) -> list[str]:
        specs = []
        for pat in self.EXPLICIT_OUTPUT_PATTERNS:
            for m in pat.finditer(text):
                noun = m.group(1).strip().upper().replace(" ", "_")
                specs.append(noun)
        return specs

    def _extract_spec_from_artifacts(self, artifacts: set[Artifact]) -> list[str]:
        specs = []
        for a in artifacts:
            if a in self.ARTIFACT_TO_SPEC:
                specs.append(self.ARTIFACT_TO_SPEC[a])
        return specs

    def _extract_spec_from_keywords(self, text: str) -> list[str]:
        tl = text.lower()
        specs = []
        for spec, kws in self.SPEC_KEYWORDS.items():
            if any(kw in tl for kw in kws):
                specs.append(spec)
        return specs

    def extract_specs(
        self,
        text: str,
        artifacts: set[Artifact],
        req: REQ,
    ) -> list[str]:
        scored: dict[str, int] = {}

        for s in self._extract_explicit_spec(text):
            scored[s] = scored.get(s, 0) + 3

        for s in self._extract_spec_from_artifacts(artifacts):
            scored[s] = scored.get(s, 0) + 2

        for s in self._extract_spec_from_keywords(text):
            scored[s] = scored.get(s, 0) + 1

        # SPEC names the domain artifact, not its format or mathematical shape
        final = [
            s
            for s, _ in sorted(scored.items(), key=lambda x: -x[1])
            if s in self.SPEC_ONTOLOGY and s not in self.NON_DOMAIN_SPECS
        ]
        if req != REQ.VALIDATE:
            final = [s for s in final if s != "VALIDATION_RESULT"]

        return final[:1]


class IntentDetectorV2:
    def __init__(self, nlp: Language, vocab: BaseVocabulary):
        self.nlp = nlp
        self.vocab = vocab
        self._specs_detector = _SPECDetector()

    @staticmethod
    def _detect_signals(text: str, vocab: dict) -> set[Signal]:
        text = text.lower()
        signals = set()

        for req_key, phrases in vocab.items():
            for p in phrases:
                if p in text:
                    signal = VOCAB_SIGNAL_MAP.get(req_key)
                    if signal:
                        signals.add(signal)
                    break

        return signals

    @staticmethod
    def _has_validation_target(artifacts: set[Artifact]) -> bool:
        return any(
            a in artifacts
            for a in (
                Artifact.STRUCTURED,
                Artifact.TEXT,
                Artifact.DECISION,
            )
        )

    @staticmethod
    def _has_transform_target(artifacts: set[Artifact]) -> bool:
        return any(a in artifacts for a in (Artifact.STRUCTURED, Artifact.TEXT))

    def _detect_epistemic_grounding(self, text: str) -> bool:
        tl = text.lower()

        has_future = any(k in tl for k in self.vocab.EPISTEMIC_KEYWORDS["future"])
        has_uncertainty = any(
            k in tl for k in self.vocab.EPISTEMIC_KEYWORDS["uncertainty"]
        )
        has_real_world = any(
            k in tl for k in self.vocab.EPISTEMIC_KEYWORDS["real_world"]
        )

        return has_uncertainty and (has_future or has_real_world)

    @staticmethod
    def _detect_artifacts(text: str) -> set[Artifact]:
        artifacts = set()
        tl = text.lower()

        if re.search(r"\{[\s\S]*?\}", text):
            artifacts.add(Artifact.STRUCTURED)

        if re.search(r"\b(probability|odds|chance|likelihood)\b", tl):
            artifacts.add(Artifact.PROBABILITY)

        if re.search(r"^\s*[-*]\s+", text, re.MULTILINE):
            artifacts.add(Artifact.LIST)

        if re.search(r"\b(validate|verify|check compliance|ensure)\b", tl):
            artifacts.add(Artifact.VALIDATION)

        if re.search(r"\b(recommend|best option|choose|decision)\b", tl):
            artifacts.add(Artifact.DECISION)

        if "report" in tl or "analysis" in tl:
            artifacts.add(Artifact.TEXT)

        return artifacts

    def _resolve_req(self, text: str, signals: set[Signal], artifacts: set[Artifact]) -> REQ:
        if (
            Artifact.VALIDATION in artifacts or Signal.VALIDATION in signals
        ):
            return REQ.VALIDATE

        if Signal.EXTRACTION in signals and Artifact.PROBABILITY not in artifacts:
            # Probability implies synthesis; never treat as EXTRACT
            return REQ.EXTRACT

        if Signal.PREDICTION in signals:
            return REQ.PREDICT

        if Signal.TRANSFORMATION in signals:
            return REQ.TRANSFORM

        if Signal.FORMATTING in signals:
            return REQ.FORMAT

        if Artifact.PROBABILITY in artifacts:
            if self._detect_epistemic_grounding(text):
                return REQ.PREDICT
            return REQ.GENERATE

        if any(
            a in artifacts for a in (Artifact.STRUCTURED, Artifact.TEXT, Artifact.LIST)
        ):
            return REQ.GENERATE

        if Signal.RANKING in signals or Artifact.DECISION in artifacts:
            return REQ.RANK

        if Signal.DEBUGGING in signals:
            return REQ.DEBUG

        if Signal.SEARCH in signals:
            return REQ.SEARCH

        if Signal.EXECUTION in signals:
            return REQ.EXECUTE
        return REQ.ANALYZE

    def detect(self, text: str) -> Intent:
        signals = self._detect_signals(text, self.vocab.REQ_TOKENS)
        artifacts = self._detect_artifacts(text)
        req = self._resolve_req(signals=signals, text=text, artifacts=artifacts)
        specs = self._specs_detector.extract_specs(text, artifacts=artifacts, req=req)

        return Intent(
            token=req,
            specs=specs,
        )
