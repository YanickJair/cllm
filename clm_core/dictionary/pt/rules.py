from clm_core.utils.parser_rules import BaseRules


class PTRules(BaseRules):
    """Portuguese language pattern matching rules"""

    def __init__(self):
        super().__init__()

    @property
    def COMPARISON_MAP(self) -> dict[str, str]:
        return {
            r"\bdiferenças?\b": "DIFFERENCES",
            r"\bdistinguir\b": "DIFFERENCES",
            r"\bcontrastar\b": "DIFFERENCES",
            r"\bsimilaridades?\b": "SIMILARITIES",
            r"\bsemelhanças?\b": "SIMILARITIES",
            r"\bcomum\b": "SIMILARITIES",
            r"\bprós\s*(e|&)?\s*contras\b": "PROS_CONS",
            r"\bvantagens\s*(e|&)?\s*desvantagens\b": "PROS_CONS",
            r"\bbenefícios\s*(e|&)?\s*malefícios\b": "PROS_CONS",
            r"\bcompensações?\b": "TRADEOFFS",
            r"\btrade-?offs?\b": "TRADEOFFS",
        }

    @property
    def DOMAIN_REGEX(self) -> dict[str, str]:
        return {
            "SUPPORT": r"\b(chamada|ticket|caso|cliente|suporte|reclamação|helpdesk)\b",
            "TECHNICAL": r"\b(erro|bug|falha|stacktrace|api|debug|servidor|exceção)\b",
            "DOCUMENT": r"\b(documento|artigo|manual|transcrição|guia|texto)\b",
            "BUSINESS": r"\b(relatório|executivo|análise|kpi|dashboard)\b",
            "LEGAL": r"\b(contrato|política|conformidade|cláusula|gdpr|lgpd)\b",
            "FINANCE": r"\b(fatura|cobrança|pagamento|reembolso|transação)\b",
            "SECURITY": r"\b(violação|ameaça|risco|malware|auditoria)\b",
            "MEDICAL": r"\b(paciente|clínico|diagnóstico|tratamento)\b",
            "SALES": r"\b(lead|crm|oportunidade|prospecto)\b",
            "EDUCATION": r"\b(lição|professor|aluno|currículo)\b",
        }

    @property
    def DURATION_PATTERNS(self) -> list[str]:
        return [
            r"(\d+)[\s-]*(?:minuto|min)s?",
            r"(\d+)[\s-]*(?:hora|hr)s?",
        ]

    @property
    def STANDARD_FIELD_KEYWORDS(self) -> dict[str, str]:
        return {
            r"\bproblema(s)?\b": "ISSUE",
            r"\bquestão(ões)?\b": "PROBLEM",
            r"\berro(s)?\b": "ERROR",
            r"\bbug(s)?\b": "BUG",
            r"\bnome(s)?\b": "NAMES",
            r"\bdata(s)?\b": "DATES",
            r"\bquantia(s)?\b": "AMOUNTS",
            r"\bvalor(es)?\b": "AMOUNTS",
            r"\bemail(s)?\b": "EMAILS",
            r"\be-mail(s)?\b": "EMAILS",
            r"\btelefone(s)?\b": "PHONES",
            r"\bendereço(s)?\b": "ADDRESSES",
            r"\bsentimento\b": "SENTIMENT",
            r"\burgência\b": "URGENCY",
            r"\bprioridade\b": "PRIORITY",
            r"\bcategoria\b": "CATEGORY",
            r"\bação(ões)?\b": "ACTIONS",
            r"\bpróximos passos\b": "NEXT_STEPS",
            r"\bpróximas etapas\b": "NEXT_STEPS",
            r"\bitens de ação\b": "ACTIONS",
            r"\bprazo(s)?\b": "DEADLINES",
            r"\bdata(s)? limite\b": "DEADLINES",
            r"\bsegurança\b": "SECURITY",
            r"\bdesempenho\b": "PERFORMANCE",
            r"\bperformance\b": "PERFORMANCE",
        }

    @property
    def AUDIENCE_MAP(self) -> dict[str, str]:
        return {
            r"\bnão[- ]?técnico\b": "NON_TECHNICAL",
            r"\b(iniciante|iniciantes|criança|crianças|simples|geral|leigo)\b": "BEGINNER",
            r"\b(especialista|avançado|profissionais|expert)\b": "EXPERT",
            r"\btécnico\b": "TECHNICAL",
            r"\b(negócio|executivos|gerência|diretoria)\b": "BUSINESS",
        }

    @property
    def LENGTH_MAP(self) -> dict[str, str]:
        return {
            r"\b(breve|curto|conciso|rápido|resumo)\b": "BRIEF",
            r"\b(detalhado|completo|exaustivo|profundo|extenso)\b": "DETAILED",
        }

    @property
    def STYLE_MAP(self) -> dict[str, str]:
        return {
            r"\b(simples|fácil|direto)\b": "SIMPLE",
            r"\b(formal|empresarial|profissional)\b": "FORMAL",
        }

    @property
    def TONE_MAP(self) -> dict[str, str]:
        return {
            r"\bprofissional\b": "PROFESSIONAL",
            r"\bformal\b": "PROFESSIONAL",
            r"\bempresarial\b": "PROFESSIONAL",
            r"\bcasual\b": "CASUAL",
            r"\binformal\b": "CASUAL",
            r"\bamigável\b": "CASUAL",
            r"\bempático\b": "EMPATHETIC",
            r"\bcompassivo\b": "EMPATHETIC",
            r"\bcompreensivo\b": "EMPATHETIC",
        }

    @property
    def NUMBER_WORDS(self) -> dict[str, int]:
        return {
            "um": 1,
            "uma": 1,
            "dois": 2,
            "duas": 2,
            "par": 2,
            "três": 3,
            "quatro": 4,
            "cinco": 5,
            "seis": 6,
            "sete": 7,
            "oito": 8,
            "nove": 9,
            "dez": 10,
            "poucos": -1,
            "alguns": -1,
            "vários": -2,
            "muitos": -3,
        }

    @property
    def SPEC_PATTERNS(self) -> list[tuple[str, str]]:
        return [
            (r"(\d+)\s*linhas?\b", "LINES"),
            (r"(\d+)\s*palavras?\b", "WORDS"),
            (r"(\d+)\s*(?:elementos?|coisas?|itens?)\b", "ITEMS"),
            (r"(\d+)\s*(?:dicas?|sugestões?)\b", "COUNT"),
            (r"(\d+)\s*(?:exemplos?|instâncias?)\b", "COUNT"),
            (r"(\d+)\s*(?:passos?|etapas?)\b", "STEPS"),
            (r"(\d+)\s*(?:formas?|métodos?|maneiras?)\b", "COUNT"),
        ]

    @property
    def PROGRAMMING_LANGUAGE_PATTERN(self) -> list[tuple[str, str]]:
        return [
            (r"\bpython\b", "PYTHON"),
            (r"\bdjango\b", "PYTHON"),
            (r"\bflask\b", "PYTHON"),
            (r"\bpandas\b", "PYTHON"),
            (r"\b\.py\b", "PYTHON"),
            (r"\bjavascript\b", "JAVASCRIPT"),
            (r"\bnode\.?js\b", "JAVASCRIPT"),
            (r"\breact\b", "JAVASCRIPT"),
            (r"\bvue\b", "JAVASCRIPT"),
            (r"\bangular\b", "JAVASCRIPT"),
            (r"\b\.js\b", "JAVASCRIPT"),
            (r"\bjava\b(?!script)", "JAVA"),
            (r"\bspring\b", "JAVA"),
            (r"\bmaven\b", "JAVA"),
            (r"\bc\+\+\b", "CPP"),
            (r"\bcpp\b", "CPP"),
            (r"\bgolang\b", "GO"),
            (r"\bgo\s+(?:código|programa|script)", "GO"),
            (r"\brust\b", "RUST"),
            (r"\btypescript\b", "TYPESCRIPT"),
            (r"\b\.ts\b", "TYPESCRIPT"),
        ]

    @property
    def EXTRACTION_INDICATORS(self) -> list[str]:
        return [
            r"\bextrair\b",
            r"\bidentificar\b",
            r"\bencontrar\b",
            r"\bobter\b",
            r"\bretirar\b",
            r"\bdestacar\b",
            r"\bmostrar\b",
            r"\bretornar\b",
            r"\brecuperar\b",
            r"\bcomparar\b",
            r"\bcontrastar\b",
            r"\blistar\b",
            r"\bquais são\b",
            r"\bo que são\b",
        ]

    @property
    def QA_CRITERIA(self) -> dict[str, str]:
        return {
            r"\b(verificação|verificar|verificado)\b": "VERIFICATION",
            r"\b(política|políticas|aderência à política)\b": "POLICY",
            r"\b(habilidades interpessoais|empatia|clareza|responsabilidade)\b": "SOFT_SKILLS",
            r"\b(precisão|preciso|exatidão)\b": "ACCURACY",
            r"\b(conformidade|conforme|violações?)\b": "COMPLIANCE",
            r"\b(sentimento|emoção|humor)\b": "SENTIMENT",
            r"\b(divulgações?|divulgações obrigatórias?)\b": "DISCLOSURES",
        }

    @property
    def QA_INDICATORS(self) -> list[str]:
        return [
            r"\bpontuação\b",
            r"\bnota\b",
            r"\bqa\b",
            r"\bgarantia de qualidade\b",
            r"\bconformidade\b",
            r"\bauditoria\b",
        ]

    @property
    def QUESTION_PATTERNS(self) -> list[tuple[str, int]]:
        return [
            (r"o que (?:é|são|significa) (?:o |a |os |as |um |uma )?([\w\s]+?)(?:\?|$)", 1),
            (r"como (?:funciona|funcionam|pode|podem) ([\w\s]+?)(?:\?|$)", 1),
            (r"por que (?:é|são|está|estão) ([\w\s]+?)(?:\?|$)", 1),
            (r"onde (?:está|estão|fica|ficam) ([\w\s]+?)(?:\?|$)", 1),
            (r"quando (?:é|foi|será) ([\w\s]+?)(?:\?|$)", 1),
            (r"quem (?:é|são|foi|foram) (?:o |a )?([\w\s]+?)(?:\?|$)", 1),
        ]

    @property
    def EXPLAIN_PATTERNS(self) -> list[tuple[str, int]]:
        return [
            (r"(?:explique|descreva) como ([\w\s]+?)(?: funciona| trabalha|$)", 1),
            (
                r"(?:explique|descreva|esclareça|detalhe) (?:o |a |os |as |um |uma )?([\w\s]+?)(?:\s+em|\s+com|\s+para|\.|\?|$)",
                1,
            ),
            (r"(?:me conte|me fale) sobre ([\w\s]+?)(?:\s+em|\s+com|\.|\?|$)", 1),
        ]

    @property
    def CONCEPT_PATTERN(self) -> tuple[str, int]:
        return (
            r"(?:conceito|ideia|noção|princípio|teoria) de ([\w\s]+?)(?:\s+em|\.|\?|$)",
            1,
        )

    @property
    def PROCEDURE_PATTERN(self) -> tuple[str, int]:
        return (r"como (?:posso|se pode|fazer para) ([\w\s]+?)(?:\s+em|\s+com|\.|\?|$)", 1)

    @property
    def CLEANUP_TAIL(self) -> str:
        return r"\s+(de|em|para|com|sobre|desde|a|ao|por|detalhe|detalhes|técnico|específico)$"

    @property
    def SUBJECT_PATTERNS(self) -> list[tuple[str, str]]:
        return [
            (r"\bverbo[s]?\b", "VERB"),
            (r"\bsubstantivo[s]?\b", "NOUN"),
            (r"\badjetivo[s]?\b", "ADJECTIVE"),
            (r"\badvérbio[s]?\b", "ADVERB"),
            (r"\bpronome[s]?\b", "PRONOUN"),
            (r"\bpreposição(ões)?\b", "PREPOSITION"),
            (r"\bconjunção(ões)?\b", "CONJUNCTION"),
            (r"\bdica[s]?\b", "TIP"),
            (r"\bsugestão(ões)?\b", "TIP"),
            (r"\bmétodo[s]?\b", "METHOD"),
            (r"\btécnica[s]?\b", "TECHNIQUE"),
            (r"\bestratégia[s]?\b", "STRATEGY"),
            (r"\babordagem(ns)?\b", "APPROACH"),
            (r"\bprática[s]?\b", "PRACTICE"),
            (r"\balgoritmo[s]?\b", "ALGORITHM"),
            (r"\bfunção(ões)?\b", "FUNCTION"),
            (r"\bfórmula[s]?\b", "FORMULA"),
            (r"\bequação(ões)?\b", "EQUATION"),
            (r"\bteorema[s]?\b", "THEOREM"),
            (r"\bprova[s]?\b", "PROOF"),
            (r"\bexemplo[s]?\b", "EXAMPLE"),
            (r"\bideia[s]?\b", "IDEA"),
            (r"\bforma[s]?\b", "METHOD"),
            (r"\bmaneira[s]?\b", "METHOD"),
            (r"\bpasso[s]?\b", "STEP"),
            (r"\betapa[s]?\b", "STEP"),
            (r"\bfator(es)?\b", "FACTOR"),
            (r"\brazão(ões)?\b", "REASON"),
            (r"\bmotivo[s]?\b", "REASON"),
            (r"\bbenefício[s]?\b", "BENEFIT"),
            (r"\bvantagem(ns)?\b", "ADVANTAGE"),
            (r"\bdesvantagem(ns)?\b", "DISADVANTAGE"),
            (r"\bcaracterística[s]?\b", "FEATURE"),
            (r"\bmétrica[s]?\b", "METRIC"),
            (r"\bindicador(es)?\b", "INDICATOR"),
            (r"\bpercepção(ões)?\b", "INSIGHT"),
            (r"\bdescoberta[s]?\b", "FINDING"),
            (r"\bachado[s]?\b", "FINDING"),
        ]

    @property
    def TYPE_MAP(self) -> dict[str, str]:
        return {
            "chamada": "CALL",
            "ligação": "CALL",
            "ligação telefônica": "CALL",
            "reunião": "MEETING",
            "encontro": "MEETING",
            "chat": "CHAT",
            "conversa": "CONVERSATION",
            "relatório": "REPORT",
            "artigo": "ARTICLE",
        }

    @property
    def CONTEXT_MAP(self) -> dict[str, str]:
        return {
            "cliente": "CUSTOMER",
            "suporte": "SUPPORT",
            "vendas": "SALES",
            "técnico": "TECHNICAL",
        }

    @property
    def ISSUE_PATTERNS(self) -> list[str]:
        return [
            r"sobre\s+([\w\s]+?)(?:\s+e|$)",
            r"a respeito de\s+([\w\s]+?)(?:\s+e|$)",
            r"acerca de\s+([\w\s]+?)(?:\s+e|$)",
            r"relacionado a\s+([\w\s]+?)(?:\s+e|$)",
        ]
