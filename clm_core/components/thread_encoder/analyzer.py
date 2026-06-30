import re
from typing import Annotated, Optional

from spacy.language import Language
from annotated_doc import Doc

from clm_core.components.intent_detector import IntentDetector
from clm_core.components.target_extractor import TargetExtractor
from clm_core.dictionary.en.patterns import (
    CALL_TYPE_TO_DOMAIN,
    CUSTOMER_INTENT_KEYWORDS,
    EXPLICIT_AGENT_ACTION_PHRASES,
    ISSUE_TO_DOMAIN,
    ISSUE_TO_INTENT,
    ISSUE_TO_SERVICE,
    SYSTEM_ACTION_KEYWORDS,
    TRIGGER_CAUSE_KEYWORDS,
)
from clm_core.utils.parser_rules import BaseRules
from clm_core.utils.vocabulary import BaseVocabulary

from . import (
    Action,
    CallInfo,
    ConversationTimeline,
    CustomerProfile,
    Issue,
    MonetaryAmount,
    PromiseCommitment,
    RefundReference,
    Resolution,
    ResolutionState,
    TimelineEvent,
    TranscriptAnalysis,
    Turn,
)
from .patterns import TranscriptPatterns
from .utils.named_entity import EntityExtractor
from .utils.sentiment_analyzer import SentimentAnalyzer
from .utils.temporal_analyzer import TemporalAnalyzer
from .vocabulary import TranscriptVocabulary

_DEFAULT_REDACTION_PATTERN = (
    r"\[\*+REDACTED\*+\]|\*{3,}|\[REDACTED\]|<redacted>|XXX+|\[PII\]"
)


class TranscriptAnalyzer:
    def __init__(
        self,
        nlp: Annotated[
            Language, Doc("Loaded spaCy language model used for NLP processing.")
        ],
        vocab: Annotated[
            BaseVocabulary,
            Doc("Vocabulary providing default keyword sets and token maps."),
        ],
        rules: Annotated[BaseRules, Doc("Parser rules used by the target extractor.")],
        patterns: Annotated[
            TranscriptPatterns,
            Doc("Language-specific patterns and keyword maps for extraction."),
        ],
        redaction_pattern: Annotated[
            Optional[str],
            Doc(
                "Regex pattern for detecting redacted fields. Defaults to the built-in pattern when None."
            ),
        ] = None,
    ):
        self.nlp = nlp
        self.patterns = patterns
        self.vocab = TranscriptVocabulary()
        self._redaction_pattern = redaction_pattern or _DEFAULT_REDACTION_PATTERN
        self.intent_detector = IntentDetector(nlp=nlp, vocab=vocab)
        self.target_extractor = TargetExtractor(nlp, vocab=vocab, rules=rules)
        self.temporal_extractor = TemporalAnalyzer(
            nlp=nlp,
            day_names=patterns.day_names,
            word_to_num=patterns.word_to_num,
        )
        self.sentiment_analyzer = SentimentAnalyzer(
            emotion_keywords=patterns.emotion_keywords,
        )
        self.entity_extractor = EntityExtractor(
            nlp=nlp,
            ner_domain_patterns=patterns.ner_domain_patterns,
        )

        self._issue_type_index = self._build_keyword_index(patterns.issue_type_keywords)
        self._severity_index = self._build_keyword_index(patterns.severity_keywords)
        self._resolution_index = self._build_keyword_index(patterns.resolution_keywords)
        self._billing_cause_index = self._build_keyword_index(
            patterns.billing_cause_keywords
        )
        self._technical_issue_index = self._build_keyword_index(
            patterns.technical_issue_map
        )
        self._issue_confirmation_index = self._build_keyword_index(
            patterns.issue_confirmation_map
        )
        self._troubleshooting_index = self._build_keyword_index(
            patterns.troubleshooting_actions
        )
        self._action_tokens_index = self._build_action_tokens_index()
        self._customer_intent_index = self._build_keyword_index(
            {k: set(v) for k, v in CUSTOMER_INTENT_KEYWORDS.items()}
        )
        self._explicit_agent_actions_index = self._build_keyword_index(
            {k: set(v) for k, v in EXPLICIT_AGENT_ACTION_PHRASES.items()}
        )

    @staticmethod
    def _build_keyword_index(
        keyword_dict: Annotated[
            dict, Doc("Mapping from category name to iterable of keywords.")
        ],
    ) -> list[tuple[str, str]]:
        """Build a flat list of (keyword, category) tuples sorted by keyword length desc.

        Longer keywords are checked first to match phrases like 'processed twice'
        before single words like 'twice'.
        """
        pairs = []
        for category, keywords in keyword_dict.items():
            for kw in keywords:
                pairs.append((kw.lower() if isinstance(kw, str) else kw, category))
        pairs.sort(key=lambda x: len(x[0]), reverse=True)
        return pairs

    @staticmethod
    def _lookup_category(
        text: Annotated[str, Doc("Lowercased text to search within.")],
        index: Annotated[
            list[tuple[str, str]],
            Doc("Pre-built (keyword, category) index sorted by keyword length desc."),
        ],
    ) -> Optional[str]:
        """Fast lookup using pre-built index. Returns first matching category."""
        for keyword, category in index:
            if keyword in text:
                return category
        return None

    @staticmethod
    def _lookup_all_categories(
        text: Annotated[str, Doc("Lowercased text to search within.")],
        index: Annotated[
            list[tuple[str, str]],
            Doc("Pre-built (keyword, category) index sorted by keyword length desc."),
        ],
    ) -> list[str]:
        """Fast lookup returning all matching categories (deduplicated, order preserved)."""
        seen = set()
        result = []
        for keyword, category in index:
            if keyword in text and category not in seen:
                seen.add(category)
                result.append(category)
        return result

    def _build_action_tokens_index(self) -> list[tuple[str, str, bool]]:
        """Build index for ACTION_TOKENS with explicit-only flag.

        Returns list of (keyword, action_event, is_explicit_only) tuples.
        Merges language-specific patterns.action_tokens with vocab defaults.
        """
        pairs = []
        merged: dict[str, list[str]] = {}
        for raw_action, keywords in self.vocab.ACTION_TOKENS.items():
            merged[raw_action] = list(keywords)
        for raw_action, keywords in self.patterns.action_tokens.items():
            merged.setdefault(raw_action, []).extend(keywords)

        for raw_action, keywords in merged.items():
            if raw_action not in self.patterns.action_event_map:
                continue
            action_event = self.patterns.action_event_map[raw_action]
            is_explicit = action_event in self.patterns.explicit_only_actions
            for kw in keywords:
                pairs.append((kw.lower(), action_event, is_explicit))
        pairs.sort(key=lambda x: len(x[0]), reverse=True)
        return pairs

    def analyze(
        self,
        transcript: str,
        metadata: Optional[dict] = None,
        turns: Annotated[
            Optional[list[Turn]],
            Doc("""
            Pre-built turns to analyze. When provided, `_parse_turns()` is skipped entirely
            and these turns are used directly by the extraction pipeline.

            Turns whose speaker is not a recognized role (`"agent"` or `"customer"`) are
            normalized to `"customer"` so all role-gated extractors — intent, trigger,
            amounts, sentiment — produce results rather than silently falling through.

            Pass `None` (default) to parse roles from `transcript` as usual.
            """),
        ] = None,
    ) -> TranscriptAnalysis:
        metadata = metadata or {}
        if turns is None:
            turns = self._parse_turns(transcript)

        # Normalize Unicode quotation marks/apostrophes to ASCII equivalents so
        # pattern matching works regardless of whether the input uses curly quotes.
        turns = [
            t.model_copy(
                update={
                    "text": t.text.replace("\u2019", "'")
                    .replace("\u2018", "'")
                    .replace("\u201c", '"')
                    .replace("\u201d", '"')
                }
            )
            for t in turns
        ]

        has_roles = any(t.speaker in ("agent", "customer") for t in turns)
        if not has_roles:
            turns = [t.model_copy(update={"speaker": "customer"}) for t in turns]

        docs = list(self.nlp.pipe([t.text for t in turns])) if turns else []
        for turn, doc in zip(turns, docs):
            turn.doc = doc
            turn.intent = self.intent_detector.get_primary_intent(
                self.intent_detector.detect(turn.text, doc=doc)
            )
            turn.targets.append(self.target_extractor.extract(text=turn.text, doc=doc))
            turn.sentiment, _ = self.sentiment_analyzer.analyze_turn(
                turn.text, turn.speaker
            )
            turn.entities = self.entity_extractor.extract(turn.text, doc=doc)

        call_info = self._extract_call_info(turns, metadata)
        customer = self._extract_customer_profile(turns)
        issues = self._extract_issues(turns, call_type=call_info.type)
        actions = self._extract_actions(turns)
        resolution = self._extract_resolution(turns)
        sentiment_trajectory = self.sentiment_analyzer.track_trajectory(turns)
        resolution_state = self._extract_resolution_state(turns, resolution)
        refund_reference = self._extract_refund_reference(turns, issues, actions)
        timeline = self._extract_conversation_timeline(turns)
        promises = self._extract_promises(turns)
        promises = self._infer_implicit_commitments(promises, actions, turns)
        domain = self._extract_domain(call_info, issues)

        # Override UNCLASSIFIED when a profile/identity action was detected
        if domain == "UNCLASSIFIED":
            action_types = {a.type for a in actions}
            if action_types & {
                "PROFILE_UPDATED",
                "IDENTITY_VERIFIED",
                "ACCOUNT_VERIFIED",
            }:
                domain = "ACCOUNT"
        service = self._extract_service(issues, turns)
        customer_intent, secondary_intent = self._extract_customer_intent(
            issues, turns, actions
        )
        trigger_cause = self._extract_trigger_cause(turns)

        if trigger_cause == "REQUEST_CANCELLATION":
            action_types = {a.type for a in actions}
            if (
                "RETENTION_OFFER" in action_types
                and "SERVICE_CANCELLED" not in action_types
            ):
                trigger_cause = "CANCELLATION_DEFLECTED"

        context_provided, context_values = self._extract_context_provided(
            turns, call_info
        )
        system_actions = self._extract_system_actions(turns)
        amounts = self._extract_all_amounts(turns)
        redacted_fields = self._extract_redacted_fields(turns)

        extraction_confidence = self._compute_extraction_confidence(
            domain, customer_intent, trigger_cause, actions, resolution
        )
        requires_review = self._needs_review(
            extraction_confidence, actions, issues, call_info.type, trigger_cause
        )

        return TranscriptAnalysis(
            call_info=call_info,
            customer=customer,
            turns=turns,
            issues=issues,
            actions=actions,
            resolution=resolution,
            sentiment_trajectory=sentiment_trajectory,
            resolution_state=resolution_state,
            refund_reference=refund_reference,
            timeline=timeline,
            promises=promises,
            domain=domain,
            service=service,
            customer_intent=customer_intent,
            secondary_intent=secondary_intent,
            trigger_cause=trigger_cause,
            context_provided=context_provided,
            context_values=context_values,
            system_actions=system_actions,
            amounts=amounts,
            redacted_fields=redacted_fields,
            extraction_confidence=extraction_confidence,
            requires_review=requires_review,
        )

    @staticmethod
    def _compute_extraction_confidence(
        domain: Annotated[
            Optional[str], Doc("Extracted domain label, or None if unclassified.")
        ],
        customer_intent: Annotated[
            Optional[str], Doc("Primary customer intent, or None if not detected.")
        ],
        trigger_cause: Annotated[
            Optional[str], Doc("Trigger cause label, or None if not detected.")
        ],
        actions: Annotated[list, Doc("List of extracted agent actions.")],
        resolution: Annotated[
            object, Doc("Resolution object; its `type` field is inspected.")
        ],
    ) -> float:
        score = 0.5
        if domain and domain != "UNCLASSIFIED":
            score += 0.1
        if customer_intent:
            score += 0.1
        if trigger_cause:
            score += 0.1
        if actions:
            score += 0.1
        if resolution.type not in ("UNKNOWN",):
            score += 0.1
        return min(score, 1.0)

    @staticmethod
    def _needs_review(
        confidence: Annotated[float, Doc("Extraction confidence score in [0, 1].")],
        actions: Annotated[list, Doc("Extracted agent actions.")],
        issues: Annotated[list, Doc("Extracted issues from the conversation.")],
        call_type: Annotated[
            str, Doc("Call type label, e.g. 'SUPPORT' or 'SALES'.")
        ] = "SUPPORT",
        trigger_cause: Annotated[
            Optional[str], Doc("Trigger cause label, or None.")
        ] = None,
    ) -> bool:
        """Return True when the extraction result requires human review.

        Flags the result when confidence is low, when no actions or issues were
        found, when the trigger cause is absent (workflow activation event could
        not be determined), or when a SALES call contains no monetization action.
        """
        if confidence < 0.7:
            return True
        if not actions and not issues:
            return True
        if not trigger_cause:
            return True
        if call_type == "SALES":
            _MONETIZATION_ACTIONS = {
                "PLAN_UPGRADED",
                "ADDON_OFFERED",
                "ADDON_ACTIVATED",
                "DISCOUNT_OFFERED",
                "DISCOUNT_APPLIED",
                "TRIAL_ACTIVATED",
            }
            if not ({a.type for a in actions} & _MONETIZATION_ACTIONS):
                return True
        return False

    def _parse_turns(
        self,
        transcript: Annotated[
            str, Doc("Raw transcript string with one 'Speaker: text' line per turn.")
        ],
    ) -> list[Turn]:
        agent_labels = self.patterns.agent_speaker_labels or ["agent", "agente"]
        customer_labels = self.patterns.customer_speaker_labels or [
            "customer",
            "caller",
            "cliente",
            "client",
        ]
        turns = []
        for line in transcript.strip().split("\n"):
            if not line or ":" not in line:
                continue
            speaker, text = line.split(":", 1)
            speaker = speaker.strip().lower()
            if any(label in speaker for label in agent_labels):
                speaker = "agent"
            elif any(label in speaker for label in customer_labels):
                speaker = "customer"
            else:
                speaker = "system"
            turns.append(Turn(speaker=speaker, text=text.strip()))
        return turns

    def _extract_actions(
        self,
        turns: Annotated[
            list[Turn], Doc("All conversation turns; only agent turns are processed.")
        ],
    ) -> list[Action]:
        """
        Extract canonical, atomic ACTION EVENTS from agent turns.

        Each Action represents a confirmed fact (event),
        not a derived outcome or result.
        """
        actions: dict[str, Action] = {}

        # Free-form threads have no agent labels (all turns are "customer").
        # Fall back to scanning every turn so action patterns are not silently skipped.
        agent_turns_exist = any(t.speaker == "agent" for t in turns)

        for turn in turns:
            if agent_turns_exist and turn.speaker != "agent":
                continue

            text = turn.text

            action_events = self._detect_action_events(text)
            if not action_events:
                continue

            for action_type in action_events:
                if action_type not in actions:
                    actions[action_type] = Action(type=action_type, attributes={})

                action = actions[action_type]

                if "REFUND" in action_type or "ESCALATION" in action_type:
                    if ref := self._extract_reference_number(turn):
                        action.attributes["reference"] = ref

                if "REFUND" in action_type or "CREDIT" in action_type:
                    amount, method = self._extract_financial_details(turn)
                    if amount:
                        action.attributes.setdefault("amount", amount)
                    if method:
                        action.attributes.setdefault("payment_method", method)

        return list(actions.values())

    def _detect_action_events(
        self, text: Annotated[str, Doc("Agent turn text to scan for action events.")]
    ) -> list[str]:
        """Detect action events from agent turn text using a priority-ordered cascade.

        Detection order:
        1. Explicit agent action phrases (highest priority).
        2. Issue confirmation patterns.
        3. Troubleshooting patterns.
        4. Action tokens (keyword-based).
        """
        text_lower = text.lower()
        seen = set()
        events = []

        for kw, category in self._explicit_agent_actions_index:
            if kw in text_lower and category not in seen:
                seen.add(category)
                events.append(category)

        for kw, category in self._issue_confirmation_index:
            if kw in text_lower and category not in seen:
                seen.add(category)
                events.append(category)

        for kw, category in self._troubleshooting_index:
            if kw in text_lower and category not in seen:
                seen.add(category)
                events.append(category)

        for kw, action_event, is_explicit in self._action_tokens_index:
            if action_event in seen:
                continue
            if kw not in text_lower:
                continue
            if is_explicit:
                phrases = self.patterns.explicit_action_phrases.get(action_event, set())
                if not any(p in text_lower for p in phrases):
                    continue
            seen.add(action_event)
            events.append(action_event)

        return events

    def _detect_technical_issue_detail(
        self, text: Annotated[str, Doc("Lowercased customer text to classify.")]
    ) -> Optional[str]:
        return self._lookup_category(text.lower(), self._technical_issue_index)

    def _extract_action_details(
        self,
        action_type: Annotated[
            str, Doc("The detected action event type (e.g. 'REFUND', 'CREDIT').")
        ],
        turn: Annotated[
            Turn, Doc("The agent turn from which additional details are extracted.")
        ],
    ):
        amount, method = None, None
        attributes = {}
        if action_type in ["REFUND", "CREDIT", "CHARGE", "PAYMENT"]:
            amount, method = self._extract_financial_details(turn)
            if ref := self._extract_reference_number(turn):
                attributes["reference"] = ref
            if timeline := self._extract_timeline(turn.text):
                attributes["timeline"] = timeline
        return amount, method, attributes

    def _extract_resolution(
        self,
        turns: Annotated[
            list[Turn],
            Doc("All conversation turns; only the last 5 agent turns are examined."),
        ],
    ) -> Resolution:
        agent_turns = [t for t in turns if t.speaker == "agent"]
        recent = agent_turns[-5:] if agent_turns else []

        for turn in reversed(recent):
            text = turn.text.lower()
            key = self._lookup_category(text, self._resolution_index)
            if key:
                if key == "PENDING_REPLACEMENT":
                    res_type = "PENDING"
                    next_steps = "REPLACEMENT"
                else:
                    res_type = key
                    next_steps = None
                timeline = self._extract_timeline(text)
                return Resolution(
                    type=res_type, timeline=timeline, next_steps=next_steps
                )

        return Resolution(type="UNKNOWN", timeline=None, next_steps=None)

    @staticmethod
    def _match_any(
        text: Annotated[str, Doc("Text to search within.")],
        keywords: Annotated[list[str], Doc("Keywords to test against the text.")],
    ) -> bool:
        return any(kw in text for kw in keywords)

    def _extract_timeline(
        self,
        text: Annotated[
            str, Doc("Text to extract a timeline from (may be lowercased).")
        ],
    ) -> Optional[str]:
        """Extract a timeline string from text using a priority-ordered cascade.

        Tries, in order:
        1. Language-specific timeline patterns (most specific, e.g. "3 a 5 días hábiles").
        2. Temporal extractor for duration inference.
        3. Language-specific timeline keywords ("today", "tomorrow", and equivalents).
        4. "in X hours/days" patterns with word-number support (language-specific word_to_num).
        """
        text_lower = text.lower()

        for regex, fmt in self.patterns.timeline_patterns:
            if match := re.search(regex, text_lower, re.I):
                groups = match.groups()
                return fmt.format(*groups)

        pattern = self.temporal_extractor.extract(text)
        if pattern:
            if getattr(pattern, "resolved_date", None):
                return pattern.resolved_date
            if getattr(pattern, "duration", None):
                return str(pattern.duration).upper()

        timeline_kw = self.patterns.timeline_keywords or {}
        for kw, value in timeline_kw.items():
            if kw in text_lower:
                return value

        word_to_num = self.patterns.word_to_num or {}
        word_alts = "|".join(re.escape(w) for w in word_to_num) if word_to_num else None
        num_pat = rf"(?:{word_alts}|\d+)" if word_alts else r"\d+"
        if match := re.search(
            rf"in\s+(a\s+)?({num_pat})\s+(?:of\s+)?hours?", text_lower, re.I
        ):
            raw = ((match.group(1) or "") + match.group(2)).strip().lower()
            num = word_to_num.get(raw, match.group(2))
            return f"{num}h"
        if match := re.search(
            rf"in\s+(a\s+)?({num_pat})\s+(?:of\s+)?days?", text_lower, re.I
        ):
            raw = ((match.group(1) or "") + match.group(2)).strip().lower()
            num = word_to_num.get(raw, match.group(2))
            return f"{num}d"
        if match := re.search(
            rf"by\s+(a\s+)?({num_pat})\s+(?:of\s+)?days?", text_lower, re.I
        ):
            raw = ((match.group(1) or "") + match.group(2)).strip().lower()
            num = word_to_num.get(raw, match.group(2))
            return f"{num}d"
        return None

    def _determine_action_result(
        self,
        turns: Annotated[
            list[Turn],
            Doc(
                "All conversation turns, used to inspect the 2 turns immediately after the action."
            ),
        ],
        action_index: Annotated[int, Doc("Index of the action turn within `turns`.")],
        action_turn: Annotated[Turn, Doc("The turn where the action was detected.")],
    ) -> str:
        text_lower = action_turn.text.lower()

        if any(
            k in text_lower
            for k in self.patterns.action_completion_keywords
            | self.patterns.action_completion_phrases
        ):
            return "COMPLETED"

        for pattern in self.patterns.action_now_patterns:
            if re.search(pattern, text_lower):
                return "COMPLETED"

        for t in turns[action_index + 1 : action_index + 3]:
            tl = t.text.lower()
            if t.speaker == "customer" and any(
                k in tl for k in self.patterns.positive_customer_confirmations
            ):
                return "COMPLETED"
            if t.speaker == "agent" and any(
                k in tl for k in self.patterns.agent_confirmation_phrases
            ):
                return "COMPLETED"
        return "PENDING"

    def _extract_financial_details(
        self,
        turn: Annotated[
            Turn, Doc("The turn from which amount and payment method are extracted.")
        ],
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Prefer using named entities from turn.entities if present; otherwise fallback to regex heuristics.
        Returns (amount, payment_method)
        """
        amount = None
        ents = getattr(turn, "entities", {}) or {}

        money_candidates = ents.get("money") or ents.get("money_amounts") or []
        if money_candidates:
            amount = money_candidates[0]

        if not amount:
            if m := re.search(r"\$\s?([\d,]+(?:\.\d{1,2})?)", turn.text):
                amount = f"${m.group(1)}"

        method = self._detect_refund_method(turn.text.lower())
        return amount, method

    _REF_BLACKLIST = {
        "number",
        "reference",
        "confirmation",
        "immediately",
        "right",
        "today",
        "tomorrow",
        "please",
        "thank",
        "thanks",
        "okay",
        "here",
        "that",
        "this",
        "your",
        "the",
        "will",
        "been",
    }

    @classmethod
    def _extract_reference_number(
        cls,
        turn: Annotated[
            Turn, Doc("The turn whose text is scanned for reference numbers.")
        ],
    ) -> Optional[str]:
        """Extract reference numbers (e.g. RFD-908712, ESC-45390, "confirmation #12345").

        Tries in order:
        1. Structured PREFIX-DIGITS pattern (most reliable).
        2. "reference/confirmation" followed by a code (requires at least one digit).
        3. "id/ticket/case/order" followed by a code (requires at least one digit).
        """
        text = turn.text
        if m := re.search(r"\b([A-Z]{2,5}-\d{3,})\b", text):
            return m.group(0)

        if m := re.search(
            r"(?:reference|confirmation|ref)[^\w]{0,6}#?\s*([A-Z0-9-]*\d[A-Z0-9-]{2,29})",
            text,
            re.I,
        ):
            candidate = m.group(1)
            if candidate.lower() not in cls._REF_BLACKLIST:
                return candidate

        if m := re.search(
            r"(?:id|ticket|case|order)[^\w]{0,6}#?\s*([A-Z0-9-]*\d[A-Z0-9-]{2,29})",
            text,
            re.I,
        ):
            candidate = m.group(1)
            if candidate.lower() not in cls._REF_BLACKLIST:
                return candidate

        return None

    def _extract_customer_profile(
        self,
        turns: Annotated[
            list[Turn],
            Doc("All conversation turns; entity fields are read from each turn."),
        ],
    ) -> CustomerProfile:
        """Extract the customer's profile from the conversation.

        Args:
            turns: List of turns in the conversation.

        Returns:
            The customer's profile if found, otherwise None.
        Examples:
            >>> analyzer = TranscriptAnalyzer()
            >>> turns = [
            ...     Turn(speaker="customer", text="I have a problem with my account."),
            ...     Turn(speaker="agent", text="What seems to be the issue?"),
            ...     Turn(speaker="customer", text="I'm not getting my bill."),
            ... ]
            >>> analyzer._extract_customer_profile(turns)
            CustomerProfile(name='John', account='12345', tier='STANDARD')
        """
        profile = CustomerProfile()
        profile.name = self._extract_customer_name(turns)

        for t in turns:
            ents = getattr(t, "entities", {}) or {}
            if emails := ents.get("emails"):
                profile.attributes = profile.attributes or {}
                profile.attributes["email"] = emails[0]
            if accounts := ents.get("accounts") or ents.get("account_numbers"):
                profile.account = profile.account or accounts[0]
            if plans := ents.get("plans"):
                profile.tier = profile.tier or self._map_plan_to_tier(plans[0])

        return profile

    @staticmethod
    def _map_plan_to_tier(
        plan: Annotated[str, Doc("Raw plan name string (case-insensitive).")],
    ) -> str:
        """Map a plan to a tier.

        Args:
            plan: The plan name.

        Returns:
            The tier corresponding to the plan.
        Examples:
            >>> analyzer = TranscriptAnalyzer()
            >>> analyzer._map_plan_to_tier("Premium")
            'PREMIUM'
        """
        plan = plan.lower()
        if "premium" in plan:
            return "PREMIUM"
        if "enterprise" in plan:
            return "ENTERPRISE"
        if "basic" in plan:
            return "BASIC"
        return "STANDARD"

    def _extract_customer_name(
        self,
        turns: Annotated[
            list[Turn],
            Doc(
                "All conversation turns; first 3 agent turns and entity fields are examined."
            ),
        ],
    ) -> Optional[str]:
        """Extract the customer's name from the conversation.

        Args:
            turns: List of turns in the conversation.

        Returns:
            The customer's name if found, otherwise None.
        Examples:
            >>> analyzer = TranscriptAnalyzer()
            >>> turns = [
            ...     Turn(speaker="customer", text="I have a problem with my account."),
            ...     Turn(speaker="agent", text="What seems to be the issue?"),
            ...     Turn(speaker="customer", text="I'm not getting my bill."),
            ... ]
            >>> analyzer._extract_customer_name(turns)
            'John'
        """
        intro_patterns = self.patterns.name_intro_patterns or [
            r"(?:my name is|i'?m|this is)\s+([A-Z][a-z]+)"
        ]
        thanks_patterns = self.patterns.name_thanks_patterns or [
            r"thank(?:s| you),\s+([A-Z][a-z]+)"
        ]
        for t in turns[:3]:
            if t.speaker == "agent":
                doc = t.doc
                if doc:
                    for ent in doc.ents:
                        if ent.label_ == "PERSON":
                            return ent.text
                for pat in intro_patterns:
                    if match := re.search(pat, t.text, re.I):
                        return match.group(1).title()
                for pat in thanks_patterns:
                    if match := re.search(pat, t.text):
                        return match.group(1)
        for t in turns:
            ents = getattr(t, "entities", {}) or {}
            emails = ents.get("emails") or []
            if emails:
                local_part = emails[0].split("@")[0]
                if "." in local_part:
                    return local_part.split(".")[0].title()
        return None

    def _extract_issues(
        self,
        turns: Annotated[
            list[Turn],
            Doc(
                "All conversation turns; customer turns are scanned first, agent turns as fallback."
            ),
        ],
        call_type: Annotated[
            str,
            Doc("Call type label used to suppress billing disputes in SALES contexts."),
        ] = "SUPPORT",
    ) -> list[Issue]:
        """Extract issues from a list of turns.

        Customer turns are scanned first; agent turns are used as a fallback when
        no issue type is found in customer text.

        Monetary context guardrail: in a SALES context, amounts are pricing information,
        not billing disputes. Billing dispute requires unexpected charge language plus
        refund context — money alone is not a billing issue.

        Args:
            turns: List of turns in the conversation.

        Returns:
            A list of issues extracted from the conversation.
        Examples:
            >>> analyzer = TranscriptAnalyzer()
            >>> turns = [
            ...     Turn(speaker="customer", text="I have a problem with my account."),
            ...     Turn(speaker="agent", text="What seems to be the issue?"),
            ...     Turn(speaker="customer", text="I'm not getting my bill."),
            ... ]
            >>> analyzer._extract_issues(turns)
            [Issue(type="ACCOUNT_ISSUE", severity="LOW", cause="BILLING_DISPUTE", plan_change=None, amounts=[], days=[])]
        """
        customer_text = " ".join(
            t.text for t in turns if t.speaker == "customer"
        ).lower()
        issue_type = self._get_issue_type(customer_text)

        if not issue_type:
            agent_text = " ".join(t.text for t in turns if t.speaker == "agent").lower()
            issue_type = self._get_issue_type(agent_text)

        if not issue_type:
            return []

        _BILLING_ISSUE_TYPES = {"BILLING_DISPUTE", "UNEXPECTED_CHARGE"}
        if call_type == "SALES" and issue_type in _BILLING_ISSUE_TYPES:
            issue_type = None

        if not issue_type:
            return []

        severity = self._detect_severity(customer_text)
        cause, plan_change = None, None
        amounts = []

        if issue_type in ["BILLING_DISPUTE", "UNEXPECTED_CHARGE", "REFUND_REQUEST"]:
            cause, plan_change = self._detect_billing_cause(turns)
            amounts = self._extract_disputed_amounts(turns)

        days = self.temporal_extractor.extract(customer_text).days or []
        attrs = {"days": days} if days else {}
        if issue_type in {"CONNECTIVITY", "TECHNICAL"}:
            cause = self._detect_technical_issue_detail(customer_text)
            return [
                Issue(
                    type=issue_type,
                    severity=severity,
                    cause=cause,
                    attributes=attrs,
                )
            ]

        return [
            Issue(
                type=issue_type,
                severity=severity,
                cause=cause,
                plan_change=plan_change,
                disputed_amounts=amounts,
                attributes=attrs,
            )
        ]

    def _get_issue_type(
        self,
        text: Annotated[
            str, Doc("Lowercased combined text from customer or agent turns.")
        ],
    ) -> Optional[str]:
        return self._lookup_category(text, self._issue_type_index)

    def _detect_severity(
        self,
        text: Annotated[
            str, Doc("Lowercased customer text to classify severity from.")
        ],
    ) -> str:
        return self._lookup_category(text.lower(), self._severity_index) or "LOW"

    def _extract_disputed_amounts(
        self,
        turns: Annotated[
            list[Turn], Doc("All conversation turns; only customer turns are scanned.")
        ],
    ) -> list[str]:
        """Extract disputed amounts from customer turns.

        Args:
            turns: List of turns.

        Returns:
            List of disputed amounts.
        Examples:
            >>> _extract_disputed_amounts([Turn("customer", "I think my bill is wrong"), Turn("agent", "What amount do you think is wrong?"), Turn("customer", "I think it's $100")])
            ['$100']
        """
        keywords = list(self.patterns.disputed_amount_keywords or [])
        amounts = []
        for t in (t for t in turns if t.speaker == "customer"):
            if any(k in t.text.lower() for k in keywords):
                amounts.extend(getattr(t, "entities", {}).get("money", []))
        return list(dict.fromkeys(amounts))

    _AMOUNT_REGEX = re.compile(
        r"\$\s?[\d,]+(?:\.\d{1,2})?|\b[\d,]+(?:\.\d{1,2})?\s*(?:USD|EUR)\b",
        re.I,
    )

    def _extract_all_amounts(
        self,
        turns: Annotated[
            list[Turn],
            Doc("All conversation turns; every turn is scanned for monetary amounts."),
        ],
    ) -> list[MonetaryAmount]:
        """Extract all monetary amounts from all turns with their reason.

        A secondary pass uses a narrow 30-character suffix window to detect billing
        period indicators (MONTH/YEAR). A wide context window causes adjacent prices
        (e.g. "$49 a month, or $480 annual") to share keywords; the suffix-only
        window resolves the ambiguity.

        Amounts without any recognized context keyword are skipped.
        """
        amount_reason_map = self.patterns.amount_reason_context or []
        billing_period_map = self.patterns.billing_period_context or []
        seen: set[tuple[str, Optional[str], str]] = set()
        results: list[MonetaryAmount] = []

        for idx, turn in enumerate(turns):
            text = turn.text
            for match in self._AMOUNT_REGEX.finditer(text):
                amount_str = match.group(0).strip()
                start, end = match.start(), match.end()
                ctx_start = max(0, start - 50)
                ctx_end = min(len(text), end + 50)
                context = text[ctx_start:ctx_end].lower()

                reason = None
                for keyword, r in amount_reason_map:
                    if keyword in context:
                        reason = r
                        break

                if not reason and billing_period_map:
                    suffix = text[end : min(len(text), end + 30)].lower()
                    for keyword, r in billing_period_map:
                        if keyword in suffix:
                            reason = r
                            break

                if not reason:
                    continue  # skip bare uncontextualized amounts

                key = (amount_str, reason, turn.speaker)
                if key not in seen:
                    seen.add(key)
                    results.append(
                        MonetaryAmount(
                            amount=amount_str,
                            reason=reason,
                            speaker=turn.speaker,
                            turn_index=idx,
                        )
                    )

        return results

    def _extract_redacted_fields(
        self,
        turns: Annotated[
            list[Turn],
            Doc(
                "All conversation turns; every turn is scanned for redacted field markers."
            ),
        ],
    ) -> list[str]:
        """Detect redacted field tokens from all turns using configured redaction_pattern."""
        redacted_field_context = self.patterns.redacted_field_context or []
        pattern = re.compile(self._redaction_pattern, re.I)
        seen: set[str] = set()
        results: list[str] = []

        for turn in turns:
            text = turn.text
            for match in pattern.finditer(text):
                start, end = match.start(), match.end()
                ctx_start = max(0, start - 40)
                ctx_end = min(len(text), end + 40)
                context = text[ctx_start:ctx_end].lower()

                token = "FIELD_REDACTED"
                for keyword, field_token in redacted_field_context:
                    if keyword in context:
                        token = field_token
                        break

                if token not in seen:
                    seen.add(token)
                    results.append(token)

        return results

    def _detect_billing_cause(
        self,
        turns: Annotated[
            list[Turn],
            Doc(
                "All conversation turns; only agent turns are examined for billing cause keywords."
            ),
        ],
    ) -> tuple[Optional[str], Optional[str]]:
        for t in (t for t in turns if t.speaker == "agent"):
            text = t.text.lower()
            cause = self._lookup_category(text, self._billing_cause_index)
            if cause:
                plan_change = None
                if cause in {"MID_CYCLE_UPGRADE", "MID_CYCLE_DOWNGRADE"}:
                    if match := re.search(r"from (\w+) to (\w+)", text):
                        plan_change = (
                            f"{match.group(1).upper()}→{match.group(2).upper()}"
                        )
                return cause, plan_change
        return None, None

    def _extract_call_info(
        self,
        turns: Annotated[
            list[Turn],
            Doc("All conversation turns used to infer call type from combined text."),
        ],
        metadata: Annotated[
            dict,
            Doc(
                "Call metadata dict; may contain 'call_id', 'channel', and 'agent' keys."
            ),
        ],
    ) -> CallInfo:
        """
        Extracts call information from the clm_core.

        Args:
            turns: List of turns in the clm_core.
            metadata: Metadata associated with the call.

        Returns:
            CallInfo object containing extracted information.
        """
        agent_name = metadata.get("agent") or self._detect_agent_name(turns)
        full_text = " ".join(t.text.lower() for t in turns)
        sales_keywords = self.patterns.call_type_sales_keywords or [
            "upgrade",
            "pricing",
            "buy",
            "interested in",
        ]
        call_type = (
            "SALES" if any(x in full_text for x in sales_keywords) else "SUPPORT"
        )
        return CallInfo(
            call_id=metadata.get("call_id", "unknown"),
            type=call_type,
            channel=metadata.get("channel", "VOICE"),
            duration=len(turns),
            agent=agent_name,
        )

    _NAME_BLACKLIST = {
        "sorry",
        "happy",
        "glad",
        "pleased",
        "here",
        "calling",
        "able",
        "going",
        "looking",
        "checking",
        "helping",
        "available",
        "ready",
        "sure",
        "certain",
        "afraid",
        "delighted",
        "excited",
        "thrilled",
    }

    def _detect_agent_name(
        self,
        turns: Annotated[
            list[Turn],
            Doc("All conversation turns; only the first 3 agent turns are checked."),
        ],
    ) -> Optional[str]:
        """Detects the agent's name from the clm_core.
        We will find the agent's name by looking for a PERSON entity
        in the text or by matching a pattern.

        Args:
            turns: List of turns in the clm_core.

        Returns:
            The detected agent's name or None if not found.

        Examples:
            >>> _detect_agent_name([Turn("agent", "Hello, my name is John.")])
            'John'
        """
        agent_patterns = self.patterns.agent_name_patterns or [
            r"(?:my name is|this is)\s+([A-Z][a-z]+)"
        ]
        for t in (t for t in turns[:3] if t.speaker == "agent"):
            doc = getattr(t, "doc", None)
            if doc:
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        name = ent.text.lower()
                        if name not in self._NAME_BLACKLIST:
                            return ent.text
            for pat in agent_patterns:
                if match := re.search(pat, t.text, re.I):
                    candidate = match.group(1)
                    if candidate.lower() not in self._NAME_BLACKLIST:
                        return candidate
        return None

    def _extract_resolution_state(
        self,
        turns: Annotated[
            list[Turn],
            Doc(
                "All conversation turns split into agent and customer sub-lists internally."
            ),
        ],
        resolution: Annotated[
            Resolution,
            Doc(
                "Resolution extracted from agent turns; its type drives the state machine."
            ),
        ],
    ) -> ResolutionState:
        """Extract enhanced resolution state with granularity."""
        agent_turns = [t for t in turns if t.speaker == "agent"]
        customer_turns = [t for t in turns if t.speaker == "customer"]

        completeness = self._detect_resolution_completeness(agent_turns)
        customer_satisfaction = self._derive_customer_satisfaction(customer_turns)
        follow_up_needed, follow_up_reason = self._detect_follow_up_needed(agent_turns)
        resolution_type = self._map_resolution_to_state(
            resolution.type, completeness, follow_up_needed, customer_satisfaction
        )

        return ResolutionState(
            type=resolution_type,
            completeness=completeness,
            customer_satisfaction=customer_satisfaction,
            follow_up_needed=follow_up_needed,
            follow_up_reason=follow_up_reason,
        )

    def _detect_resolution_completeness(
        self,
        agent_turns: Annotated[
            list[Turn],
            Doc(
                "Agent-only turns; the last 5 are joined and scanned for resolution state tokens."
            ),
        ],
    ) -> Optional[str]:
        """Detect if resolution was full, partial, or none."""
        recent = agent_turns[-5:] if agent_turns else []
        text = " ".join(t.text.lower() for t in recent)

        tokens = (
            self.patterns.resolution_state_tokens or self.vocab.RESOLUTION_STATE_TOKENS
        )
        for state, keywords in tokens.items():
            if any(kw in text for kw in keywords):
                if state == "FULLY_RESOLVED":
                    return "FULL"
                elif state == "PARTIALLY_RESOLVED":
                    return "PARTIAL"
        return None

    def _derive_customer_satisfaction(
        self,
        customer_turns: Annotated[
            list[Turn],
            Doc(
                "Customer-only turns; the last 3 are joined and scanned for satisfaction tokens."
            ),
        ],
    ) -> Optional[str]:
        """Derive satisfaction from final customer turns."""
        if not customer_turns:
            return None

        final_turns = customer_turns[-3:]
        text = " ".join(t.text.lower() for t in final_turns)

        tokens = (
            self.patterns.customer_satisfaction_tokens
            or self.vocab.CUSTOMER_SATISFACTION_TOKENS
        )
        for satisfaction, keywords in tokens.items():
            if any(kw in text for kw in keywords):
                return satisfaction

        if final_turns:
            final_sentiment = final_turns[-1].sentiment
            if final_sentiment in ["SATISFIED", "GRATEFUL", "RELIEVED"]:
                return "SATISFIED"
            elif final_sentiment in ["FRUSTRATED", "ANGRY", "DISAPPOINTED"]:
                return "DISSATISFIED"

        return "NEUTRAL"

    def _detect_follow_up_needed(
        self,
        agent_turns: Annotated[
            list[Turn],
            Doc(
                "Agent-only turns; the last 3 are joined and scanned for follow-up tokens."
            ),
        ],
    ) -> tuple[bool, Optional[str]]:
        """Detect if follow-up is needed and why."""
        recent = agent_turns[-3:] if agent_turns else []
        text = " ".join(t.text.lower() for t in recent)

        tokens = (
            self.patterns.follow_up_needed_tokens or self.vocab.FOLLOW_UP_NEEDED_TOKENS
        )
        for reason, keywords in tokens.items():
            if any(kw in text for kw in keywords):
                return True, reason

        return False, None

    @staticmethod
    def _map_resolution_to_state(
        resolution_type: Annotated[
            str,
            Doc(
                "Resolution type string, e.g. 'RESOLVED', 'PENDING', 'ESCALATED', or 'UNKNOWN'."
            ),
        ],
        completeness: Annotated[
            Optional[str],
            Doc("Completeness label ('FULL' or 'PARTIAL'), or None if undetermined."),
        ],
        follow_up_needed: Annotated[
            bool, Doc("Whether a follow-up action was detected.")
        ],
        customer_satisfaction: Annotated[
            Optional[str],
            Doc(
                "Customer satisfaction label used to infer resolution when type is UNKNOWN."
            ),
        ] = None,
    ) -> str:
        """Map resolution to granular state, considering customer satisfaction.

        When resolution type is UNKNOWN, customer satisfaction is used to infer
        the resolution: SATISFIED maps to FULLY_RESOLVED or RESOLVED, NEUTRAL maps
        to RESOLVED_PENDING_VERIFICATION, and anything else maps to UNRESOLVED.
        """
        if resolution_type == "RESOLVED":
            if completeness == "FULL" and not follow_up_needed:
                return "FULLY_RESOLVED"
            elif completeness == "PARTIAL":
                return "PARTIALLY_RESOLVED"
            else:
                return "RESOLVED_PENDING_VERIFICATION"
        elif resolution_type == "PENDING":
            return "PENDING"
        elif resolution_type == "ESCALATED":
            return "ESCALATED"
        else:
            if customer_satisfaction == "SATISFIED":
                if completeness == "FULL":
                    return "FULLY_RESOLVED"
                return "RESOLVED"
            elif customer_satisfaction == "NEUTRAL":
                return "RESOLVED_PENDING_VERIFICATION"
            return "UNRESOLVED"

    def _extract_refund_reference(
        self,
        turns: Annotated[
            list[Turn],
            Doc(
                "All conversation turns; only agent turns are scanned for refund details."
            ),
        ],
        issues: Annotated[
            list[Issue],
            Doc("Extracted issues used to determine whether this is a refund case."),
        ],
        actions: Annotated[
            list[Action],
            Doc(
                "Extracted actions used as fallback source for reference number, amount, and method."
            ),
        ],
    ) -> Optional[RefundReference]:
        """Extract refund details for billing/refund cases (case-dependent).

        Also pulls reference number, amount, and method from matching action
        attributes when not already found in turn text.  Returns None when no
        meaningful data (reference number, amount, or status) was found.
        """
        issue_types = [i.type for i in issues]
        is_refund_case = any(
            it in issue_types
            for it in [
                "BILLING_DISPUTE",
                "REFUND_REQUEST",
                "DUPLICATE_CHARGE",
                "UNEXPECTED_CHARGE",
                "MISSING_REFUND",
            ]
        )

        has_refund_action = any(
            "REFUND" in a.type or "CREDIT" in a.type for a in actions
        )

        if not is_refund_case and not has_refund_action:
            return None

        refund = RefundReference()

        for turn in turns:
            if turn.speaker != "agent":
                continue

            text = turn.text
            text_lower = text.lower()

            if not refund.reference_number:
                refund.reference_number = self._extract_refund_reference_number(text)

            if not refund.amount:
                amount, _ = self._extract_financial_details(turn)
                refund.amount = amount

            if not refund.method:
                refund.method = self._detect_refund_method(text_lower)

            if not refund.status:
                refund.status = self._detect_refund_status(text_lower)

            if not refund.timeline:
                refund.timeline = self._extract_timeline(text_lower)

        for action in actions:
            if "REFUND" in action.type or "CREDIT" in action.type:
                if not refund.reference_number and "reference" in action.attributes:
                    refund.reference_number = action.attributes["reference"]
                if not refund.amount and action.amount:
                    refund.amount = action.amount
                if not refund.method and action.payment_method:
                    refund.method = action.payment_method

        if any([refund.reference_number, refund.amount, refund.status]):
            return refund

        return None

    _NON_REFUND_PREFIXES = frozenset(
        {
            "ESC",
            "TKT",
            "INC",
            "CAS",
            "TEC",
            "SUP",
            "SRQ",
            "PRB",
            "CHG",
        }
    )

    @classmethod
    def _extract_refund_reference_number(
        cls,
        text: Annotated[
            str, Doc("Raw agent turn text to scan for refund reference numbers.")
        ],
    ) -> Optional[str]:
        """Extract refund-specific reference numbers.

        Prefers known refund prefixes (RFD, REF, CRD, BCR) and explicitly
        excludes known non-refund prefixes (ESC, TKT, INC, TEC, ...) from the
        generic PREFIX-DIGITS fallback pattern.

        Tries in order:
        1. Known refund-specific prefixes (most reliable): RFD, REF, CRD, BCR.
        2. "refund reference/number/id" followed by an alphanumeric code.
        3. Generic PREFIX-DIGITS pattern — only if prefix is not a known
           non-refund identifier type (e.g. ESC-, TKT-, INC-).
        """
        for pattern in (
            r"\bRFD-?\d{5,10}\b",
            r"\bREF-?\d{5,10}\b",
            r"\bCRD-?\d{5,10}\b",
            r"\bBCR-?\d{5,10}\b",
        ):
            if match := re.search(pattern, text, re.I):
                return match.group(0)

        if match := re.search(
            r"refund\s*(?:reference\s*)?(?:number|id|#)?\s*[:=—–-]?\s*([A-Z0-9-]*\d[A-Z0-9-]{3,14})",
            text,
            re.I,
        ):
            return match.group(1)

        if match := re.search(r"\b([A-Z]{2,5})-(\d{3,})\b", text):
            prefix = match.group(1).upper()
            if prefix not in cls._NON_REFUND_PREFIXES:
                return match.group(0)

        return None

    def _detect_refund_method(
        self,
        text: Annotated[
            str, Doc("Lowercased turn text to match against refund method tokens.")
        ],
    ) -> Optional[str]:
        """Detect refund method from text."""
        tokens = self.patterns.refund_method_tokens or self.vocab.REFUND_METHOD_TOKENS
        for method, keywords in tokens.items():
            if any(kw in text for kw in keywords):
                return method
        return None

    def _detect_refund_status(
        self,
        text: Annotated[
            str, Doc("Lowercased turn text to match against refund status tokens.")
        ],
    ) -> Optional[str]:
        """Detect refund status from text."""
        tokens = self.patterns.refund_status_tokens or self.vocab.REFUND_STATUS_TOKENS
        for status, keywords in tokens.items():
            if any(kw in text for kw in keywords):
                return status
        return None

    def _extract_conversation_timeline(
        self,
        turns: Annotated[
            list[Turn],
            Doc("All conversation turns iterated to build the event sequence."),
        ],
    ) -> ConversationTimeline:
        """Extract conversation timeline with key events."""
        events = []
        first_issue_turn = None
        first_resolution_turn = None

        for idx, turn in enumerate(turns):
            text_lower = turn.text.lower()

            event_type = self._detect_timeline_event_type(text_lower, turn.speaker)

            if event_type:
                event = TimelineEvent(
                    event_type=event_type,
                    description=self._summarize_event(turn.text, event_type),
                    turn_index=idx,
                    timestamp=turn.timestamp,
                    actor=turn.speaker,
                )
                events.append(event)

                if event_type == "ISSUE_RAISED" and first_issue_turn is None:
                    first_issue_turn = idx
                elif (
                    event_type in ["RESOLUTION_PROPOSED", "ACTION_TAKEN"]
                    and first_resolution_turn is None
                ):
                    first_resolution_turn = idx

        time_to_first_action = None
        time_to_resolution = None

        if first_issue_turn is not None:
            first_action = next(
                (e.turn_index for e in events if e.event_type == "ACTION_TAKEN"), None
            )
            if first_action is not None:
                time_to_first_action = first_action - first_issue_turn

            if first_resolution_turn is not None:
                time_to_resolution = first_resolution_turn - first_issue_turn

        return ConversationTimeline(
            events=events,
            first_issue_turn=first_issue_turn,
            first_resolution_turn=first_resolution_turn,
            time_to_first_action=time_to_first_action,
            time_to_resolution=time_to_resolution,
        )

    def _detect_timeline_event_type(
        self,
        text: Annotated[
            str, Doc("Lowercased turn text to match against timeline event tokens.")
        ],
        speaker: Annotated[
            str,
            Doc(
                "Turn speaker role ('customer' or 'agent'); gates which event types are eligible."
            ),
        ],
    ) -> Optional[str]:
        """Detect timeline event type from turn text.

        ISSUE_RAISED events are expected from the customer speaker.
        ACTION_TAKEN, RESOLUTION_PROPOSED, and INVESTIGATION_STARTED events are
        expected from the agent speaker; turns from other speakers are skipped
        for those event types.
        """
        tokens = self.patterns.timeline_event_tokens or self.vocab.TIMELINE_EVENT_TOKENS
        for event_type, keywords in tokens.items():
            if event_type == "ISSUE_RAISED" and speaker != "customer":
                continue
            if (
                event_type
                in ["ACTION_TAKEN", "RESOLUTION_PROPOSED", "INVESTIGATION_STARTED"]
                and speaker != "agent"
            ):
                continue

            if any(kw in text for kw in keywords):
                return event_type

        return None

    @staticmethod
    def _summarize_event(
        text: Annotated[str, Doc("Raw turn text to summarize.")],
        event_type: Annotated[
            str,
            Doc(
                "Event type label (currently unused; reserved for future specialization)."
            ),
        ],
    ) -> str:
        """Create brief summary of event."""
        sentences = text.split(".")
        summary = sentences[0] if sentences else text
        return summary[:100].strip()

    def _extract_promises(
        self,
        turns: Annotated[
            list[Turn],
            Doc(
                "All conversation turns; only agent turns are scanned for promise indicators."
            ),
        ],
    ) -> list[PromiseCommitment]:
        """Extract agent promises and commitments (case-dependent).

        For each agent turn, scans promise_commitment_tokens first, then checks
        language-specific extra_commitment_patterns separately.
        """
        promises = []

        extra_commitment_patterns = self.patterns.extra_commitment_patterns or {}

        # Free-form threads have no agent labels; scan all turns for promise indicators.
        agent_turns_exist = any(t.speaker == "agent" for t in turns)

        for idx, turn in enumerate(turns):
            if agent_turns_exist and turn.speaker != "agent":
                continue

            text = turn.text
            text_lower = text.lower()

            tokens = (
                self.patterns.promise_commitment_tokens
                or self.vocab.PROMISE_COMMITMENT_TOKENS
            )
            for promise_type, keywords in tokens.items():
                matching_keyword = next(
                    (kw for kw in keywords if kw in text_lower), None
                )

                if matching_keyword:
                    timeline = self._extract_promise_timeline(text_lower)
                    amount = None

                    if promise_type in ["CREDIT_PROMISE", "REFUND_PROMISE"]:
                        amount, _ = self._extract_financial_details(turn)

                    confidence = self._calculate_promise_confidence(
                        text_lower, promise_type
                    )

                    promise = PromiseCommitment(
                        type=promise_type,
                        description=self._extract_promise_description(
                            text, matching_keyword
                        ),
                        timeline=timeline,
                        amount=amount,
                        turn_index=idx,
                        confidence=confidence,
                    )
                    promises.append(promise)

            for commit_type, phrases in extra_commitment_patterns.items():
                matching = next((p for p in phrases if p in text_lower), None)
                if matching:
                    timeline = self._extract_promise_timeline(text_lower)
                    promises.append(
                        PromiseCommitment(
                            type=commit_type,
                            description=self._extract_promise_description(
                                text, matching
                            ),
                            timeline=timeline,
                            turn_index=idx,
                            confidence=0.8,
                        )
                    )

        return self._dedupe_promises(promises)

    def _extract_promise_timeline(
        self,
        text: Annotated[
            str, Doc("Lowercased agent turn text to extract a timeline from.")
        ],
    ) -> Optional[str]:
        """Extract timeline from promise text.

        Tries the generic timeline extractor first, then falls back to
        language-specific promise timeline patterns (format-string based).
        """
        timeline = self._extract_timeline(text)
        if timeline:
            return timeline

        for regex, fmt in self.patterns.promise_timeline_patterns:
            if match := re.search(regex, text, re.I):
                groups = match.groups()
                formatted = fmt.format(*[g.upper() if g else g for g in groups])
                return formatted

        return None

    def _calculate_promise_confidence(
        self,
        text: Annotated[
            str,
            Doc(
                "Lowercased agent turn text used to look for confidence-boosting indicators."
            ),
        ],
        promise_type: Annotated[
            str,
            Doc(
                "Promise type label; financial types get an extra boost when a monetary amount is present."
            ),
        ],
    ) -> float:
        """Calculate confidence in promise detection."""
        confidence = 0.6

        strong_indicators = list(self.patterns.promise_confidence_strong or [])
        if any(ind in text for ind in strong_indicators):
            confidence += 0.2

        timeline_re = r"\d+ (?:day|hour)"
        if self.patterns.timeline_keywords:
            kw_alts = "|".join(re.escape(k) for k in self.patterns.timeline_keywords)
            timeline_re = rf"{timeline_re}|{kw_alts}"
        if re.search(timeline_re, text, re.I):
            confidence += 0.1

        if promise_type in ["CREDIT_PROMISE", "REFUND_PROMISE"]:
            if "$" in text or re.search(r"\d+\.?\d*", text):
                confidence += 0.1

        return min(confidence, 1.0)

    @staticmethod
    def _extract_promise_description(
        text: Annotated[
            str,
            Doc("Raw agent turn text from which the relevant sentence is extracted."),
        ],
        keyword: Annotated[
            str, Doc("The matched promise keyword used to locate the sentence.")
        ],
    ) -> str:
        """Extract the promise description around the keyword."""
        sentences = text.split(".")
        for sentence in sentences:
            if keyword in sentence.lower():
                return sentence.strip()[:150]
        return text[:150]

    _SINGLE_INSTANCE_PROMISE_TYPES = {"REFUND_PROMISE", "CREDIT_PROMISE"}
    """Promise types where only the first detected instance is kept (no timeline variants).

    These promises describe a single outcome whose timeline is set on first mention;
    a later agent turn referencing the same promise with a different timeline
    (e.g. "later today" vs "3-5 business days") would otherwise emit a conflicting token.
    """

    @staticmethod
    def _dedupe_promises(
        promises: Annotated[
            list[PromiseCommitment],
            Doc(
                "Raw list of detected promises, potentially containing duplicates of the same type."
            ),
        ],
    ) -> list[PromiseCommitment]:
        """Remove duplicate promises of the same type.

        For REFUND_PROMISE and CREDIT_PROMISE, only one instance per type is kept.
        The amount-bearing representative is preferred (more informative), since
        the same promise may be detected by both the primary token loop (with amount
        extraction) and the extra patterns loop (without). This prevents semantic
        duplicates like CREDIT_24H_20 and CREDIT_24H.

        For single-instance types, picks the best (amount-bearing) representative
        first before emitting.
        """
        seen_keys: set = set()
        unique = []

        single_best: dict = {}
        for p in promises:
            if p.type in TranscriptAnalyzer._SINGLE_INSTANCE_PROMISE_TYPES:
                existing = single_best.get(p.type)
                if existing is None or (p.amount and not existing.amount):
                    single_best[p.type] = p

        emitted_single: set = set()
        for p in promises:
            if p.type in TranscriptAnalyzer._SINGLE_INSTANCE_PROMISE_TYPES:
                if p.type not in emitted_single and p is single_best[p.type]:
                    emitted_single.add(p.type)
                    unique.append(p)
            else:
                key = (p.type, p.amount, p.timeline)
                if key not in seen_keys:
                    seen_keys.add(key)
                    unique.append(p)
        return unique

    def _infer_implicit_commitments(
        self,
        promises: list[PromiseCommitment],
        actions: list[Action],
        turns: list[Turn],
    ) -> list[PromiseCommitment]:
        """Infer commitments from action context when no explicit promise keyword was found.

        If REFUND_INITIATED is in the detected actions but no REFUND_PROMISE was
        produced by keyword matching, scan all turns for a timeline. A timeline-only
        phrase like "within 3-5 business days" is a strong refund commitment signal.
        """
        action_types = {a.type for a in actions}
        has_refund_promise = any(p.type == "REFUND_PROMISE" for p in promises)

        if "REFUND_INITIATED" in action_types and not has_refund_promise:
            for idx, turn in enumerate(turns):
                timeline = self._extract_promise_timeline(turn.text.lower())
                if timeline:
                    promises = list(promises) + [
                        PromiseCommitment(
                            type="REFUND_PROMISE",
                            description=turn.text,
                            timeline=timeline,
                            amount=None,
                            turn_index=idx,
                            confidence=0.8,
                        )
                    ]
                    break

        return promises

    @classmethod
    def _extract_domain(
        cls,
        call_info: Annotated[
            CallInfo,
            Doc("Call metadata; its `type` field is used as fallback domain signal."),
        ],
        issues: Annotated[
            list[Issue],
            Doc(
                "Extracted issues; the first issue's type drives primary domain lookup."
            ),
        ],
    ) -> Optional[str]:
        """Extract v2 DOMAIN from issues and call info.

        Issue-derived domain takes priority, except when the call type provides
        stronger signal (e.g. a SALES call should not resolve to FULFILLMENT —
        shipment keywords may have matched incidentally, such as "analytics tracking").
        In that case remaining issues are tried for a better match before falling
        back to the call-type-derived domain.

        Falls back to call_info.type only for call types that carry specific domain
        signal (not the generic SUPPORT type). Returns "UNCLASSIFIED" when no
        domain can be determined.
        """
        if issues:
            issue_type = issues[0].type
            if issue_type in ISSUE_TO_DOMAIN:
                domain = ISSUE_TO_DOMAIN[issue_type]
                if call_info.type == "SALES" and domain == "FULFILLMENT":
                    for issue in issues[1:]:
                        alt = ISSUE_TO_DOMAIN.get(issue.type)
                        if alt and alt != "FULFILLMENT":
                            return alt
                    return CALL_TYPE_TO_DOMAIN.get(call_info.type, "PRODUCT")
                return domain

        _INFORMATIVE_CALL_TYPES = {
            "BILLING",
            "TECHNICAL",
            "SALES",
            "RETENTION",
            "LOGISTICS",
            "RETURNS",
        }
        if (
            call_info.type in _INFORMATIVE_CALL_TYPES
            and call_info.type in CALL_TYPE_TO_DOMAIN
        ):
            return CALL_TYPE_TO_DOMAIN[call_info.type]

        return "UNCLASSIFIED"

    @classmethod
    def _extract_service(
        cls,
        issues: Annotated[
            list[Issue],
            Doc(
                "Extracted issues; the first issue's type is mapped to a service label."
            ),
        ],
        turns: Annotated[
            list[Turn],
            Doc(
                "Conversation turns (currently unused; reserved for future service extraction)."
            ),
        ],
    ) -> Optional[str]:
        """Extract v2 SERVICE from issues."""
        if issues:
            issue_type = issues[0].type
            if issue_type in ISSUE_TO_SERVICE:
                return ISSUE_TO_SERVICE[issue_type]
        return None

    def _extract_customer_intent(
        self,
        issues: Annotated[
            list[Issue],
            Doc(
                "Extracted issues; used as fallback when no intent is found in turn text."
            ),
        ],
        turns: Annotated[
            list[Turn],
            Doc(
                "All conversation turns; customer turns are scanned first, agent turns as fallback."
            ),
        ],
        actions: Annotated[
            Optional[list[Action]],
            Doc(
                "Extracted actions used to refine or infer the intent when keyword matching yields a generic result."
            ),
        ] = None,
    ) -> tuple[Optional[str], Optional[str]]:
        """Extract v2 CUSTOMER_INTENT from customer turns using direct keyword matching.

        Resolution order:
        1. Scan customer turns using CUSTOMER_INTENT_KEYWORDS (longest match first).
        2. Fallback 1: try agent turns (agents often restate the issue).
        3. Fallback 2: derive from issue type via ISSUE_TO_INTENT.
        4. Context-based narrowing: refine REPORT_BILLING_ISSUE using actions/issues.
        5. Fallback 3: agent-action-based inference (if agent issued a refund,
           the customer wanted one).

        Returns (primary_intent, secondary_intent).
        """
        primary = None
        secondary = None
        actions = actions or []

        customer_text = " ".join(
            t.text.lower() for t in turns if t.speaker == "customer"
        )

        intents = self._lookup_all_categories(
            customer_text, self._customer_intent_index
        )
        if intents:
            primary = intents[0]
            if len(intents) > 1:
                secondary = intents[1]

        if not primary:
            agent_text = " ".join(t.text.lower() for t in turns if t.speaker == "agent")
            intents = self._lookup_all_categories(
                agent_text, self._customer_intent_index
            )
            if intents:
                primary = intents[0]
                if len(intents) > 1:
                    secondary = intents[1]

        if not primary and issues:
            primary = ISSUE_TO_INTENT.get(issues[0].type)
            if len(issues) > 1 and not secondary:
                secondary = ISSUE_TO_INTENT.get(issues[1].type)

        if primary == "REPORT_BILLING_ISSUE":
            action_types = {a.type for a in actions}
            issue_types = {i.type for i in issues}
            if "REFUND_INITIATED" in action_types or "CREDIT_APPLIED" in action_types:
                primary = "REQUEST_REFUND"
            elif "DUPLICATE_CHARGE" in issue_types:
                primary = "REPORT_DUPLICATE_CHARGE"
            elif "UNEXPECTED_CHARGE" in issue_types:
                primary = "REPORT_UNEXPECTED_CHARGE"

        if not primary and actions:
            action_types = {a.type for a in actions}
            if "REFUND_INITIATED" in action_types or "CREDIT_APPLIED" in action_types:
                primary = "REQUEST_REFUND"

        return primary, secondary

    def _extract_context_provided(
        self,
        turns: Annotated[
            list[Turn],
            Doc(
                "All conversation turns; only customer turns are scanned for context tokens."
            ),
        ],
        call_info: Annotated[
            Optional[CallInfo],
            Doc(
                "Call metadata; the agent name is extracted to prevent it from triggering NAME_PROVIDED."
            ),
        ] = None,
    ) -> tuple[list[str], dict[str, str]]:
        """Extract v2 CONTEXT tokens indicating what information the customer provided.

        Returns a tuple of (tokens, values) where tokens is the list of context flag
        strings and values is a dict mapping each token to its extracted value (when
        available), e.g. {"EMAIL_PROVIDED": "user@example.com"}.

        Returns fact-of-information tokens without leaking PII. Agent names are
        collected first so that NAME_PROVIDED is not emitted when a customer thanks
        the agent by name.

        NAME_PROVIDED is emitted when a spaCy PERSON entity is found in a customer
        turn (excluding the agent's name) or when a name introduction pattern matches.

        OLD_NAME_PROVIDED and NEW_NAME_PROVIDED are emitted together when a
        "change X to Y" name-change pattern is detected.

        DELAY_N_DAYS is emitted when the customer mentions a number of days alongside
        delay context words (e.g. "waiting", "been", "ago", "since").

        Typographic apostrophes (U+2019) in trigger keywords are normalized to
        straight apostrophes so patterns like "hasn't" and "aren't" match correctly.
        """
        context = []
        values: dict[str, str] = {}
        seen = set()

        agent_names = set()
        if call_info and call_info.agent:
            agent_names.add(call_info.agent.lower())

        def _add(token: str, value: str | None = None):
            if token not in seen:
                context.append(token)
                seen.add(token)
            if value and token not in values:
                values[token] = value

        for turn in turns:
            if turn.speaker != "customer":
                continue
            ents = getattr(turn, "entities", {}) or {}
            text_lower = turn.text.lower()

            if ents.get("emails"):
                _add("EMAIL_PROVIDED", ents["emails"][0])

            if ents.get("phone_numbers"):
                _add("PHONE_NUMBER_PROVIDED", ents["phone_numbers"][0])

            if ents.get("account_numbers") or ents.get("accounts"):
                val = (ents.get("account_numbers") or ents.get("accounts") or [])[0]
                _add("ACCOUNT_ID_PROVIDED", val)

            if ents.get("order_numbers"):
                _add("ORDER_ID_PROVIDED", ents["order_numbers"][0])

            if ents.get("tracking_numbers"):
                _add("TRACKING_ID_PROVIDED", ents["tracking_numbers"][0])

            if ents.get("money"):
                _add("PAYMENT_AMOUNT_PROVIDED", ents["money"][0])

            if ents.get("ticket_numbers"):
                _add("TICKET_ID_PROVIDED", ents["ticket_numbers"][0])

            if ents.get("case_numbers"):
                _add("CASE_ID_PROVIDED", ents["case_numbers"][0])

            if ents.get("product_models"):
                _add("PRODUCT_ID_PROVIDED", ents["product_models"][0])

            if ents.get("escalation_ids"):
                _add("ESCALATION_ID_PROVIDED", ents["escalation_ids"][0])

            if ents.get("verification_codes"):
                _add("VERIFICATION_CODE_PROVIDED", ents["verification_codes"][0])

            doc = getattr(turn, "doc", None)
            if doc:
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        name = ent.text.lower()
                        if name not in agent_names:
                            _add("NAME_PROVIDED", ent.text)
                            break

            intro_patterns = self.patterns.name_intro_patterns or [
                r"(?:my name is|i'?m|this is)\s+([A-Z][a-z]+)"
            ]
            for pat in intro_patterns:
                m = re.search(pat, text_lower)
                if m:
                    _add("NAME_PROVIDED", m.group(1) if m.lastindex else None)
                    break

            name_change_patterns = self.patterns.name_change_patterns or [
                r"\b(?:change|update)\s+(?:my\s+)?(?:name\s+)?(?:from\s+)?(\w+)\s+to\s+(\w+)"
            ]
            for pat in name_change_patterns:
                m = re.search(pat, text_lower)
                if m:
                    _add(
                        "OLD_NAME_PROVIDED",
                        m.group(1) if m.lastindex and m.lastindex >= 1 else None,
                    )
                    _add(
                        "NEW_NAME_PROVIDED",
                        m.group(2) if m.lastindex and m.lastindex >= 2 else None,
                    )
                    break

            delay_match = re.search(r"\b(\d+)\s*days?\b", text_lower)
            delay_context = self.patterns.delay_context_words or [
                "waiting",
                "been",
                "ago",
                "since",
            ]
            if delay_match and any(w in text_lower for w in delay_context):
                days = delay_match.group(1)
                _add(f"DELAY_{days}_DAYS")

        return context, values

    def _extract_trigger_cause(
        self,
        turns: Annotated[
            list[Turn],
            Doc("All conversation turns; only the first 3 customer turns are scanned."),
        ],
    ) -> Optional[str]:
        """Extract the trigger cause — why the customer contacted support.

        Scans only the first 3 customer turns for causal indicators (locked fields,
        missing delivery, price increases, etc.) using TRIGGER_CAUSE_KEYWORDS sorted
        longest-first. The trigger is the first actionable customer request and is
        locked after extraction — it is not inferred from the outcome.

        Typographic apostrophes (U+2019) are normalized to straight apostrophes so
        keywords like "hasn't" and "aren't" match transcript text correctly.
        """
        trigger_index = sorted(
            [
                (kw.lower(), cause)
                for cause, kws in TRIGGER_CAUSE_KEYWORDS.items()
                for kw in kws
            ],
            key=lambda x: len(x[0]),
            reverse=True,
        )

        early_customer_turns = [t for t in turns if t.speaker == "customer"][:3]
        customer_text = " ".join(t.text.lower() for t in early_customer_turns)
        customer_text = customer_text.replace("\u2019", "'")

        for kw, cause in trigger_index:
            if kw in customer_text:
                return cause

        return None

    @classmethod
    def _extract_system_actions(
        cls,
        turns: Annotated[
            list[Turn],
            Doc(
                "All conversation turns; system and agent turns are combined and scanned for system action keywords."
            ),
        ],
    ) -> list[str]:
        """Extract v2 SYSTEM_ACTIONS from system turns and agent references."""
        actions = []
        seen = set()

        system_text = " ".join(
            t.text.lower() for t in turns if t.speaker in ("system", "agent")
        )

        for action, keywords in SYSTEM_ACTION_KEYWORDS.items():
            if action not in seen and any(kw in system_text for kw in keywords):
                actions.append(action)
                seen.add(action)
        return actions
