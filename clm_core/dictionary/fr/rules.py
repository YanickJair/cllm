from clm_core.utils.parser_rules import BaseRules


class FRRules(BaseRules):
    """French language pattern matching rules"""

    def __init__(self):
        super().__init__()

    @property
    def COMPARISON_MAP(self) -> dict[str, str]:
        return {
            r"\bdifférences?\b": "DIFFERENCES",
            r"\bdistinguer\b": "DIFFERENCES",
            r"\bcontraster\b": "DIFFERENCES",
            r"\bsimilarités?\b": "SIMILARITIES",
            r"\bressemblances?\b": "SIMILARITIES",
            r"\bcommun\b": "SIMILARITIES",
            r"\bavantages\s*(et|&)?\s*inconvénients\b": "PROS_CONS",
            r"\bpour\s*(et|&)?\s*contre\b": "PROS_CONS",
            r"\bpros\s*(et|&)?\s*cons\b": "PROS_CONS",
            r"\bcompromis\b": "TRADEOFFS",
            r"\btrade-?offs?\b": "TRADEOFFS",
        }

    @property
    def DOMAIN_REGEX(self) -> dict[str, str]:
        return {
            "SUPPORT": r"\b(appel|ticket|dossier|client|support|réclamation|helpdesk)\b",
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

    @property
    def DURATION_PATTERNS(self) -> list[str]:
        return [
            r"(\d+)[\s-]*(?:minute|min)s?",
            r"(\d+)[\s-]*(?:heure|hr)s?",
        ]

    @property
    def STANDARD_FIELD_KEYWORDS(self) -> dict[str, str]:
        return {
            r"\bproblème(s)?\b": "ISSUE",
            r"\bquestion(s)?\b": "PROBLEM",
            r"\berreur(s)?\b": "ERROR",
            r"\bbug(s)?\b": "BUG",
            r"\bnom(s)?\b": "NAMES",
            r"\bdate(s)?\b": "DATES",
            r"\bmontant(s)?\b": "AMOUNTS",
            r"\bsomme(s)?\b": "AMOUNTS",
            r"\bemail(s)?\b": "EMAILS",
            r"\bcourriel(s)?\b": "EMAILS",
            r"\btéléphone(s)?\b": "PHONES",
            r"\badresse(s)?\b": "ADDRESSES",
            r"\bsentiment\b": "SENTIMENT",
            r"\burgence\b": "URGENCY",
            r"\bpriorité\b": "PRIORITY",
            r"\bcatégorie\b": "CATEGORY",
            r"\baction(s)?\b": "ACTIONS",
            r"\bprochaines étapes\b": "NEXT_STEPS",
            r"\bétapes suivantes\b": "NEXT_STEPS",
            r"\béléments d'action\b": "ACTIONS",
            r"\bdate(s)? limite\b": "DEADLINES",
            r"\bdélai(s)?\b": "DEADLINES",
            r"\béchéance(s)?\b": "DEADLINES",
            r"\bsécurité\b": "SECURITY",
            r"\bperformance\b": "PERFORMANCE",
        }

    @property
    def AUDIENCE_MAP(self) -> dict[str, str]:
        return {
            r"\bnon[- ]?technique\b": "NON_TECHNICAL",
            r"\b(débutant|débutants|enfant|enfants|simple|général)\b": "BEGINNER",
            r"\b(expert|avancé|spécialiste|professionnels)\b": "EXPERT",
            r"\btechnique\b": "TECHNICAL",
            r"\b(affaires|exécutifs|direction|management)\b": "BUSINESS",
        }

    @property
    def LENGTH_MAP(self) -> dict[str, str]:
        return {
            r"\b(bref|brève|court|concis|rapide|résumé)\b": "BRIEF",
            r"\b(détaillé|complet|exhaustif|approfondi|étendu)\b": "DETAILED",
        }

    @property
    def STYLE_MAP(self) -> dict[str, str]:
        return {
            r"\b(simple|facile|clair)\b": "SIMPLE",
            r"\b(formel|professionnel|d'affaires)\b": "FORMAL",
        }

    @property
    def TONE_MAP(self) -> dict[str, str]:
        return {
            r"\bprofessionnel\b": "PROFESSIONAL",
            r"\bformel\b": "PROFESSIONAL",
            r"\bd'affaires\b": "PROFESSIONAL",
            r"\bdécontracté\b": "CASUAL",
            r"\binformel\b": "CASUAL",
            r"\bamical\b": "CASUAL",
            r"\bempathique\b": "EMPATHETIC",
            r"\bcompatissant\b": "EMPATHETIC",
            r"\bcompréhensif\b": "EMPATHETIC",
        }

    @property
    def NUMBER_WORDS(self) -> dict[str, int]:
        return {
            "un": 1,
            "une": 1,
            "deux": 2,
            "paire": 2,
            "couple": 2,
            "trois": 3,
            "quatre": 4,
            "cinq": 5,
            "six": 6,
            "sept": 7,
            "huit": 8,
            "neuf": 9,
            "dix": 10,
            "peu": -1,
            "quelques": -1,
            "plusieurs": -2,
            "beaucoup": -3,
        }

    @property
    def SPEC_PATTERNS(self) -> list[tuple[str, str]]:
        return [
            (r"(\d+)\s*lignes?\b", "LINES"),
            (r"(\d+)\s*mots?\b", "WORDS"),
            (r"(\d+)\s*(?:éléments?|choses?|items?)\b", "ITEMS"),
            (r"(\d+)\s*(?:conseils?|suggestions?)\b", "COUNT"),
            (r"(\d+)\s*(?:exemples?|instances?)\b", "COUNT"),
            (r"(\d+)\s*(?:étapes?|phases?)\b", "STEPS"),
            (r"(\d+)\s*(?:façons?|méthodes?|manières?)\b", "COUNT"),
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
            (r"\bgo\s+(?:code|programme|script)", "GO"),
            (r"\brust\b", "RUST"),
            (r"\btypescript\b", "TYPESCRIPT"),
            (r"\b\.ts\b", "TYPESCRIPT"),
        ]

    @property
    def EXTRACTION_INDICATORS(self) -> list[str]:
        return [
            r"\bextraire\b",
            r"\bidentifier\b",
            r"\btrouver\b",
            r"\bobtenir\b",
            r"\bretirer\b",
            r"\bsouligner\b",
            r"\bmontrer\b",
            r"\bretourner\b",
            r"\brécupérer\b",
            r"\bcomparer\b",
            r"\bcontraster\b",
            r"\blister\b",
            r"\bquels sont\b",
            r"\bqu'est-ce que\b",
        ]

    @property
    def QA_CRITERIA(self) -> dict[str, str]:
        return {
            r"\b(vérification|vérifier|vérifié)\b": "VERIFICATION",
            r"\b(politique|politiques|respect de la politique)\b": "POLICY",
            r"\b(compétences relationnelles|empathie|clarté|responsabilité)\b": "SOFT_SKILLS",
            r"\b(précision|précis|exactitude)\b": "ACCURACY",
            r"\b(conformité|conforme|violations?)\b": "COMPLIANCE",
            r"\b(sentiment|émotion|humeur)\b": "SENTIMENT",
            r"\b(divulgations?|divulgations obligatoires?)\b": "DISCLOSURES",
        }

    @property
    def QA_INDICATORS(self) -> list[str]:
        return [
            r"\bscore\b",
            r"\bnote\b",
            r"\bqa\b",
            r"\bassurance qualité\b",
            r"\bconformité\b",
            r"\baudit\b",
        ]

    @property
    def QUESTION_PATTERNS(self) -> list[tuple[str, int]]:
        return [
            (r"qu(?:'est-ce que|el|elle) (?:est|sont) (?:le |la |les |un |une )?([\w\s]+?)(?:\?|$)", 1),
            (r"comment (?:fonctionne|fonctionnent|peut|peuvent) ([\w\s]+?)(?:\?|$)", 1),
            (r"pourquoi (?:est|sont|est-ce que) ([\w\s]+?)(?:\?|$)", 1),
            (r"où (?:est|sont|se trouve) ([\w\s]+?)(?:\?|$)", 1),
            (r"quand (?:est|était|sera) ([\w\s]+?)(?:\?|$)", 1),
            (r"qui (?:est|sont|était|étaient) (?:le |la )?([\w\s]+?)(?:\?|$)", 1),
        ]

    @property
    def EXPLAIN_PATTERNS(self) -> list[tuple[str, int]]:
        return [
            (r"(?:explique|décris) comment ([\w\s]+?)(?: fonctionne| marche|$)", 1),
            (
                r"(?:explique|décris|clarifie|détaille) (?:le |la |les |un |une )?([\w\s]+?)(?:\s+en|\s+avec|\s+pour|\.|\?|$)",
                1,
            ),
            (r"(?:dis-moi|parle-moi de) ([\w\s]+?)(?:\s+en|\s+avec|\.|\?|$)", 1),
        ]

    @property
    def CONCEPT_PATTERN(self) -> tuple[str, int]:
        return (
            r"(?:concept|idée|notion|principe|théorie) de ([\w\s]+?)(?:\s+en|\.|\?|$)",
            1,
        )

    @property
    def PROCEDURE_PATTERN(self) -> tuple[str, int]:
        return (r"comment (?:puis-je|peut-on|faire pour) ([\w\s]+?)(?:\s+en|\s+avec|\.|\?|$)", 1)

    @property
    def CLEANUP_TAIL(self) -> str:
        return r"\s+(de|en|pour|avec|sur|depuis|à|au|par|détail|détails|technique|spécifique)$"

    @property
    def SUBJECT_PATTERNS(self) -> list[tuple[str, str]]:
        return [
            (r"\bverbe[s]?\b", "VERB"),
            (r"\bnom[s]?\b", "NOUN"),
            (r"\badjectif[s]?\b", "ADJECTIVE"),
            (r"\badverbe[s]?\b", "ADVERB"),
            (r"\bpronom[s]?\b", "PRONOUN"),
            (r"\bpréposition[s]?\b", "PREPOSITION"),
            (r"\bconjonction[s]?\b", "CONJUNCTION"),
            (r"\bconseil[s]?\b", "TIP"),
            (r"\bsuggestion[s]?\b", "TIP"),
            (r"\bméthode[s]?\b", "METHOD"),
            (r"\btechnique[s]?\b", "TECHNIQUE"),
            (r"\bstratégie[s]?\b", "STRATEGY"),
            (r"\bapproche[s]?\b", "APPROACH"),
            (r"\bpratique[s]?\b", "PRACTICE"),
            (r"\balgorithme[s]?\b", "ALGORITHM"),
            (r"\bfonction[s]?\b", "FUNCTION"),
            (r"\bformule[s]?\b", "FORMULA"),
            (r"\béquation[s]?\b", "EQUATION"),
            (r"\bthéorème[s]?\b", "THEOREM"),
            (r"\bpreuve[s]?\b", "PROOF"),
            (r"\bexemple[s]?\b", "EXAMPLE"),
            (r"\bidée[s]?\b", "IDEA"),
            (r"\bfaçon[s]?\b", "METHOD"),
            (r"\bmanière[s]?\b", "METHOD"),
            (r"\bétape[s]?\b", "STEP"),
            (r"\bfacteur[s]?\b", "FACTOR"),
            (r"\braison[s]?\b", "REASON"),
            (r"\bmotif[s]?\b", "REASON"),
            (r"\bavantage[s]?\b", "BENEFIT"),
            (r"\binconvénient[s]?\b", "DISADVANTAGE"),
            (r"\bcaractéristique[s]?\b", "FEATURE"),
            (r"\bmétrique[s]?\b", "METRIC"),
            (r"\bindicateur[s]?\b", "INDICATOR"),
            (r"\bperspective[s]?\b", "INSIGHT"),
            (r"\bconstat[s]?\b", "FINDING"),
            (r"\bdécouverte[s]?\b", "FINDING"),
        ]

    @property
    def TYPE_MAP(self) -> dict[str, str]:
        return {
            "appel": "CALL",
            "appel téléphonique": "CALL",
            "réunion": "MEETING",
            "rencontre": "MEETING",
            "chat": "CHAT",
            "conversation": "CONVERSATION",
            "rapport": "REPORT",
            "article": "ARTICLE",
        }

    @property
    def CONTEXT_MAP(self) -> dict[str, str]:
        return {
            "client": "CUSTOMER",
            "support": "SUPPORT",
            "ventes": "SALES",
            "technique": "TECHNICAL",
        }

    @property
    def ISSUE_PATTERNS(self) -> list[str]:
        return [
            r"à propos de\s+([\w\s]+?)(?:\s+et|$)",
            r"concernant\s+([\w\s]+?)(?:\s+et|$)",
            r"au sujet de\s+([\w\s]+?)(?:\s+et|$)",
            r"relatif à\s+([\w\s]+?)(?:\s+et|$)",
        ]
