# Fixes and improvements:

1. State Logic Violations (Still Present)
Case 1 — Duplicate Charge
[RESOLUTION:REFUND_INITIATED]
[STATE:RESOLVED]

This violates the rule:
Refund initiated ≠ resolved.

It should be:
[RESOLUTION:REFUND_INITIATED]
[STATE:PENDING_REFUND]

Case 2 — Fee Waived
Duplicated commitments again:
[COMMITMENT:CREDIT_24H_20]
[COMMITMENT:CREDIT_24H]

- Issue here: Your validation layer is still not preventing semantic duplicates.

2. Missing Trigger in Some Cases (See transcripts_v2.json)

Missing it:
Refund delay escalation (Jason)
Replacement follow-up (Nina)
Sync failure (Ryan)
Security case

Trigger must exist in 100% of interactions.

3. Sales Case (Laura) — Still Underspecified
Current:

[AGENT_ACTIONS:DISCOUNT_APPLIED→TRIAL_ACTIVATED]

Missing:
ADDON_OFFERED
DISCOUNT_OFFERED

Captured acceptance but not the persuasion steps.
For sales intelligence, this matters.

Better:
ADDON_OFFERED→DISCOUNT_OFFERED→TRIAL_ACTIVATED

4. Premium Upgrade (Chloe) — Missing Monetization Artifacts
failed to capture pricing artifacts:
$49 monthly
$480 annual

Those should be:
[ARTIFACT:AMT=$49/MONTH]
[ARTIFACT:AMT=$480/YEAR]

5. Security Case — Operational Semantics Weak
Current:

[RESOLUTION:LOGIN_RESTORED]
[STATE:RESOLVED]

But the real operational changes were:
ACCOUNT_LOCKED
PASSWORD_RESET
TWO_FACTOR_ENABLED
SESSION_REVOKED

Compressed too aggressively.
This removes security-level traceability.

6. Outage Restoration Case — Underreporting Monetization
This one is important.

Original included:
“I’ll extend your billing cycle by five days.”

Compressed:
[COMMITMENT:BILLING_EXTENSION_3H]

Two problems:
Wrong duration (3H instead of 5 days)
Did not mark it as a state or resolution change

This should include:
[AGENT_ACTIONS:BILLING_EXTENSION_APPLIED]
[ARTIFACT:BILLING_EXTENSION=5_DAYS]