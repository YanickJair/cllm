from typing import Optional

from src.core.vocabulary import Vocabulary


class TranscriptVocabulary(Vocabulary):
    DOMAIN_TOKENS = {
        "SUPPORT": [
            "support", "customer service", "helpdesk", "technical support",
            "assistance", "customer care", "agent support", "troubleshooting help",
            "product support", "after-sales service", "client assistance"
        ],
        "SALES": [
            "sales", "sales call", "prospecting", "upsell", "cross-sell",
            "lead generation", "cold call", "renewal", "account expansion",
            "upgrade offer", "product recommendation", "quote", "proposal", 
            "conversion", "demo request", "subscription plan", "sales pitch"
        ],
        "BILLING": [
            "billing", "payment", "account", "invoice", "charges",
            "refund", "credit", "billing cycle", "subscription fee",
            "overcharge", "payment issue", "card declined", "auto-pay",
            "invoice dispute", "account balance", "billing statement"
        ],
        "TECHNICAL": [
            "technical", "troubleshooting", "debugging", "diagnostics", "configuration",
            "setup", "installation", "connectivity", "error code", "system issue",
            "hardware", "software", "device issue", "network", "firmware", "signal",
            "technical malfunction", "outage", "glitch", "performance issue"
        ],
        "ACCOUNT_MANAGEMENT": [
            "account", "login", "credentials", "password", "access", 
            "account setup", "reset password", "update profile", "manage account",
            "change email", "verify identity", "account locked", "security question"
        ],
        "RETENTION": [
            "retention", "cancellation prevention", "save offer", "customer churn",
            "win-back", "keep customer", "cancel request", "retention strategy",
            "save deal", "renew contract", "loyalty retention"
        ],
        "FEEDBACK": [
            "feedback", "survey", "review", "rating", "complaint", "suggestion",
            "customer satisfaction", "nps", "experience feedback", "comment", "survey response"
        ],
        "LOGISTICS": [
            "delivery", "shipping", "order", "tracking", "delay", 
            "warehouse", "carrier", "package", "shipment", "order status", 
            "fulfillment", "lost item", "damaged delivery"
        ],
        "PRODUCT_INFO": [
            "product", "features", "specifications", "compatibility", "availability",
            "price", "model", "version", "stock", "details", "manual", "how it works"
        ],
        "RETURNS": [
            "return", "exchange", "replacement", "return policy", "rma",
            "refund process", "send back", "return label", "defective item"
        ],
        "MARKETING": [
            "promotion", "campaign", "advertising", "email blast", "offer",
            "marketing campaign", "discount", "social media", "event", "lead nurturing"
        ],
        "COMPLIANCE": [
            "privacy", "security", "data protection", "gdpr", "policy", 
            "terms of service", "legal", "compliance", "authorization", "verification"
        ]
    }

    CALL_TOKENS = {
        "CALL": {
            "type": [
                "SUPPORT", "SALES", "BILLING", "TECHNICAL", "RETENTION", 
                "LOGISTICS", "ACCOUNT_MANAGEMENT", "FEEDBACK", "RETURNS"
            ],
            "channel": [
                "VOICE", "CHAT", "EMAIL", "SOCIAL", "SMS", "VIDEO", "PORTAL"
            ],
            "duration": int,  # minutes
            "agent": str,
            "customer": str
        }
    }
    ISSUE_TOKENS = {
        # Connectivity & Technical Issues
        "INTERNET_OUTAGE": ["internet", "connection", "outage", "dropping", "disconnect", "no signal"],
        "SLOW_INTERNET": ["slow", "lagging", "buffering", "low speed", "latency"],
        "WIFI_ISSUE": ["wifi", "router", "modem", "network", "ssid"],
        "DEVICE_NOT_SYNCING": ["sync", "pairing", "bluetooth", "connect device"],
        "APP_CRASH": ["app crash", "application stopped", "not opening", "bug", "freeze"],
        "SOFTWARE_UPDATE_ERROR": ["update failed", "version issue", "firmware", "patch"],
        "BROWSER_COMPATIBILITY": ["browser", "chrome", "firefox", "safari", "edge", "compatibility"],
        "ACCOUNT_TIMEOUT": ["session expired", "timeout", "inactive", "auto logout"],
        "SERVER_DOWN": ["server", "system down", "maintenance", "unavailable"],
        "LOGIN_FAILURE": ["login", "password", "access", "locked", "credentials", "reset"],
        "AUTHENTICATION_ERROR": ["2fa", "otp", "verification code", "auth", "security check"],
        "EMAIL_NOT_RECEIVED": ["email not received", "no email", "spam", "missing email"],

        # Billing & Payments
        "BILLING_DISPUTE": ["billing", "charge", "overcharge", "refund", "incorrect amount"],
        "PAYMENT_FAILED": ["payment failed", "declined", "error payment", "transaction failed"],
        "DUPLICATE_CHARGE": ["charged twice", "duplicate payment", "double billing"],
        "MISSING_REFUND": ["refund not received", "pending refund", "waiting for refund"],
        "INVALID_COUPON": ["coupon not working", "promo code invalid", "discount not applied"],
        "SUBSCRIPTION_CANCELLATION": ["cancel subscription", "terminate plan", "stop renewal"],
        "PLAN_UPGRADE": ["upgrade plan", "change plan", "higher tier"],
        "PLAN_DOWNGRADE": ["downgrade", "reduce plan", "switch to basic"],
        "INVOICE_REQUEST": ["invoice", "receipt", "billing statement"],
        "CREDIT_CARD_UPDATE": ["update card", "expired card", "new card details"],
        "AUTO_RENEWAL_ISSUE": ["auto renewal", "auto charge", "subscription renew"],

        # Orders & Shipping
        "DELIVERY_DELAY": ["delivery", "shipping", "delayed", "late", "not arrived"],
        "LOST_PACKAGE": ["lost package", "missing order", "did not receive"],
        "DAMAGED_PACKAGE": ["damaged", "broken item", "crushed", "leaking"],
        "WRONG_ITEM": ["wrong item", "incorrect order", "wrong product"],
        "RETURN_REQUEST": ["return item", "send back", "return policy"],
        "EXCHANGE_REQUEST": ["exchange", "replacement", "swap product"],
        "ORDER_CANCELLATION": ["cancel order", "stop shipment", "undo purchase"],
        "TRACKING_ISSUE": ["tracking", "status update", "shipment id"],
        "CUSTOMS_HOLD": ["customs", "held", "import fee", "clearance delay"],

        # Product & Hardware
        "PRODUCT_DEFECT": ["broken", "defect", "damaged", "not working", "faulty"],
        "PRODUCT_NOT_RECEIVED": ["not received", "missing product", "no delivery"],
        "INSTALLATION_ISSUE": ["install", "setup", "installation", "configuration"],
        "COMPATIBILITY_ISSUE": ["compatible", "supported device", "requirements"],
        "FEATURE_NOT_WORKING": ["feature not working", "function missing", "option greyed out"],
        "OVERHEATING_DEVICE": ["overheating", "too hot", "temperature issue"],
        "BATTERY_PROBLEM": ["battery drain", "charging issue", "not charging", "low battery"],
        "SCREEN_ISSUE": ["display", "screen flicker", "dead pixels", "black screen"],
        "AUDIO_PROBLEM": ["no sound", "audio issue", "mic not working", "speaker"],
        "CAMERA_PROBLEM": ["camera", "photo blurry", "not opening camera"],

        # Account Management
        "ACCOUNT_LOCKED": ["locked account", "cannot access", "suspended"],
        "ACCOUNT_HACKED": ["unauthorized access", "account compromised", "security breach"],
        "PROFILE_UPDATE": ["update info", "change name", "edit address", "email update"],
        "DATA_PRIVACY_REQUEST": ["gdpr", "data removal", "delete account", "privacy"],
        "ACCOUNT_CREATION_ERROR": ["sign up", "create account", "registration failed"],
        "MULTIPLE_ACCOUNTS": ["duplicate accounts", "merge accounts", "multiple profiles"],

        # Customer Service
        "RUDE_AGENT": ["rude", "unhelpful", "bad service", "agent behavior"],
        "LONG_WAIT_TIME": ["waiting", "on hold", "queue too long", "delay response"],
        "CALL_DISCONNECTED": ["call dropped", "cut off", "disconnect call"],
        "NO_CALLBACK": ["no callback", "promised call", "didn't call back"],
        "INCORRECT_INFO": ["wrong info", "misinformed", "wrong instructions"],
        "ESCALATION_REQUEST": ["supervisor", "manager", "escalate", "complaint"],

        # Returns & Refunds
        "RETURN_REFUSED": ["return denied", "return rejected"],
        "EXPIRED_RETURN_WINDOW": ["return window closed", "too late to return"],
        "REFUND_DELAY": ["refund delayed", "refund taking too long"],

        # Logistics & Fulfillment
        "ADDRESS_CHANGE": ["change address", "wrong address", "update address"],
        "WAREHOUSE_DELAY": ["warehouse", "processing delay", "fulfillment issue"],
        "OUT_OF_STOCK": ["out of stock", "backorder", "unavailable product"],
        "PREORDER_DELAY": ["preorder delay", "release postponed"],

        # SaaS / Software Issues
        "LICENSE_ERROR": ["license", "activation key", "invalid key"],
        "ACCOUNT_SYNC_ERROR": ["sync issue", "data not syncing", "integration failed"],
        "API_ERROR": ["api", "endpoint", "request failed", "response error"],
        "REPORTING_ISSUE": ["report", "dashboard", "analytics issue"],
        "DATA_EXPORT_ERROR": ["export failed", "download csv", "data export"],
        "EMAIL_INTEGRATION_ISSUE": ["email integration", "inbox sync", "mail connector"],

        # Banking & Financial
        "CARD_DECLINED": ["card declined", "transaction failed", "payment rejected"],
        "UNAUTHORIZED_TRANSACTION": ["fraud", "unauthorized", "unknown charge"],
        "MISSING_STATEMENT": ["bank statement", "monthly report", "transaction history"],
        "ACCOUNT_FREEZE": ["frozen account", "hold", "restricted"],
        "KYC_VERIFICATION": ["kyc", "id verification", "identity document"],

        # Insurance & Claims
        "CLAIM_REJECTION": ["claim rejected", "denied", "refused"],
        "CLAIM_STATUS": ["claim status", "pending claim", "check claim"],
        "POLICY_RENEWAL": ["renew policy", "extend coverage", "policy expiry"],
        "PREMIUM_PAYMENT_ISSUE": ["premium", "payment failed", "late payment"],

        # Utilities / Telecom
        "POWER_OUTAGE": ["power outage", "no electricity", "blackout"],
        "MOBILE_DATA_ISSUE": ["mobile data", "4g", "5g", "no signal"],
        "SIM_NOT_WORKING": ["sim card", "no service", "invalid sim"],
        "VOICEMAIL_PROBLEM": ["voicemail", "messages missing", "not recording"],
        "ROAMING_ISSUE": ["roaming", "international charges", "no service abroad"],

        # E-commerce / Subscription
        "COUPON_NOT_APPLIED": ["promo code", "discount not applied"],
        "GIFT_CARD_ISSUE": ["gift card", "voucher not working"],
        "LOYALTY_POINTS_MISSING": ["points missing", "rewards not added"],
        "SUBSCRIPTION_RENEWAL_ISSUE": ["auto renew", "renewal failed"],

        # Support Process
        "CASE_NOT_UPDATED": ["no update", "status unknown", "ticket pending"],
        "DUPLICATE_TICKET": ["duplicate ticket", "multiple cases"],
        "INCORRECT_ESCALATION": ["wrong team", "misrouted case"],

        # Miscellaneous
        "FEEDBACK_SUBMISSION": ["feedback", "review", "survey"],
        "ACCESSIBILITY_ISSUE": ["screen reader", "contrast", "accessibility"],
        "LANGUAGE_BARRIER": ["language issue", "translation", "not understood"],
        "TIMEZONE_CONFUSION": ["timezone", "wrong time", "appointment mix-up"],
        "APPOINTMENT_RESCHEDULE": ["reschedule", "change appointment", "meeting time"],
        "DOCUMENT_UPLOAD_ERROR": ["upload failed", "file too large", "unsupported format"]
    }

    ACTION_TOKENS = {
        "TROUBLESHOOT": [
            "troubleshoot", "diagnose", "check", "test", "inspect", "analyze", "investigate",
            "look into", "run diagnostics", "perform a check", "verify", "review", "run a test",
            "reset", "reboot", "restart", "ping", "run a line test", "try some steps", 
            "test connection", "analyze logs", "simulate issue", "debug", "identify the cause",
            "look for root cause", "follow troubleshooting steps", "perform remote check",
            "attempt to fix", "replicate the issue", "clear cache", "flush DNS", 
            "factory reset", "reconfigure", "perform maintenance", "try restarting the device",
            "check signal", "inspect settings", "perform manual test"
        ],

        "ESCALATE": [
            "escalate", "transfer", "forward", "send to tier 2", "pass this along",
            "hand off", "bring to a supervisor", "submit to escalation", "report up", 
            "send to higher support", "loop in", "raise to", "flag for review",
            "submit a ticket", "open escalation case", "send to escalation team",
            "escalate to engineering", "pass to technical team", "route to correct department",
            "handover to next level", "get my supervisor involved", "submit escalation form",
            "forward to specialist", "submit for further review"
        ],

        "SCHEDULE": [
            "schedule", "appointment", "book", "set up", "arrange", "reserve", 
            "organize", "reschedule", "confirm time", "slot in", "plan", "assign",
            "schedule a technician", "book a call", "set up a visit", "book an appointment",
            "confirm availability", "schedule maintenance", "schedule callback",
            "book technician visit", "schedule installation", "reschedule visit",
            "confirm appointment time", "set a date", "create booking", 
            "schedule repair", "arrange delivery", "set appointment window"
        ],

        "REFUND": [
            "refund", "credit", "reimburse", "return money", "issue a refund",
            "send compensation", "process a credit", "reverse charge", "apply adjustment",
            "offer goodwill credit", "partial refund", "full refund", "money back",
            "issue credit note", "apply balance", "refund request", "initiate refund process",
            "reverse payment", "compensate", "credit customer account", 
            "adjust invoice", "refund difference", "apply billing correction"
        ],

        "REPLACE": [
            "replace", "exchange", "substitute", "swap", "send a new one",
            "ship replacement", "issue replacement", "resend", "send another", 
            "replace unit", "replacement request", "dispatch new product", 
            "send replacement item", "arrange exchange", "exchange request",
            "replace defective unit", "ship replacement device", "send replacement package",
            "process replacement", "replacement order", "replace under warranty",
            "initiate RMA", "replace broken item", "replacement shipment"
        ],

        "CANCEL": [
            "cancel", "terminate", "stop service", "close account", "discontinue", 
            "end subscription", "opt out", "turn off", "deactivate", "cease service",
            "cancel my order", "void transaction", "cancel appointment", "stop renewal",
            "remove service", "cancel request", "opt out of plan", "terminate contract",
            "unsubscribe", "end membership", "disable feature", "cancel policy"
        ],

        "UPDATE_INFO": [
            "update", "change", "modify", "edit", "correct", "fix details", 
            "revise", "adjust", "amend", "change address", "update payment", 
            "change plan", "update email", "update contact info", "correct name",
            "update billing info", "update card details", "change account settings",
            "update phone number", "change password", "update preferences",
            "change subscription", "revise account details", "edit information"
        ],

        "FOLLOW_UP": [
            "follow up", "check status", "call back", "get an update", 
            "see progress", "reconnect", "touch base", "ask for update",
            "reach back", "follow through", "request update", "ask for progress",
            "call again", "follow up later", "request feedback", 
            "check on request", "follow up on issue", "send reminder", 
            "status check", "request case update"
        ],

        "VERIFY": [
            "verify", "confirm", "validate", "double check", "authenticate", 
            "ensure", "make sure", "check identity", "confirm details",
            "verify account", "confirm customer information", "validate credentials",
            "security check", "confirm name and address", "verify payment method",
            "identity verification", "confirm authorization", "confirm ownership"
        ],

        "OFFER_DISCOUNT": [
            "discount", "offer credit", "apply promotion", "give coupon",
            "provide incentive", "price adjustment", "loyalty offer",
            "apply discount", "special offer", "apply promo code",
            "goodwill gesture", "courtesy credit", "offer price reduction",
            "give rebate", "apply loyalty points", "limited-time offer",
            "apply customer retention discount", "waive fee", "apply voucher"
        ],

        "EDUCATE": [
            "explain", "teach", "guide", "walk through", "show how", 
            "provide instructions", "help understand", "clarify steps",
            "give directions", "demonstrate", "walk the customer through",
            "explain policy", "explain process", "help them learn",
            "guide through setup", "teach them to use", "walk through solution"
        ],

        "DOCUMENT": [
            "document", "note", "record", "log", "write down", "add to notes",
            "update ticket", "record case details", "add comment", 
            "summarize", "enter information", "attach to record", 
            "log findings", "document resolution", "add to CRM"
        ],

        "NOTIFY": [
            "notify", "inform", "let know", "update", "alert", "send message", 
            "send email", "text customer", "notify via SMS", "contact customer",
            "notify of change", "advise", "update customer", "send confirmation",
            "notify about status", "send notification"
        ],

        "APPROVE": [
            "approve", "authorize", "confirm", "grant", "greenlight", 
            "validate approval", "give permission", "allow", "sanction", 
            "confirm authorization", "approve request", "authorize refund"
        ],

        "DENY": [
            "deny", "reject", "decline", "not approve", "refuse", 
            "unable to approve", "deny request", "not possible", 
            "reject claim", "decline application"
        ]
    }


    RESOLUTION_TOKENS = {
        "RESOLVED": [
            "resolved", "fixed", "solved", "sorted", "taken care of", "completed",
            "all set", "issue cleared", "working now", "restored", "addressed",
            "done", "problem gone", "handled", "successfully resolved"
        ],
        "PENDING": [
            "pending", "waiting", "scheduled", "in progress", "under review",
            "being worked on", "queued", "awaiting response", "in process",
            "to be done", "not yet completed", "next step", "work order created"
        ],
        "ESCALATED": [
            "escalated", "transferred", "sent to higher level", "moved to supervisor",
            "forwarded", "raised", "handed off", "passed on", "under escalation",
            "sent to management", "escalation ticket created"
        ],
        "UNRESOLVED": [
            "unresolved", "ongoing", "open", "still having issues", "not fixed",
            "still broken", "no solution", "not working", "still the same", 
            "didn't help", "unsolved", "still waiting", "not yet resolved"
        ],
        "CANCELLED": [
            "cancelled", "closed", "terminated", "stopped", "voided", 
            "withdrawn", "discontinued", "dropped", "closed out"
        ]
    }

    SENTIMENT_TOKENS = {
        "FRUSTRATED": [
            "frustrated", "annoyed", "upset", "disappointed", "irritated",
            "fed up", "tired of this", "this is ridiculous", "this keeps happening",
            "I’ve had enough", "getting frustrated", "really annoyed"
        ],
        "ANGRY": [
            "angry", "furious", "mad", "outraged", "furious about this",
            "this is unacceptable", "I’m done", "I want to speak to a manager",
            "this is the last straw", "you guys messed up", "very angry"
        ],
        "SATISFIED": [
            "satisfied", "happy", "pleased", "grateful", "thank you so much",
            "appreciate your help", "that’s great", "awesome", "perfect",
            "works now", "you’ve been very helpful", "excellent service"
        ],
        "NEUTRAL": [
            "neutral", "okay", "fine", "alright", "that’s fine", "no problem",
            "cool", "okay thanks", "that works", "understood", "I see"
        ],
        "CONFUSED": [
            "confused", "unclear", "unsure", "don’t understand", "not sure what’s happening",
            "what do you mean", "I don’t get it", "can you explain", "lost me there",
            "this doesn’t make sense", "what’s going on"
        ],
        "RELIEVED": [
            "relieved", "that’s a relief", "glad to hear that", "phew", 
            "that’s good news", "thank goodness", "finally", "I feel better now"
        ],
        "APOLOGETIC": [
            "sorry", "apologies", "my mistake", "I didn’t realize", "I see now",
            "thanks for clarifying", "my bad"
        ]
    }

    FREQUENCY_TOKENS = {
        "ONCE": [
            "once", "one time", "just once", "happened once", 
            "only once", "the first time", "single occurrence"
        ],
        "TWICE": [
            "twice", "two times", "a couple of times", "happened twice", 
            "second time", "this happened again", "a few days apart"
        ],
        "OCCASIONAL": [
            "occasional", "sometimes", "every now and then", "from time to time",
            "off and on", "now and then", "once in a while", "sporadic", 
            "periodically", "randomly", "infrequent", "here and there"
        ],
        "INTERMITTENT": [
            "intermittent", "on and off", "keeps happening", "comes and goes",
            "off and on", "drops in and out", "flaky", "unreliable connection",
            "interrupted", "happens randomly", "inconsistent", "cutting in and out"
        ],
        "DAILY": [
            "daily", "every day", "all day", "each day", "day after day", 
            "every single day", "once a day", "throughout the day", 
            "happens daily", "each morning", "each evening"
        ],
        "WEEKLY": [
            "weekly", "every week", "each week", "once a week", 
            "per week", "every weekend", "every few days", "about once a week"
        ],
        "MONTHLY": [
            "monthly", "every month", "each month", "once a month", 
            "per month", "monthly basis", "around the same time each month"
        ],
        "CONSTANT": [
            "constant", "always", "continuously", "constantly", "nonstop", 
            "non-stop", "repeatedly", "keeps happening", "ongoing", 
            "all the time", "24/7", "every minute", "every second", 
            "never stops", "never ending", "persistent", "happening constantly"
        ],
        "RECURRING": [
            "recurring", "repeatedly", "keeps coming back", "comes up again",
            "happens again", "still happening", "recurs", "same issue again", 
            "problem returned", "happened before", "back again"
        ],
        "RARE": [
            "rare", "rarely", "hardly ever", "seldom", "almost never",
            "once in a blue moon", "barely happens", "not often", "unusual"
        ]
    }


    @classmethod
    def get_issue_token(cls, text: str) -> Optional[str]:
        """Find issue type from text"""
        text_lower = text.lower()
        for issue_type, keywords in cls.ISSUE_TOKENS.items():
            if any(keyword in text_lower for keyword in keywords):
                return issue_type
        return None

    @classmethod
    def get_action_token(cls, text: str) -> Optional[str]:
        """Find action type from text"""
        text_lower = text.lower()
        for action_type, keywords in cls.ACTION_TOKENS.items():
            if any(keyword in text_lower for keyword in keywords):
                return action_type
        return None

    @classmethod
    def get_sentiment_token(cls, text: str) -> Optional[str]:
        """Find sentiment from text"""
        text_lower = text.lower()
        for sentiment, keywords in cls.SENTIMENT_TOKENS.items():
            if any(keyword in text_lower for keyword in keywords):
                return sentiment
        return None