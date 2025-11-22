import re


class Rules:
    COMPARISON_MAP = {
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
    STANDARD_FIELD_KEYWORDS = {
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
    AUDIENCE_MAP = {
        r"\bnon[- ]?technical\b": "NON_TECHNICAL",
        r"\b(beginner|beginners|child|kid|5-?year-?old|10-?year-?old|simple|layman|general audience)\b": "BEGINNER",
        r"\b(expert|advanced|specialist|professionals)\b": "EXPERT",
        r"\btechnical\b": "TECHNICAL",
        r"\b(business|executives|management)\b": "BUSINESS",
    }
    LENGTH_MAP = {
        r"\b(brief|short|concise|quick|summary)\b": "BRIEF",
        r"\b(detailed|comprehensive|thorough|in-?depth|complete)\b": "DETAILED",
    }
    STYLE_MAP = {
        r"\b(simple|easy|straightforward)\b": "SIMPLE",
        r"\b(formal|business[- ]?like|professional)\b": "FORMAL",
    }

    TONE_MAP = {
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
    NUMBER_WORDS = {
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
    SPEC_PATTERNS = [
        (r"(\d+)\s*lines?\b", "LINES"),
        (r"(\d+)\s*words?\b", "WORDS"),
        (r"(\d+)\s*(?:items?|things?|elements?)\b", "ITEMS"),
        (r"(\d+)\s*(?:tips?|suggestions?)\b", "COUNT"),
        (r"(\d+)\s*(?:examples?|instances?)\b", "COUNT"),
        (r"(\d+)\s*(?:steps?|stages?)\b", "STEPS"),
        (r"(\d+)\s*(?:ways?|methods?)\b", "COUNT"),
    ]

    # extraction indicators (implied extraction request)
    EXTRACTION_INDICATORS = [
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

    QA_CRITERIA = {
        r"\b(verification|verify|verified)\b": "VERIFICATION",
        r"\b(policy|policies|policy adherence)\b": "POLICY",
        r"\b(soft[- ]?skills?|empathy|clarity|ownership)\b": "SOFT_SKILLS",
        r"\b(accuracy|accurate|process accuracy)\b": "ACCURACY",
        r"\b(compliance|compliant|violations?)\b": "COMPLIANCE",
        r"\b(sentiment|emotion|feeling|mood)\b": "SENTIMENT",
        r"\b(disclosures?|mandatory disclosures?)\b": "DISCLOSURES",
    }
    QA_INDICATORS = [
        r"\bscore\b",
        r"\bqa\b",
        r"\bquality assurance\b",
        r"\bcompliance\b",
        r"\baudit\b",
    ]

    # Compile regexes once
    COMPILED = {
        "comparison": [(re.compile(p, re.I), v) for p, v in COMPARISON_MAP.items()],
        "standard": [(re.compile(p, re.I), v) for p, v in STANDARD_FIELD_KEYWORDS.items()],
        "audience": [(re.compile(p, re.I), v) for p, v in AUDIENCE_MAP.items()],
        "length": [(re.compile(p, re.I), v) for p, v in LENGTH_MAP.items()],
        "style": [(re.compile(p, re.I), v) for p, v in STYLE_MAP.items()],
        "tone": [(re.compile(p, re.I), v) for p, v in TONE_MAP.items()],
        "specs": [(re.compile(p, re.I), name) for p, name in SPEC_PATTERNS],
        "extraction_indicators": [re.compile(p, re.I) for p in EXTRACTION_INDICATORS],
        "qa_criteria": [(re.compile(p, re.I), v) for p, v in QA_CRITERIA.items()],
        "qa_indicators": [re.compile(p, re.I) for p in QA_INDICATORS]
    }
