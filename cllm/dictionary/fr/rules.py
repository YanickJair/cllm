from cllm.utils.parser_rules import BaseRules


class FRRules(BaseRules):
    """French language pattern matching rules"""

    @property
    def COMPARISON_MAP(self) -> dict[str, str]:
        pass

    @property
    def DURATION_PATTERNS(self) -> list[str]:
        pass

    @property
    def STANDARD_FIELD_KEYWORDS(self) -> dict[str, str]:
        pass

    @property
    def AUDIENCE_MAP(self) -> dict[str, str]:
        pass

    @property
    def LENGTH_MAP(self) -> dict[str, str]:
        pass

    @property
    def STYLE_MAP(self) -> dict[str, str]:
        pass

    @property
    def TONE_MAP(self) -> dict[str, str]:
        pass

    @property
    def NUMBER_WORDS(self) -> dict[str, int]:
        pass

    @property
    def SPEC_PATTERNS(self) -> list[tuple[str, str]]:
        pass

    @property
    def PROGRAMMING_LANGUAGE_PATTERN(self) -> list[tuple[str, str]]:
        pass

    @property
    def EXTRACTION_INDICATORS(self) -> list[str]:
        pass

    @property
    def QA_CRITERIA(self) -> dict[str, str]:
        pass

    @property
    def QA_INDICATORS(self) -> list[str]:
        pass

    @property
    def QUESTION_PATTERNS(self) -> list[tuple[str, int]]:
        pass

    @property
    def EXPLAIN_PATTERNS(self) -> list[tuple[str, int]]:
        pass

    @property
    def CONCEPT_PATTERN(self) -> tuple[str, int]:
        pass

    @property
    def PROCEDURE_PATTERN(self) -> tuple[str, int]:
        pass

    @property
    def CLEANUP_TAIL(self) -> str:
        pass

    @property
    def SUBJECT_PATTERNS(self) -> list[tuple[str, str]]:
        pass

    @property
    def TYPE_MAP(self) -> dict[str, str]:
        pass

    @property
    def CONTEXT_MAP(self) -> dict[str, str]:
        pass

    @property
    def ISSUE_PATTERNS(self) -> list[str]:
        pass

    def __init__(self):
        super().__init__()

    @property
    def DOMAIN_REGEX(self) -> dict[str, str]:
        return {
            "SUPPORT": r"\b(appel|ticket|dossier|client|support|réclamation)\b",
            "TECHNICAL": r"\b(erreur|bug|crash|stacktrace|api|débogage|serveur|exception)\b",
            "DOCUMENT": r"\b(document|article|manuel|transcription|guide)\b",
            "BUSINESS": r"\b(rapport|exécutif|analyse|kpi|tableau de bord)\b",
            "LEGAL": r"\b(contrat|politique|conformité|clause|rgpd)\b",
            "FINANCE": r"\b(facture|facturation|paiement|remboursement|transaction)\b",
            "SECURITY": r"\b(violation|menace|risque|malware|audit)\b",
            "MEDICAL": r"\b(patient|clinique|diagnostic|traitement)\b",
            "SALES": r"\b(lead|crm|opportunité|prospect)\b",
            "EDUCATION": r"\b(leçon|enseignant|étudiant|programme)\b",
        }
