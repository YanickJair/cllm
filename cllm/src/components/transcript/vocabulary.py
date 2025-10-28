from typing import Optional

from src.core.vocabulary import Vocabulary


class TranscriptVocabulary(Vocabulary):
    DOMAIN_TOKENS = {
        "SUPPORT": ["support", "customer service", "helpdesk", "technical support"],
        "SALES": ["sales", "sales call", "prospecting"],
        "BILLING": ["billing", "payment", "account"],
        "TECHNICAL": ["technical", "troubleshooting", "debugging"]
    }
    CALL_TOKENS = {
        "CALL": {
            "type": ["SUPPORT", "SALES", "BILLING"],
            "channel": ["VOICE", "CHAT", "EMAIL"],
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
        "TROUBLESHOOT": ["troubleshoot", "diagnose", "check", "test"],
        "ESCALATE": ["escalate", "transfer", "forward"],
        "SCHEDULE": ["schedule", "appointment", "book"],
        "REFUND": ["refund", "credit", "reimburse"],
        "REPLACE": ["replace", "exchange", "substitute"]
    }
    RESOLUTION_TOKENS = {
        "RESOLVED": ["resolved", "fixed", "solved"],
        "PENDING": ["pending", "waiting", "scheduled"],
        "ESCALATED": ["escalated", "transferred"],
        "UNRESOLVED": ["unresolved", "ongoing", "open"]
    }
    SENTIMENT_TOKENS = {
        "FRUSTRATED": ["frustrated", "annoyed", "upset"],
        "ANGRY": ["angry", "furious", "mad"],
        "SATISFIED": ["satisfied", "happy", "pleased"],
        "NEUTRAL": ["neutral", "okay", "fine"],
        "CONFUSED": ["confused", "unclear", "uncertain"]
    }
    FREQUENCY_TOKENS = {
        "ONCE": ["once", "one time"],
        "DAILY": ["daily", "every day"],
        "WEEKLY": ["weekly", "every week"],
        "INTERMITTENT": ["intermittent", "sometimes", "occasionally"],
        "CONSTANT": ["constant", "always", "continuously"]
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