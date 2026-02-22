"""
Pattern definitions and constants for target extraction - French
"""

TECHNICAL_CONCEPTS = [
    "structures de données",
    "algorithmes",
    "complexité computationnelle",
    "systèmes d'exploitation",
    "mémoire virtuelle",
    "concurrence",
    "multithreading",
    "calcul parallèle",
    "systèmes distribués",
    "équilibrage de charge",
    "architecture événementielle",
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
    "serveurs proxy",
    "pare-feu",
    "nat",
    "bgp",
    "bases de données relationnelles",
    "bases de données documentaires",
    "bases de données graphes",
    "bases de données temporelles",
    "indexation",
    "optimisation des requêtes",
    "acid",
    "event sourcing",
    "entrepôt de données",
    "etl",
    "lacs de données",
    "mise en cache",
    "redis",
    "elasticsearch",
    "programmation orientée objet",
    "programmation fonctionnelle",
    "développement piloté par les tests",
    "patrons de conception",
    "injection de dépendances",
    "intégration continue",
    "déploiement continu",
    "contrôle de version",
    "git",
    "monolithe",
    "microfrontends",
    "conception pilotée par le domaine",
    "architecture propre",
    "infrastructure as code",
    "terraform",
    "ansible",
    "jenkins",
    "pipelines cicd",
    "surveillance",
    "observabilité",
    "journalisation",
    "prometheus",
    "grafana",
    "tests de charge",
    "ingénierie du chaos",
    "apprentissage par renforcement",
    "vision par ordinateur",
    "traitement du langage naturel",
    "ia générative",
    "transformers",
    "auto-encodeurs",
    "ingénierie des caractéristiques",
    "prétraitement des données",
    "déploiement de modèles",
    "mlops",
    "bases de données vectorielles",
    "chiffrement",
    "hachage",
    "ssl",
    "tls",
    "oauth",
    "jwt",
    "architecture zero trust",
    "tests de pénétration",
    "analyse de vulnérabilités",
    "contrôle d'accès",
    "iam",
    "next.js",
    "svelte",
    "astro",
    "webassembly",
    "typescript",
    "tailwind css",
    "applications web progressives",
    "design responsive",
    "optimisation des performances web",
    "grpc",
    "openapi",
    "soap",
    "limitation de débit",
    "passerelle api",
    "files de messages",
    "rabbitmq",
    "kafka",
    "systèmes événementiels",
    "tâches en arrière-plan",
    "webhooks",
    "ecs",
    "eks",
    "lambda",
    "cloud run",
    "app engine",
    "cloudflare workers",
    "maillage de services",
    "istio",
    "helm",
    "orchestration de conteneurs",
    "edge computing",
    "fog computing",
    "5g",
    "iot",
    "ar",
    "vr",
    "xr",
    "apprentissage fédéré",
    "chiffrement quantique",
    "jumeaux numériques",
    "informatique neuromorphique",
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
    "pipelines de données",
    "analytique temps réel",
    "intelligence d'affaires",
    "power bi",
    "tableau",
]

CX_TECHNICAL_CONCEPTS = [
    "expérience client",
    "parcours client",
    "satisfaction client",
    "rétention client",
    "fidélité client",
    "valeur vie client",
    "net promoter score",
    "nps",
    "csat",
    "ces",
    "score d'effort client",
    "taux d'attrition",
    "voix du client",
    "voc",
    "système de tickets",
    "logiciel de helpdesk",
    "sla",
    "temps de première réponse",
    "temps moyen de traitement",
    "aht",
    "résolution au premier appel",
    "fcr",
    "temps de résolution",
    "gestion des files d'attente",
    "gestion des escalades",
    "travail après appel",
    "acw",
    "codes de clôture",
    "disposition d'appel",
    "scripts d'appel",
    "base de connaissances",
    "automatisation faq",
    "portail libre-service",
    "support omnicanal",
    "support multicanal",
    "gestion des appels",
    "appels entrants",
    "appels sortants",
    "file d'appels",
    "transfert accompagné",
    "transfert à froid",
    "escalade d'appel",
    "création de ticket",
    "support vocal",
    "support email",
    "support chat",
    "chat en direct",
    "support réseaux sociaux",
    "support whatsapp",
    "support sms",
    "support vidéo",
    "agents polyvalents",
    "changement de canal",
    "co-navigation",
    "partage d'écran",
    "crm",
    "espace de travail agent",
    "bureau agent unifié",
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
    "assistants virtuels",
    "ia conversationnelle",
    "traitement du langage naturel",
    "routage nlp",
    "analyse de sentiment",
    "détection d'intention",
    "analytique vocale",
    "reconnaissance vocale",
    "analytique prédictive",
    "routage ia",
    "réponses automatisées",
    "copilote ia",
    "assistant ia agent",
    "workflows automatisés",
    "rpa",
    "transfert bot",
    "priorisation de file",
    "routage d'appels",
    "routage basé sur les compétences",
    "détection d'émotions",
    "prochaine meilleure action",
    "plateforme de données client",
    "cdp",
    "intégration crm",
    "intégration de données",
    "analytique temps réel",
    "tableaux de bord",
    "automatisation des rapports",
    "analyse de cohortes",
    "analytique textuelle",
    "analytique du parcours",
    "analytique feedback",
    "segmentation client",
    "tableau de bord performance agent",
    "classements",
    "suivi kpi",
    "intégration api",
    "webhooks",
    "intégration outils bi",
    "authentification unique",
    "sso",
    "oauth",
    "api rest",
    "api graphql",
    "automatisation des workflows",
    "ifttt",
    "zapier",
    "synchronisation des données",
    "récupération de données temps réel",
    "expérience utilisateur",
    "interface utilisateur",
    "design ux",
    "design ui",
    "personnalisation",
    "onboarding client",
    "cartographie du parcours",
    "cartes de chaleur",
    "tests a/b",
    "optimisation de conversion",
    "analytique comportementale",
    "boucles de feedback utilisateur",
    "réponses contextuelles",
    "centre de contact as a service",
    "ivr",
    "serveur vocal interactif",
    "numéroteur automatique",
    "numéroteur prédictif",
    "distributeur automatique d'appels",
    "acd",
    "enregistrement d'appels",
    "enregistrement d'écran",
    "monitoring d'appels",
    "coaching en direct",
    "transcription vocale",
    "téléphonie cloud",
    "conception menu ivr",
    "monitoring temps réel",
    "tableaux de bord agents",
    "softphone",
    "intégration casque",
    "voip",
    "connexion vpn",
    "monitoring latence",
    "disponibilité système",
    "métriques qualité réseau",
    "latence d'appel",
    "perte de paquets",
    "webrtc",
    "centre de contact navigateur",
    "environnements client léger",
    "rgpd",
    "ccpa",
    "confidentialité des données",
    "masquage pii",
    "rédaction de données",
    "conformité pci",
    "conformité sécurité",
    "contrôle d'accès",
    "chiffrement",
    "journaux d'audit",
    "permissions basées sur les rôles",
    "capture de paiement sécurisée",
    "vérification d'identité",
    "authentification d'appel",
    "biométrie vocale",
    "authentification basée sur les connaissances",
    "consentement enregistrement session",
    "authentification à deux facteurs",
    "modules e-learning",
    "microapprentissage",
    "gamification",
    "sessions de coaching",
    "onboarding agents",
    "simulations d'appels",
    "feedback ia",
    "analytique formation",
    "suggestions de connaissances",
    "affichage contextuel des connaissances",
    "invites d'assistance temps réel",
    "environnements de formation virtuels",
    "profil client",
    "historique des interactions",
    "notes de dossier",
    "sentiment client",
    "intention client",
    "orchestration du parcours",
    "support proactif",
    "support prédictif",
    "hyperpersonnalisation",
    "engagement contextuel",
    "jumeau numérique client",
    "ia émotionnelle",
    "traduction temps réel",
    "support réalité augmentée",
    "systèmes auto-réparateurs",
    "moteur de recommandations",
    "suivi sentiment agent",
    "transcription temps réel",
    "prise de notes automatisée",
    "invites d'engagement proactif",
]

COMPOUND_PHRASES = {
    "support client": "TICKET",
    "ticket de support": "TICKET",
    "message email": "EMAIL",
    "transcription de chat": "TRANSCRIPT",
    "appel téléphonique": "CALL",
    "code source": "CODE",
}

TYPE_KEYWORDS = {
    "appel": "CALL",
    "réunion": "MEETING",
    "rencontre": "MEETING",
    "chat": "CHAT",
    "conversation": "CONVERSATION",
    "rapport": "REPORT",
    "article": "ARTICLE",
}

CONTEXT_KEYWORDS = {
    "client": "CUSTOMER",
    "support": "SUPPORT",
    "ventes": "SALES",
    "technique": "TECHNICAL",
}

NER_DOMAIN_PATTERNS = {
    "ACCOUNT_NUMBER": [
        r"\b[A-Z]{2,4}\d{6,12}\b",
        r"\bcompte(?: numéro)?[:\s#]+([A-Z0-9-]+)\b",
        r"\bnuméro de compte[:\s#]+([A-Z0-9-]+)\b",
        r"\bprofil[:\s#]+([A-Z0-9-]+)\b",
        r"\bID[:\s#]+([A-Z0-9-]+)\b",
    ],
    "ORDER_NUMBER": [
        r"\bcommande(?: numéro)?[:\s#]+([A-Z0-9-]+)\b",
        r"\bnuméro de commande[:\s#]+([A-Z0-9-]+)\b",
        r"\bORD-?\d{5,12}\b",
        r"\bPO-?\d{5,12}\b",
    ],
    "TRACKING_NUMBER": [
        r"\b([A-Z]{2}-\d{7,12})\b",
        r"\bTRK\d{8,14}\b",
        r"\bsuivi(?: numéro)?[:\s#]+([A-Z0-9-]+)\b",
        r"\bnuméro de suivi[:\s#]+([A-Z0-9-]+)\b",
    ],
    "TICKET_NUMBER": [
        r"\bTIC?-?\d{5,12}\b",
        r"\bTK-?\d{5,12}\b",
        r"\bticket(?: numéro)?[:\s#]+([A-Z0-9-]+)\b",
        r"\bincident[:\s#]+([A-Z0-9-]+)\b",
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
            "frustrant",
            "frustré",
            "frustrée",
            "agaçant",
            "agacé",
            "agacée",
            "irrité",
            "irritée",
            "ras-le-bol",
            "fatigué de ça",
        ],
        "intensity": 0.7,
    },
    "ANGRY": {
        "keywords": [
            "en colère",
            "furieux",
            "furieuse",
            "fâché",
            "fâchée",
            "indigné",
            "indignée",
            "inacceptable",
            "ridicule",
        ],
        "intensity": 0.9,
    },
    "DISAPPOINTED": {
        "keywords": [
            "déçu",
            "déçue",
            "désappointé",
            "désappointée",
            "je m'attendais à mieux",
            "pas content",
            "insatisfait",
            "insatisfaite",
        ],
        "intensity": 0.7,
    },
    "WORRIED": {
        "keywords": [
            "inquiet",
            "inquiète",
            "préoccupé",
            "préoccupée",
            "anxieux",
            "anxieuse",
            "nerveux",
            "nerveuse",
            "craintif",
            "craintive",
        ],
        "intensity": 0.6,
    },
    "CONFUSED": {
        "keywords": [
            "confus",
            "confuse",
            "je ne comprends pas",
            "pas sûr",
            "perdu",
            "perdue",
            "ce n'est pas clair",
        ],
        "intensity": 0.5,
    },
    "GRATEFUL": {
        "keywords": [
            "merci",
            "reconnaissant",
            "reconnaissante",
            "j'apprécie",
            "très aimable",
            "excellente aide",
        ],
        "intensity": 0.6,
    },
    "SATISFIED": {
        "keywords": [
            "satisfait",
            "satisfaite",
            "content",
            "contente",
            "heureux",
            "heureuse",
            "ravi",
            "ravie",
            "parfait",
            "excellent",
            "fantastique",
        ],
        "intensity": 0.8,
    },
}

DAY_NAMES = {
    "lundi": "MON",
    "mardi": "TUE",
    "mercredi": "WED",
    "jeudi": "THU",
    "vendredi": "FRI",
    "samedi": "SAT",
    "dimanche": "SUN",
}

WORD_TO_NUM = {
    "un": 1,
    "une": 1,
    "deux": 2,
    "trois": 3,
    "quatre": 4,
    "cinq": 5,
    "six": 6,
    "sept": 7,
    "paire": 2,
    "couple": 2,
}

DAY_ORDER = ["LUN", "MAR", "MER", "JEU", "VEN", "SAM", "DIM"]

NER_ADDRESS_ABBREVIATIONS = {
    "Rue": "R.",
    "Avenue": "Av.",
    "Boulevard": "Bd.",
    "Place": "Pl.",
    "Chemin": "Ch.",
    "Allée": "All.",
}

# ── Transcript analyzer patterns ──

RESOLUTION_KEYWORDS = {
    "RESOLVED": {"résolu", "corrigé", "réglé", "approuvé", "remboursement"},
    "ESCALATED": {"escalader", "superviseur", "transférer"},
    "PENDING_REPLACEMENT": {"remplacer", "remplacement", "échange"},
}

BILLING_CAUSE_KEYWORDS = {
    "DUPLICATE_PROCESSING": {"doublon", "traité deux fois", "retraité"},
    "DOUBLE_BILLING": {"double facturation", "facturé deux fois"},
    "PRORATION_CONFUSION": {"prorata", "au prorata"},
    "SYSTEM_ERROR": {"erreur", "faute"},
    "MID_CYCLE_UPGRADE": {"mise à niveau", "upgrade"},
    "MID_CYCLE_DOWNGRADE": {"rétrogradation", "downgrade"},
    "BILLING_OVERLAP": {"chevauchement"},
}

ISSUE_TYPE_KEYWORDS = {
    "BILLING_DISPUTE": {"facture", "frais", "remboursement"},
    "CONNECTIVITY": {"internet", "connexion", "wifi"},
    "PERFORMANCE": {"lent", "vitesse", "débit"},
}

SEVERITY_KEYWORDS = {
    "HIGH": {
        "critique",
        "urgent",
        "urgence",
        "ne fonctionne plus du tout",
        "ne peux pas travailler",
    },
    "MEDIUM": {
        "frustré",
        "agaçant",
        "j'en ai besoin pour travailler",
        "important",
    },
}

ISSUE_CONFIRMATION_MAP = {
    "DUPLICATE_CHARGE_CONFIRMED": {
        "doublon",
        "traité deux fois",
        "double facturation",
        "deux frais",
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
    "envoyé",
    "traité",
    "terminé",
    "classé",
    "appliqué",
    "émis",
    "fait",
    "effectué",
}

ACTION_COMPLETION_PHRASES = {
    "je viens d'envoyer",
    "je viens de traiter",
    "déjà envoyé",
    "déjà traité",
}

ACTION_NOW_PATTERNS = [
    r"(j'ai|je viens de) (envoyer|traiter|classer)\b",
    r"je suis en train de (traiter|envoyer|classer) (ça|le|la)?\s*(maintenant)?\b",
]

POSITIVE_CUSTOMER_CONFIRMATIONS = {
    "parfait",
    "super",
    "merci",
    "compris",
    "reçu",
    "j'apprécie",
}

AGENT_CONFIRMATION_PHRASES = {
    "c'est tout bon",
    "vous êtes prêt",
    "c'est fait",
    "terminé",
}

EXPLICIT_ACTION_PHRASES = {
    "DOCUMENTATION_UPDATED": {
        "j'ai documenté",
        "j'ai ajouté des notes",
        "j'ai enregistré ceci",
        "ajouté au ticket",
        "j'ai mis à jour les notes du dossier",
    },
    "ACCOUNT_UPDATED": {
        "j'ai mis à jour votre compte",
        "votre compte a été mis à jour",
        "j'ai changé votre forfait",
        "j'ai modifié vos paramètres",
    },
}

TECHNICAL_ISSUE_MAP = {
    "OUTAGE": ["panne", "en panne", "hors ligne", "plusieurs clients"],
    "PACKET_LOSS": ["perte de paquets", "ligne dégradée"],
    "INTERMITTENT_CONNECTIVITY": ["coupe sans arrêt", "intermittent"],
}

TROUBLESHOOTING_ACTIONS = {
    "TROUBLESHOOTING_PERFORMED": {
        "j'ai lancé un test",
        "réinitialisé",
        "redémarré",
        "nettoyé",
        "effectué",
        "appliqué un correctif",
    },
    "DIAGNOSTIC_PERFORMED": {
        "vérifié",
        "examiné",
        "je vois",
        "consulté les journaux",
        "je constate",
        "consulté",
        "lancé des diagnostics",
        "test de ligne",
    },
}

# ── Multilingual / speaker detection ──

AGENT_SPEAKER_LABELS = ["agent", "conseiller", "conseillère"]
CUSTOMER_SPEAKER_LABELS = ["client", "cliente", "customer", "appelant"]

# ── Timeline defaults (French) ──

TIMELINE_KEYWORDS = {
    "demain": "TOMORROW",
    "aujourd'hui": "TODAY",
    "aujourd'hui": "TODAY",
}

TIMELINE_PATTERNS = [
    (r"(\d+)\s*à\s*(\d+)\s*jours?\s*ouvrables?", "{0}-{1}d"),
    (r"dans\s+(\d+)\s*heures?", "{0}h"),
    (r"dans\s+(\d+)\s*jours?", "{0}d"),
    (r"sous\s+(\d+)\s*heures?", "{0}h"),
    (r"sous\s+(\d+)\s*jours?", "{0}d"),
    (r"d'ici\s+(\d+)\s*jours?", "{0}d"),
]

# ── Disputed amount keywords ──

DISPUTED_AMOUNT_KEYWORDS = [
    "frais",
    "facture",
    "paiement",
    "montant",
    "relevé",
    "charge",
    "payment",
]

# ── Amount reason context ──

AMOUNT_REASON_CONTEXT = [
    ("doublon", "DUPLICATE_CHARGE"),
    ("duplicate", "DUPLICATE_CHARGE"),
    ("remboursement", "REFUND"),
    ("refund", "REFUND"),
    ("extra", "EXTRA_CHARGE"),
    ("réduction", "DISCOUNT"),
    ("discount", "DISCOUNT"),
    ("crédit", "CREDIT"),
    ("credit", "CREDIT"),
    ("frais", "FEE"),
    ("fee", "FEE"),
    ("facturation", "CHARGE"),
    ("charge", "CHARGE"),
    ("charged", "CHARGE"),
]

# ── Redacted field context ──

REDACTED_FIELD_CONTEXT = [
    ("email", "EMAIL_REDACTED"),
    ("e-mail", "EMAIL_REDACTED"),
    ("téléphone", "PHONE_REDACTED"),
    ("telephone", "PHONE_REDACTED"),
    ("phone", "PHONE_REDACTED"),
    ("numéro", "PHONE_REDACTED"),
    ("number", "PHONE_REDACTED"),
    ("adresse", "ADDRESS_REDACTED"),
    ("address", "ADDRESS_REDACTED"),
    ("nom", "NAME_REDACTED"),
    ("name", "NAME_REDACTED"),
]

# ── Call type detection ──

CALL_TYPE_SALES_KEYWORDS = [
    "mise à niveau",
    "tarif",
    "acheter",
    "intéressé par",
    "upgrade",
    "pricing",
]

# ── Name extraction patterns ──

NAME_INTRO_PATTERNS = [
    r"(?:je m'appelle|mon nom est|je suis)\s+([A-ZÀÂÇÉÈÊËÎÏÔÙÛÜ][a-zàâçéèêëîïôùûü]+)",
    r"(?:my name is|i'?m|this is)\s+([A-Z][a-z]+)",
]

NAME_THANKS_PATTERNS = [
    r"merci,\s+([A-ZÀÂÇÉÈÊËÎÏÔÙÛÜ][a-zàâçéèêëîïôùûü]+)",
    r"thank(?:s| you),\s+([A-Z][a-z]+)",
]

NAME_CHANGE_PATTERNS = [
    r"\b(?:changer|modifier|mettre à jour)\s+(?:mon\s+)?(?:nom\s+)?(?:de\s+)?\w+\s+en\s+\w+",
]

AGENT_NAME_PATTERNS = [
    r"(?:je m'appelle|mon nom est|je suis)\s+([A-ZÀÂÇÉÈÊËÎÏÔÙÛÜ][a-zàâçéèêëîïôùûü]+)",
    r"(?:my name is|this is)\s+([A-Z][a-z]+)",
]

# ── Delay context words ──

DELAY_CONTEXT_WORDS = [
    "attendre",
    "j'attends",
    "depuis",
    "il y a",
    "waiting",
    "been",
    "ago",
    "since",
]

# ── Extra commitment patterns ──

EXTRA_COMMITMENT_PATTERNS = {
    "CONFIRMATION_EMAIL": [
        "vous enverrai une confirmation",
        "email de confirmation",
        "vous recevrez un email",
        "confirmation par email",
        "send you a confirmation",
        "confirmation email",
    ],
    "FOLLOWUP": [
        "je ferai un suivi",
        "je vais faire le suivi",
        "personnellement je ferai le suivi",
        "i'll follow up",
        "follow up with you",
    ],
    "MONITORING": [
        "surveiller",
        "suivre",
        "monitoring",
        "keep an eye on",
    ],
}

# ── Promise timeline patterns ──

PROMISE_TIMELINE_PATTERNS = [
    (r"dans\s+(\d+)\s*heures?", "{0}h"),
    (r"dans\s+(\d+)\s*jours?", "{0}d"),
    (r"sous\s+(\d+)\s*heures?", "{0}h"),
    (r"pour\s+(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)", "{0}"),
    (r"avant\s+(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)", "{0}"),
    (r"within\s+(\d+)\s*hours?", "{0}h"),
    (r"within\s+(\d+)\s*days?", "{0}d"),
]

# ── Promise confidence strong indicators ──

PROMISE_CONFIDENCE_STRONG = [
    "je vais",
    "nous allons",
    "je vais",
    "définitivement",
    "certainement",
    "absolument",
    "will",
    "going to",
    "i'll",
]
