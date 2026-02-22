"""
Pattern definitions and constants for target extraction - Portuguese
"""

TECHNICAL_CONCEPTS = [
    "estruturas de dados",
    "algoritmos",
    "complexidade computacional",
    "sistemas operacionais",
    "memória virtual",
    "concorrência",
    "multithreading",
    "computação paralela",
    "sistemas distribuídos",
    "balanceamento de carga",
    "arquitetura orientada a eventos",
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
    "bancos de dados relacionais",
    "bancos de dados documentais",
    "bancos de dados de grafos",
    "bancos de dados de séries temporais",
    "indexação",
    "otimização de consultas",
    "acid",
    "event sourcing",
    "data warehouse",
    "etl",
    "data lakes",
    "cache",
    "redis",
    "elasticsearch",
    "programação orientada a objetos",
    "programação funcional",
    "desenvolvimento guiado por testes",
    "padrões de projeto",
    "injeção de dependência",
    "integração contínua",
    "deploy contínuo",
    "controle de versão",
    "git",
    "monolito",
    "microfrontends",
    "design orientado ao domínio",
    "arquitetura limpa",
    "infraestrutura como código",
    "terraform",
    "ansible",
    "jenkins",
    "pipelines cicd",
    "monitoramento",
    "observabilidade",
    "logging",
    "prometheus",
    "grafana",
    "testes de carga",
    "engenharia do caos",
    "aprendizado por reforço",
    "visão computacional",
    "processamento de linguagem natural",
    "ia generativa",
    "transformers",
    "autoencoders",
    "engenharia de features",
    "pré-processamento de dados",
    "deploy de modelos",
    "mlops",
    "bancos de dados vetoriais",
    "criptografia",
    "hashing",
    "ssl",
    "tls",
    "oauth",
    "jwt",
    "arquitetura zero trust",
    "testes de penetração",
    "varredura de vulnerabilidades",
    "controle de acesso",
    "iam",
    "next.js",
    "svelte",
    "astro",
    "webassembly",
    "typescript",
    "tailwind css",
    "aplicações web progressivas",
    "design responsivo",
    "otimização de performance web",
    "grpc",
    "openapi",
    "soap",
    "limitação de taxa",
    "api gateway",
    "filas de mensagens",
    "rabbitmq",
    "kafka",
    "sistemas orientados a eventos",
    "jobs em background",
    "webhooks",
    "ecs",
    "eks",
    "lambda",
    "cloud run",
    "app engine",
    "cloudflare workers",
    "service mesh",
    "istio",
    "helm",
    "orquestração de containers",
    "edge computing",
    "fog computing",
    "5g",
    "iot",
    "ar",
    "vr",
    "xr",
    "aprendizado federado",
    "criptografia quântica",
    "gêmeos digitais",
    "computação neuromórfica",
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
    "pipelines de dados",
    "analytics em tempo real",
    "business intelligence",
    "power bi",
    "tableau",
]

CX_TECHNICAL_CONCEPTS = [
    "experiência do cliente",
    "jornada do cliente",
    "satisfação do cliente",
    "retenção de clientes",
    "fidelidade do cliente",
    "valor vitalício do cliente",
    "net promoter score",
    "nps",
    "csat",
    "ces",
    "pontuação de esforço do cliente",
    "taxa de churn",
    "voz do cliente",
    "voc",
    "sistema de tickets",
    "software de help desk",
    "sla",
    "tempo de primeira resposta",
    "tempo médio de atendimento",
    "tma",
    "resolução na primeira chamada",
    "fcr",
    "tempo de resolução",
    "gestão de filas",
    "gestão de escalação",
    "trabalho pós-atendimento",
    "acw",
    "códigos de encerramento",
    "disposição de chamada",
    "scripts de atendimento",
    "base de conhecimento",
    "automação de faq",
    "portal de autoatendimento",
    "suporte omnichannel",
    "suporte multicanal",
    "gestão de chamadas",
    "chamadas receptivas",
    "chamadas ativas",
    "fila de chamadas",
    "transferência quente",
    "transferência fria",
    "escalação de chamada",
    "criação de ticket",
    "suporte por voz",
    "suporte por email",
    "suporte por chat",
    "chat ao vivo",
    "suporte em redes sociais",
    "suporte whatsapp",
    "suporte sms",
    "suporte por vídeo",
    "agentes multiskill",
    "mudança de canal",
    "co-navegação",
    "compartilhamento de tela",
    "crm",
    "área de trabalho do agente",
    "desktop unificado do agente",
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
    "assistentes virtuais",
    "ia conversacional",
    "processamento de linguagem natural",
    "roteamento nlp",
    "análise de sentimento",
    "detecção de intenção",
    "analytics de voz",
    "reconhecimento de voz",
    "analytics preditivo",
    "roteamento ia",
    "respostas automatizadas",
    "copiloto ia",
    "assistente ia para agentes",
    "workflows automatizados",
    "rpa",
    "transferência de bot",
    "priorização de fila",
    "roteamento de chamadas",
    "roteamento baseado em habilidades",
    "detecção de emoções",
    "próxima melhor ação",
    "plataforma de dados do cliente",
    "cdp",
    "integração crm",
    "integração de dados",
    "analytics em tempo real",
    "dashboards",
    "automação de relatórios",
    "análise de coortes",
    "analytics de texto",
    "analytics da jornada",
    "analytics de feedback",
    "segmentação de clientes",
    "dashboard de performance do agente",
    "rankings",
    "acompanhamento de kpi",
    "integração api",
    "webhooks",
    "integração com ferramentas bi",
    "single sign-on",
    "sso",
    "oauth",
    "api rest",
    "api graphql",
    "automação de workflows",
    "ifttt",
    "zapier",
    "sincronização de dados",
    "busca de dados em tempo real",
    "experiência do usuário",
    "interface do usuário",
    "design ux",
    "design ui",
    "personalização",
    "onboarding de clientes",
    "mapeamento da jornada",
    "mapas de calor",
    "testes a/b",
    "otimização de conversão",
    "analytics comportamental",
    "loops de feedback do usuário",
    "respostas contextuais",
    "contact center as a service",
    "ura",
    "unidade de resposta audível",
    "discador automático",
    "discador preditivo",
    "distribuidor automático de chamadas",
    "dac",
    "gravação de chamadas",
    "gravação de tela",
    "monitoramento de chamadas",
    "coaching ao vivo",
    "transcrição de voz",
    "telefonia na nuvem",
    "design de menu ura",
    "monitoramento em tempo real",
    "dashboards de agentes",
    "softphone",
    "integração de headset",
    "voip",
    "conexão vpn",
    "monitoramento de latência",
    "uptime do sistema",
    "métricas de qualidade de rede",
    "latência de chamada",
    "perda de pacotes",
    "webrtc",
    "contact center baseado em navegador",
    "ambientes thin client",
    "lgpd",
    "gdpr",
    "privacidade de dados",
    "mascaramento de pii",
    "redação de dados",
    "conformidade pci",
    "conformidade de segurança",
    "controle de acesso",
    "criptografia",
    "logs de auditoria",
    "permissões baseadas em função",
    "captura segura de pagamento",
    "verificação de identidade",
    "autenticação de chamada",
    "biometria de voz",
    "autenticação baseada em conhecimento",
    "consentimento de gravação de sessão",
    "autenticação de dois fatores",
    "módulos de e-learning",
    "microlearning",
    "gamificação",
    "sessões de coaching",
    "onboarding de agentes",
    "simulações de chamadas",
    "feedback de ia",
    "analytics de treinamento",
    "sugestões de conhecimento",
    "surfacing contextual de conhecimento",
    "prompts de assistência em tempo real",
    "ambientes de treinamento virtual",
    "perfil do cliente",
    "histórico de interações",
    "notas do caso",
    "sentimento do cliente",
    "intenção do cliente",
    "orquestração da jornada",
    "suporte proativo",
    "suporte preditivo",
    "hiperpersonalização",
    "engajamento contextual",
    "gêmeo digital do cliente",
    "ia de emoções",
    "tradução em tempo real",
    "suporte de realidade aumentada",
    "sistemas auto-reparáveis",
    "motor de recomendações",
    "acompanhamento de sentimento do agente",
    "transcrição em tempo real",
    "anotação automática",
    "prompts de engajamento proativo",
]

COMPOUND_PHRASES = {
    "suporte ao cliente": "TICKET",
    "ticket de suporte": "TICKET",
    "chamado de suporte": "TICKET",
    "mensagem de email": "EMAIL",
    "transcrição de chat": "TRANSCRIPT",
    "chamada telefônica": "CALL",
    "ligação telefônica": "CALL",
    "código fonte": "CODE",
}

TYPE_KEYWORDS = {
    "chamada": "CALL",
    "ligação": "CALL",
    "reunião": "MEETING",
    "encontro": "MEETING",
    "chat": "CHAT",
    "conversa": "CONVERSATION",
    "relatório": "REPORT",
    "artigo": "ARTICLE",
}

CONTEXT_KEYWORDS = {
    "cliente": "CUSTOMER",
    "suporte": "SUPPORT",
    "vendas": "SALES",
    "técnico": "TECHNICAL",
}

NER_DOMAIN_PATTERNS = {
    "ACCOUNT_NUMBER": [
        r"\b[A-Z]{2,4}\d{6,12}\b",
        r"\bconta(?: número)?[:\s#]+([A-Z0-9-]+)\b",
        r"\bnúmero da conta[:\s#]+([A-Z0-9-]+)\b",
        r"\bperfil[:\s#]+([A-Z0-9-]+)\b",
        r"\bID[:\s#]+([A-Z0-9-]+)\b",
    ],
    "ORDER_NUMBER": [
        r"\bpedido(?: número)?[:\s#]+([A-Z0-9-]+)\b",
        r"\bnúmero do pedido[:\s#]+([A-Z0-9-]+)\b",
        r"\bORD-?\d{5,12}\b",
        r"\bPO-?\d{5,12}\b",
    ],
    "TRACKING_NUMBER": [
        r"\b([A-Z]{2}-\d{7,12})\b",
        r"\bTRK\d{8,14}\b",
        r"\brastreamento(?: número)?[:\s#]+([A-Z0-9-]+)\b",
        r"\bnúmero de rastreio[:\s#]+([A-Z0-9-]+)\b",
    ],
    "TICKET_NUMBER": [
        r"\bTIC?-?\d{5,12}\b",
        r"\bTK-?\d{5,12}\b",
        r"\bticket(?: número)?[:\s#]+([A-Z0-9-]+)\b",
        r"\bchamado[:\s#]+([A-Z0-9-]+)\b",
    ],
    "EMAIL": [
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    ],
    "PHONE_NUMBER": [
        r"\b\+?\d{1,3}[-\s]?\(?\d{2,4}\)?[-\s]?\d{3}[-\s]?\d{3,5}\b",
        r"\b\d{10,11}\b",
    ],
}

EMOTION_KEYWORDS = {
    "FRUSTRATED": {
        "keywords": [
            "frustrante",
            "frustrado",
            "frustrada",
            "irritado",
            "irritada",
            "chateado",
            "chateada",
            "cansado disso",
            "de saco cheio",
        ],
        "intensity": 0.7,
    },
    "ANGRY": {
        "keywords": [
            "com raiva",
            "furioso",
            "furiosa",
            "bravo",
            "brava",
            "indignado",
            "indignada",
            "inaceitável",
            "ridículo",
            "absurdo",
        ],
        "intensity": 0.9,
    },
    "DISAPPOINTED": {
        "keywords": [
            "decepcionado",
            "decepcionada",
            "desapontado",
            "desapontada",
            "esperava melhor",
            "não estou feliz",
            "insatisfeito",
            "insatisfeita",
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
            "nervoso",
            "nervosa",
            "receoso",
            "receosa",
        ],
        "intensity": 0.6,
    },
    "CONFUSED": {
        "keywords": [
            "confuso",
            "confusa",
            "não entendo",
            "não tenho certeza",
            "perdido",
            "perdida",
            "não está claro",
        ],
        "intensity": 0.5,
    },
    "GRATEFUL": {
        "keywords": [
            "obrigado",
            "obrigada",
            "grato",
            "grata",
            "agradeço",
            "muito gentil",
            "excelente ajuda",
        ],
        "intensity": 0.6,
    },
    "SATISFIED": {
        "keywords": [
            "satisfeito",
            "satisfeita",
            "contente",
            "feliz",
            "encantado",
            "encantada",
            "perfeito",
            "excelente",
            "fantástico",
            "maravilhoso",
        ],
        "intensity": 0.8,
    },
}

DAY_NAMES = {
    "segunda": "MON",
    "segunda-feira": "MON",
    "terça": "TUE",
    "terça-feira": "TUE",
    "quarta": "WED",
    "quarta-feira": "WED",
    "quinta": "THU",
    "quinta-feira": "THU",
    "sexta": "FRI",
    "sexta-feira": "FRI",
    "sábado": "SAT",
    "domingo": "SUN",
}

WORD_TO_NUM = {
    "um": 1,
    "uma": 1,
    "dois": 2,
    "duas": 2,
    "três": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "par": 2,
}

DAY_ORDER = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]

NER_ADDRESS_ABBREVIATIONS = {
    "Rua": "R.",
    "Avenida": "Av.",
    "Estrada": "Estr.",
    "Praça": "Pça.",
    "Travessa": "Trav.",
    "Alameda": "Al.",
}

# ── Transcript analyzer patterns ──

RESOLUTION_KEYWORDS = {
    "RESOLVED": {"resolvido", "corrigido", "solucionado", "aprovado", "reembolso"},
    "ESCALATED": {"escalar", "supervisor", "transferir"},
    "PENDING_REPLACEMENT": {"substituir", "substituição", "troca"},
}

BILLING_CAUSE_KEYWORDS = {
    "DUPLICATE_PROCESSING": {"duplicado", "processado duas vezes", "reprocessado"},
    "DOUBLE_BILLING": {"cobrança dupla", "cobrado duas vezes"},
    "PRORATION_CONFUSION": {"rateio", "pro rata"},
    "SYSTEM_ERROR": {"erro", "engano"},
    "MID_CYCLE_UPGRADE": {"upgrade", "melhoria"},
    "MID_CYCLE_DOWNGRADE": {"downgrade", "redução"},
    "BILLING_OVERLAP": {"sobreposição"},
}

ISSUE_TYPE_KEYWORDS = {
    "BILLING_DISPUTE": {"fatura", "cobrança", "reembolso"},
    "CONNECTIVITY": {"internet", "conexão", "wifi"},
    "PERFORMANCE": {"lento", "velocidade"},
}

SEVERITY_KEYWORDS = {
    "HIGH": {
        "crítico",
        "urgente",
        "emergência",
        "não funciona de jeito nenhum",
        "não consigo trabalhar",
    },
    "MEDIUM": {
        "frustrado",
        "irritante",
        "preciso para trabalhar",
        "importante",
    },
}

ISSUE_CONFIRMATION_MAP = {
    "DUPLICATE_CHARGE_CONFIRMED": {
        "duplicado",
        "processado duas vezes",
        "cobrança dupla",
        "duas cobranças",
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
    "processado",
    "concluído",
    "arquivado",
    "aplicado",
    "emitido",
    "pronto",
    "feito",
}

ACTION_COMPLETION_PHRASES = {
    "acabei de enviar",
    "acabei de processar",
    "já enviado",
    "já processado",
}

ACTION_NOW_PATTERNS = [
    r"(eu )?acabei de (enviar|processar|arquivar)\b",
    r"estou (processando|enviando|arquivando) (isso|o|a)?\s*(agora)?\b",
]

POSITIVE_CUSTOMER_CONFIRMATIONS = {
    "perfeito",
    "ótimo",
    "obrigado",
    "entendi",
    "recebido",
    "agradeço",
}

AGENT_CONFIRMATION_PHRASES = {
    "tudo pronto",
    "está tudo certo",
    "isso está feito",
    "concluído",
}

EXPLICIT_ACTION_PHRASES = {
    "DOCUMENTATION_UPDATED": {
        "eu documentei",
        "adicionei notas",
        "registrei isso",
        "adicionado ao ticket",
        "atualizei as notas do caso",
    },
    "ACCOUNT_UPDATED": {
        "atualizei sua conta",
        "sua conta foi atualizada",
        "alterei seu plano",
        "alterei suas configurações",
    },
}

TECHNICAL_ISSUE_MAP = {
    "OUTAGE": ["queda", "fora do ar", "offline", "vários clientes"],
    "PACKET_LOSS": ["perda de pacotes", "linha degradada"],
    "INTERMITTENT_CONNECTIVITY": ["fica caindo", "intermitente"],
}

TROUBLESHOOTING_ACTIONS = {
    "TROUBLESHOOTING_PERFORMED": {
        "executei um teste",
        "reiniciei",
        "reiniciar",
        "limpei",
        "realizei",
        "apliquei correção",
    },
    "DIAGNOSTIC_PERFORMED": {
        "verifiquei",
        "analisei",
        "consigo ver",
        "revisei os logs",
        "estou vendo",
        "consultei",
        "executei diagnósticos",
        "teste de linha",
    },
}

# ── Multilingual / speaker detection ──

AGENT_SPEAKER_LABELS = ["agente", "agent"]
CUSTOMER_SPEAKER_LABELS = ["cliente", "client", "customer", "chamador"]

# ── Timeline defaults (Portuguese) ──

TIMELINE_KEYWORDS = {
    "amanhã": "TOMORROW",
    "hoje": "TODAY",
}

TIMELINE_PATTERNS = [
    (r"(\d+)\s*a\s*(\d+)\s*dias?\s*úteis?", "{0}-{1}d"),
    (r"dentro\s+de\s+(\d+)\s*horas?", "{0}h"),
    (r"dentro\s+de\s+(\d+)\s*dias?", "{0}d"),
    (r"em\s+(\d+)\s*a\s*(\d+)\s*dias?", "{0}-{1}d"),
]

# ── Disputed amount keywords ──

DISPUTED_AMOUNT_KEYWORDS = [
    "cobrança",
    "fatura",
    "pagamento",
    "valor",
    "extrato",
    "charge",
    "payment",
]

# ── Amount reason context ──

AMOUNT_REASON_CONTEXT = [
    ("duplicado", "DUPLICATE_CHARGE"),
    ("duplicate", "DUPLICATE_CHARGE"),
    ("reembolso", "REFUND"),
    ("refund", "REFUND"),
    ("extra", "EXTRA_CHARGE"),
    ("desconto", "DISCOUNT"),
    ("discount", "DISCOUNT"),
    ("crédito", "CREDIT"),
    ("credit", "CREDIT"),
    ("taxa", "FEE"),
    ("fee", "FEE"),
    ("cobrança", "CHARGE"),
    ("charge", "CHARGE"),
    ("charged", "CHARGE"),
]

# ── Redacted field context ──

REDACTED_FIELD_CONTEXT = [
    ("email", "EMAIL_REDACTED"),
    ("e-mail", "EMAIL_REDACTED"),
    ("telefone", "PHONE_REDACTED"),
    ("celular", "PHONE_REDACTED"),
    ("phone", "PHONE_REDACTED"),
    ("número", "PHONE_REDACTED"),
    ("number", "PHONE_REDACTED"),
    ("endereço", "ADDRESS_REDACTED"),
    ("address", "ADDRESS_REDACTED"),
    ("nome", "NAME_REDACTED"),
    ("name", "NAME_REDACTED"),
]

# ── Call type detection ──

CALL_TYPE_SALES_KEYWORDS = [
    "atualização",
    "preço",
    "comprar",
    "interessado em",
    "upgrade",
    "pricing",
]

# ── Name extraction patterns ──

NAME_INTRO_PATTERNS = [
    r"(?:meu nome é|me chamo|sou o|sou a)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)",
    r"(?:my name is|i'?m|this is)\s+([A-Z][a-z]+)",
]

NAME_THANKS_PATTERNS = [
    r"obrigado,\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)",
    r"obrigada,\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)",
    r"thank(?:s| you),\s+([A-Z][a-z]+)",
]

NAME_CHANGE_PATTERNS = [
    r"\b(?:mudar|alterar|atualizar)\s+(?:meu\s+)?(?:nome\s+)?(?:de\s+)?\w+\s+para\s+\w+",
]

AGENT_NAME_PATTERNS = [
    r"(?:meu nome é|me chamo|sou o|sou a)\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+)",
    r"(?:my name is|this is)\s+([A-Z][a-z]+)",
]

# ── Delay context words ──

DELAY_CONTEXT_WORDS = [
    "esperando",
    "aguardando",
    "faz",
    "desde",
    "waiting",
    "been",
    "ago",
    "since",
]

# ── Extra commitment patterns ──

EXTRA_COMMITMENT_PATTERNS = {
    "CONFIRMATION_EMAIL": [
        "enviarei uma confirmação",
        "e-mail de confirmação",
        "receberá um e-mail",
        "confirmação por email",
        "send you a confirmation",
        "confirmation email",
    ],
    "FOLLOWUP": [
        "vou acompanhar",
        "farei o acompanhamento",
        "vou fazer o seguimento",
        "i'll follow up",
        "follow up with you",
    ],
    "MONITORING": [
        "monitorar",
        "acompanhar",
        "monitoring",
        "keep an eye on",
    ],
}

# ── Promise timeline patterns ──

PROMISE_TIMELINE_PATTERNS = [
    (r"dentro\s+de\s+(\d+)\s*horas?", "{0}h"),
    (r"dentro\s+de\s+(\d+)\s*dias?", "{0}d"),
    (r"até\s+(segunda|terça|quarta|quinta|sexta|sábado|domingo)", "{0}"),
    (r"em\s+até\s+(\d+)\s*dias?", "{0}d"),
    (r"within\s+(\d+)\s*hours?", "{0}h"),
    (r"within\s+(\d+)\s*days?", "{0}d"),
]

# ── Promise confidence strong indicators ──

PROMISE_CONFIDENCE_STRONG = [
    "vou",
    "vamos",
    "irei",
    "definitivamente",
    "certamente",
    "com certeza",
    "will",
    "going to",
    "i'll",
]
