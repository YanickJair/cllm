from clm_core.utils.parser_rules import BaseRules


class ESRules(BaseRules):
    """English language pattern matching rules"""

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
            "SUPPORT": r"\b(llamada|ticket|caso|cliente|soporte|queja)\b",
            "TECHNICAL": r"\b(error|bug|fallo|stacktrace|api|depuración|servidor|excepción)\b",
            "DOCUMENT": r"\b(documento|artículo|manual|transcripción|guía)\b",
            "BUSINESS": r"\b(informe|ejecutivo|análisis|kpi|panel)\b",
            "LEGAL": r"\b(contrato|política|cumplimiento|cláusula|rgpd)\b",
            "FINANCE": r"\b(factura|cobro|pago|reembolso|transacción)\b",
            "SECURITY": r"\b(brecha|amenaza|riesgo|malware|auditoría)\b",
            "MEDICAL": r"\b(paciente|clínico|diagnóstico|tratamiento)\b",
            "SALES": r"\b(lead|crm|oportunidad|prospecto)\b",
            "EDUCATION": r"\b(lección|profesor|estudiante|currículo)\b",
        }
