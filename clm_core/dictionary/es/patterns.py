"""
Pattern definitions and constants for target extraction - Spanish
"""

TECHNICAL_CONCEPTS = [
    "estructuras de datos",
    "algoritmos",
    "complejidad computacional",
    "sistemas operativos",
    "memoria virtual",
    "concurrencia",
    "multihilo",
    "computación paralela",
    "sistemas distribuidos",
    "balanceo de carga",
    "arquitectura orientada a eventos",
    "ip",
    "udp",
    "icmp",
    "ssh",
    "ftp",
    "smtp",
    "snmp",
    "websockets",
    "vpn",
    "cdn",
    "servidores proxy",
    "firewalls",
    "nat",
    "bgp",
    "bases de datos relacionales",
    "bases de datos documentales",
    "bases de datos de grafos",
    "bases de datos de series temporales",
    "indexación",
    "optimización de consultas",
    "acid",
    "event sourcing",
    "almacén de datos",
    "etl",
    "lagos de datos",
    "caché",
    "redis",
    "elasticsearch",
    "programación orientada a objetos",
    "programación funcional",
    "desarrollo guiado por pruebas",
    "patrones de diseño",
    "inyección de dependencias",
    "integración continua",
    "despliegue continuo",
    "control de versiones",
    "git",
    "monolito",
    "microfrontends",
    "diseño dirigido por dominio",
    "arquitectura limpia",
    "infraestructura como código",
    "terraform",
    "ansible",
    "jenkins",
    "pipelines cicd",
    "monitoreo",
    "observabilidad",
    "logging",
    "prometheus",
    "grafana",
    "pruebas de carga",
    "ingeniería del caos",
    "aprendizaje por refuerzo",
    "visión por computadora",
    "procesamiento de lenguaje natural",
    "ia generativa",
    "transformers",
    "autoencoders",
    "ingeniería de características",
    "preprocesamiento de datos",
    "despliegue de modelos",
    "mlops",
    "bases de datos vectoriales",
    "encriptación",
    "hashing",
    "ssl",
    "tls",
    "oauth",
    "jwt",
    "arquitectura zero trust",
    "pruebas de penetración",
    "escaneo de vulnerabilidades",
    "control de acceso",
    "iam",
    "next.js",
    "svelte",
    "astro",
    "webassembly",
    "typescript",
    "tailwind css",
    "aplicaciones web progresivas",
    "diseño responsive",
    "optimización del rendimiento web",
    "grpc",
    "openapi",
    "soap",
    "limitación de tasa",
    "api gateway",
    "colas de mensajes",
    "rabbitmq",
    "kafka",
    "sistemas orientados a eventos",
    "trabajos en segundo plano",
    "webhooks",
    "ecs",
    "eks",
    "lambda",
    "cloud run",
    "app engine",
    "cloudflare workers",
    "malla de servicios",
    "istio",
    "helm",
    "orquestación de contenedores",
    "computación en el borde",
    "fog computing",
    "5g",
    "iot",
    "ar",
    "vr",
    "xr",
    "aprendizaje federado",
    "encriptación cuántica",
    "gemelos digitales",
    "computación neuromórfica",
    "go",
    "rust",
    "swift",
    "kotlin",
    "scala",
    "r",
    "bash",
    "c",
    "c++",
    "java",
    "ruby",
    "php",
    "dart",
    "flutter",
    "swiftui",
    "big data",
    "hadoop",
    "spark",
    "kafka streams",
    "flink",
    "databricks",
    "pipelines de datos",
    "analítica en tiempo real",
    "inteligencia de negocios",
    "power bi",
    "tableau",
]

CX_TECHNICAL_CONCEPTS = [
    "experiencia del cliente",
    "viaje del cliente",
    "satisfacción del cliente",
    "retención de clientes",
    "lealtad del cliente",
    "valor de vida del cliente",
    "net promoter score",
    "nps",
    "csat",
    "ces",
    "puntuación de esfuerzo del cliente",
    "tasa de abandono",
    "voz del cliente",
    "voc",
    "sistema de tickets",
    "software de mesa de ayuda",
    "sla",
    "tiempo de primera respuesta",
    "tiempo promedio de manejo",
    "aht",
    "resolución en primera llamada",
    "fcr",
    "tiempo de resolución",
    "gestión de colas",
    "gestión de escalamiento",
    "trabajo posterior a la llamada",
    "acw",
    "códigos de cierre",
    "disposición de llamada",
    "guiones de llamada",
    "base de conocimiento",
    "automatización de faq",
    "portal de autoservicio",
    "soporte omnicanal",
    "soporte multicanal",
    "manejo de llamadas",
    "llamadas entrantes",
    "llamadas salientes",
    "cola de llamadas",
    "transferencia cálida",
    "transferencia fría",
    "escalamiento de llamada",
    "creación de ticket",
    "soporte por voz",
    "soporte por email",
    "soporte por chat",
    "chat en vivo",
    "soporte en redes sociales",
    "soporte whatsapp",
    "soporte sms",
    "soporte por video",
    "agentes mixtos",
    "cambio de canal",
    "co-navegación",
    "compartir pantalla",
    "crm",
    "espacio de trabajo del agente",
    "escritorio unificado del agente",
    "zendesk",
    "freshdesk",
    "intercom",
    "salesforce service cloud",
    "hubspot service hub",
    "helpscout",
    "genesys",
    "genesys cloud",
    "twilio flex",
    "nice incontact",
    "five9",
    "avaya",
    "amazon connect",
    "ccaas",
    "frontapp",
    "aircall",
    "qualtrics",
    "medallia",
    "chatbots",
    "voicebots",
    "asistentes virtuales",
    "ia conversacional",
    "procesamiento de lenguaje natural",
    "enrutamiento nlp",
    "análisis de sentimiento",
    "detección de intención",
    "analítica de voz",
    "reconocimiento de voz",
    "analítica predictiva",
    "enrutamiento ia",
    "respuestas automatizadas",
    "copiloto ia",
    "asistente ia para agentes",
    "flujos de trabajo automatizados",
    "rpa",
    "transferencia de bot",
    "priorización de cola",
    "enrutamiento de llamadas",
    "enrutamiento basado en habilidades",
    "detección de emociones",
    "siguiente mejor acción",
    "plataforma de datos del cliente",
    "cdp",
    "integración crm",
    "integración de datos",
    "analítica en tiempo real",
    "dashboards",
    "automatización de reportes",
    "análisis de cohortes",
    "analítica de texto",
    "analítica del viaje",
    "analítica de feedback",
    "segmentación de clientes",
    "dashboard de rendimiento del agente",
    "tablas de clasificación",
    "seguimiento de kpi",
    "integración api",
    "webhooks",
    "integración con herramientas bi",
    "inicio de sesión único",
    "sso",
    "oauth",
    "api rest",
    "api graphql",
    "automatización de flujos",
    "ifttt",
    "zapier",
    "sincronización de datos",
    "obtención de datos en tiempo real",
    "experiencia de usuario",
    "interfaz de usuario",
    "diseño ux",
    "diseño ui",
    "personalización",
    "onboarding de clientes",
    "mapeo del viaje",
    "mapas de calor",
    "pruebas a/b",
    "optimización de conversión",
    "analítica comportamental",
    "bucles de retroalimentación del usuario",
    "respuestas conscientes del contexto",
    "centro de contacto como servicio",
    "ivr",
    "respuesta de voz interactiva",
    "marcador automático",
    "marcador predictivo",
    "distribuidor automático de llamadas",
    "acd",
    "grabación de llamadas",
    "grabación de pantalla",
    "monitoreo de llamadas",
    "coaching en vivo",
    "voz a texto",
    "telefonía en la nube",
    "diseño de menú ivr",
    "monitoreo en tiempo real",
    "dashboards de agentes",
    "softphone",
    "integración de auriculares",
    "voip",
    "conexión vpn",
    "monitoreo de latencia",
    "tiempo de actividad del sistema",
    "métricas de calidad de red",
    "latencia de llamada",
    "pérdida de paquetes",
    "webrtc",
    "centro de contacto basado en navegador",
    "entornos de cliente ligero",
    "rgpd",
    "ccpa",
    "privacidad de datos",
    "enmascaramiento de pii",
    "redacción de datos",
    "cumplimiento pci",
    "cumplimiento de seguridad",
    "control de acceso",
    "encriptación",
    "registros de auditoría",
    "permisos basados en roles",
    "captura de pago segura",
    "verificación de identidad",
    "autenticación de llamada",
    "biometría de voz",
    "autenticación basada en conocimiento",
    "consentimiento de grabación de sesión",
    "autenticación de dos factores",
    "módulos de e-learning",
    "microaprendizaje",
    "gamificación",
    "sesiones de coaching",
    "onboarding de agentes",
    "simulaciones de llamadas",
    "feedback de ia",
    "analítica de entrenamiento",
    "sugerencias de conocimiento",
    "surfacing contextual de conocimiento",
    "indicaciones de asistencia en tiempo real",
    "entornos de entrenamiento virtual",
    "perfil del cliente",
    "historial de interacciones",
    "notas del caso",
    "sentimiento del cliente",
    "intención del cliente",
    "orquestación del viaje",
    "soporte proactivo",
    "soporte predictivo",
    "hiperpersonalización",
    "engagement contextual",
    "gemelo digital del cliente",
    "ia de emociones",
    "traducción en tiempo real",
    "soporte de realidad aumentada",
    "sistemas auto-reparables",
    "motor de recomendaciones",
    "seguimiento de sentimiento del agente",
    "transcripción en tiempo real",
    "toma de notas automatizada",
    "indicaciones de engagement proactivo",
]

COMPOUND_PHRASES = {
    "soporte al cliente": "TICKET",
    "ticket de soporte": "TICKET",
    "mensaje de email": "EMAIL",
    "transcripción de chat": "TRANSCRIPT",
    "llamada telefónica": "CALL",
    "código fuente": "CODE",
}

TYPE_KEYWORDS = {
    "llamada": "CALL",
    "reunión": "MEETING",
    "junta": "MEETING",
    "chat": "CHAT",
    "conversación": "CONVERSATION",
    "informe": "REPORT",
    "reporte": "REPORT",
    "artículo": "ARTICLE",
}

CONTEXT_KEYWORDS = {
    "cliente": "CUSTOMER",
    "soporte": "SUPPORT",
    "ventas": "SALES",
    "técnico": "TECHNICAL",
}

NER_DOMAIN_PATTERNS = {
    "ACCOUNT_NUMBER": [
        r"\b[A-Z]{2,4}\d{6,12}\b",
        r"\bcuenta(?: número)?[:\s#]+([A-Z0-9-]+)\b",
        r"\bnúmero de cuenta[:\s#]+([A-Z0-9-]+)\b",
        r"\bperfil[:\s#]+([A-Z0-9-]+)\b",
        r"\bID[:\s#]+([A-Z0-9-]+)\b",
    ],
    "ORDER_NUMBER": [
        r"\bpedido(?: número)?[:\s#]+([A-Z0-9-]+)\b",
        r"\borden[:\s#]+([A-Z0-9-]+)\b",
        r"\bORD-?\d{5,12}\b",
        r"\bPO-?\d{5,12}\b",
    ],
    "TRACKING_NUMBER": [
        r"\b([A-Z]{2}-\d{7,12})\b",
        r"\bTRK\d{8,14}\b",
        r"\bseguimiento(?: número)?[:\s#]+([A-Z0-9-]+)\b",
        r"\brastreo[:\s#]+([A-Z0-9-]+)\b",
    ],
    "TICKET_NUMBER": [
        r"\bTIC?-?\d{5,12}\b",
        r"\bTK-?\d{5,12}\b",
        r"\bticket(?: número)?[:\s#]+([A-Z0-9-]+)\b",
        r"\bincidencia[:\s#]+([A-Z0-9-]+)\b",
    ],
    "EMAIL": [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    ],
    "PHONE_NUMBER": [
        r"\b\+?\d{1,3}[-\s]?\(?\d{2,4}\)?[-\s]?\d{3}[-\s]?\d{3,5}\b",
        r"\b\d{10}\b",
    ],
}

EMOTION_KEYWORDS = {
    "FRUSTRATED": {
        "keywords": [
            "frustrante",
            "frustrado",
            "frustrada",
            "molesto",
            "molesta",
            "irritado",
            "irritada",
            "harto",
            "harta",
            "cansado de esto",
        ],
        "intensity": 0.7,
    },
    "ANGRY": {
        "keywords": [
            "enojado",
            "enojada",
            "furioso",
            "furiosa",
            "enfadado",
            "enfadada",
            "indignado",
            "indignada",
            "inaceptable",
            "ridículo",
        ],
        "intensity": 0.9,
    },
    "DISAPPOINTED": {
        "keywords": [
            "decepcionado",
            "decepcionada",
            "desilusionado",
            "desilusionada",
            "esperaba mejor",
            "no estoy contento",
            "insatisfecho",
            "insatisfecha",
        ],
        "intensity": 0.7,
    },
    "WORRIED": {
        "keywords": [
            "preocupado",
            "preocupada",
            "inquieto",
            "inquieta",
            "ansioso",
            "ansiosa",
            "nervioso",
            "nerviosa",
            "temeroso",
            "temerosa",
        ],
        "intensity": 0.6,
    },
    "CONFUSED": {
        "keywords": [
            "confundido",
            "confundida",
            "no entiendo",
            "no estoy seguro",
            "perdido",
            "perdida",
            "no me queda claro",
        ],
        "intensity": 0.5,
    },
    "GRATEFUL": {
        "keywords": [
            "gracias",
            "agradecido",
            "agradecida",
            "aprecio",
            "muy amable",
            "excelente ayuda",
        ],
        "intensity": 0.6,
    },
    "SATISFIED": {
        "keywords": [
            "satisfecho",
            "satisfecha",
            "contento",
            "contenta",
            "feliz",
            "encantado",
            "encantada",
            "perfecto",
            "excelente",
            "fantástico",
        ],
        "intensity": 0.8,
    },
}

DAY_NAMES = {
    "lunes": "MON",
    "martes": "TUE",
    "miércoles": "WED",
    "jueves": "THU",
    "viernes": "FRI",
    "sábado": "SAT",
    "domingo": "SUN",
}

WORD_TO_NUM = {
    "uno": 1,
    "una": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "par": 2,
}

DAY_ORDER = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]

NER_ADDRESS_ABBREVIATIONS = {
    "Calle": "C/",
    "Avenida": "Av.",
    "Carretera": "Ctra.",
    "Paseo": "P.º",
    "Plaza": "Pza.",
    "Boulevard": "Blvd.",
}

# ── Transcript analyzer patterns ──

RESOLUTION_KEYWORDS = {
    "RESOLVED": {"resuelto", "solucionado", "arreglado", "aprobado", "reembolso"},
    "ESCALATED": {"escalar", "supervisor", "transferir"},
    "PENDING_REPLACEMENT": {"reemplazar", "reemplazo", "cambio"},
}

BILLING_CAUSE_KEYWORDS = {
    "DUPLICATE_PROCESSING": {"duplicado", "procesado dos veces", "reintentado"},
    "DOUBLE_BILLING": {"doble cobro", "cobro doble"},
    "PRORATION_CONFUSION": {"prorrateo", "prorrateado"},
    "SYSTEM_ERROR": {"error", "equivocación"},
    "MID_CYCLE_UPGRADE": {"mejora", "upgrade"},
    "MID_CYCLE_DOWNGRADE": {"degradación", "downgrade"},
    "BILLING_OVERLAP": {"solapamiento", "superposición"},
}

ISSUE_TYPE_KEYWORDS = {
    "BILLING_DISPUTE": {"factura", "cargo", "reembolso", "cobro"},
    "CONNECTIVITY": {"internet", "conexión", "wifi"},
    "PERFORMANCE": {"lento", "velocidad"},
}

SEVERITY_KEYWORDS = {
    "HIGH": {
        "crítico",
        "urgente",
        "emergencia",
        "no funciona para nada",
        "no puedo trabajar",
    },
    "MEDIUM": {
        "frustrado",
        "molesto",
        "lo necesito para trabajar",
        "importante",
    },
}

ISSUE_CONFIRMATION_MAP = {
    "DUPLICATE_CHARGE_CONFIRMED": {
        "duplicado",
        "procesado dos veces",
        "doble cobro",
        "dos cargos",
    }
}

ACTION_EVENT_MAP = {
    "VERIFY": "ACCOUNT_VERIFIED",
    "TROUBLESHOOT": "TROUBLESHOOT",
    "ESCALATE": "ESCALATION_CREATED",
    "REPLACE": "REPLACEMENT_ORDERED",
    "SCHEDULE": "APPOINTMENT_SCHEDULED",
    "UPDATE_INFO": "ACCOUNT_UPDATED",
    "CANCEL": "SERVICE_CANCELLED",
    "OFFER_DISCOUNT": "DISCOUNT_APPLIED",
    "APPROVE": "REQUEST_APPROVED",
    "DENY": "REQUEST_DENIED",
    "NOTIFY": "CUSTOMER_NOTIFIED",
    "DOCUMENT": "DOCUMENTATION_UPDATED",
    "ACTIVATE_TRIAL": "TRIAL_ACTIVATED",
    "REFUND": "REFUND_SUBMITTED",
    "CREDIT": "CREDIT_APPLIED",
}

EXPLICIT_ONLY_ACTIONS = {
    "DOCUMENTATION_UPDATED",
    "ACCOUNT_UPDATED",
    "REQUEST_APPROVED",
}

SUPPORTED_ACTION_TYPES = {
    "REFUND",
    "CREDIT",
    "TROUBLESHOOT",
    "ESCALATE",
    "REPLACE",
    "CHARGE",
    "PAYMENT",
}

ACTION_COMPLETION_KEYWORDS = {
    "enviado",
    "procesado",
    "completado",
    "archivado",
    "aplicado",
    "emitido",
    "listo",
    "hecho",
}

ACTION_COMPLETION_PHRASES = {
    "acabo de enviar",
    "acabo de procesar",
    "ya enviado",
    "ya procesado",
}

ACTION_NOW_PATTERNS = [
    r"(he|acabo de) (enviar|procesar|archivar)\b",
    r"estoy (procesando|enviando|archivando) (lo|el|la|eso)?\s*(ahora)?\b",
]

POSITIVE_CUSTOMER_CONFIRMATIONS = {
    "perfecto",
    "genial",
    "gracias",
    "entendido",
    "recibido",
    "agradezco",
}

AGENT_CONFIRMATION_PHRASES = {
    "todo listo",
    "ya está listo",
    "eso está hecho",
    "completado",
}

EXPLICIT_ACTION_PHRASES = {
    "DOCUMENTATION_UPDATED": {
        "he documentado",
        "he añadido notas",
        "lo registré",
        "he registrado esto",
        "añadido al ticket",
        "actualicé las notas del caso",
    },
    "ACCOUNT_UPDATED": {
        "he actualizado su cuenta",
        "su cuenta ha sido actualizada",
        "cambié su plan",
        "he cambiado su configuración",
    },
}

TECHNICAL_ISSUE_MAP = {
    "OUTAGE": ["corte", "caído", "fuera de línea", "múltiples clientes"],
    "PACKET_LOSS": ["pérdida de paquetes", "línea degradada"],
    "INTERMITTENT_CONNECTIVITY": ["se cae constantemente", "intermitente"],
}

TROUBLESHOOTING_ACTIONS = {
    "TROUBLESHOOTING_PERFORMED": {
        "ejecuté una prueba",
        "reinicié",
        "reiniciar",
        "limpié",
        "realicé",
        "apliqué corrección",
    },
    "DIAGNOSTIC_PERFORMED": {
        "verifiqué",
        "revisé",
        "puedo ver",
        "revisé los registros",
        "veo",
        "consulté",
        "ejecuté diagnósticos",
        "prueba de línea",
    },
}

# ── Language-specific vocabulary tokens ──

ACTION_TOKENS = {
    "REFUND": [
        "reembolso",
        "solicitud de reembolso",
        "devolver dinero",
        "devolución",
        "reintegro",
        "procesar reembolso",
        "emitir reembolso",
        "reembolso parcial",
        "reembolso completo",
        "reversar cargo",
        "ajuste de facturación",
    ],
    "CREDIT": [
        "crédito",
        "abono",
        "crédito en cuenta",
        "aplicar crédito",
        "nota de crédito",
    ],
    "TROUBLESHOOT": [
        "diagnosticar",
        "verificar",
        "revisar",
        "prueba",
        "reiniciar",
        "restablecer",
        "ejecutar diagnóstico",
    ],
    "ESCALATE": [
        "escalar",
        "transferir",
        "supervisor",
        "enviar a nivel superior",
    ],
    "REPLACE": [
        "reemplazar",
        "cambio",
        "sustitución",
        "enviar reemplazo",
    ],
    "SCHEDULE": [
        "programar",
        "cita",
        "agendar",
        "reservar",
    ],
    "VERIFY": [
        "verificar",
        "confirmar",
        "validar",
        "autenticar",
    ],
}

PROMISE_COMMITMENT_TOKENS = {
    "CALLBACK": [
        "le llamaré",
        "le devolveré la llamada",
        "le contactaremos",
        "espere una llamada",
    ],
    "FOLLOW_UP_EMAIL": [
        "le enviaré un correo",
        "recibirá un correo",
        "le envío un email",
        "correo de confirmación",
        "correo electrónico de confirmación",
        "enviar confirmación por correo",
        "le llegará un correo",
    ],
    "CREDIT_PROMISE": [
        "crédito en su cuenta",
        "aplicar un crédito",
        "abono en su cuenta",
        "crédito de",
    ],
    "REFUND_PROMISE": [
        "reembolso de",
        "recibirá un reembolso",
        "procesar el reembolso",
        "devolución de",
        "se le reembolsará",
        "solicitud de reembolso",
    ],
    "DELIVERY_PROMISE": [
        "será entregado",
        "llegará",
        "enviaremos",
        "espere la entrega",
    ],
    "RESOLUTION_PROMISE": [
        "será resuelto",
        "quedará solucionado",
        "nos encargaremos",
        "vamos a solucionar",
    ],
}

REFUND_STATUS_TOKENS = {
    "INITIATED": [
        "iniciado",
        "enviado",
        "solicitado",
        "acabo de procesar",
        "he enviado la solicitud",
        "procesando su reembolso",
    ],
    "PROCESSING": [
        "en proceso",
        "siendo procesado",
        "en trámite",
        "en revisión",
    ],
    "COMPLETED": [
        "completado",
        "reembolsado",
        "crédito aplicado",
        "reembolso emitido",
        "ya reembolsado",
    ],
    "PENDING_APPROVAL": [
        "pendiente de aprobación",
        "necesita aprobación",
        "aprobación del supervisor",
        "en espera de autorización",
    ],
}

REFUND_METHOD_TOKENS = {
    "CARD_CREDIT": [
        "tarjeta de crédito",
        "tarjeta",
        "a su tarjeta",
        "método de pago original",
    ],
    "ACCOUNT_CREDIT": [
        "crédito en cuenta",
        "crédito en su cuenta",
        "saldo de cuenta",
        "abono en cuenta",
    ],
    "CHECK": [
        "cheque",
        "cheque por correo",
    ],
    "PAYPAL": [
        "paypal",
        "cuenta de paypal",
    ],
    "BANK_TRANSFER": [
        "transferencia bancaria",
        "depósito directo",
        "cuenta bancaria",
    ],
}

TIMELINE_EVENT_TOKENS = {
    "ISSUE_RAISED": [
        "mi problema es",
        "estoy teniendo problemas",
        "el problema es",
        "he notado",
        "hay un problema",
        "llamo por",
        "necesito ayuda con",
        "tengo un problema",
    ],
    "INVESTIGATION_STARTED": [
        "déjeme revisar",
        "voy a verificar",
        "déjeme consultar",
        "revisando ahora",
        "viendo su cuenta",
        "puedo ver",
        "déjeme investigar",
    ],
    "ACTION_TAKEN": [
        "he procesado",
        "acabo de enviar",
        "listo",
        "completado",
        "aplicado",
        "programado",
        "he iniciado",
        "acabo de procesar",
    ],
    "RESOLUTION_PROPOSED": [
        "esto debería",
        "debería estar resuelto",
        "debería ver",
        "vamos a resolver",
        "eso debería solucionar",
    ],
    "CONFIRMATION_RECEIVED": [
        "sí, funciona",
        "perfecto",
        "se ve bien",
        "ya lo veo",
        "eso es correcto",
        "ya funciona",
    ],
    "ESCALATION_TRIGGERED": [
        "escalar",
        "transferir a",
        "supervisor",
        "especialista",
        "nivel superior",
    ],
}

RESOLUTION_STATE_TOKENS = {
    "FULLY_RESOLVED": [
        "completamente resuelto",
        "totalmente resuelto",
        "todo listo",
        "todo está arreglado",
        "problema solucionado",
        "asunto resuelto",
        "todo resuelto",
    ],
    "PARTIALLY_RESOLVED": [
        "parcialmente resuelto",
        "casi arreglado",
        "aún quedan algunos problemas",
        "una cosa más",
        "sin embargo",
        "todavía falta",
        "problema principal resuelto",
    ],
    "PENDING_VERIFICATION": [
        "avísenos si",
        "por favor confirme",
        "llame si",
        "monitoree",
        "debería estar funcionando",
        "pruébelo",
    ],
}

CUSTOMER_SATISFACTION_TOKENS = {
    "SATISFIED": [
        "muchas gracias",
        "excelente",
        "perfecto",
        "maravilloso",
        "agradezco su ayuda",
        "ha sido muy amable",
        "eso funciona",
        "genial",
        "muy agradecido",
    ],
    "NEUTRAL": [
        "está bien",
        "de acuerdo",
        "entiendo",
        "ya veo",
        "bien",
        "ok",
        "suena bien",
    ],
    "DISSATISFIED": [
        "no estoy satisfecho",
        "no estoy contento",
        "sigo frustrado",
        "esto no es aceptable",
        "esperaba algo mejor",
        "decepcionado",
        "no ayudó",
        "sigo con problemas",
    ],
}

FOLLOW_UP_NEEDED_TOKENS = {
    "PENDING_ACTION": [
        "será procesado",
        "dentro de",
        "debería recibir",
        "le enviaremos",
        "será completado",
        "tomará efecto",
        "en los próximos",
    ],
    "VERIFICATION_NEEDED": [
        "avísenos si",
        "llame si",
        "contáctenos si",
        "por favor monitoree",
        "confirme que",
        "verifique que",
    ],
    "SCHEDULED_CALLBACK": [
        "le llamaremos",
        "le daré seguimiento",
        "nos comunicaremos",
        "espere una llamada",
        "le llamaré mañana",
    ],
}

TIMELINE_KEYWORDS = {
    "mañana": "TOMORROW",
    "hoy": "TODAY",
}

TIMELINE_PATTERNS = [
    (r"(\d+)\s*a\s*(\d+)\s*días\s*hábiles", "{0}-{1}d"),
    (r"dentro de (\d+)\s*días", "{0}d"),
    (r"dentro de (\d+)\s*horas?", "{0}h"),
    (r"en (\d+)\s*a\s*(\d+)\s*días", "{0}-{1}d"),
]

PROMISE_CONFIDENCE_STRONG = [
    "voy a",
    "le enviaré",
    "le envío",
    "vamos a",
    "le garantizo",
    "definitivamente",
    "sin duda",
    "por supuesto",
]

DISPUTED_AMOUNT_KEYWORDS = [
    "cargo",
    "factura",
    "cobro",
    "pago",
    "monto",
    "importe",
]

# ── Multilingual / speaker detection ──

AGENT_SPEAKER_LABELS = ["agente", "agent"]
CUSTOMER_SPEAKER_LABELS = ["cliente", "client", "customer", "llamante"]

# ── Name extraction patterns ──

NAME_INTRO_PATTERNS = [
    r"(?:me llamo|mi nombre es|soy)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)",
    r"(?:my name is|i'?m|this is)\s+([A-Z][a-z]+)",
]

NAME_THANKS_PATTERNS = [
    r"gracias,\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)",
    r"thank(?:s| you),\s+([A-Z][a-z]+)",
]

NAME_CHANGE_PATTERNS = [
    r"\b(?:cambiar|actualizar|modificar)\s+(?:mi\s+)?(?:nombre\s+)?(?:de\s+)?\w+\s+a\s+\w+",
]

AGENT_NAME_PATTERNS = [
    r"(?:me llamo|mi nombre es|soy)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)",
    r"(?:my name is|this is)\s+([A-Z][a-z]+)",
]

# ── Delay context words ──

DELAY_CONTEXT_WORDS = ["esperando", "llevo", "hace", "desde", "waiting", "been", "ago", "since"]

# ── Call type detection ──

CALL_TYPE_SALES_KEYWORDS = ["actualización", "precio", "comprar", "interesado en", "upgrade", "pricing"]

# ── Amount reason context ──

AMOUNT_REASON_CONTEXT = [
    ("duplicado", "DUPLICATE_CHARGE"),
    ("duplicate", "DUPLICATE_CHARGE"),
    ("reembolso", "REFUND"),
    ("refund", "REFUND"),
    ("extra", "EXTRA_CHARGE"),
    ("descuento", "DISCOUNT"),
    ("discount", "DISCOUNT"),
    ("crédito", "CREDIT"),
    ("credit", "CREDIT"),
    ("cargo", "CHARGE"),
    ("cobro", "CHARGE"),
    ("fee", "FEE"),
    ("charge", "CHARGE"),
    ("charged", "CHARGE"),
]

# ── Redacted field context ──

REDACTED_FIELD_CONTEXT = [
    ("email", "EMAIL_REDACTED"),
    ("correo", "EMAIL_REDACTED"),
    ("teléfono", "PHONE_REDACTED"),
    ("telefono", "PHONE_REDACTED"),
    ("phone", "PHONE_REDACTED"),
    ("número", "PHONE_REDACTED"),
    ("number", "PHONE_REDACTED"),
    ("dirección", "ADDRESS_REDACTED"),
    ("address", "ADDRESS_REDACTED"),
    ("nombre", "NAME_REDACTED"),
    ("name", "NAME_REDACTED"),
]

# ── Extra commitment patterns ──

EXTRA_COMMITMENT_PATTERNS = {
    "CONFIRMATION_EMAIL": [
        "le enviaré una confirmación",
        "correo de confirmación",
        "recibirá un correo",
        "confirmación por email",
        "send you a confirmation",
        "confirmation email",
    ],
    "FOLLOWUP": [
        "le haré seguimiento",
        "voy a hacer seguimiento",
        "personalmente le haré seguimiento",
        "seguimiento mañana",
        "i'll follow up",
        "follow up with you",
    ],
    "MONITORING": [
        "monitorear",
        "vigilar",
        "monitoring",
        "keep an eye on",
    ],
}

# ── Promise timeline patterns ──

PROMISE_TIMELINE_PATTERNS = [
    (r"dentro\s+de\s+(\d+)\s*horas?", "{0}h"),
    (r"dentro\s+de\s+(\d+)\s*días?", "{0}d"),
    (r"para\s+el\s+(lunes|martes|miércoles|jueves|viernes|sábado|domingo)", "{0}"),
    (r"antes\s+del\s+(lunes|martes|miércoles|jueves|viernes|sábado|domingo)", "{0}"),
    (r"en\s+los?\s+próximos?\s+(\d+)\s*días?", "{0}d"),
    (r"within\s+(\d+)\s*hours?", "{0}h"),
    (r"within\s+(\d+)\s*days?", "{0}d"),
]

# ── Promise confidence strong indicators ──

PROMISE_CONFIDENCE_STRONG = [
    "voy a", "le enviaré", "vamos a", "definitivamente",
    "sin duda", "por supuesto", "will", "going to", "i'll",
]
