from src.utils.parser_rules import BaseRules


class ENRules(BaseRules):
    """English language pattern matching rules"""

    def __init__(self):
        super().__init__()

    @property
    def COMPARISON_MAP(self) -> dict[str, str]:
        return {
            r"\bdifferences?\b": "DIFFERENCES",
            r"\bdistinguish\b": "DIFFERENCES",
            r"\bcontrast\b": "DIFFERENCES",
            r"\bsimilarities?\b": "SIMILARITIES",
            r"\bcommon\b": "SIMILARITIES",
            r"\bpros\s*(and|&)?\s*cons\b": "PROS_CONS",
            r"\badvantages\s*(and|&)?\s*disadvantages\b": "PROS_CONS",
            r"\bbenefits\s*(and|&)?\s*drawbacks\b": "PROS_CONS",
            r"\btrade-?offs?\b": "TRADEOFFS",
        }

    @property
    def DOMAIN_REGEX(self) -> dict[str, str]:
        return {
            "SUPPORT": r"\b(call|ticket|csr|customer|support|helpdesk)\b",
            "TECHNICAL": r"\b(error|bug|crash|stacktrace|api|debug|server|exception)\b",
            "DOCUMENT": r"\b(document|article|manual|writeup|transcript)\b",
            "BUSINESS": r"\b(report|executive|analysis|kpi|dashboard)\b",
            "LEGAL": r"\b(contract|policy|compliance|clause|gdpr)\b",
            "FINANCE": r"\b(invoice|billing|payment|refund|transaction)\b",
            "SECURITY": r"\b(breach|threat|risk|malware|audit)\b",
            "MEDICAL": r"\b(patient|clinical|diagnosis|treatment)\b",
            "SALES": r"\b(lead|crm|opportunity|prospect)\b",
            "EDUCATION": r"\b(lesson|teacher|student|curriculum)\b",
        }

    @property
    def DURATION_PATTERNS(self) -> list[str]:
        return [
            r"(\d+)[\s-]*(?:minute|min)s?",
            r"(\d+)[\s-]*(?:hour|hr)s?",
        ]

    @property
    def STANDARD_FIELD_KEYWORDS(self) -> dict[str, str]:
        return {
            r"\bissue(s)?\b": "ISSUE",
            r"\bproblem(s)?\b": "PROBLEM",
            r"\berror(s)?\b": "ERROR",
            r"\bbug(s)?\b": "BUG",
            r"\bname(s)?\b": "NAMES",
            r"\bdate(s)?\b": "DATES",
            r"\bamount(s)?\b": "AMOUNTS",
            r"\bemail(s)?\b": "EMAILS",
            r"\bphone(s)?\b": "PHONES",
            r"\baddress(es)?\b": "ADDRESSES",
            r"\bsentiment\b": "SENTIMENT",
            r"\burgen(cy)?\b": "URGENCY",
            r"\bpriority\b": "PRIORITY",
            r"\bcategory\b": "CATEGORY",
            r"\baction(s)?\b": "ACTIONS",
            r"\bnext steps\b": "NEXT_STEPS",
            r"\baction items\b": "ACTIONS",
            r"\bdeadline(s)?\b": "DEADLINES",
            r"\bsecurity\b": "SECURITY",
            r"\bperformance\b": "PERFORMANCE",
        }

    @property
    def AUDIENCE_MAP(self) -> dict[str, str]:
        return {
            r"\bnon[- ]?technical\b": "NON_TECHNICAL",
            r"\b(beginner|beginners|child|kid|5-?year-?old|10-?year-?old|simple|layman|general audience)\b": "BEGINNER",
            r"\b(expert|advanced|specialist|professionals)\b": "EXPERT",
            r"\btechnical\b": "TECHNICAL",
            r"\b(business|executives|management)\b": "BUSINESS",
        }

    @property
    def LENGTH_MAP(self) -> dict[str, str]:
        return {
            r"\b(brief|short|concise|quick|summary)\b": "BRIEF",
            r"\b(detailed|comprehensive|thorough|in-?depth|complete)\b": "DETAILED",
        }

    @property
    def STYLE_MAP(self) -> dict[str, str]:
        return {
            r"\b(simple|easy|straightforward)\b": "SIMPLE",
            r"\b(formal|business[- ]?like|professional)\b": "FORMAL",
        }

    @property
    def TONE_MAP(self) -> dict[str, str]:
        return {
            r"\bprofessional\b": "PROFESSIONAL",
            r"\bformal\b": "PROFESSIONAL",
            r"\bbusiness-?like\b": "PROFESSIONAL",
            r"\bcasual\b": "CASUAL",
            r"\binformal\b": "CASUAL",
            r"\bfriendly\b": "CASUAL",
            r"\bempathetic\b": "EMPATHETIC",
            r"\bcompassionate\b": "EMPATHETIC",
            r"\bunderstanding\b": "EMPATHETIC",
        }

    @property
    def NUMBER_WORDS(self) -> dict[str, int]:
        return {
            "one": 1,
            "a": 1,
            "an": 1,
            "single": 1,
            "two": 2,
            "couple": 2,
            "pair": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
            "few": -1,
            "several": -2,
            "many": -3,
        }

    @property
    def SPEC_PATTERNS(self) -> list[tuple[str, str]]:
        return [
            (r"(\d+)\s*lines?\b", "LINES"),
            (r"(\d+)\s*words?\b", "WORDS"),
            (r"(\d+)\s*(?:items?|things?|elements?)\b", "ITEMS"),
            (r"(\d+)\s*(?:tips?|suggestions?)\b", "COUNT"),
            (r"(\d+)\s*(?:examples?|instances?)\b", "COUNT"),
            (r"(\d+)\s*(?:steps?|stages?)\b", "STEPS"),
            (r"(\d+)\s*(?:ways?|methods?)\b", "COUNT"),
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
            (r"\bgo\s+(?:code|lang|program|script)", "GO"),
            (r"\brust\b", "RUST"),
            (r"\btypescript\b", "TYPESCRIPT"),
            (r"\b\.ts\b", "TYPESCRIPT"),
        ]

    @property
    def EXTRACTION_INDICATORS(self) -> list[str]:
        return [
            r"\bextract\b",
            r"\bidentify\b",
            r"\bfind\b",
            r"\bget\b",
            r"\bpull out\b",
            r"\bhighlight\b",
            r"\bshow\b",
            r"\breturn\b",
            r"\bretrieve\b",
            r"\bcompare\b",
            r"\bcontrast\b",
            r"\blist\b",
            r"\bwhat are\b",
        ]

    @property
    def QA_CRITERIA(self) -> dict[str, str]:
        return {
            r"\b(verification|verify|verified)\b": "VERIFICATION",
            r"\b(policy|policies|policy adherence)\b": "POLICY",
            r"\b(soft[- ]?skills?|empathy|clarity|ownership)\b": "SOFT_SKILLS",
            r"\b(accuracy|accurate|process accuracy)\b": "ACCURACY",
            r"\b(compliance|compliant|violations?)\b": "COMPLIANCE",
            r"\b(sentiment|emotion|feeling|mood)\b": "SENTIMENT",
            r"\b(disclosures?|mandatory disclosures?)\b": "DISCLOSURES",
        }

    @property
    def QA_INDICATORS(self) -> list[str]:
        return [
            r"\bscore\b",
            r"\bqa\b",
            r"\bquality assurance\b",
            r"\bcompliance\b",
            r"\baudit\b",
        ]

    @property
    def QUESTION_PATTERNS(self) -> list[tuple[str, int]]:
        return [
            (r"what (?:is|are|\'s) (?:the |an? )?([\w\s]+?)(?:\?|$)", 1),
            (
                r"how (?:does|do|can|is|are) ([\w\s]+?)(?: work| function| operate|\?|$)",
                1,
            ),
            (r"why (?:is|are|does|do) ([\w\s]+?)(?:\?|$)", 1),
            (r"where (?:is|are|can) ([\w\s]+?)(?:\?|$)", 1),
            (r"when (?:is|are|was|were|did) ([\w\s]+?)(?:\?|$)", 1),
            (r"who (?:is|are|was|were) (?:the )?([\w\s]+?)(?:\?|$)", 1),
        ]

    @property
    def EXPLAIN_PATTERNS(self) -> list[tuple[str, int]]:
        return [
            (
                r"(?:explain|describe) how ([\w\s]+?)(?: works?| functions?| operates?|$)",
                1,
            ),
            (
                r"(?:explain|describe|clarify|detail) (?:the |an? )?([\w\s]+?)(?:\s+in|\s+with|\s+for|\.|\?|$)",
                1,
            ),
            (r"tell me about ([\w\s]+?)(?:\s+in|\s+with|\.|\?|$)", 1),
        ]

    @property
    def CONCEPT_PATTERN(self) -> tuple[str, int]:
        return (
            r"(?:concept|idea|notion|principle|theory) of ([\w\s]+?)(?:\s+in|\.|\?|$)",
            1,
        )

    @property
    def PROCEDURE_PATTERN(self) -> tuple[str, int]:
        return (r"how (?:to|can I|do I) ([\w\s]+?)(?:\s+in|\s+with|\.|\?|$)", 1)

    @property
    def CLEANUP_TAIL(self) -> str:
        return r"\s+(of|in|for|with|about|from|to|at|on|by|detail|details|technical|specific)$"

    @property
    def SUBJECT_PATTERNS(self) -> list[tuple[str, str]]:
        return [
            (r"\bverb[s]?\b", "VERB"),
            (r"\bnoun[s]?\b", "NOUN"),
            (r"\badjective[s]?\b", "ADJECTIVE"),
            (r"\badverb[s]?\b", "ADVERB"),
            (r"\bpronoun[s]?\b", "PRONOUN"),
            (r"\bpreposition[s]?\b", "PREPOSITION"),
            (r"\bconjunction[s]?\b", "CONJUNCTION"),
            (r"\btip[s]?\b", "TIP"),
            (r"\bsuggestion[s]?\b", "TIP"),
            (r"\bmethod[s]?\b", "METHOD"),
            (r"\btechnique[s]?\b", "TECHNIQUE"),
            (r"\bstrateg(?:y|ies)\b", "STRATEGY"),
            (r"\bapproach(?:es)?\b", "APPROACH"),
            (r"\bpractice[s]?\b", "PRACTICE"),
            (r"\balgorithm[s]?\b", "ALGORITHM"),
            (r"\bfunction[s]?\b", "FUNCTION"),
            (r"\bformula[s]?\b", "FORMULA"),
            (r"\bequation[s]?\b", "EQUATION"),
            (r"\btheorem[s]?\b", "THEOREM"),
            (r"\bproof[s]?\b", "PROOF"),
            (r"\bexample[s]?\b", "EXAMPLE"),
            (r"\bidea[s]?\b", "IDEA"),
            (r"\bway[s]?\b", "METHOD"),
            (r"\bstep[s]?\b", "STEP"),
            (r"\bfactor[s]?\b", "FACTOR"),
            (r"\breason[s]?\b", "REASON"),
            (r"\bbenefit[s]?\b", "BENEFIT"),
            (r"\badvantage[s]?\b", "ADVANTAGE"),
            (r"\bdisadvantage[s]?\b", "DISADVANTAGE"),
            (r"\bfeature[s]?\b", "FEATURE"),
            (r"\bcharacteristic[s]?\b", "CHARACTERISTIC"),
            (r"\bmetric[s]?\b", "METRIC"),
            (r"\bindicator[s]?\b", "INDICATOR"),
            (r"\binsight[s]?\b", "INSIGHT"),
            (r"\bfinding[s]?\b", "FINDING"),
        ]

    @property
    def TYPE_MAP(self) -> dict[str, str]:
        return {
            "call": "CALL",
            "phone call": "CALL",
            "meeting": "MEETING",
            "chat": "CHAT",
            "conversation": "CONVERSATION",
            "report": "REPORT",
            "article": "ARTICLE",
        }

    @property
    def CONTEXT_MAP(self) -> dict[str, str]:
        return {
            "customer": "CUSTOMER",
            "support": "SUPPORT",
            "sales": "SALES",
            "technical": "TECHNICAL",
        }

    @property
    def ISSUE_PATTERNS(self) -> list[str]:
        return [
            r"about\s+([\w\s]+?)(?:\s+and|$)",
            r"regarding\s+([\w\s]+?)(?:\s+and|$)",
        ]
