TURN_PATTERNS = {
    "en": {
        # --- Resolution Signals ---
        "CONFIRMATION": [
            [{"LEMMA": {"IN": ["yes", "yeah", "yep", "correct"]}}, {"LEMMA": {"IN": ["correct", "right", "exactly", "precisely"]}}],
            [{"LEMMA": "that"}, {"LEMMA": {"IN": ["correct", "right", "exact", "precise"]}}],
            [{"LEMMA": {"IN": ["exactly", "precisely", "absolutely", "definitely", "affirmative"]}}],
            [{"LEMMA": {"IN": ["yes", "yeah"]}}, {"LEMMA": "confirm"}],
            [{"LEMMA": "that"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["correct", "right", "accurate"]}}],
        ],
        "ACCEPTANCE": [
            [{"LEMMA": {"IN": ["sound", "look", "seem"]}}, {"LEMMA": {"IN": ["good", "fine", "great", "perfect", "wonderful"]}}],
            [{"LEMMA": {"IN": ["okay", "ok", "alright"]}}, {"LEMMA": {"IN": ["understand", "agree", "accept"]}}],
            [{"LEMMA": "that"}, {"LEMMA": {"IN": ["work", "help", "do"]}}],
            [{"LEMMA": "I"}, {"LEMMA": {"IN": ["accept", "agree", "approve"]}}],
            [{"LEMMA": {"IN": ["perfect", "great", "wonderful", "fantastic"]}}, {"LEMMA": {"IN": ["work", "help", "do"]}}],
            [{"LEMMA": "I"}, {"LEMMA": "go"}, {"LEMMA": "with"}],
            [{"LEMMA": "that"}, {"LEMMA": {"IN": ["fine", "good", "acceptable", "okay"]}}],
        ],
        "REJECTION": [
            [{"LEMMA": "no"}, {"LEMMA": "that"}, {"LEMMA": {"IN": ["right", "correct", "accurate"]}}],
            [{"LEMMA": "that"}, {"LEMMA": "not"}, {"LEMMA": "what"}, {"LEMMA": "I"}],
            [{"LEMMA": "I"}, {"LEMMA": {"IN": ["disagree", "refuse", "decline", "reject"]}}],
            [{"LEMMA": "not"}, {"LEMMA": {"IN": ["acceptable", "satisfactory", "good", "enough"]}}],
            [{"LEMMA": "that"}, {"LEMMA": {"IN": ["do", "work"]}}, {"LEMMA": "not"}],
            [{"LEMMA": "I"}, {"LEMMA": "do"}, {"LEMMA": "not"}, {"LEMMA": {"IN": ["agree", "accept", "approve"]}}],
            [{"LEMMA": "no"}, {"LEMMA": {"IN": ["way", "chance", "absolutely"]}}],
        ],
        "ACKNOWLEDGMENT": [
            [{"LEMMA": "I"}, {"LEMMA": {"IN": ["understand", "see", "hear", "get"]}}],
            [{"LEMMA": "I"}, {"LEMMA": "see"}, {"LEMMA": "what"}],
            [{"LEMMA": {"IN": ["understood", "noted", "received", "acknowledged"]}}],
            [{"LEMMA": "make"}, {"LEMMA": "sense"}],
            [{"LEMMA": "get"}, {"LEMMA": "it"}],
            [{"LEMMA": "I"}, {"LEMMA": "follow"}],
            [{"LEMMA": "that"}, {"LEMMA": "make"}, {"LEMMA": "sense"}],
        ],

        # --- Escalation Signals ---
        "COMPLAINT": [
            [{"LEMMA": "this"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["unacceptable", "ridiculous", "terrible", "awful", "horrible", "outrageous"]}}],
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["unhappy", "frustrated", "angry", "upset", "disappointed", "dissatisfied"]}}],
            [{"LEMMA": "this"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["disaster", "mess", "nightmare", "joke"]}}],
            [{"LEMMA": {"IN": ["terrible", "awful", "horrible", "poor", "bad"]}}, {"LEMMA": {"IN": ["service", "experience", "support", "product"]}}],
            [{"LEMMA": "I"}, {"LEMMA": "not"}, {"LEMMA": {"IN": ["happy", "satisfied", "pleased"]}}],
            [{"LEMMA": "this"}, {"LEMMA": "should"}, {"LEMMA": "not"}, {"LEMMA": "happen"}],
            [{"LEMMA": {"IN": ["completely", "totally", "absolutely"]}}, {"LEMMA": {"IN": ["unacceptable", "wrong", "ridiculous"]}}],
        ],
        "THREAT": [
            [{"LEMMA": {"IN": ["want", "need", "plan"]}}, {"LEMMA": "cancel"}],
            [{"LEMMA": {"IN": ["switch", "leave", "move"]}}, {"LEMMA": {"IN": ["provider", "competitor", "elsewhere", "away"]}}],
            [{"LEMMA": {"IN": ["talk", "speak", "escalate"]}}, {"LEMMA": {"IN": ["manager", "supervisor", "director", "executive"]}}],
            [{"LEMMA": "I"}, {"LEMMA": "will"}, {"OP": "?"}, {"LEMMA": {"IN": ["cancel", "leave", "report", "sue", "complain"]}}],
            [{"LEMMA": "take"}, {"LEMMA": "business"}, {"LEMMA": "elsewhere"}],
            [{"LEMMA": "file"}, {"LEMMA": {"IN": ["complaint", "lawsuit", "report", "claim"]}}],
            [{"LEMMA": {"IN": ["post", "write", "share"]}}, {"LEMMA": {"IN": ["review", "complaint", "experience"]}}],
            [{"LEMMA": "never"}, {"LEMMA": {"IN": ["use", "come", "return", "buy"]}}],
            [{"LEMMA": {"IN": ["contact", "call", "report"]}}, {"LEMMA": {"IN": ["authority", "regulatory", "ombudsman", "regulator"]}}],
        ],
        "REPETITION": [
            [{"LEMMA": {"IN": ["already", "again", "repeatedly"]}}, {"LEMMA": {"IN": ["say", "tell", "explain", "mention", "call"]}}],
            [{"LEMMA": "this"}, {"LEMMA": "be"}, {"LEMMA": "the"}, {"LEMMA": {"IN": ["second", "third", "fourth", "fifth", "multiple"]}}],
            [{"LEMMA": "I"}, {"LEMMA": "already"}, {"LEMMA": {"IN": ["tell", "say", "explain", "mention", "call"]}}],
            [{"LEMMA": "as"}, {"LEMMA": "I"}, {"LEMMA": {"IN": ["mention", "state", "say", "explain", "note"]}}],
            [{"LEMMA": "for"}, {"LEMMA": "the"}, {"LEMMA": {"IN": ["second", "third", "fourth", "hundredth"]}}],
            [{"LEMMA": "I"}, {"LEMMA": "have"}, {"LEMMA": {"IN": ["wait", "call", "try"]}}, {"LEMMA": "for"}],
            [{"LEMMA": "keep"}, {"LEMMA": {"IN": ["have", "get", "experience"]}}, {"LEMMA": {"IN": ["issue", "problem", "error", "same"]}}],
        ],
        "CONTRADICTION": [
            [{"LEMMA": "but"}, {"LEMMA": "you"}, {"LEMMA": {"IN": ["say", "tell", "promise", "guarantee"]}}],
            [{"LEMMA": "that"}, {"LEMMA": "not"}, {"LEMMA": "what"}, {"LEMMA": {"IN": ["tell", "inform", "say", "promise"]}}],
            [{"LEMMA": "you"}, {"LEMMA": {"IN": ["promise", "guarantee", "assure", "confirm"]}}, {"LEMMA": "that"}],
            [{"LEMMA": {"IN": ["other", "previous", "last", "another"]}}, {"LEMMA": {"IN": ["agent", "representative", "person", "staff"]}}, {"LEMMA": "say"}],
            [{"LEMMA": "that"}, {"LEMMA": {"IN": ["contradict", "conflict", "differ"]}}],
            [{"LEMMA": "but"}, {"LEMMA": {"IN": ["website", "email", "letter", "document", "contract"]}}, {"LEMMA": "say"}],
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "tell"}, {"LEMMA": "something"}, {"LEMMA": "different"}],
        ],

        # --- Information Signals ---
        "CLARIFICATION": [
            [{"LEMMA": "what"}, {"LEMMA": "I"}, {"LEMMA": "mean"}],
            [{"LEMMA": "to"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["specific", "clear", "precise", "exact"]}}],
            [{"LEMMA": "let"}, {"LEMMA": "I"}, {"LEMMA": {"IN": ["clarify", "explain", "rephrase", "elaborate"]}}],
            [{"LEMMA": "in"}, {"LEMMA": "other"}, {"LEMMA": "word"}],
            [{"LEMMA": "to"}, {"LEMMA": "put"}, {"LEMMA": "it"}],
            [{"LEMMA": "what"}, {"LEMMA": "I"}, {"LEMMA": "try"}, {"LEMMA": "say"}],
            [{"LEMMA": {"IN": ["more", "most"]}}, {"LEMMA": {"IN": ["specific", "precise", "exactly"]}}],
        ],
        "ELABORATION": [
            [{"LEMMA": {"IN": ["also", "additionally", "furthermore", "moreover"]}}, {"LEMMA": {"IN": ["the", "I", "it", "this", "there"]}}],
            [{"LEMMA": "on"}, {"LEMMA": "top"}, {"LEMMA": "of"}, {"LEMMA": "that"}],
            [{"LEMMA": "not"}, {"LEMMA": "only"}, {"LEMMA": "that"}, {"LEMMA": "but"}],
            [{"LEMMA": "to"}, {"LEMMA": "add"}, {"LEMMA": "to"}, {"LEMMA": "that"}],
            [{"LEMMA": "there"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["also", "another", "more"]}}],
            [{"LEMMA": "in"}, {"LEMMA": "addition"}, {"LEMMA": "to"}],
        ],
        "CORRECTION": [
            [{"LEMMA": "actually"}, {"LEMMA": {"IN": ["it", "that", "the"]}}, {"LEMMA": {"IN": ["be", "say", "show"]}}],
            [{"LEMMA": "no"}, {"LEMMA": {"IN": ["amount", "date", "number", "time", "charge", "figure"]}}],
            [{"LEMMA": "I"}, {"LEMMA": "mean"}, {"LEMMA": "to"}, {"LEMMA": "say"}],
            [{"LEMMA": "sorry"}, {"LEMMA": "I"}, {"LEMMA": {"IN": ["mean", "say"]}}],
            [{"LEMMA": "to"}, {"LEMMA": "correct"}, {"LEMMA": "myself"}],
            [{"LEMMA": "not"}, {"OP": "+"}, {"LEMMA": "but"}],
            [{"LEMMA": "I"}, {"LEMMA": {"IN": ["misspeak", "mistake", "error"]}}],
        ],
        "EXPANSION": [
            # "while we're at it"
            [{"LEMMA": "while"}, {"LEMMA": "we"}, {"LEMMA": "be"}, {"LEMMA": "at"}, {"LEMMA": "it"}],
            # "actually there's more"
            [{"LEMMA": "actually"}, {"LEMMA": "there"}, {"LEMMA": "be"}, {"LEMMA": "more"}],
            # "that's not the only problem/issue"
            [{"LEMMA": "that"}, {"LEMMA": "not"}, {"LEMMA": "the"}, {"LEMMA": "only"}, {"LEMMA": {"IN": ["problem", "issue", "thing"]}}],
            # "I also have a question/issue about"
            [{"LEMMA": "I"}, {"LEMMA": "also"}, {"LEMMA": "have"}, {"LEMMA": {"IN": ["question", "issue", "problem", "concern"]}}],
            # "there's something else"
            [{"LEMMA": "there"}, {"LEMMA": "be"}, {"LEMMA": "something"}, {"LEMMA": "else"}],
            # "related to that"
            [{"LEMMA": "related"}, {"LEMMA": "to"}, {"LEMMA": "that"}],
            # "on that note"
            [{"LEMMA": "on"}, {"LEMMA": "that"}, {"LEMMA": "note"}],
        ],

        # --- Intent Signals ---
        "REQUEST": [
            [{"LEMMA": {"IN": ["can", "could", "would"]}}, {"LEMMA": "you"}, {"OP": "?"}, {"LEMMA": "please"}],
            [{"LEMMA": {"IN": ["can", "could"]}}, {"LEMMA": "you"}, {"LEMMA": {"IN": ["help", "assist", "support"]}}],
            [{"LEMMA": "I"}, {"LEMMA": "would"}, {"LEMMA": {"IN": ["like", "appreciate", "prefer"]}}],
            [{"LEMMA": "please"}, {"LEMMA": {"IN": ["help", "fix", "resolve", "check", "look", "update"]}}],
            [{"LEMMA": "be"}, {"LEMMA": "it"}, {"LEMMA": "possible"}, {"LEMMA": "to"}],
            [{"LEMMA": "I"}, {"LEMMA": "would"}, {"LEMMA": "like"}, {"LEMMA": "to"}],
            [{"LEMMA": "could"}, {"LEMMA": "you"}, {"LEMMA": "please"}, {"LEMMA": {"IN": ["check", "verify", "confirm", "look"]}}],
        ],
        "DEMAND": [
            [{"LEMMA": "I"}, {"LEMMA": "need"}, {"LEMMA": "you"}, {"LEMMA": "to"}],
            [{"LEMMA": "you"}, {"LEMMA": {"IN": ["have", "must", "need"]}}, {"LEMMA": "to"}],
            [{"LEMMA": {"IN": ["fix", "resolve", "sort", "handle"]}}, {"LEMMA": "this"}, {"LEMMA": {"IN": ["now", "immediately", "today", "asap"]}}],
            [{"LEMMA": "I"}, {"LEMMA": {"IN": ["demand", "require", "insist", "expect"]}}],
            [{"LEMMA": "this"}, {"LEMMA": "need"}, {"LEMMA": "to"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["fix", "resolve", "address", "sort"]}}],
            [{"LEMMA": "I"}, {"LEMMA": "want"}, {"LEMMA": "this"}, {"LEMMA": {"IN": ["resolve", "fix", "sort"]}}, {"LEMMA": {"IN": ["now", "immediately", "today"]}}],
            [{"LEMMA": "make"}, {"LEMMA": "sure"}, {"LEMMA": "that"}],
        ],
        "INQUIRY": [
            [{"LEMMA": "do"}, {"LEMMA": "you"}, {"LEMMA": "know"}, {"LEMMA": {"IN": ["if", "whether"]}}],
            [{"LEMMA": "what"}, {"LEMMA": {"IN": ["be", "is", "are"]}}, {"LEMMA": "the"}],
            [{"LEMMA": "how"}, {"LEMMA": {"IN": ["do", "can", "should", "would"]}}, {"LEMMA": "I"}],
            [{"LEMMA": "when"}, {"LEMMA": {"IN": ["will", "can", "should", "would"]}}],
            [{"LEMMA": "why"}, {"LEMMA": {"IN": ["do", "be", "have", "can"]}}],
            [{"LEMMA": "be"}, {"LEMMA": "there"}, {"LEMMA": {"IN": ["a", "an", "any"]}}],
            [{"LEMMA": "can"}, {"LEMMA": "you"}, {"LEMMA": "tell"}, {"LEMMA": "I"}],
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "wonder"}, {"LEMMA": {"IN": ["if", "whether", "about"]}}],
        ],
        "GUIDE": [
            # "can you walk/guide me through"
            [{"LEMMA": {"IN": ["can", "could"]}}, {"LEMMA": "you"}, {"LEMMA": {"IN": ["walk", "guide", "show"]}}],
            # "show me how"
            [{"LEMMA": "show"}, {"LEMMA": "I"}, {"LEMMA": "how"}],
            # "step by step"
            [{"LEMMA": "step"}, {"LEMMA": "by"}, {"LEMMA": "step"}],
            # "how do I get started"
            [{"LEMMA": "how"}, {"LEMMA": "do"}, {"LEMMA": "I"}, {"LEMMA": "get"}, {"LEMMA": "start"}],
            # "can you explain the process"
            [{"LEMMA": {"IN": ["can", "could"]}}, {"LEMMA": "you"}, {"LEMMA": "explain"}, {"LEMMA": "process"}],
            # "what are the next steps"
            [{"LEMMA": "what"}, {"LEMMA": "be"}, {"LEMMA": "the"}, {"LEMMA": "next"}, {"LEMMA": "step"}],
            # "help me understand"
            [{"LEMMA": "help"}, {"LEMMA": "I"}, {"LEMMA": "understand"}],
            # "what should I do"
            [{"LEMMA": "what"}, {"LEMMA": "should"}, {"LEMMA": "I"}, {"LEMMA": "do"}],
            # "what do I need to do"
            [{"LEMMA": "what"}, {"LEMMA": "do"}, {"LEMMA": "I"}, {"LEMMA": "need"}, {"LEMMA": "to"}, {"LEMMA": "do"}],
            # "where do I begin"
            [{"LEMMA": "where"}, {"LEMMA": "do"}, {"LEMMA": "I"}, {"LEMMA": "begin"}],
            # "how can I proceed"
            [{"LEMMA": "how"}, {"LEMMA": "can"}, {"LEMMA": "I"}, {"LEMMA": "proceed"}],
            # "tell me what I need"
            [{"LEMMA": "tell"}, {"LEMMA": "I"}, {"LEMMA": "what"}, {"LEMMA": "I"}, {"LEMMA": "need"}],
        ],

        # --- Relationship Signals ---
        "GREETING": [
            [{"LEMMA": {"IN": ["hello", "hi", "hey", "greetings", "howdy"]}}],
            [{"LEMMA": "good"}, {"LEMMA": {"IN": ["morning", "afternoon", "evening", "day"]}}],
            [{"LEMMA": "how"}, {"LEMMA": {"IN": ["be", "are"]}}, {"LEMMA": "you"}],
            [{"LEMMA": "nice"}, {"LEMMA": "to"}, {"LEMMA": {"IN": ["meet", "speak", "talk"]}}],
            [{"LEMMA": "hope"}, {"LEMMA": "you"}, {"LEMMA": {"IN": ["do", "be"]}}],
        ],
        "COMPLIMENT": [
            [{"LEMMA": "you"}, {"LEMMA": "have"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["helpful", "great", "wonderful", "fantastic", "amazing"]}}],
            [{"LEMMA": "thank"}, {"LEMMA": "you"}, {"LEMMA": {"IN": ["so", "very"]}}, {"LEMMA": "much"}],
            [{"LEMMA": "you"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["amazing", "wonderful", "fantastic", "great", "excellent"]}}],
            [{"LEMMA": {"IN": ["excellent", "outstanding", "superb", "exceptional"]}}, {"LEMMA": {"IN": ["service", "support", "help", "assistance"]}}],
            [{"LEMMA": "I"}, {"LEMMA": "appreciate"}, {"LEMMA": "your"}, {"LEMMA": {"IN": ["help", "assistance", "support", "patience"]}}],
            [{"LEMMA": "you"}, {"LEMMA": "have"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["patient", "kind", "understanding", "professional"]}}],
        ],
        "CLOSING": [
            [{"LEMMA": "that"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["all", "everything", "it"]}}],
            [{"LEMMA": {"IN": ["goodbye", "bye", "farewell", "cheerio", "ciao"]}}],
            [{"LEMMA": "have"}, {"LEMMA": "a"}, {"LEMMA": {"IN": ["good", "great", "nice", "wonderful"]}}, {"LEMMA": {"IN": ["day", "evening", "night", "weekend"]}}],
            [{"LEMMA": "thank"}, {"LEMMA": "you"}, {"LEMMA": "and"}, {"LEMMA": {"IN": ["goodbye", "bye"]}}],
            [{"LEMMA": "I"}, {"LEMMA": "think"}, {"LEMMA": "that"}, {"LEMMA": "cover"}, {"LEMMA": "everything"}],
            [{"LEMMA": "no"}, {"LEMMA": {"IN": ["more", "other", "further"]}}, {"LEMMA": {"IN": ["question", "issue", "problem", "concern"]}}],
            [{"LEMMA": "that"}, {"LEMMA": "will"}, {"LEMMA": "be"}, {"LEMMA": "all"}],
        ],

        # --- Neutral / Statement ---
        "STATEMENT": [
            [{"LEMMA": "I"}, {"LEMMA": {"IN": ["notice", "see", "find", "observe", "discover"]}}, {"LEMMA": "that"}],
            [{"LEMMA": "my"}, {"LEMMA": {"IN": ["account", "order", "payment", "subscription", "plan", "bill"]}}],
            [{"LEMMA": "the"}, {"LEMMA": {"IN": ["charge", "payment", "amount", "fee", "cost"]}}, {"LEMMA": "be"}],
            [{"LEMMA": "I"}, {"LEMMA": "have"}, {"LEMMA": "be"}, {"LEMMA": "a"}, {"LEMMA": "customer"}],
            [{"LEMMA": "the"}, {"LEMMA": {"IN": ["issue", "problem", "error", "bug"]}}, {"LEMMA": "be"}],
        ],
        "PROBLEM_DESCRIPTION": [
            [{"LEMMA": "I"}, {"LEMMA": "notice"}],
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "charge"}],
            [{"LEMMA": "charge"}, {"LOWER": {"IN": ["twice", "double", "twice."]}}],
            [{"LEMMA": "bill"}, {"LOWER": "twice"}],
            [{"LEMMA": "there"}, {"LEMMA": "be"}, {"LOWER": "two"}, {"LEMMA": "charge"}],
            [{"LEMMA": "duplicate"}, {"LEMMA": "charge"}],
        ],

        # --- Uncertainty ---
        "DOUBT": [
            [{"LEMMA": "I"}, {"LEMMA": "not"}, {"LEMMA": "sure"}],
            [{"LEMMA": "I"}, {"LEMMA": "do"}, {"LEMMA": "not"}, {"LEMMA": "know"}],
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "hesitant"}],
            [{"LEMMA": "I"}, {"LEMMA": "not"}, {"LEMMA": "convince"}],
            [{"LEMMA": "I"}, {"LEMMA": "have"}, {"LEMMA": "doubt"}],
            [{"LEMMA": "I"}, {"LEMMA": "still"}, {"LEMMA": "think"}],
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "on"}, {"LEMMA": "the"}, {"LEMMA": "fence"}],
        ],
        "UNCERTAINTY": [
            [{"LEMMA": "maybe"}],
            [{"LEMMA": "possibly"}],
            [{"LEMMA": "perhaps"}],
            [{"LEMMA": "it"}, {"LEMMA": "depend"}],
            [{"LEMMA": "I"}, {"LEMMA": "consider"}],
            [{"LEMMA": "I"}, {"LEMMA": "explore"}, {"LEMMA": "option"}],
        ],

        # --- Sales Signals ---
        "PURCHASE_INTENT": [
            [{"LEMMA": "I"}, {"LEMMA": "would"}, {"LEMMA": "like"}, {"LEMMA": "buy"}],
            [{"LEMMA": "I"}, {"LEMMA": "would"}, {"LEMMA": "like"}, {"LEMMA": "sign"}],
            [{"LEMMA": "how"}, {"LEMMA": "much"}, {"LEMMA": "do"}, {"LEMMA": "it"}, {"LEMMA": "cost"}],
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "interested"}],
            [{"LEMMA": {"IN": ["can", "could"]}}, {"LEMMA": "I"}, {"LEMMA": "try"}],
            [{"LEMMA": "be"}, {"LEMMA": "there"}, {"LEMMA": "trial"}],
            [{"LEMMA": "I"}, {"LEMMA": "would"}, {"LEMMA": "like"}, {"LEMMA": "demo"}],
        ],
        "PRICE_CONCERN": [
            [{"LEMMA": "that"}, {"LEMMA": "expensive"}],
            [{"LEMMA": "too"}, {"LEMMA": "expensive"}],
            [{"LEMMA": "outside"}, {"LEMMA": "budget"}],
            [{"LEMMA": {"IN": ["can", "could"]}}, {"LEMMA": "you"}, {"LEMMA": "do"}, {"LEMMA": "good"}],
            [{"LEMMA": "be"}, {"LEMMA": "there"}, {"LEMMA": "discount"}],
            [{"LEMMA": "offer"}, {"LEMMA": "promotion"}],
        ],

        # --- Evaluation ---
        "COMPARISON": [
            [{"LEMMA": "what"}, {"LEMMA": "difference"}],
            [{"LEMMA": "how"}, {"LEMMA": "do"}, {"LEMMA": "it"}, {"LEMMA": "compare"}],
            [{"LEMMA": "which"}, {"LEMMA": "one"}, {"LEMMA": "be"}, {"LEMMA": "good"}],
            [{"LOWER": {"IN": ["vs", "versus"]}}],
            [{"LEMMA": "compare"}, {"LEMMA": "to"}],
        ],
        "OBJECTION": [
            [{"LEMMA": "I"}, {"LEMMA": "do"}, {"LEMMA": "not"}, {"LEMMA": "see"}, {"LEMMA": "value"}],
            [{"LEMMA": "why"}, {"LEMMA": "should"}, {"LEMMA": "I"}],
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "concern"}],
            [{"LEMMA": "that"}, {"LEMMA": "will"}, {"LEMMA": "not"}, {"LEMMA": "work"}],
            [{"LEMMA": "we"}, {"LEMMA": "not"}, {"LEMMA": "ready"}],
        ],
        "EVALUATING": [
            # "let me think about that"
            [{"LEMMA": "let"}, {"LEMMA": "I"}, {"LEMMA": "think"}, {"LEMMA": "about"}],
            # "let me assess/review/evaluate"
            [{"LEMMA": "let"}, {"LEMMA": "I"}, {"LEMMA": {"IN": ["assess", "review", "evaluate", "look"]}}],
            # "tell me more about"
            [{"LEMMA": "tell"}, {"LEMMA": "I"}, {"LEMMA": "more"}, {"LEMMA": "about"}],
            # "what are the pros and cons"
            [{"LEMMA": "what"}, {"LEMMA": "be"}, {"LEMMA": "the"}, {"LEMMA": "pro"}],
            # "is this worth it"
            [{"LEMMA": "be"}, {"LEMMA": "this"}, {"LEMMA": "worth"}],
            # "I'm reviewing/assessing"
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["review", "assess", "evaluate"]}}],
            # "how does this compare"
            [{"LEMMA": "how"}, {"LEMMA": "do"}, {"LEMMA": "this"}, {"LEMMA": "compare"}],
            # "what would I get"
            [{"LEMMA": "what"}, {"LEMMA": "would"}, {"LEMMA": "I"}, {"LEMMA": "get"}],
        ],

        # --- Commitment ---
        "DECISION": [
            [{"LEMMA": "let"}, {"LEMMA": "we"}, {"LEMMA": "do"}],
            [{"LEMMA": "go"}, {"LEMMA": "ahead"}],
            [{"LEMMA": "sign"}, {"LEMMA": "I"}, {"LEMMA": "up"}],
            [{"LEMMA": "I"}, {"LEMMA": "will"}, {"LEMMA": "proceed"}],
            [{"LEMMA": "I"}, {"LEMMA": "will"}, {"LEMMA": "take"}],
        ],
        "DEFERMENT": [
            [{"LEMMA": "I"}, {"LEMMA": "will"}, {"LEMMA": "think"}],
            [{"LEMMA": "not"}, {"LEMMA": "right"}, {"LEMMA": "now"}],
            [{"LEMMA": "I"}, {"LEMMA": "will"}, {"LEMMA": "come"}, {"LEMMA": "back"}],
            [{"LEMMA": "I"}, {"LEMMA": "need"}, {"LEMMA": "more"}, {"LEMMA": "time"}],
            [{"LEMMA": "let"}, {"LEMMA": "I"}, {"LEMMA": "discuss"}],
        ],

        # --- Customer Journey ---
        "RETENTION_RISK": [
            # "I'm thinking of leaving/canceling/switching"
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "think"}, {"LEMMA": "of"}, {"LEMMA": {"IN": ["leave", "cancel", "switch"]}}],
            # "I'm reconsidering"
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "reconsider"}],
            # "this is making me reconsider"
            [{"LEMMA": "this"}, {"LEMMA": "make"}, {"LEMMA": "I"}, {"LEMMA": "reconsider"}],
            # "I might have to go/switch/leave"
            [{"LEMMA": "I"}, {"LEMMA": "might"}, {"LEMMA": "have"}, {"LEMMA": "to"}, {"LEMMA": {"IN": ["go", "switch", "leave"]}}],
            # "I'm not sure this is worth it"
            [{"LEMMA": "I"}, {"LEMMA": "not"}, {"LEMMA": "sure"}, {"LEMMA": "this"}, {"LEMMA": "be"}, {"LEMMA": "worth"}],
            # "I'm not getting the value"
            [{"LEMMA": "I"}, {"LEMMA": "not"}, {"LEMMA": "get"}, {"LEMMA": "value"}],
            # "this isn't what I expected"
            [{"LEMMA": "this"}, {"LEMMA": "not"}, {"LEMMA": "what"}, {"LEMMA": "I"}, {"LEMMA": "expect"}],
        ],
        "CHURN": [
            # "cancel my account/subscription/plan/service"
            [{"LEMMA": "cancel"}, {"LEMMA": "my"}, {"LEMMA": {"IN": ["account", "subscription", "plan", "service", "membership"]}}],
            # "please cancel"
            [{"LEMMA": "please"}, {"LEMMA": "cancel"}],
            # "I want to cancel"
            [{"LEMMA": "I"}, {"LEMMA": "want"}, {"LEMMA": "to"}, {"LEMMA": "cancel"}],
            # "close my account"
            [{"LEMMA": "close"}, {"LEMMA": "my"}, {"LEMMA": "account"}],
            # "I've decided to leave/cancel"
            [{"LEMMA": "I"}, {"LEMMA": "have"}, {"LEMMA": "decide"}, {"LEMMA": "to"}, {"LEMMA": {"IN": ["leave", "cancel"]}}],
            # "terminate my subscription/account"
            [{"LEMMA": "terminate"}, {"LEMMA": "my"}, {"LEMMA": {"IN": ["subscription", "account", "service", "membership"]}}],
            # "I'm canceling"
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "cancel"}],
        ],
        "ONBOARDING": [
            # "I just signed up"
            [{"LEMMA": "I"}, {"LEMMA": "just"}, {"LEMMA": "sign"}, {"LEMMA": "up"}],
            # "I'm new here/to this"
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "new"}],
            # "I just joined/created/opened"
            [{"LEMMA": "I"}, {"LEMMA": "just"}, {"LEMMA": {"IN": ["join", "create", "open"]}}],
            # "first time using/logging/accessing"
            [{"LEMMA": "first"}, {"LEMMA": "time"}, {"LEMMA": {"IN": ["use", "log", "access"]}}],
            # "I'm getting started"
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "get"}, {"LEMMA": "start"}],
            # "just set up my account"
            [{"LEMMA": "just"}, {"LEMMA": "set"}, {"LEMMA": "up"}, {"LEMMA": "account"}],
            # "how do I set up"
            [{"LEMMA": "how"}, {"LEMMA": "do"}, {"LEMMA": "I"}, {"LEMMA": "set"}, {"LEMMA": "up"}],
        ],

        # --- Customer Confusion (primary) ---
        "CONFUSION": [
            # "I don't understand"
            [{"LEMMA": "I"}, {"LEMMA": "do"}, {"LEMMA": "not"}, {"LEMMA": "understand"}],
            # "I'm confused"
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "confused"}],
            # "that doesn't make sense"
            [{"LEMMA": "that"}, {"LEMMA": "do"}, {"LEMMA": "not"}, {"LEMMA": "make"}, {"LEMMA": "sense"}],
            # "what do you mean"
            [{"LEMMA": "what"}, {"LEMMA": "do"}, {"LEMMA": "you"}, {"LEMMA": "mean"}],
            # "I don't follow"
            [{"LEMMA": "I"}, {"LEMMA": "do"}, {"LEMMA": "not"}, {"LEMMA": "follow"}],
            # "not sure what you mean"
            [{"LEMMA": "not"}, {"LEMMA": "sure"}, {"LEMMA": "what"}, {"LEMMA": "you"}, {"LEMMA": "mean"}],
            # "that's confusing/confused"
            [{"LEMMA": "that"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["confusing", "confused"]}}],
            # "I'm lost"
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LOWER": "lost"}],
            # "having trouble understanding"
            [{"LEMMA": "have"}, {"LEMMA": "trouble"}, {"LEMMA": "understand"}],
            # "what does that mean"
            [{"LEMMA": "what"}, {"LEMMA": "do"}, {"LEMMA": "that"}, {"LEMMA": "mean"}],
            # "can you clarify"
            [{"LEMMA": {"IN": ["can", "could"]}}, {"LEMMA": "you"}, {"LEMMA": "clarify"}],
        ],

        # --- Agent-Acknowledged (secondary; used for Layer-3 completion detection) ---
        "APOLOGY": [
            # "I'm sorry" / "I am sorry"
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "sorry"}],
            # "I apologize" / "we apologize"
            [{"LEMMA": {"IN": ["I", "we"]}}, {"LEMMA": "apologize"}],
            # "my apologies" / "our apologies"
            [{"LEMMA": {"IN": ["my", "our"]}}, {"LEMMA": "apology"}],
            # "sorry for the trouble/inconvenience"
            [{"LEMMA": "sorry"}, {"LEMMA": "for"}, {"LEMMA": "the"}, {"LEMMA": {"IN": ["trouble", "inconvenience", "confusion", "delay", "issue"]}}],
            # "please accept my apologies"
            [{"LEMMA": "please"}, {"LEMMA": "accept"}, {"LEMMA": "my"}, {"LEMMA": "apology"}],
            # "I sincerely apologize"
            [{"LEMMA": "sincerely"}, {"LEMMA": "apologize"}],
        ],
        "EMPATHY": [
            # emotional noun after "understand" distinguishes from ACKNOWLEDGMENT ("I understand" alone)
            [{"LEMMA": "I"}, {"LEMMA": "understand"}, {"LEMMA": "your"}, {"LEMMA": {"IN": ["frustration", "concern", "situation", "feeling", "difficulty"]}}],
            # "I can see why you're upset/frustrated"
            [{"LEMMA": "I"}, {"LEMMA": "can"}, {"LEMMA": "see"}, {"LEMMA": "why"}],
            # "that must be (very/really/so) frustrating/difficult"
            [{"LEMMA": "that"}, {"LEMMA": "must"}, {"LEMMA": "be"}, {"OP": "?"}, {"LEMMA": {"IN": ["frustrating", "difficult", "upsetting", "stressful", "hard"]}}],
            # "I understand how you feel"
            [{"LEMMA": "I"}, {"LEMMA": "understand"}, {"LEMMA": "how"}, {"LEMMA": "you"}, {"LEMMA": "feel"}],
            # "I completely/fully understand"
            [{"LEMMA": {"IN": ["completely", "fully", "totally"]}}, {"LEMMA": "understand"}],
            # "I know how frustrating/difficult this can be"
            [{"LEMMA": "I"}, {"LEMMA": "know"}, {"LEMMA": "how"}, {"LEMMA": {"IN": ["frustrating", "difficult", "hard", "challenging"]}}],
            # "that must have been difficult/frustrating"
            [{"LEMMA": "that"}, {"LEMMA": "must"}, {"LEMMA": "have"}, {"LEMMA": "be"}, {"LEMMA": {"IN": ["difficult", "hard", "frustrating", "upsetting"]}}],
        ],
        "RESOLUTION_OFFER": [
            # "what I can do for you is"
            [{"LEMMA": "what"}, {"LEMMA": "I"}, {"LEMMA": "can"}, {"LEMMA": "do"}, {"LEMMA": "for"}, {"LEMMA": "you"}],
            # "I'll go ahead and"
            [{"LEMMA": "I"}, {"LEMMA": "will"}, {"LEMMA": "go"}, {"LEMMA": "ahead"}],
            # "let me take care of that"
            [{"LEMMA": "let"}, {"LEMMA": "I"}, {"LEMMA": "take"}, {"LEMMA": "care"}],
            # "I can offer you"
            [{"LEMMA": "I"}, {"LEMMA": "can"}, {"LEMMA": "offer"}, {"LEMMA": "you"}],
            # "I'm going to resolve/fix/handle this"
            [{"LEMMA": "I"}, {"LEMMA": "be"}, {"LEMMA": "go"}, {"LEMMA": "to"}, {"LEMMA": {"IN": ["resolve", "fix", "address", "sort", "handle"]}}],
            # "I'll make sure"
            [{"LEMMA": "I"}, {"LEMMA": "will"}, {"LEMMA": "make"}, {"LEMMA": "sure"}],
            # "let me see what I can do"
            [{"LEMMA": "let"}, {"LEMMA": "I"}, {"LEMMA": "see"}, {"LEMMA": "what"}, {"LEMMA": "I"}, {"LEMMA": "can"}, {"LEMMA": "do"}],
            # "I will process/arrange/handle that"
            [{"LEMMA": "I"}, {"LEMMA": "will"}, {"LEMMA": {"IN": ["process", "arrange", "apply", "handle"]}}],
        ],
        "VERIFICATION_REQUEST": [
            # "can/could you confirm/verify your"
            [{"LEMMA": {"IN": ["can", "could"]}}, {"LEMMA": "you"}, {"LEMMA": {"IN": ["confirm", "verify"]}}, {"LEMMA": "your"}],
            # "can/could you provide/share your"
            [{"LEMMA": {"IN": ["can", "could"]}}, {"LEMMA": "you"}, {"LEMMA": {"IN": ["provide", "share"]}}, {"LEMMA": "your"}],
            # "for security purposes"
            [{"LEMMA": "for"}, {"LEMMA": "security"}, {"LEMMA": "purpose"}],
            # "I need to verify/confirm your"
            [{"LEMMA": "I"}, {"LEMMA": "need"}, {"LEMMA": "to"}, {"LEMMA": {"IN": ["verify", "confirm"]}}, {"LEMMA": "your"}],
            # "may I have your"
            [{"LEMMA": "may"}, {"LEMMA": "I"}, {"LEMMA": "have"}, {"LEMMA": "your"}],
            # "before I proceed/continue"
            [{"LEMMA": "before"}, {"LEMMA": "I"}, {"LEMMA": {"IN": ["proceed", "continue"]}}],
            # "I'll need to confirm/verify"
            [{"LEMMA": "I"}, {"LEMMA": "will"}, {"LEMMA": "need"}, {"LEMMA": "to"}, {"LEMMA": {"IN": ["confirm", "verify"]}}],
        ],
    },

    "fr": {
        "THREAT": [
            [{"LEMMA": {"IN": ["vouloir", "devoir", "prévoir"]}}, {"LEMMA": "annuler"}],
            [{"LEMMA": {"IN": ["changer", "partir", "quitter"]}}, {"LEMMA": {"IN": ["fournisseur", "prestataire", "opérateur"]}}],
            [{"LEMMA": {"IN": ["parler", "escalader"]}}, {"LEMMA": {"IN": ["responsable", "superviseur", "directeur"]}}],
        ],
        "COMPLAINT": [
            [{"LEMMA": "ce"}, {"LEMMA": "être"}, {"LEMMA": {"IN": ["inacceptable", "ridicule", "terrible", "horrible"]}}],
            [{"LEMMA": "je"}, {"LEMMA": "être"}, {"LEMMA": {"IN": ["mécontent", "frustré", "en colère", "déçu"]}}],
        ],
        "ACCEPTANCE": [
            [{"LEMMA": {"IN": ["ça", "cela"]}}, {"LEMMA": {"IN": ["marcher", "convenir", "aller"]}}],
            [{"LEMMA": {"IN": ["accord", "parfait", "bien", "excellent"]}}],
        ],
        "GREETING": [
            [{"LEMMA": {"IN": ["bonjour", "bonsoir", "salut", "allô"]}}],
            [{"LEMMA": "comment"}, {"LEMMA": {"IN": ["aller", "être"]}}, {"LEMMA": "vous"}],
        ],
        "CLOSING": [
            [{"LEMMA": {"IN": ["aurevoir", "adieu", "bonne", "merci"]}}],
            [{"LEMMA": "c'est"}, {"LEMMA": "tout"}],
        ],
        "INQUIRY": [
            [{"LEMMA": "est"}, {"LEMMA": "ce"}, {"LEMMA": "que"}],
            [{"LEMMA": "pouvez"}, {"LEMMA": "vous"}, {"LEMMA": "me"}, {"LEMMA": "dire"}],
            [{"LEMMA": "comment"}, {"LEMMA": {"IN": ["puis", "peut", "dois"]}}],
        ],
        "REQUEST": [
            [{"LEMMA": "pourriez"}, {"LEMMA": "vous"}, {"LEMMA": "s'il"}, {"LEMMA": "vous"}, {"LEMMA": "plaît"}],
            [{"LEMMA": "je"}, {"LEMMA": "voudrais"}, {"LEMMA": {"IN": ["que", "vous"]}}],
            [{"LEMMA": "s'il"}, {"LEMMA": "vous"}, {"LEMMA": "plaît"}, {"LEMMA": {"IN": ["aider", "corriger", "vérifier"]}}],
        ],
        "GUIDE": [
            [{"LEMMA": {"IN": ["pouvez", "pourriez"]}}, {"LEMMA": "vous"}, {"LEMMA": {"IN": ["m'expliquer", "expliquer", "m'accompagner"]}}],
            [{"LEMMA": "montrez"}, {"LEMMA": {"IN": ["moi", "me"]}}, {"LEMMA": "comment"}],
            [{"LEMMA": "que"}, {"LEMMA": "dois"}, {"LEMMA": "je"}, {"LEMMA": "faire"}],
            [{"LEMMA": "quelles"}, {"LEMMA": "sont"}, {"LEMMA": "les"}, {"LEMMA": "prochaines"}, {"LEMMA": "étape"}],
        ],
        "CHURN": [
            [{"LEMMA": "annuler"}, {"LEMMA": "mon"}, {"LEMMA": {"IN": ["compte", "abonnement", "contrat"]}}],
            [{"LEMMA": "je"}, {"LEMMA": "vouloir"}, {"LEMMA": "résilier"}],
            [{"LEMMA": "clôturer"}, {"LEMMA": "mon"}, {"LEMMA": "compte"}],
        ],
        "RETENTION_RISK": [
            [{"LEMMA": "je"}, {"LEMMA": "penser"}, {"LEMMA": "à"}, {"LEMMA": {"IN": ["résilier", "partir", "annuler"]}}],
            [{"LEMMA": "je"}, {"LEMMA": "reconsidérer"}],
            [{"LEMMA": "ce"}, {"LEMMA": "ne"}, {"LEMMA": "pas"}, {"LEMMA": "valoir"}, {"LEMMA": "la"}, {"LEMMA": "peine"}],
        ],
        "ONBOARDING": [
            [{"LEMMA": "je"}, {"LEMMA": "venir"}, {"LEMMA": "de"}, {"LEMMA": "s'inscrire"}],
            [{"LEMMA": "je"}, {"LEMMA": "être"}, {"LEMMA": "nouveau"}],
            [{"LEMMA": "première"}, {"LEMMA": "fois"}],
        ],
        "EVALUATING": [
            [{"LEMMA": "laissez"}, {"LEMMA": "moi"}, {"LEMMA": "réfléchir"}],
            [{"LEMMA": "dites"}, {"LEMMA": "moi"}, {"LEMMA": "plus"}],
            [{"LEMMA": "est"}, {"LEMMA": "ce"}, {"LEMMA": "que"}, {"LEMMA": "ça"}, {"LEMMA": "valoir"}],
        ],
        "UNCERTAINTY": [
            [{"LEMMA": "peut-être"}],
            [{"LEMMA": "possiblement"}],
            [{"LEMMA": "cela"}, {"LEMMA": "dépendre"}],
        ],
        "DEFERMENT": [
            [{"LEMMA": "je"}, {"LEMMA": "vais"}, {"LEMMA": "réfléchir"}],
            [{"LEMMA": "pas"}, {"LEMMA": "pour"}, {"LEMMA": "l'instant"}],
            [{"LEMMA": "j'ai"}, {"LEMMA": "besoin"}, {"LEMMA": "de"}, {"LEMMA": "temps"}],
        ],
        "EXPANSION": [
            [{"LEMMA": "pendant"}, {"LEMMA": "qu'on"}, {"LEMMA": "y"}, {"LEMMA": "être"}],
            [{"LEMMA": "il"}, {"LEMMA": "y"}, {"LEMMA": "avoir"}, {"LEMMA": "autre"}, {"LEMMA": "chose"}],
            [{"LEMMA": "en"}, {"LEMMA": "rapport"}, {"LEMMA": "avec"}, {"LEMMA": "ça"}],
        ],
        "CONFUSION": [
            [{"LEMMA": "je"}, {"LEMMA": "ne"}, {"LEMMA": "comprendre"}, {"LEMMA": "pas"}],
            [{"LEMMA": "je"}, {"LEMMA": "être"}, {"LEMMA": "confus"}],
            [{"LEMMA": "cela"}, {"LEMMA": "ne"}, {"LEMMA": "pas"}, {"LEMMA": "avoir"}, {"LEMMA": "sens"}],
            [{"LEMMA": "que"}, {"LEMMA": "vouloir"}, {"LEMMA": "dire"}],
        ],
        "APOLOGY": [
            [{"LEMMA": "je"}, {"LEMMA": "être"}, {"LEMMA": "désolé"}],
            [{"LEMMA": "je"}, {"LEMMA": "s'excuser"}],
            [{"LEMMA": "mes"}, {"LEMMA": "excuse"}],
            [{"LEMMA": "désolé"}, {"LEMMA": "pour"}, {"LEMMA": "le"}, {"LEMMA": {"IN": ["désagrément", "problème", "retard"]}}],
        ],
        "EMPATHY": [
            [{"LEMMA": "je"}, {"LEMMA": "comprendre"}, {"LEMMA": "votre"}, {"LEMMA": {"IN": ["frustration", "préoccupation", "situation"]}}],
            [{"LEMMA": "cela"}, {"LEMMA": "devoir"}, {"LEMMA": "être"}, {"LEMMA": {"IN": ["frustrant", "difficile", "stressant"]}}],
            [{"LEMMA": "je"}, {"LEMMA": "comprendre"}, {"LEMMA": "tout"}, {"LEMMA": "à"}, {"LEMMA": "fait"}],
            [{"LEMMA": "je"}, {"LEMMA": "voir"}, {"LEMMA": "pourquoi"}],
        ],
        "RESOLUTION_OFFER": [
            [{"LEMMA": "ce"}, {"LEMMA": "que"}, {"LEMMA": "je"}, {"LEMMA": "pouvoir"}, {"LEMMA": "faire"}, {"LEMMA": "pour"}, {"LEMMA": "vous"}],
            [{"LEMMA": "je"}, {"LEMMA": "aller"}, {"LEMMA": "s'occuper"}],
            [{"LEMMA": "laissez"}, {"LEMMA": "moi"}, {"LEMMA": {"IN": ["régler", "résoudre", "traiter"]}}],
            [{"LEMMA": "je"}, {"LEMMA": "vais"}, {"LEMMA": "m'assurer"}],
        ],
        "VERIFICATION_REQUEST": [
            [{"LEMMA": "pouvez"}, {"LEMMA": "vous"}, {"LEMMA": {"IN": ["confirmer", "vérifier"]}}, {"LEMMA": "votre"}],
            [{"LEMMA": "pour"}, {"LEMMA": "raison"}, {"LEMMA": "de"}, {"LEMMA": "sécurité"}],
            [{"LEMMA": "j'avoir"}, {"LEMMA": "besoin"}, {"LEMMA": "de"}, {"LEMMA": "vérifier"}],
            [{"LEMMA": "puis"}, {"LEMMA": "je"}, {"LEMMA": "avoir"}, {"LEMMA": "votre"}],
        ],
    },

    "es": {
        "THREAT": [
            [{"LEMMA": {"IN": ["querer", "necesitar", "planear"]}}, {"LEMMA": "cancelar"}],
            [{"LEMMA": {"IN": ["cambiar", "dejar", "mover"]}}, {"LEMMA": {"IN": ["proveedor", "competidor", "compañía"]}}],
            [{"LEMMA": {"IN": ["hablar", "escalar"]}}, {"LEMMA": {"IN": ["gerente", "supervisor", "director"]}}],
        ],
        "COMPLAINT": [
            [{"LEMMA": "esto"}, {"LEMMA": "ser"}, {"LEMMA": {"IN": ["inaceptable", "ridículo", "terrible", "horrible"]}}],
            [{"LEMMA": "estar"}, {"LEMMA": {"IN": ["insatisfecho", "frustrado", "enojado", "molesto", "decepcionado"]}}],
        ],
        "ACCEPTANCE": [
            [{"LEMMA": "eso"}, {"LEMMA": {"IN": ["funcionar", "estar"]}}],
            [{"LEMMA": {"IN": ["acuerdo", "perfecto", "bien", "excelente"]}}],
        ],
        "GREETING": [
            [{"LEMMA": {"IN": ["hola", "buenos", "buenas", "saludos"]}}],
            [{"LEMMA": "cómo"}, {"LEMMA": {"IN": ["estar", "ser"]}}, {"LEMMA": "usted"}],
        ],
        "CLOSING": [
            [{"LEMMA": {"IN": ["adiós", "hasta", "chao", "gracias"]}}],
            [{"LEMMA": "eso"}, {"LEMMA": "ser"}, {"LEMMA": "todo"}],
        ],
        "INQUIRY": [
            [{"LEMMA": "puede"}, {"LEMMA": "usted"}, {"LEMMA": "decirme"}],
            [{"LEMMA": "cómo"}, {"LEMMA": {"IN": ["puedo", "puede", "debo"]}}],
            [{"LEMMA": "cuándo"}, {"LEMMA": {"IN": ["será", "puede", "podré"]}}],
        ],
        "REQUEST": [
            [{"LEMMA": "podría"}, {"LEMMA": "usted"}, {"LEMMA": "por"}, {"LEMMA": "favor"}],
            [{"LEMMA": "me"}, {"LEMMA": "gustaría"}, {"LEMMA": {"IN": ["que", "recibir"]}}],
            [{"LEMMA": "por"}, {"LEMMA": "favor"}, {"LEMMA": {"IN": ["ayudar", "corregir", "verificar"]}}],
        ],
        "GUIDE": [
            [{"LEMMA": {"IN": ["puede", "podría"]}}, {"LEMMA": "explicarme"}],
            [{"LEMMA": "muéstreme"}, {"LEMMA": "cómo"}],
            [{"LEMMA": "qué"}, {"LEMMA": "debo"}, {"LEMMA": "hacer"}],
            [{"LEMMA": "cuáles"}, {"LEMMA": "son"}, {"LEMMA": "los"}, {"LEMMA": "siguiente"}, {"LEMMA": "paso"}],
        ],
        "CHURN": [
            [{"LEMMA": "cancelar"}, {"LEMMA": "mi"}, {"LEMMA": {"IN": ["cuenta", "suscripción", "contrato"]}}],
            [{"LEMMA": "quiero"}, {"LEMMA": "cancelar"}],
            [{"LEMMA": "cerrar"}, {"LEMMA": "mi"}, {"LEMMA": "cuenta"}],
        ],
        "RETENTION_RISK": [
            [{"LEMMA": "estoy"}, {"LEMMA": "pensar"}, {"LEMMA": "en"}, {"LEMMA": {"IN": ["cancelar", "salir", "cambiar"]}}],
            [{"LEMMA": "estoy"}, {"LEMMA": "reconsiderar"}],
            [{"LEMMA": "no"}, {"LEMMA": "valer"}, {"LEMMA": "la"}, {"LEMMA": "pena"}],
        ],
        "ONBOARDING": [
            [{"LEMMA": "acabo"}, {"LEMMA": "de"}, {"LEMMA": "registrarme"}],
            [{"LEMMA": "soy"}, {"LEMMA": "nuevo"}],
            [{"LEMMA": "primera"}, {"LEMMA": "vez"}],
        ],
        "EVALUATING": [
            [{"LEMMA": "déjame"}, {"LEMMA": "pensar"}],
            [{"LEMMA": "cuéntame"}, {"LEMMA": "más"}],
            [{"LEMMA": "vale"}, {"LEMMA": "la"}, {"LEMMA": "pena"}],
        ],
        "UNCERTAINTY": [
            [{"LEMMA": "quizás"}],
            [{"LEMMA": "posiblemente"}],
            [{"LEMMA": "depende"}],
        ],
        "DEFERMENT": [
            [{"LEMMA": "lo"}, {"LEMMA": "pensaré"}],
            [{"LEMMA": "no"}, {"LEMMA": "por"}, {"LEMMA": "ahora"}],
            [{"LEMMA": "necesito"}, {"LEMMA": "más"}, {"LEMMA": "tiempo"}],
        ],
        "EXPANSION": [
            [{"LEMMA": "mientras"}, {"LEMMA": "estamos"}, {"LEMMA": "en"}, {"LEMMA": "eso"}],
            [{"LEMMA": "hay"}, {"LEMMA": "algo"}, {"LEMMA": "más"}],
            [{"LEMMA": "relacionado"}, {"LEMMA": "con"}, {"LEMMA": "eso"}],
        ],
        "CONFUSION": [
            [{"LEMMA": "no"}, {"LEMMA": "entender"}],
            [{"LEMMA": "estar"}, {"LEMMA": "confundido"}],
            [{"LEMMA": "eso"}, {"LEMMA": "no"}, {"LEMMA": "tener"}, {"LEMMA": "sentido"}],
            [{"LEMMA": "qué"}, {"LEMMA": "querer"}, {"LEMMA": "decir"}],
        ],
        "APOLOGY": [
            [{"LEMMA": "lo"}, {"LEMMA": "sentir"}],
            [{"LEMMA": "me"}, {"LEMMA": "disculpar"}],
            [{"LEMMA": "mis"}, {"LEMMA": "disculpa"}],
            [{"LEMMA": "disculpe"}, {"LEMMA": "por"}, {"LEMMA": {"IN": ["inconveniente", "problema", "retraso", "molestia"]}}],
        ],
        "EMPATHY": [
            [{"LEMMA": "entender"}, {"LEMMA": "su"}, {"LEMMA": {"IN": ["frustración", "preocupación", "situación"]}}],
            [{"LEMMA": "eso"}, {"LEMMA": "deber"}, {"LEMMA": "ser"}, {"LEMMA": {"IN": ["frustrante", "difícil", "estresante"]}}],
            [{"LEMMA": "entender"}, {"LEMMA": "perfectamente"}],
            [{"LEMMA": "entender"}, {"LEMMA": "cómo"}, {"LEMMA": "sentir"}],
        ],
        "RESOLUTION_OFFER": [
            [{"LEMMA": "lo"}, {"LEMMA": "que"}, {"LEMMA": "poder"}, {"LEMMA": "hacer"}, {"LEMMA": "por"}, {"LEMMA": "usted"}],
            [{"LEMMA": "voy"}, {"LEMMA": "a"}, {"LEMMA": "ocuparme"}],
            [{"LEMMA": "déjame"}, {"LEMMA": {"IN": ["resolver", "solucionar", "gestionar"]}}],
            [{"LEMMA": "voy"}, {"LEMMA": "a"}, {"LEMMA": {"IN": ["resolver", "solucionar", "arreglar"]}}],
        ],
        "VERIFICATION_REQUEST": [
            [{"LEMMA": "puede"}, {"LEMMA": {"IN": ["confirmar", "verificar"]}}, {"LEMMA": "su"}],
            [{"LEMMA": "por"}, {"LEMMA": "razón"}, {"LEMMA": "de"}, {"LEMMA": "seguridad"}],
            [{"LEMMA": "necesitar"}, {"LEMMA": "verificar"}, {"LEMMA": "su"}],
            [{"LEMMA": "puede"}, {"LEMMA": "proporcionar"}, {"LEMMA": "su"}],
        ],
    },

    "pt": {
        "THREAT": [
            [{"LEMMA": {"IN": ["querer", "precisar", "planejar"]}}, {"LEMMA": "cancelar"}],
            [{"LEMMA": {"IN": ["mudar", "sair", "trocar"]}}, {"LEMMA": {"IN": ["fornecedor", "operador", "empresa"]}}],
            [{"LEMMA": {"IN": ["falar", "escalar"]}}, {"LEMMA": {"IN": ["gerente", "supervisor", "diretor"]}}],
        ],
        "COMPLAINT": [
            [{"LEMMA": "isso"}, {"LEMMA": "ser"}, {"LEMMA": {"IN": ["inaceitável", "ridículo", "terrível", "horrível"]}}],
            [{"LEMMA": "estar"}, {"LEMMA": {"IN": ["insatisfeito", "frustrado", "irritado", "chateado", "decepcionado"]}}],
        ],
        "ACCEPTANCE": [
            [{"LEMMA": "isso"}, {"LEMMA": {"IN": ["funcionar", "estar"]}}],
            [{"LEMMA": {"IN": ["acordo", "perfeito", "bem", "ótimo", "excelente"]}}],
        ],
        "GREETING": [
            [{"LEMMA": {"IN": ["olá", "oi", "bom", "boa", "saudações"]}}],
            [{"LEMMA": "como"}, {"LEMMA": {"IN": ["estar", "vai"]}}, {"LEMMA": "você"}],
        ],
        "CLOSING": [
            [{"LEMMA": {"IN": ["tchau", "adeus", "até", "obrigado"]}}],
            [{"LEMMA": "isso"}, {"LEMMA": "ser"}, {"LEMMA": "tudo"}],
        ],
        "INQUIRY": [
            [{"LEMMA": "pode"}, {"LEMMA": "me"}, {"LEMMA": "dizer"}],
            [{"LEMMA": "como"}, {"LEMMA": {"IN": ["posso", "pode", "devo"]}}],
            [{"LEMMA": "quando"}, {"LEMMA": {"IN": ["será", "pode", "poderei"]}}],
        ],
        "REQUEST": [
            [{"LEMMA": "poderia"}, {"LEMMA": "você"}, {"LEMMA": "por"}, {"LEMMA": "favor"}],
            [{"LEMMA": "eu"}, {"LEMMA": "gostaria"}, {"LEMMA": {"IN": ["que", "de"]}}],
            [{"LEMMA": "por"}, {"LEMMA": "favor"}, {"LEMMA": {"IN": ["ajudar", "corrigir", "verificar"]}}],
        ],
        "GUIDE": [
            [{"LEMMA": {"IN": ["pode", "poderia"]}}, {"LEMMA": "me"}, {"LEMMA": "explicar"}],
            [{"LEMMA": "me"}, {"LEMMA": "mostre"}, {"LEMMA": "como"}],
            [{"LEMMA": "o"}, {"LEMMA": "que"}, {"LEMMA": "devo"}, {"LEMMA": "fazer"}],
            [{"LEMMA": "quais"}, {"LEMMA": "são"}, {"LEMMA": "os"}, {"LEMMA": "próximo"}, {"LEMMA": "passo"}],
        ],
        "CHURN": [
            [{"LEMMA": "cancelar"}, {"LEMMA": "minha"}, {"LEMMA": {"IN": ["conta", "assinatura", "contrato"]}}],
            [{"LEMMA": "quero"}, {"LEMMA": "cancelar"}],
            [{"LEMMA": "fechar"}, {"LEMMA": "minha"}, {"LEMMA": "conta"}],
        ],
        "RETENTION_RISK": [
            [{"LEMMA": "estou"}, {"LEMMA": "pensar"}, {"LEMMA": "em"}, {"LEMMA": {"IN": ["cancelar", "sair", "mudar"]}}],
            [{"LEMMA": "estou"}, {"LEMMA": "reconsiderar"}],
            [{"LEMMA": "não"}, {"LEMMA": "vale"}, {"LEMMA": "a"}, {"LEMMA": "pena"}],
        ],
        "ONBOARDING": [
            [{"LEMMA": "acabei"}, {"LEMMA": "de"}, {"LEMMA": "me"}, {"LEMMA": "cadastrar"}],
            [{"LEMMA": "sou"}, {"LEMMA": "novo"}],
            [{"LEMMA": "primeira"}, {"LEMMA": "vez"}],
        ],
        "EVALUATING": [
            [{"LEMMA": "deixa"}, {"LEMMA": "eu"}, {"LEMMA": "pensar"}],
            [{"LEMMA": "me"}, {"LEMMA": "conta"}, {"LEMMA": "mais"}],
            [{"LEMMA": "vale"}, {"LEMMA": "a"}, {"LEMMA": "pena"}],
        ],
        "UNCERTAINTY": [
            [{"LEMMA": "talvez"}],
            [{"LEMMA": "possivelmente"}],
            [{"LEMMA": "depende"}],
        ],
        "DEFERMENT": [
            [{"LEMMA": "vou"}, {"LEMMA": "pensar"}],
            [{"LEMMA": "não"}, {"LEMMA": "agora"}],
            [{"LEMMA": "preciso"}, {"LEMMA": "de"}, {"LEMMA": "mais"}, {"LEMMA": "tempo"}],
        ],
        "EXPANSION": [
            [{"LEMMA": "enquanto"}, {"LEMMA": "estamos"}, {"LEMMA": "nisso"}],
            [{"LEMMA": "há"}, {"LEMMA": "outra"}, {"LEMMA": "coisa"}],
            [{"LEMMA": "relacionado"}, {"LEMMA": "a"}, {"LEMMA": "isso"}],
        ],
        "CONFUSION": [
            [{"LEMMA": "não"}, {"LEMMA": "entender"}],
            [{"LEMMA": "estar"}, {"LEMMA": "confuso"}],
            [{"LEMMA": "isso"}, {"LEMMA": "não"}, {"LEMMA": "fazer"}, {"LEMMA": "sentido"}],
            [{"LEMMA": "o"}, {"LEMMA": "que"}, {"LEMMA": "querer"}, {"LEMMA": "dizer"}],
        ],
        "APOLOGY": [
            [{"LEMMA": "sinto"}, {"LEMMA": "muito"}],
            [{"LEMMA": "me"}, {"LEMMA": "desculpar"}],
            [{"LEMMA": "minhas"}, {"LEMMA": "desculpa"}],
            [{"LEMMA": "desculpe"}, {"LEMMA": "pelo"}, {"LEMMA": {"IN": ["inconveniente", "problema", "atraso", "transtorno"]}}],
        ],
        "EMPATHY": [
            [{"LEMMA": "entender"}, {"LEMMA": "sua"}, {"LEMMA": {"IN": ["frustração", "preocupação", "situação"]}}],
            [{"LEMMA": "isso"}, {"LEMMA": "dever"}, {"LEMMA": "ser"}, {"LEMMA": {"IN": ["frustrante", "difícil", "estressante"]}}],
            [{"LEMMA": "entender"}, {"LEMMA": "completamente"}],
            [{"LEMMA": "entender"}, {"LEMMA": "como"}, {"LEMMA": "sentir"}],
        ],
        "RESOLUTION_OFFER": [
            [{"LEMMA": "o"}, {"LEMMA": "que"}, {"LEMMA": "poder"}, {"LEMMA": "fazer"}, {"LEMMA": "por"}, {"LEMMA": "você"}],
            [{"LEMMA": "vou"}, {"LEMMA": "cuidar"}, {"LEMMA": "disso"}],
            [{"LEMMA": "deixa"}, {"LEMMA": "eu"}, {"LEMMA": {"IN": ["resolver", "solucionar", "tratar"]}}],
            [{"LEMMA": "vou"}, {"LEMMA": {"IN": ["resolver", "solucionar", "corrigir"]}}],
        ],
        "VERIFICATION_REQUEST": [
            [{"LEMMA": "pode"}, {"LEMMA": {"IN": ["confirmar", "verificar"]}}, {"LEMMA": "seu"}],
            [{"LEMMA": "por"}, {"LEMMA": "razão"}, {"LEMMA": "de"}, {"LEMMA": "segurança"}],
            [{"LEMMA": "preciso"}, {"LEMMA": "verificar"}, {"LEMMA": "seu"}],
            [{"LEMMA": "pode"}, {"LEMMA": "fornecer"}, {"LEMMA": "seu"}],
        ],
    },
}
