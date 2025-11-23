from transformers.tokenization_utils_base import PreTokenizedInput
from ...utils.vocabulary import BaseVocabulary


class FRVocabulary(BaseVocabulary):
    def __init__(self):
        super().__init__()

    @property
    def QUANTIFIER_WORDS(self) -> list[str]:
        return ["tous", "toutes", "tout", "chaque", "entier", "complet"]

    @property
    def DEMONSTRATIVES(self) -> list[str]:
        return ["ce", "cet", "cette", "ces"]

    @property
    def COMPOUND_PHRASES(self) -> dict[str, str]:
        return {
            "support client": "TICKET",
            "ticket de support": "TICKET",
            "message email": "EMAIL",
            "transcription de chat": "TRANSCRIPT",
            "appel téléphonique": "CALL",
            "code source": "CODE",
            "plan d'affaires": "PLAN",
            "description du produit": "DESCRIPTION",
        }

    @property
    def domain_candidates(self) -> dict[str, list[str]]:
        return {
            "support": ["problème", "question", "sentiment", "actions", "urgence", "priorité"],
            "code": ["bug", "erreur", "sécurité", "performance"],
            "document": ["noms", "dates", "montants", "adresses", "emails", "courriels", "téléphones"],
            "qa": ["vérification", "politique", "compétences relationnelles", "soft skills", "précision", "exactitude", "conformité", "compliance", "divulgations"],
        }

    @property
    def rank_triggers(self) -> set[str]:
        return {
            "classer", "ranger", "trier", "ordonner", "ordre",
            "ordonner par", "trier par", "classer par",
            "prioriser", "haut", "supérieur", "premier", "top",
            "bas", "inférieur", "dernier", "le plus haut", "le plus élevé", "maximum",
            "le plus bas", "minimum", "meilleur", "meilleurs", "meilleures", "pire", "pires"
        }

    @property
    def CONCEPT_INDICATORS(self) -> list[str]:
        """Optional - can have sensible default"""
        return ["concept de", "idée de", "notion de", "principe de"]

    @property
    def MEETING_WORDS(self) -> list[str]:
        """Optional - can have empty default"""
        return ["réunion", "conférence", "rencontre", "séance"]

    @property
    def PROPOSAL_WORDS(self) -> list[str]:
        """Optional - can have empty default"""
        return ["proposition", "propositon", "offre", "suggestion", "idée"]

    @property
    def ARTICLES(self) -> list[str]:
        """Optional - can have empty default"""
        return ["le", "la", "les", "l'", "un", "une", "des"]

    @property
    def REQ_TOKENS(self) -> dict[str, list[str]]:
        return {
            "ANALYZE": [
                "analyser",
                "réviser",
                "examiner",
                "évaluer",
                "inspecter",
                "vérifier",
                "auditer",
                "enquêter",
                "étudier",
            ],
            "MATCH": [
                "faire correspondre",
                "comparer",
                "aligner",
                "mapper",
                "corréler",
                "apparier",
                "croiser",
                "rapprocher",
            ],
            # Information extraction
            "EXTRACT": [
                "extraire",
                "retirer",
                "identifier",
                "trouver",
                "localiser",
                "obtenir",
                "récupérer",
                "retourner",
                "inclure",
                "sélectionner",
                "chercher",
            ],
            "SELECT": [
                "sélectionner",
                "choisir",
                "filtrer",
                "identifier les correspondances",
                "opter",
                "élire",
            ],
            # Content generation
        "GENERATE": [
            "générer",
            "créer",
            "écrire",
            "rédiger",
            "composer",
            "produire",
            "construire",
            "développer",
            "concevoir",
            "élaborer",
            "faire",
            "nommer",
            "suggérer",
            "formuler",
            "former",
            "proposer",
            "transcrire",
        ],
        # Summaries and condensing
        "SUMMARIZE": [
            "résumer",
            "condenser",
            "synthétiser",
            "récapituler",
            "abréger",
        ],
        # Content transformation
        "TRANSFORM": [
            "convertir",
            "transformer",
            "changer",
            "réécrire",
            "traduire",
            "compléter",
            "modifier",
            "adapter",
            "ajuster",
            "reformuler",
            "altérer",
            "éditer",
            "ajouter",
            "paraphraser",
            "remplir",
            "supprimer",
            "enlever",
            "remplacer",
            "inverser",
        ],
        # Explanations and descriptions
        "EXPLAIN": [
            "expliquer",
            "décrire",
            "clarifier",
            "élaborer",
            "détailler",
            "exposer",
            "illustrer",
            "exprimer",
            "raconter",
            "discuter",
            "définir",
            "parler de",
            "dis-moi",
            "parle-moi de",
        ],
        # Comparisons
        "COMPARE": [
            "comparer",
            "contraster",
            "versus",
            "vs",
            "différence entre",
            "différencier",
            "distinguer",
        ],
        # Classification and organization
        "CLASSIFY": [
            "classifier",
            "catégoriser",
            "trier",
            "regrouper",
            "étiqueter",
            "organiser",
            "ranger",
            "segmenter",
        ],
        # Debugging and fixing
        "DEBUG": [
            "déboguer",
            "dépanner",
            "diagnostiquer",
            "corriger un bug",
            "trouver un bug",
            "traquer",
            "identifier le problème",
        ],
        # Optimization and improvement
        "OPTIMIZE": [
            "optimiser",
            "améliorer",
            "perfectionner",
            "refactoriser",
            "accélérer",
            "simplifier",
            "maximiser",
            "minimiser",
            "réduire",
            "augmenter",
        ],
        # Validation and verification
        "VALIDATE": [
            "valider",
            "vérifier",
            "contrôler",
            "confirmer",
            "tester",
            "assurer",
            "certifier",
            "authentifier",
        ],
        # Search operations
        "SEARCH": [
            "chercher",
            "rechercher",
            "trouver",
            "localiser",
            "consulter",
            "découvrir",
        ],
        # Ranking and prioritization
        "RANK": [
            "prioriser",
            "ordonner",
            "classer par",
            "noter",
            "évaluer",
            "hiérarchiser",
        ],
        # Predictions and forecasting
        "PREDICT": [
            "prédire",
            "prévoir",
            "estimer",
            "projeter",
            "anticiper",
            "extrapoler",
            "pronostiquer",
        ],
        # Formatting
        "FORMAT": [
            "formater",
            "structurer",
            "organiser",
            "disposer",
            "mettre en forme",
        ],
        # Detection
        "DETECT": [
            "détecter",
            "repérer",
            "découvrir",
            "percevoir",
            "reconnaître",
            "remarquer",
            "identifier",
        ],
        # Mathematical operations
        "CALCULATE": [
            "calculer",
            "computer",
            "déterminer",
            "quantifier",
            "mesurer",
            "compter",
            "additionner",
            "totaliser",
        ],
        # Aggregation
        "AGGREGATE": [
            "agréger",
            "regrouper",
            "combiner",
            "consolider",
            "rassembler",
            "fusionner",
            "compiler",
            "collecter",
            "réunir",
        ],
        # Decision-making
        "DETERMINE": [
            "déterminer",
            "décider",
            "évaluer",
            "conclure",
            "établir",
            "choisir",
            "définir",
        ],
        # Routing and assignment
        "ROUTE": [
            "router",
            "attribuer",
            "diriger",
            "transférer",
            "envoyer à",
            "déléguer",
            "affecter",
        ],
        # Action execution
        "EXECUTE": [
            "utiliser",
            "appliquer",
            "implémenter",
            "exécuter",
            "réaliser",
            "employer",
            "mettre en œuvre",
        ],
        # List generation
        "LIST": [
            "lister",
            "énumérer",
            "détailler",
            "dresser la liste",
            "répertorier",
        ],
    }

    @property
    def NOISE_VERBS(self) -> set[str]:
        return {
        "être",
        "avoir",
        "faire",
        "pouvoir",
        "devoir",
        "vouloir",
        "aller",
        "venir",
        "falloir",
        "rester",
        "vivre",
        "habiter",
        "continuer",
        "demeurer",
        "suivre",
        "baser",
        "avoir besoin",
        "commencer",
        "devenir",
        "sembler",
        "paraître",
        "apparaître",
        "montrer",
        "voir",
        "savoir",
        "penser",
        "sentir",
        "dire",
        "parler",
        "appeler",
    }

    @property
    def CONTEXT_FILTERS(self) -> dict[str, list[str]]:
        return {
            "donner": ["donné", "donnant", "donne-moi", "donnez-moi"],
            "suivre": ["suivant", "ci-dessous", "comme suit"],
            "baser": ["basé sur", "en se basant sur"],
            "utiliser": ["utile", "utilisé pour", "utilisable"],
            "continuer": ["continu", "continuer à", "continuer de"],
            "demeurer": ["demeur", "demeurer à", "demeurer de"],
            "suivre": ["suivant", "ci-dessous", "comme suit"],
            "baser": ["basé sur", "en se basant sur"],
            "avoir besoin": ["besoin", "nécessité", "nécessité de"],
            "commencer": ["commenc", "commencer à", "commencer de"],
            "devenir": ["deven", "devenir à", "devenir de"],
            "sembler": ["semble", "sembler à", "sembler de"],
            "paraître": ["paraît", "paraître à", "paraître de"],
            "apparaître": ["apparaît", "apparaître à", "apparaître de"],
            "montrer": ["montre", "montrer à", "montrer de"],
            "voir": ["voit", "voir à", "voir de"],
            "savoir": ["sait", "savoir à", "savoir de"],
            "penser": ["pense", "penser à", "penser de"],
            "sentir": ["sent", "sentir à", "sentir de"],
            "dire": ["dit", "dire à", "dire de"],
            "parler": ["parle", "parler à", "parler de"],
            "appeler": ["appelle", "appeler à", "appeler de"],
        }

    @property
    def TARGET_TOKENS(self) -> dict[str, list[str]]:
        return {
            "CODE": [
                "code",
                "script",
                "programme",
                "fonction",
                "méthode",
                "classe",
                "extrait",
            ],
            "DATA": [
                "données",
                "dataset",
            "jeu de données",
            "base de données",
            "feuille de calcul",
            "tableau",
            "csv",
        ],
        "QUERY": [
            "requête",
            "query",
            "sql",
            "requête sql",
            "requête de base de données",
        ],
        "ENDPOINT": [
            "endpoint",
            "api",
            "point d'accès",
            "service rest",
        ],
        "COMPONENT": [
            "composant",
            "module",
            "paquet",
            "bibliothèque",
            "librairie",
        ],
        "SYSTEM": [
            "système",
            "application",
            "appli",
            "logiciel",
            "plateforme",
        ],
        "TEST": [
            "test",
            "test unitaire",
            "cas de test",
            "suite de tests",
        ],
        "LOG": [
            "log",
            "logs",
            "fichier de log",
            "journal",
            "historique",
        ],
        "RECORD": [
            "enregistrement",
            "entrée",
            "ligne",
            "élément",
        ],
        "STRATEGY": [
            "stratégie",
            "approche",
            "plan",
            "méthodologie",
        ],
        "NBA_CATALOG": [
            "nba",
            "nbas",
            "prochaine meilleure action",
            "actions prédéfinies",
            "actions possibles",
            "actions disponibles",
        ],
        "DOCUMENT": [
            "document",
            "doc",
            "fichier",
            "rapport",
            "article",
        ],
        "EMAIL": [
            "email",
            "courriel",
            "message",
            "correspondance",
        ],
        "REPORT": [
            "rapport",
            "analyse",
            "conclusions",
            "compte rendu",
        ],
        "TICKET": [
            "ticket",
            "incident",
            "cas",
            "demande",
        ],
        "TRANSCRIPT": [
            "transcription",
            "conversation",
            "dialogue",
            "historique de chat",
        ],
        "FEEDBACK": [
            "feedback",
            "retour",
            "commentaire",
            "évaluation",
            "critique",
            "avis",
        ],
        "COMMENT": [
            "commentaire",
            "remarque",
            "note",
            "observation",
        ],
        "CUSTOMER_INTENT": [
            "intention du client",
            "besoin du client",
            "demande du client",
            "objectif du client",
            "problème du client",
        ],
        "COMPLAINT": [
            "plainte",
            "réclamation",
            "problème",
            "grief",
        ],
        "REQUEST": [
            "demande",
            "requête",
            "sollicitation",
        ],
        "INQUIRY": [
            "demande de renseignement",
            "question",
            "interrogation",
        ],
        "INTERACTION": [
            "interaction",
            "échange",
            "contact",
        ],
        "CALL": [
            "appel",
            "appel téléphonique",
        ],
        "DESCRIPTION": [
            "description",
            "détail",
        ],
        "SUMMARY": [
            "résumé",
            "sommaire",
            "synthèse",
        ],
        "PLAN": [
            "plan",
            "planification",
            "projet",
        ],
        "POST": [
            "post",
            "publication",
            "article",
        ],
        "PRESS_RELEASE": [
            "communiqué de presse",
            "annonce",
        ],
        "INTRODUCTION": [
            "introduction",
            "présentation",
        ],
        "CAPTION": [
            "légende",
            "sous-titre",
        ],
        "QUESTIONS": [
            "questions",
            "questionnaire",
            "faq",
        ],
        "RESPONSE": [
            "réponse",
            "réplique",
            "modèle de réponse",
        ],
        "LOGS": [
            "logs",
            "journaux",
            "historiques",
        ],
        "CORRELATION": [
            "corrélation",
            "corrélations",
            "relation",
            "relations",
        ],
        "TRADEOFF": [
            "compromis",
            "arbitrage",
        ],
        "PARADIGM": [
            "paradigme",
            "paradigmes",
            "modèle",
        ],
        "PAIN_POINTS": [
            "points de douleur",
            "problèmes",
            "difficultés",
            "irritants",
        ],
        "PATTERN": [
            "motif",
            "modèle",
            "tendance",
            "tendances",
            "pattern",
        ],
        "CHURN": [
            "churn",
            "attrition",
            "désabonnement",
            "résiliation",
        ],
        "FEATURES": [
            "fonctionnalités",
            "caractéristiques",
            "features",
        ],
        "METRICS": [
            "revenus",
            "métriques",
            "statistiques",
            "chiffres",
            "indicateurs",
        ],
        "REGIONS": [
            "régions",
            "zones",
            "emplacements",
            "territoires",
        ],
        "ITEMS": [
            "éléments",
            "choses",
            "liste",
            "options",
            "choix",
        ],
        "CONCEPT": [
            "concept",
            "idée",
            "notion",
            "principe",
            "théorie",
        ],
        "PROCEDURE": [
            "procédure",
            "processus",
            "étapes",
            "méthode",
            "technique",
        ],
        "FACT": [
            "fait",
            "faits",
            "information",
            "informations",
            "détails",
        ],
        "ANSWER": [
            "réponse",
            "solution",
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
            "JSON": ["json", "format json"],
            "MARKDOWN": ["markdown", "md"],
            "TABLE": ["tableau", "tabulaire"],
            "LIST": ["liste", "puces", "points"],
            "PLAIN": ["texte brut", "texte simple"],
            "CSV": ["csv", "séparé par des virgules"],
        }

    @property
    def IMPERATIVE_PATTERNS(self) -> list[tuple[list[str], str, str]]:
        return [
            (["liste", "lister", "énumère", "énumérer"], "LIST", "ITEMS"),
            (["nomme", "nommer", "identifie", "identifier"], "GENERATE", "ITEMS"),
            (["donne", "donner", "fournis", "fournir", "suggère", "suggérer"], "GENERATE", "ITEMS"),
            (
                [
                    "dis",
                    "dire",
                    "explique",
                    "expliquer",
                    "décris",
                    "décrire",
                    "clarifie",
                    "clarifier",
                    "illustre",
                    "illustrer",
                ],
                "EXPLAIN",
                "CONCEPT",
            ),
        ]

    @property
    def QUESTION_WORDS(self) -> list[str]:
        return [
            "que",
            "qu'est-ce que",
            "qui",
            "où",
            "quand",
            "pourquoi",
            "comment",
            "quel",
            "quelle",
            "quels",
            "quelles",
            "lequel",
            "laquelle",
        ]
