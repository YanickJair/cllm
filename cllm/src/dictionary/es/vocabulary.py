from re import PatternError
from ...utils.vocabulary import BaseVocabulary


class ESVocabulary(BaseVocabulary):
    """CLLM token vocabulary - Spanish (Spain/Latin America)"""
    def __init__(self):
        super().__init__()

    @property
    def QUANTIFIER_WORDS(self) -> list[str]:
        return ["todos", "todas", "todo", "cada", "entero", "completo"]

    @property
    def DEMONSTRATIVES(self) -> list[str]:
        return ["este", "esta", "esto", "ese", "esa", "eso", "aquel", "aquella", "aquello"]

    @property
    def COMPOUND_PHRASES(self) -> dict[str, str]:
        return {
            "soporte al cliente": "TICKET",
            "ticket de soporte": "TICKET",
            "mensaje de correo": "EMAIL",
            "transcripción de chat": "TRANSCRIPT",
            "llamada telefónica": "CALL",
            "código fuente": "CODE",
            "plan de negocios": "PLAN",
            "descripción del producto": "DESCRIPTION",
        }

    @property
    def CONCEPT_INDICATORS(self) -> list[str]:
        """Optional - can have sensible default"""
        return ["concepto de", "idea de", "noción de", "principio de"]

    @property
    def MEETING_WORDS(self) -> list[str]:
        """Optional - can have empty default"""
        return ["reunión", "conferencia", "junta", "sesión"]

    @property
    def PROPOSAL_WORDS(self) -> list[str]:
        """Optional - can have empty default"""
        return ["propuesta", "proposición"]

    @property
    def ARTICLES(self) -> list[str]:
        """Optional - can have empty default"""
        return ["el", "la", "los", "las", "un", "una", "unos", "unas"]

    @property
    def domain_candidates(self) -> dict[str, list[str]]:
        return {
            "soporte": ["problema", "cuestión", "sentimiento", "acciones", "urgencia", "prioridad"],
            "código": ["bug", "error", "seguridad", "rendimiento", "desempeño", "performance"],
            "documento": ["nombres", "fechas", "montos", "cantidades", "direcciones", "emails", "correos", "teléfonos"],
            "qa": ["verificación", "política", "habilidades blandas", "soft skills", "precisión", "exactitud", "cumplimiento", "compliance", "divulgaciones"],
        }

    @property
    def rank_triggers(self) -> set[str]:
        return {
            "clasificar", "rankear", "ordenar", "orden", "ordenar por", "clasificar por",
            "priorizar", "superior", "primero", "arriba", "top",
            "inferior", "último", "abajo", "mayor", "más alto",
            "menor", "más bajo", "mejor", "mejores", "peor", "peores"
        }

    @property
    def REQ_TOKENS(self):
        return {
            "ANALYZE": [
                "analizar",
                "revisar",
                "examinar",
                "evaluar",
                "valorar",
                "inspeccionar",
                "auditar",
                "investigar",
                "verificar",
            ],
            "MATCH": [
                "combinar",
                "comparar",
                "alinear",
                "mapear",
                "correlacionar",
                "emparejar",
                "cotejar",
                "cruzar",
            ],
            "EXTRACT": [
                "extraer",
                "sacar",
                "identificar",
                "encontrar",
                "localizar",
                "obtener",
                "recuperar",
                "devolver",
                "incluir",
                "seleccionar",
                "buscar",
            ],
            "SELECT": [
                "seleccionar",
                "elegir",
                "escoger",
                "filtrar",
            "identificar coincidencias",
            "optar",
        ],
        "GENERATE": [
            "generar",
            "crear",
            "escribir",
            "redactar",
            "componer",
            "producir",
            "construir",
            "desarrollar",
            "diseñar",
            "elaborar",
            "hacer",
            "nombrar",
            "sugerir",
            "formular",
            "formar",
            "proponer",
            "transcribir",
        ],
        "SUMMARIZE": [
            "resumir",
            "condensar",
            "sintetizar",
            "recapitular",
            "abreviar",
            "compendiar",
        ],
        "TRANSFORM": [
            "convertir",
            "transformar",
            "cambiar",
            "reescribir",
            "traducir",
            "completar",
            "modificar",
            "adaptar",
            "ajustar",
            "reformular",
            "alterar",
            "editar",
            "añadir",
            "agregar",
            "parafrasear",
            "rellenar",
            "llenar",
            "eliminar",
            "quitar",
            "reemplazar",
            "sustituir",
            "invertir",
        ],
        "EXPLAIN": [
            "explicar",
            "describir",
            "aclarar",
            "elaborar",
            "detallar",
            "exponer",
            "ilustrar",
            "expresar",
            "contar",
            "discutir",
            "definir",
            "hablar de",
            "dime sobre",
            "cuéntame sobre",
        ],
        "COMPARE": [
            "comparar",
            "contrastar",
            "versus",
            "vs",
            "diferencia entre",
            "diferenciar",
            "distinguir",
        ],
        "CLASSIFY": [
            "clasificar",
            "categorizar",
            "ordenar",
            "agrupar",
            "etiquetar",
            "organizar",
            "segmentar",
            "separar por",
        ],
        "DEBUG": [
            "depurar",
            "debugear",
            "diagnosticar",
            "corregir bug",
            "investigar bug",
            "encontrar bug",
            "rastrear",
            "identificar problema",
        ],
        "OPTIMIZE": [
            "optimizar",
            "mejorar",
            "potenciar",
            "refactorizar",
            "acelerar",
            "simplificar",
            "maximizar",
            "minimizar",
            "reducir",
            "aumentar",
        ],
        "VALIDATE": [
            "validar",
            "verificar",
            "comprobar",
            "confirmar",
            "testear",
            "probar",
            "asegurar",
            "certificar",
            "autenticar",
        ],
        "SEARCH": [
            "buscar",
            "consultar",
            "encontrar",
            "localizar",
            "hallar",
            "descubrir",
        ],
        "RANK": [
            "priorizar",
            "ordenar",
            "clasificar por",
            "puntuar",
            "calificar",
            "rankear",
        ],
        "PREDICT": [
            "predecir",
            "pronosticar",
            "estimar",
            "proyectar",
            "anticipar",
            "prever",
            "extrapolar",
        ],
        "FORMAT": [
            "formatear",
            "estructurar",
            "organizar",
            "disponer",
            "maquetar",
        ],
        "DETECT": [
            "detectar",
            "identificar",
            "descubrir",
            "percibir",
            "reconocer",
            "notar",
        ],
        "CALCULATE": [
            "calcular",
            "computar",
            "determinar",
            "cuantificar",
            "medir",
            "contar",
            "sumar",
            "totalizar",
        ],
        "AGGREGATE": [
            "agregar",
            "agrupar",
            "combinar",
            "consolidar",
            "juntar",
            "fusionar",
            "compilar",
            "recopilar",
            "reunir",
        ],
        "DETERMINE": [
            "determinar",
            "decidir",
            "evaluar",
            "concluir",
            "establecer",
            "elegir",
            "definir",
        ],
        "ROUTE": [
            "enrutar",
            "asignar",
            "dirigir",
            "reenviar",
            "enviar a",
            "delegar",
            "asignar",
        ],
        "EXECUTE": [
            "usar",
            "aplicar",
            "implementar",
            "ejecutar",
            "realizar",
            "emplear",
            "utilizar",
            "correr",
        ],
        "LIST": [
            "listar",
            "enumerar",
            "itemizar",
            "delinear",
            "relacionar",
        ],
    }

    @property
    def NOISE_VERBS(self) -> set[str]:
        return {
            "ser",
            "estar",
            "haber",
            "tener",
            "poder",
            "deber",
            "querer",
            "ir",
            "venir",
            "hacer",
            "quedar",
            "vivir",
            "seguir",
            "continuar",
            "permanecer",
            "basarse",
            "necesitar",
            "empezar",
            "comenzar",
            "volverse",
            "parecer",
            "aparecer",
            "mostrar",
            "ver",
            "saber",
            "pensar",
            "sentir",
            "decir",
            "hablar",
            "llamar",
        }

    @property
    def CONTEXT_FILTERS(self) -> dict[str, list[str]]:
        return {
            "dar": ["dado", "dando", "dame", "da me"],
            "seguir": ["siguiente", "a continuación", "siguiendo"],
            "basar": ["basado en", "con base en"],
            "usar": ["útil", "usado para", "utilizado"],
            "continuar": ["continuación", "continuando", "continuar"],
            "permanecer": ["permanencia", "permaneciendo", "permanecer"],
            "basarse": ["basándose", "basándose en", "basarse"],
            "necesitar": ["necesidad", "necesitando", "necesitar"],
            "empezar": ["inicio", "empezando", "empezar"],
            "comenzar": ["inicio", "comenzando", "comenzar"],
            "volverse": ["volviendo", "volviendo a", "volverse"],
            "parecer": ["apariencia", "pareciendo", "parecer"],
            "aparecer": ["aparición", "apareciendo", "aparecer"],
            "mostrar": ["mostrando", "mostrando a", "mostrar"],
            "ver": ["visión", "viendo", "ver"],
            "saber": ["conocimiento", "sabiendo", "saber"],
            "pensar": ["pensamiento", "pensando", "pensar"],
            "sentir": ["sentimiento", "sentido", "sentir"],
            "decir": ["hablar", "decidiendo", "decir"],
            "hablar": ["habla", "hablando", "hablar"],
            "llamar": ["llamada", "llamando", "llamar"],
            "llamada": ["llamada", "llamando", "llamar"],
        }

    @property
    def TARGET_TOKENS(self):
        return {
            "CODE": [
                "código",
                "script",
                "programa",
                "función",
                "método",
                "clase",
                "fragmento",
            ],
            "DATA": [
                "datos",
                "dataset",
                "conjunto de datos",
            "base de datos",
            "hoja de cálculo",
            "tabla",
            "csv",
        ],
        "QUERY": [
            "query",
            "consulta",
            "sql",
            "consulta sql",
            "consulta de base de datos",
        ],
        "ENDPOINT": [
            "endpoint",
            "api",
            "punto de acceso",
            "servicio rest",
        ],
        "COMPONENT": [
            "componente",
            "módulo",
            "paquete",
            "biblioteca",
            "librería",
        ],
        "SYSTEM": [
            "sistema",
            "aplicación",
            "app",
            "software",
            "plataforma",
        ],
        "TEST": [
            "test",
            "prueba",
            "prueba unitaria",
            "caso de prueba",
            "suite de pruebas",
        ],
        "LOG": [
            "log",
            "logs",
            "archivo de log",
            "registro",
            "bitácora",
        ],
        "RECORD": [
            "registro",
            "entrada",
            "fila",
            "elemento",
        ],
        "STRATEGY": [
            "estrategia",
            "enfoque",
            "plan",
            "metodología",
        ],
        "NBA_CATALOG": [
            "nba",
            "nbas",
            "siguiente mejor acción",
            "próxima mejor acción",
            "acciones predefinidas",
            "acciones posibles",
            "acciones disponibles",
        ],
        # Documents and content
        "DOCUMENT": [
            "documento",
            "doc",
            "archivo",
            "informe",
            "artículo",
            "papel",
        ],
        "EMAIL": [
            "email",
            "correo",
            "correo electrónico",
            "mensaje",
            "correspondencia",
        ],
        "REPORT": [
            "informe",
            "reporte",
            "análisis",
            "hallazgos",
            "conclusiones",
        ],
        "TICKET": [
            "ticket",
            "incidencia",
            "caso",
            "solicitud",
        ],
        "TRANSCRIPT": [
            "transcripción",
            "conversación",
            "diálogo",
            "historial de chat",
        ],
        "FEEDBACK": [
            "feedback",
            "retroalimentación",
            "comentario",
            "evaluación",
            "crítica",
        ],
        "COMMENT": [
            "comentario",
            "observación",
            "nota",
            "anotación",
        ],
        "CUSTOMER_INTENT": [
            "intención del cliente",
            "necesidad del cliente",
            "solicitud del cliente",
            "objetivo del cliente",
            "problema del cliente",
        ],
        "COMPLAINT": [
            "queja",
            "reclamación",
            "problema",
            "reclamo",
        ],
        "REQUEST": [
            "solicitud",
            "pedido",
            "petición",
        ],
        "INQUIRY": [
            "consulta",
            "pregunta",
            "duda",
        ],
        "INTERACTION": [
            "interacción",
            "atención",
            "contacto",
        ],
        "CALL": [
            "llamada",
            "telefonema",
        ],
        "DESCRIPTION": [
            "descripción",
            "detalle",
        ],
        "SUMMARY": [
            "resumen",
            "sumario",
            "síntesis",
        ],
        "PLAN": [
            "plan",
            "planificación",
            "proyecto",
        ],
        "POST": [
            "post",
            "publicación",
            "entrada",
        ],
        "PRESS_RELEASE": [
            "comunicado de prensa",
            "nota de prensa",
            "anuncio",
        ],
        "INTRODUCTION": [
            "introducción",
            "presentación",
        ],
        "CAPTION": [
            "leyenda",
            "pie de foto",
            "caption",
        ],
        "QUESTIONS": [
            "preguntas",
            "cuestiones",
            "cuestionario",
            "faq",
        ],
        "RESPONSE": [
            "respuesta",
            "réplica",
            "contestación",
            "plantilla de respuesta",
        ],
        "LOGS": [
            "logs",
            "registros",
            "bitácoras",
        ],
        "CORRELATION": [
            "correlación",
            "correlaciones",
            "relación",
            "relaciones",
        ],
        "TRADEOFF": [
            "trade-off",
            "compensación",
            "equilibrio",
        ],
        "PARADIGM": [
            "paradigma",
            "paradigmas",
            "modelo",
        ],
        "PAIN_POINTS": [
            "puntos de dolor",
            "problemas",
            "dificultades",
        ],
        "PATTERN": [
            "patrón",
            "patrones",
            "tendencia",
            "tendencias",
        ],
        "CHURN": [
            "churn",
            "abandono",
            "rotación",
            "deserción",
        ],
        "FEATURES": [
            "funcionalidades",
            "características",
            "features",
        ],
        "METRICS": [
            "ingresos",
            "métricas",
            "estadísticas",
            "números",
            "indicadores",
        ],
        "REGIONS": [
            "regiones",
            "áreas",
            "ubicaciones",
            "territorios",
        ],
        "ITEMS": [
            "elementos",
            "cosas",
            "lista",
            "opciones",
            "alternativas",
        ],
        "CONCEPT": [
            "concepto",
            "idea",
            "noción",
            "principio",
            "teoría",
        ],
        "PROCEDURE": [
            "procedimiento",
            "proceso",
            "pasos",
            "método",
            "técnica",
        ],
        "FACT": [
            "hecho",
            "hechos",
            "información",
            "detalles",
        ],
        "ANSWER": [
            "respuesta",
            "solución",
        ],
    }

    @property
    def EXTRACT_FIELDS(self) -> tuple[str, ...]:
        return (
            "ISSUE",
            "SENTIMENT",
            "ACTIONS",
            "NEXT_STEPS",
            "URGENCY",
            "PRIORITY",
            "NAMES",
            "DATES",
            "AMOUNTS",
            "EMAILS",
            "PHONES",
            "ADDRESSES",
            "BUGS",
            "SECURITY",
            "PERFORMANCE",
            "STYLE",
            "ERRORS",
            "WARNINGS",
            "KEYWORDS",
            "TOPICS",
            "ENTITIES",
            "FACTS",
            "DECISIONS",
            "DEADLINES",
            "REQUIREMENTS",
            "FEATURES",
            "PROBLEMS",
            "SOLUTIONS",
            "RISKS",
            "METRICS",
        "KPI",
        "SCORES",
        "RATINGS",
        "FEEDBACK",
        "COMPLAINTS",
        "OWNERS",
        "ASSIGNEES",
        "STAKEHOLDERS",
        "PARTICIPANTS",
        "TIMESTAMPS",
        "DURATIONS",
        "FREQUENCIES",
        "QUANTITIES",
        "CATEGORIES",
        "TAGS",
        "LABELS",
        "STATUS",
        "TYPE",
        "CUSTOMER_INTENT",
        "RELEVANCE_SCORE",
        "NBA_ID",
        "MATCH_CONFIDENCE",
        "SEMANTIC_SIMILARITY",
        "THRESHOLD",
    )

    @property
    def OUTPUT_FORMATS(self) -> dict[str, list[str]]:
        return {
            "JSON": ["json", "formato json"],
            "MARKDOWN": ["markdown", "md"],
            "TABLE": ["tabla", "tabular"],
            "LIST": ["lista", "viñetas", "puntos"],
            "PLAIN": ["texto plano", "texto simple"],
            "CSV": ["csv", "separado por comas"],
        }

    @property
    def IMPERATIVE_PATTERNS(self) -> list[tuple[list[str], str, str]]:
        return [
            (["lista", "listar", "enumera", "enumerar", "itemiza"], "LIST", "ITEMS"),
            (["nombra", "nombrar", "identifica", "identificar"], "GENERATE", "ITEMS"),
            (["da", "dar", "proporciona", "proporcionar", "sugiere", "sugerir"], "GENERATE", "ITEMS"),
            (
                [
                    "di",
                    "decir",
                    "explica",
                    "explicar",
                    "describe",
                    "describir",
                    "aclara",
                    "aclarar",
                    "ilustra",
                    "ilustrar",
                ],
                "EXPLAIN",
                "CONCEPT",
            ),
        ]

    @property
    def QUESTION_WORDS(self) -> list[str]:
        return [
            "qué",
            "que",
            "quién",
            "quien",
            "dónde",
            "donde",
            "cuándo",
            "cuando",
            "por qué",
            "porque",
            "cómo",
            "como",
            "cuál",
            "cual",
            "cuáles",
            "cuales",
        ]
