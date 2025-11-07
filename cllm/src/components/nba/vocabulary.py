from src.utils.vocabulary import Vocabulary


class NBAVocabulary(Vocabulary):
    EXTRACT_FIELDS = [
        *Vocabulary.EXTRACT_FIELDS,
        "CUSTOMER_INTENT",
        "RELEVANCE_SCORE",
        "NBA_ID",
        "MATCH_CONFIDENCE",
        "SEMANTIC_SIMILARITY",
    ]
    REQ_TOKENS = {
        **Vocabulary.REQ_TOKENS,
        "MATCH": [
            "match",
            "compare",
            "align",
            "map",
            "correlate",
            "match against",
            "compare to",
            "check against",
            "pair",
        ],
        "SELECT": [
            "select",
            "choose",
            "pick",
            "filter",
            "identify matching",
            "find relevant",
            "determine applicable",
        ],
    }
    TARGET_TOKENS = {
        **Vocabulary.TARGET_TOKENS,
        "NBA_CATALOG": [
            "nba",
            "nbas",
            "next best action",
            "next best actions",
            "predefined actions",
            "possible actions",
            "available actions",
            "action catalog",
            "nba catalog",
            "action list",
        ],
        "CUSTOMER_INTENT": [
            "customer intent",
            "customer's intent",
            "customer need",
            "customer request",
            "customer goal",
            "customer problem",
            "customer issue",
            "intent",
        ],
        "NBA_ID": ["nba id", "action id", "nba identifier"],
    }
