CLM Action Matcher
Threshold: score ≥ 3  |  Weights: domain/intent=3, trigger/service=2, turnType=1
NLP Model Loaded <spacy.lang.en.English object at 0x10ccc52b0>
2026-06-30 21:35:22 | INFO    89987 | quick_start_demo:encode:153 - Resolved format: free_form

──────────────────────────────────────────────────────────────────────
  Turn : I noticed my account was charged twice this month — one on the 2nd and another on the 3rd.
  CLM  : domain=BILLING  intent=REPORT_DUPLICATE_CHARGE  trigger=DUPLICATE_CHARGE  service=PAYMENT  turn_type=None  (0%)
──────────────────────────────────────────────────────────────────────
  [★ best match]  score=10  ACT-001: Billing Issue Resolution
           matched on: domain=BILLING, customerIntent=REPORT_DUPLICATE_CHARGE, supportTrigger=DUPLICATE_CHARGE, service=PAYMENT
  [  match 2]  score=10  ACT-007: Refund Processing
           matched on: domain=BILLING, customerIntent=REPORT_DUPLICATE_CHARGE, supportTrigger=DUPLICATE_CHARGE, service=PAYMENT
  [  match 3]  score=3  ACT-003: Cancellation Retention
           matched on: domain=BILLING
  [  match 4]  score=3  ACT-006: Complaint Escalation
           matched on: domain=BILLING

2026-06-30 21:35:22 | INFO    89987 | quick_start_demo:encode:153 - Resolved format: free_form

──────────────────────────────────────────────────────────────────────
  Turn : I'm calling to complain about a duplicated charge on my account. I need this fixed immediately.
  CLM  : domain=BILLING  intent=REPORT_BILLING_ISSUE  trigger=None  service=PAYMENT  turn_type=None  (0%)
──────────────────────────────────────────────────────────────────────
  [★ best match]  score=5  ACT-001: Billing Issue Resolution
           matched on: domain=BILLING, service=PAYMENT
  [  match 2]  score=5  ACT-007: Refund Processing
           matched on: domain=BILLING, service=PAYMENT
  [  match 3]  score=3  ACT-003: Cancellation Retention
           matched on: domain=BILLING
  [  match 4]  score=3  ACT-006: Complaint Escalation
           matched on: domain=BILLING

2026-06-30 21:35:22 | INFO    89987 | quick_start_demo:encode:153 - Resolved format: free_form

──────────────────────────────────────────────────────────────────────
  Turn : I just signed up and I have no idea how to get started, can you walk me through it?
  CLM  : domain=UNCLASSIFIED  intent=None  trigger=None  service=None  turn_type=None  (0%)
──────────────────────────────────────────────────────────────────────
  → No matching actions above threshold

2026-06-30 21:35:22 | INFO    89987 | quick_start_demo:encode:153 - Resolved format: free_form

──────────────────────────────────────────────────────────────────────
  Turn : I want to cancel my subscription right now, this service is terrible.
  CLM  : domain=SUBSCRIPTION  intent=REQUEST_CANCELLATION  trigger=REQUEST_CANCELLATION  service=None  turn_type=None  (0%)
──────────────────────────────────────────────────────────────────────
  [★ best match]  score=3  ACT-003: Cancellation Retention
           matched on: customerIntent=REQUEST_CANCELLATION

2026-06-30 21:35:22 | INFO    89987 | quick_start_demo:encode:153 - Resolved format: free_form

──────────────────────────────────────────────────────────────────────
  Turn : I'm thinking of leaving. This isn't really what I expected.
  CLM  : domain=UNCLASSIFIED  intent=None  trigger=None  service=None  turn_type=None  (0%)
──────────────────────────────────────────────────────────────────────
  → No matching actions above threshold

2026-06-30 21:35:22 | INFO    89987 | quick_start_demo:encode:153 - Resolved format: free_form

──────────────────────────────────────────────────────────────────────
  Turn : Why can't I log into my account? I keep getting an error message.
  CLM  : domain=UNCLASSIFIED  intent=None  trigger=SYSTEM_ERROR  service=None  turn_type=None  (0%)
──────────────────────────────────────────────────────────────────────
  → No matching actions above threshold

2026-06-30 21:35:22 | INFO    89987 | quick_start_demo:encode:153 - Resolved format: free_form

──────────────────────────────────────────────────────────────────────
  Turn : Your agent promised me a refund two weeks ago and I still haven't received anything.
  CLM  : domain=FULFILLMENT  intent=FOLLOWUP_REPLACEMENT_STATUS  trigger=None  service=None  turn_type=None  (0%)
──────────────────────────────────────────────────────────────────────
  → No matching actions above threshold
