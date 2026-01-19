from clm_core.utils.parser_rules import BaseRules


class ESRules(BaseRules):
    """Spanish language pattern matching rules"""

    def __init__(self):
        super().__init__()

    @property
    def COMPARISON_MAP(self) -> dict[str, str]:
        return {
            r"\bdiferencias?\b": "DIFFERENCES",
            r"\bdistinguir\b": "DIFFERENCES",
            r"\bcontrastar\b": "DIFFERENCES",
            r"\bsimilitudes?\b": "SIMILARITIES",
            r"\bsemejanzas?\b": "SIMILARITIES",
            r"\bcomún\b": "SIMILARITIES",
            r"\bpros\s*(y|&)?\s*contras\b": "PROS_CONS",
            r"\bventajas\s*(y|&)?\s*desventajas\b": "PROS_CONS",
            r"\bbeneficios\s*(y|&)?\s*inconvenientes\b": "PROS_CONS",
            r"\bcompensaciones?\b": "TRADEOFFS",
            r"\btrade-?offs?\b": "TRADEOFFS",
        }

    @property
    def DOMAIN_REGEX(self) -> dict[str, str]:
        return {
            "SUPPORT": r"\b(llamada|ticket|caso|cliente|soporte|queja|helpdesk)\b",
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
            r"\bcuestión(es)?\b": "PROBLEM",
            r"\berror(es)?\b": "ERROR",
            r"\bbug(s)?\b": "BUG",
            r"\bnombre(s)?\b": "NAMES",
            r"\bfecha(s)?\b": "DATES",
            r"\bcantidad(es)?\b": "AMOUNTS",
            r"\bmonto(s)?\b": "AMOUNTS",
            r"\bemail(s)?\b": "EMAILS",
            r"\bcorreo(s)?\b": "EMAILS",
            r"\bteléfono(s)?\b": "PHONES",
            r"\bdirección(es)?\b": "ADDRESSES",
            r"\bsentimiento\b": "SENTIMENT",
            r"\burgencia\b": "URGENCY",
            r"\bprioridad\b": "PRIORITY",
            r"\bcategoría\b": "CATEGORY",
            r"\bacción(es)?\b": "ACTIONS",
            r"\bpróximos pasos\b": "NEXT_STEPS",
            r"\bsiguientes pasos\b": "NEXT_STEPS",
            r"\belementos de acción\b": "ACTIONS",
            r"\bfecha(s)? límite\b": "DEADLINES",
            r"\bplazo(s)?\b": "DEADLINES",
            r"\bseguridad\b": "SECURITY",
            r"\brendimiento\b": "PERFORMANCE",
            r"\bdesempeño\b": "PERFORMANCE",
        }

    @property
    def AUDIENCE_MAP(self) -> dict[str, str]:
        return {
            r"\bno[- ]?técnico\b": "NON_TECHNICAL",
            r"\b(principiante|principiantes|niño|niños|simple|general)\b": "BEGINNER",
            r"\b(experto|avanzado|especialista|profesionales)\b": "EXPERT",
            r"\btécnico\b": "TECHNICAL",
            r"\b(negocio|ejecutivos|gerencia|dirección)\b": "BUSINESS",
        }

    @property
    def LENGTH_MAP(self) -> dict[str, str]:
        return {
            r"\b(breve|corto|conciso|rápido|resumen)\b": "BRIEF",
            r"\b(detallado|completo|exhaustivo|profundo|extenso)\b": "DETAILED",
        }

    @property
    def STYLE_MAP(self) -> dict[str, str]:
        return {
            r"\b(simple|fácil|sencillo)\b": "SIMPLE",
            r"\b(formal|empresarial|profesional)\b": "FORMAL",
        }

    @property
    def TONE_MAP(self) -> dict[str, str]:
        return {
            r"\bprofesional\b": "PROFESSIONAL",
            r"\bformal\b": "PROFESSIONAL",
            r"\bempresarial\b": "PROFESSIONAL",
            r"\bcasual\b": "CASUAL",
            r"\binformal\b": "CASUAL",
            r"\bamigable\b": "CASUAL",
            r"\bempático\b": "EMPATHETIC",
            r"\bcompasivo\b": "EMPATHETIC",
            r"\bcomprensivo\b": "EMPATHETIC",
        }

    @property
    def NUMBER_WORDS(self) -> dict[str, int]:
        return {
            "uno": 1,
            "una": 1,
            "un": 1,
            "dos": 2,
            "par": 2,
            "tres": 3,
            "cuatro": 4,
            "cinco": 5,
            "seis": 6,
            "siete": 7,
            "ocho": 8,
            "nueve": 9,
            "diez": 10,
            "pocos": -1,
            "varios": -2,
            "muchos": -3,
        }

    @property
    def SPEC_PATTERNS(self) -> list[tuple[str, str]]:
        return [
            (r"(\d+)\s*líneas?\b", "LINES"),
            (r"(\d+)\s*palabras?\b", "WORDS"),
            (r"(\d+)\s*(?:elementos?|cosas?|ítems?)\b", "ITEMS"),
            (r"(\d+)\s*(?:consejos?|sugerencias?)\b", "COUNT"),
            (r"(\d+)\s*(?:ejemplos?|instancias?)\b", "COUNT"),
            (r"(\d+)\s*(?:pasos?|etapas?)\b", "STEPS"),
            (r"(\d+)\s*(?:formas?|métodos?|maneras?)\b", "COUNT"),
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
            (r"\bgo\s+(?:código|program|script)", "GO"),
            (r"\brust\b", "RUST"),
            (r"\btypescript\b", "TYPESCRIPT"),
            (r"\b\.ts\b", "TYPESCRIPT"),
        ]

    @property
    def EXTRACTION_INDICATORS(self) -> list[str]:
        return [
            r"\bextraer\b",
            r"\bidentificar\b",
            r"\bencontrar\b",
            r"\bobtener\b",
            r"\bsacar\b",
            r"\bresaltar\b",
            r"\bmostrar\b",
            r"\bdevolver\b",
            r"\brecuperar\b",
            r"\bcomparar\b",
            r"\bcontrastar\b",
            r"\blistar\b",
            r"\bcuáles son\b",
            r"\bqué son\b",
        ]

    @property
    def QA_CRITERIA(self) -> dict[str, str]:
        return {
            r"\b(verificación|verificar|verificado)\b": "VERIFICATION",
            r"\b(política|políticas|adherencia a política)\b": "POLICY",
            r"\b(habilidades blandas|empatía|claridad|responsabilidad)\b": "SOFT_SKILLS",
            r"\b(precisión|preciso|exactitud)\b": "ACCURACY",
            r"\b(cumplimiento|cumple|violaciones?)\b": "COMPLIANCE",
            r"\b(sentimiento|emoción|estado de ánimo)\b": "SENTIMENT",
            r"\b(divulgaciones?|divulgaciones obligatorias?)\b": "DISCLOSURES",
        }

    @property
    def QA_INDICATORS(self) -> list[str]:
        return [
            r"\bpuntuación\b",
            r"\bpuntaje\b",
            r"\bqa\b",
            r"\baseguramiento de calidad\b",
            r"\bcumplimiento\b",
            r"\bauditoría\b",
        ]

    @property
    def QUESTION_PATTERNS(self) -> list[tuple[str, int]]:
        return [
            (r"qué (?:es|son|significa) (?:el |la |los |las |un |una )?([\w\s]+?)(?:\?|$)", 1),
            (r"cómo (?:funciona|funcionan|puede|pueden) ([\w\s]+?)(?:\?|$)", 1),
            (r"por qué (?:es|son|está|están) ([\w\s]+?)(?:\?|$)", 1),
            (r"dónde (?:está|están|se encuentra) ([\w\s]+?)(?:\?|$)", 1),
            (r"cuándo (?:es|fue|será) ([\w\s]+?)(?:\?|$)", 1),
            (r"quién (?:es|son|fue|fueron) (?:el |la )?([\w\s]+?)(?:\?|$)", 1),
        ]

    @property
    def EXPLAIN_PATTERNS(self) -> list[tuple[str, int]]:
        return [
            (r"(?:explica|describe) cómo ([\w\s]+?)(?: funciona| trabaja|$)", 1),
            (
                r"(?:explica|describe|aclara|detalla) (?:el |la |los |las |un |una )?([\w\s]+?)(?:\s+en|\s+con|\s+para|\.|\?|$)",
                1,
            ),
            (r"(?:cuéntame|dime) sobre ([\w\s]+?)(?:\s+en|\s+con|\.|\?|$)", 1),
        ]

    @property
    def CONCEPT_PATTERN(self) -> tuple[str, int]:
        return (
            r"(?:concepto|idea|noción|principio|teoría) de ([\w\s]+?)(?:\s+en|\.|\?|$)",
            1,
        )

    @property
    def PROCEDURE_PATTERN(self) -> tuple[str, int]:
        return (r"cómo (?:puedo|se puede|hago para) ([\w\s]+?)(?:\s+en|\s+con|\.|\?|$)", 1)

    @property
    def CLEANUP_TAIL(self) -> str:
        return r"\s+(de|en|para|con|sobre|desde|a|al|por|detalle|detalles|técnico|específico)$"

    @property
    def SUBJECT_PATTERNS(self) -> list[tuple[str, str]]:
        return [
            (r"\bverbo[s]?\b", "VERB"),
            (r"\bsustantivo[s]?\b", "NOUN"),
            (r"\badjetivo[s]?\b", "ADJECTIVE"),
            (r"\badverbio[s]?\b", "ADVERB"),
            (r"\bpronombre[s]?\b", "PRONOUN"),
            (r"\bpreposición(es)?\b", "PREPOSITION"),
            (r"\bconjunción(es)?\b", "CONJUNCTION"),
            (r"\bconsejo[s]?\b", "TIP"),
            (r"\bsugerencia[s]?\b", "TIP"),
            (r"\bmétodo[s]?\b", "METHOD"),
            (r"\btécnica[s]?\b", "TECHNIQUE"),
            (r"\bestrategia[s]?\b", "STRATEGY"),
            (r"\benfoque[s]?\b", "APPROACH"),
            (r"\bpráctica[s]?\b", "PRACTICE"),
            (r"\balgoritmo[s]?\b", "ALGORITHM"),
            (r"\bfunción(es)?\b", "FUNCTION"),
            (r"\bfórmula[s]?\b", "FORMULA"),
            (r"\becuación(es)?\b", "EQUATION"),
            (r"\bteorema[s]?\b", "THEOREM"),
            (r"\bprueba[s]?\b", "PROOF"),
            (r"\bejemplo[s]?\b", "EXAMPLE"),
            (r"\bidea[s]?\b", "IDEA"),
            (r"\bforma[s]?\b", "METHOD"),
            (r"\bmanera[s]?\b", "METHOD"),
            (r"\bpaso[s]?\b", "STEP"),
            (r"\bfactor(es)?\b", "FACTOR"),
            (r"\brazón(es)?\b", "REASON"),
            (r"\bmotivo[s]?\b", "REASON"),
            (r"\bbeneficio[s]?\b", "BENEFIT"),
            (r"\bventaja[s]?\b", "ADVANTAGE"),
            (r"\bdesventaja[s]?\b", "DISADVANTAGE"),
            (r"\bcaracterística[s]?\b", "FEATURE"),
            (r"\bmétrica[s]?\b", "METRIC"),
            (r"\bindicador(es)?\b", "INDICATOR"),
            (r"\bpercepción(es)?\b", "INSIGHT"),
            (r"\bhallazgo[s]?\b", "FINDING"),
        ]

    @property
    def TYPE_MAP(self) -> dict[str, str]:
        return {
            "llamada": "CALL",
            "llamada telefónica": "CALL",
            "reunión": "MEETING",
            "junta": "MEETING",
            "chat": "CHAT",
            "conversación": "CONVERSATION",
            "informe": "REPORT",
            "reporte": "REPORT",
            "artículo": "ARTICLE",
        }

    @property
    def CONTEXT_MAP(self) -> dict[str, str]:
        return {
            "cliente": "CUSTOMER",
            "soporte": "SUPPORT",
            "ventas": "SALES",
            "técnico": "TECHNICAL",
        }

    @property
    def ISSUE_PATTERNS(self) -> list[str]:
        return [
            r"sobre\s+([\w\s]+?)(?:\s+y|$)",
            r"respecto a\s+([\w\s]+?)(?:\s+y|$)",
            r"acerca de\s+([\w\s]+?)(?:\s+y|$)",
            r"relacionado con\s+([\w\s]+?)(?:\s+y|$)",
        ]
