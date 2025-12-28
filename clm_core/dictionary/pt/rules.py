from clm_core.utils.parser_rules import BaseRules


class PTRules(BaseRules):
    """Portuguese language pattern matching rules"""

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
            "SUPPORT": r"\b(chamada|ticket|caso|cliente|suporte|reclamação|helpdesk)\b",
            "TECHNICAL": r"\b(erro|bug|falha|stacktrace|api|debug|servidor|exceção)\b",
            "DOCUMENT": r"\b(documento|artigo|manual|transcrição|guia|texto)\b",
            "BUSINESS": r"\b(relatório|executivo|análise|kpi|dashboard)\b",
            "LEGAL": r"\b(contrato|política|conformidade|cláusula|gdpr)\b",
            "FINANCE": r"\b(fatura|cobrança|pagamento|reembolso|transação)\b",
            "SECURITY": r"\b(violação|ameaça|risco|malware|auditoria)\b",
            "MEDICAL": r"\b(paciente|clínico|diagnóstico|tratamento)\b",
            "SALES": r"\b(lead|crm|oportunidade|prospecto)\b",
            "EDUCATION": r"\b(lição|professor|aluno|currículo)\b",
            "OTHER": r"\b(outro|outros|outro|outra|outras)\b",
        }
