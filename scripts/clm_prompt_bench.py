"""
CLM Benchmark Runner
=====================

Runs a set of task prompts -- each defined in both CLM-compressed form and
plain natural-language (NL) form -- against two OpenAI models, and records
token usage, latency, cost, and a structural-accuracy score for every run.

Output is written in the same shape your `clm_vs_nl.json` benchmark file
already uses, so it drops straight into your existing analyzer notebook:

    { "<model>": { "clm": [ {..sample..}, ... ], "nl": [ {..sample..}, ... ] } }

Why this shape: your notebook's `groupby(["model", "approach"])` step expects
exactly this nesting, and auto-detects numeric columns (n_tokens, latency,
input_tokens, output_tokens, cost_usd, accuracy) -- this script emits all of
those per sample.

Usage
-----
    pip install openai
    export OPENAI_API_KEY=sk-...

    python clm_benchmark_runner.py                       # full run, live API
    python clm_benchmark_runner.py --dry-run              # no API calls, sanity-check plumbing
    python clm_benchmark_runner.py --repeats 3             # average over 3 calls per (task, approach, model)
    python clm_benchmark_runner.py --models gpt-4o         # single model
    python clm_benchmark_runner.py --tasks qa_compliance_scoring
    python clm_benchmark_runner.py --output my_run.json

Notes on "accuracy"
--------------------
There's no ground-truth grading in a script that doesn't know your labels.
`grade_response()` below is a *proxy*, in two layers:

1. Key presence -- did the expected keys (including nested ones) show up
   in the parsed JSON at all.
2. Value validity -- for any field with a declared constraint (numeric
   range or enum, set via `Task.value_constraints`), does the actual value
   satisfy it.

This catches a real failure mode compression can introduce: a terse
`OUT:JSON` schema like `risk_score:FLOAT` carries no information about
what a valid float looks like, where the natural-language equivalent
("a float from 0.0 to 1.0") does -- so a model can return `risk_score: 2.5`
and a presence-only grader would still call that "accuracy: 1.0". Tasks
below embed the same constraints in both the CLM (`FLOAT[0-1]`,
`ENUM[LOW,MEDIUM,HIGH]`) and NL prompts, and the grader checks both.

This still isn't semantic correctness -- it tells you "the model followed
the schema and stayed in-bounds", not "the QA score was right". Swap
`Task.grader` for an LLM-judge or your own labeled eval if you need that.
The rest of the pipeline (timing, tokens, cost) doesn't change.

Pricing
-------
PRICING below is hardcoded from OpenAI's published per-token rates checked
July 2026 (gpt-4o: $2.50/$10.00 per 1M input/output tokens; gpt-4o-mini:
$0.15/$0.60 per 1M input/output tokens). Prices change -- update PRICING or
pass --price-per-1m-override if these are stale by the time you run this.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional


# =====================================================================
# Pricing (USD per 1,000,000 tokens). Update if OpenAI's rates change.
# =====================================================================
PRICING: dict[str, dict[str, float]] = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}

DEFAULT_MODELS = ["gpt-4o", "gpt-4o-mini"]


# =====================================================================
# Grading
# =====================================================================
def _extract_json(text: str) -> Optional[dict]:
    """Pull a JSON object out of a model response, tolerating ```json fences."""
    text = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        # fall back to first {...} block in the text
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def _get_path(obj: Any, path: list[str]) -> tuple[Any, bool]:
    """Walk a dotted path through nested dicts. Returns (value, found)."""
    cur = obj
    for part in path:
        if not isinstance(cur, dict) or part not in cur:
            return None, False
        cur = cur[part]
    return cur, True


def grade_structural_validity(response_text: str, expected_keys: list[str]) -> float:
    """
    Proxy accuracy score: fraction of expected keys present in the parsed
    JSON output. Supports dotted paths for nested keys, e.g. "qa_scores.verification".
    Returns 0.0 if the response isn't valid/parseable JSON at all.

    Kept as a standalone, simple building block -- `grade_response()` below
    is the richer default grader (adds value-constraint checking) and is
    what tasks actually use unless you override `Task.grader`.
    """
    parsed = _extract_json(response_text)
    if parsed is None or not isinstance(parsed, dict):
        return 0.0
    if not expected_keys:
        return 1.0
    hits = sum(1 for key in expected_keys if _get_path(parsed, key.split("."))[1])
    return round(hits / len(expected_keys), 4)


def check_value_constraints(parsed: dict, value_constraints: dict[str, tuple]) -> tuple[float, list[str]]:
    """
    Checks declared value constraints against a parsed JSON response.

    value_constraints maps a dotted key path to one of:
        ("range", lo, hi)          -- value must parse as float and satisfy lo <= v <= hi
        ("enum", [choices])        -- value must case-insensitively match one of choices

    Returns (validity_score, issues). Fields whose key is missing entirely are
    skipped here (that's already penalized by key-presence scoring) so they
    aren't double-counted. validity_score is 1.0 if there's nothing to check.
    """
    if not value_constraints:
        return 1.0, []

    checked = 0
    valid = 0
    issues: list[str] = []

    for key, constraint in value_constraints.items():
        value, found = _get_path(parsed, key.split("."))
        if not found:
            continue  # missing key already penalized by key-presence score
        checked += 1
        kind = constraint[0]

        if kind == "range":
            _, lo, hi = constraint
            try:
                v = float(value)
            except (TypeError, ValueError):
                issues.append(f"{key}={value!r} is not numeric (expected range [{lo}, {hi}])")
                continue
            if lo <= v <= hi:
                valid += 1
            else:
                issues.append(f"{key}={value} outside range [{lo}, {hi}]")

        elif kind == "enum":
            _, choices = constraint
            v = str(value).strip().upper()
            allowed = {c.upper() for c in choices}
            if v in allowed:
                valid += 1
            else:
                issues.append(f"{key}={value!r} not in {choices}")

        else:
            raise ValueError(f"Unknown constraint kind: {kind!r} for key {key!r}")

    if checked == 0:
        return 1.0, []
    return round(valid / checked, 4), issues


def grade_response(response_text: str, task: "Task") -> dict:
    """
    Default grader. Combines key-presence and value-constraint checks into
    one score, but reports both components separately so you can tell which
    one failed.

    Returns:
        {
            "accuracy": float,              # key_presence_score * value_validity_score
            "key_presence_score": float,
            "value_validity_score": float,
            "issues": list[str],            # human-readable, e.g. "risk_score=2.5 outside [0.0, 1.0]"
        }
    """
    parsed = _extract_json(response_text)
    if parsed is None or not isinstance(parsed, dict):
        return {
            "accuracy": 0.0,
            "key_presence_score": 0.0,
            "value_validity_score": 0.0,
            "issues": ["response is not valid/parseable JSON"],
        }

    issues: list[str] = []
    if task.expected_keys:
        missing = [key for key in task.expected_keys if not _get_path(parsed, key.split("."))[1]]
        issues.extend(f"missing key: {key}" for key in missing)
        key_presence_score = round((len(task.expected_keys) - len(missing)) / len(task.expected_keys), 4)
    else:
        key_presence_score = 1.0

    value_validity_score, value_issues = check_value_constraints(parsed, task.value_constraints)
    issues.extend(value_issues)

    accuracy = round(key_presence_score * value_validity_score, 4)
    return {
        "accuracy": accuracy,
        "key_presence_score": key_presence_score,
        "value_validity_score": value_validity_score,
        "issues": issues,
    }


# =====================================================================
# Task definitions
# =====================================================================
@dataclass
class Task:
    id: str
    description: str
    clm_system_prompt: str
    nl_system_prompt: str
    user_input: str
    expected_keys: list[str] = field(default_factory=list)
    # dotted key path -> ("range", lo, hi) | ("enum", [choices])
    value_constraints: dict[str, tuple] = field(default_factory=dict)
    grader: Callable[[str, "Task"], dict] = grade_response


TRANSCRIPT_INTERNET_OUTAGE = """\
Agent: Good morning, thank you for calling TechCorp support. My name is Sarah. How can I help you today?
Customer: Hi Sarah, I've been having issues with my internet connection for the past three days. It keeps dropping every few hours, and I work from home so this is really frustrating.
Agent: I totally understand how important that is. Let's get this sorted. Could I have your account number, please?
Customer: Sure, it's 847-392-1045.
Agent: Thanks. I see you're on the Premium 500 plan. When the connection drops, do all your devices lose internet, or just one?
Customer: Everything -- my laptop, my wife's phone, even the TV.
Agent: Got it. I'm running a quick diagnostic on your modem... okay, it looks like a line fluctuation issue in your area. We've had similar reports from nearby addresses.
Customer: So it's not just me?
Agent: Correct. A technician is already assigned to inspect the local node this afternoon. I've added your account to that ticket so you'll be notified once it's resolved.
Customer: Great. Will I need to reboot anything?
Agent: Once service stabilizes, just unplug your modem for 30 seconds and plug it back in. That will refresh your connection.
Customer: Perfect. Thanks for the help.
"""

TRANSCRIPT_BILLING_DISPUTE = """\
Agent: Hello, this is Daniel from MobileWave billing. How can I help you today?
Customer: Hi Daniel, I was charged twice for my plan this month. I only have one line, so I'm not sure why.
Agent: I see how that's confusing. Let's check it out. What's your account ID?
Customer: MW-55983.
Agent: Thanks. I see two identical payments for $89.99 -- one on the 2nd and one on the 4th. Looks like a duplicate authorization error.
Customer: Can that be fixed?
Agent: Yes, I'm submitting a refund request right now. You'll see the refund within 3-5 business days. I'll also apply a $10 courtesy credit for the inconvenience.
Customer: Wow, thanks so much.
Agent: My pleasure. Anything else I can assist with today?
Customer: Nope, that's all. Appreciate it!
"""

TRANSCRIPT_ACCOUNT_HACKED = """\
Agent: Hello, thank you for calling GameHub Security. My name is Leo. How can I assist you?
Customer: Hi Leo, I think my account got hacked. I can't log in, and I got an email saying my password was changed.
Agent: That's concerning. Can I get your original email address?
Customer: Yes, it's skylar83@outlook.com.
Agent: Thank you. I'm checking... yep, there's unauthorized access from a foreign IP. I'll temporarily freeze the account and revert your email to the original.
Customer: Thank you. Can you also make sure none of my purchases were used?
Agent: Yes -- I see one suspicious purchase for $49.99. I've flagged it for refund. You'll receive an email confirmation and a password reset link in a few minutes.
Customer: Awesome. Really appreciate the help.
Agent: My pleasure. Security first!
"""


TASKS: list[Task] = [
    Task(
        id="qa_compliance_scoring",
        description="Score agent compliance across QA categories from a call transcript.",
        clm_system_prompt=(
            "[REQ:ANALYZE>RANK] [TARGET:TRANSCRIPT:DOMAIN=QA:TOPIC=COMPLIANCE] "
            "[EXTRACT:VERIFICATION,POLICY_ADHERENCE,SOFT_SKILLS,VIOLATIONS] "
            "[OUT:JSON:{summary:STR,qa_scores:{verification:FLOAT[0-1],policy_adherence:FLOAT[0-1],"
            "soft_skills:FLOAT[0-1]},violations:[STR]}]"
        ),
        nl_system_prompt=(
            "You are a QA compliance analyst. Analyze the call transcript and score the "
            "agent's compliance across the required QA categories.\n\n"
            "Analysis criteria:\n"
            "- Mandatory disclosures and verification steps\n"
            "- Policy adherence\n"
            "- Soft-skill behaviors (empathy, clarity, ownership)\n"
            "- Compliance violations or risks\n\n"
            'Output valid JSON with this structure: a "summary" field (string), a '
            '"qa_scores" object containing "verification", "policy_adherence", and '
            '"soft_skills" as floats (0.0-1.0), and a "violations" field as an array of strings.'
        ),
        user_input=TRANSCRIPT_INTERNET_OUTAGE,
        expected_keys=[
            "summary",
            "qa_scores.verification",
            "qa_scores.policy_adherence",
            "qa_scores.soft_skills",
            "violations",
        ],
        value_constraints={
            "qa_scores.verification": ("range", 0.0, 1.0),
            "qa_scores.policy_adherence": ("range", 0.0, 1.0),
            "qa_scores.soft_skills": ("range", 0.0, 1.0),
        },
    ),
    Task(
        id="call_summary_extraction",
        description="Extract structured call metadata (domain, intent, sentiment) from a transcript.",
        clm_system_prompt=(
            "[REQ:EXTRACT] [TARGET:TRANSCRIPT:DOMAIN=SUPPORT] "
            "[EXTRACT:DOMAIN,SERVICE,CUSTOMER_INTENT,SUPPORT_TRIGGER,SENTIMENT] "
            "[OUT:JSON:{domain:STR,service:STR,customerIntent:STR,supportTrigger:STR,sentiment:STR}]"
        ),
        nl_system_prompt=(
            "You are a call analytics extractor. Read the call transcript and extract "
            "structured metadata about the interaction.\n\n"
            "Extract the following fields:\n"
            "- domain: the general category of the call\n"
            "- service: the specific product or service involved\n"
            "- customerIntent: what the customer was trying to accomplish\n"
            "- supportTrigger: the event or symptom that caused the customer to reach out\n"
            "- sentiment: the customer's overall sentiment (e.g. FRUSTRATED, NEUTRAL, SATISFIED)\n\n"
            'Output valid JSON with exactly these fields: "domain", "service", "customerIntent", '
            '"supportTrigger", "sentiment" (all strings).'
        ),
        user_input=TRANSCRIPT_BILLING_DISPUTE,
        expected_keys=["domain", "service", "customerIntent", "supportTrigger", "sentiment"],
    ),
    Task(
        id="escalation_risk_classification",
        description="Classify escalation risk and recommend a next action from a transcript.",
        clm_system_prompt=(
            "[REQ:ANALYZE>CLASSIFY] [TARGET:TRANSCRIPT:DOMAIN=SUPPORT] "
            "[OUT:JSON:{escalation_risk:ENUM[LOW,MEDIUM,HIGH],risk_score:FLOAT[0-1],"
            "recommended_action:STR}]"
        ),
        nl_system_prompt=(
            "You are a support triage analyst. Read the call transcript and assess whether "
            "this interaction carries a risk of escalation (e.g. churn, complaint escalation, "
            "security exposure).\n\n"
            'Output valid JSON with these fields: "escalation_risk" (one of LOW, MEDIUM, HIGH), '
            '"risk_score" (a float from 0.0 to 1.0), and "recommended_action" (a short string '
            "describing the next best action for the agent or team)."
        ),
        user_input=TRANSCRIPT_ACCOUNT_HACKED,
        expected_keys=["escalation_risk", "risk_score", "recommended_action"],
        value_constraints={
            "escalation_risk": ("enum", ["LOW", "MEDIUM", "HIGH"]),
            "risk_score": ("range", 0.0, 1.0),
        },
    ),
]


# =====================================================================
# Runner
# =====================================================================
def call_model(
    client,
    model: str,
    system_prompt: str,
    user_input: str,
    temperature: float = 0.0,
    max_retries: int = 3,
) -> tuple[str, dict[str, int], float]:
    """
    Calls the OpenAI Chat Completions API once. Returns (response_text, usage_dict, latency_seconds).
    Retries with exponential backoff on transient errors.
    """
    last_err = None
    for attempt in range(max_retries):
        try:
            start = time.perf_counter()
            resp = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
            )
            latency = time.perf_counter() - start
            text = resp.choices[0].message.content or ""
            usage = {
                "input_tokens": resp.usage.prompt_tokens,
                "output_tokens": resp.usage.completion_tokens,
                "n_tokens": resp.usage.total_tokens,
            }
            return text, usage, latency
        except Exception as e:  # noqa: BLE001 - deliberately broad, this is a benchmark harness
            last_err = e
            sleep_s = 2 ** attempt
            print(f"    [retry {attempt + 1}/{max_retries}] {model} error: {e} (sleeping {sleep_s}s)")
            time.sleep(sleep_s)
    raise RuntimeError(f"Failed to call {model} after {max_retries} attempts: {last_err}")


def mock_call_model(model: str, system_prompt: str, user_input: str) -> tuple[str, dict[str, int], float]:
    """Dry-run stand-in for call_model -- no network calls, deterministic fake usage."""
    text = json.dumps({"_dry_run": True, "model": model})
    approx_in = len(system_prompt.split()) + len(user_input.split())
    approx_out = 20
    usage = {
        "input_tokens": approx_in,
        "output_tokens": approx_out,
        "n_tokens": approx_in + approx_out,
    }
    return text, usage, 0.01


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    rates = PRICING.get(model)
    if not rates:
        return 0.0
    return round(
        (input_tokens / 1_000_000) * rates["input"] + (output_tokens / 1_000_000) * rates["output"],
        6,
    )


def run_benchmark(
    tasks: list[Task],
    models: list[str],
    repeats: int = 1,
    temperature: float = 0.0,
    dry_run: bool = False,
) -> dict[str, dict[str, list[dict]]]:
    client = None
    if not dry_run:
        from openai import OpenAI  # imported lazily so --dry-run works without the package/key

        client = OpenAI()

    results: dict[str, dict[str, list[dict]]] = {m: {"clm": [], "nl": []} for m in models}

    total_calls = len(tasks) * len(models) * 2 * repeats
    done = 0

    for task in tasks:
        for approach, system_prompt in (("clm", task.clm_system_prompt), ("nl", task.nl_system_prompt)):
            for model in models:
                for rep in range(repeats):
                    done += 1
                    print(f"[{done}/{total_calls}] task={task.id} approach={approach} model={model} rep={rep + 1}")

                    if dry_run:
                        text, usage, latency = mock_call_model(model, system_prompt, task.user_input)
                    else:
                        text, usage, latency = call_model(
                            client, model, system_prompt, task.user_input, temperature=temperature
                        )

                    grade = task.grader(text, task)
                    cost = cost_usd(model, usage["input_tokens"], usage["output_tokens"])

                    if grade["issues"]:
                        print(f"    issues: {grade['issues']}")

                    sample = {
                        "task_id": task.id,
                        "approach": approach,
                        "model": model,
                        "repeat": rep,
                        "n_tokens": usage["n_tokens"],
                        "input_tokens": usage["input_tokens"],
                        "output_tokens": usage["output_tokens"],
                        "tokens_used": usage["n_tokens"],
                        "latency": round(latency, 4),
                        "cost_usd": cost,
                        "accuracy": grade["accuracy"],
                        "key_presence_score": grade["key_presence_score"],
                        "value_validity_score": grade["value_validity_score"],
                        "grading_issues": grade["issues"],
                        "response_preview": text[:300],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                    results[model][approach].append(sample)

    return results


# =====================================================================
# CLI
# =====================================================================
def main() -> None:
    parser = argparse.ArgumentParser(description="Run CLM-compressed vs NL prompts across OpenAI models.")
    parser.add_argument(
        "--models",
        type=str,
        default=",".join(DEFAULT_MODELS),
        help=f"Comma-separated OpenAI model names (default: {','.join(DEFAULT_MODELS)})",
    )
    parser.add_argument(
        "--tasks",
        type=str,
        default="",
        help="Comma-separated task ids to run (default: all tasks). "
        f"Available: {', '.join(t.id for t in TASKS)}",
    )
    parser.add_argument("--repeats", type=int, default=1, help="Number of calls per (task, approach, model).")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--output", type=str, default="clm_vs_nl_live.json")
    parser.add_argument(
        "--dry-run", action="store_true", help="Skip real API calls; sanity-check the pipeline and output shape."
    )
    args = parser.parse_args()

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if args.tasks:
        wanted = {t.strip() for t in args.tasks.split(",") if t.strip()}
        tasks = [t for t in TASKS if t.id in wanted]
        missing = wanted - {t.id for t in tasks}
        if missing:
            print(f"Unknown task id(s): {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
    else:
        tasks = TASKS

    if not args.dry_run:
        import os

        if not os.environ.get("OPENAI_API_KEY"):
            print("OPENAI_API_KEY is not set. Export it, or run with --dry-run to test the pipeline.", file=sys.stderr)
            sys.exit(1)

    results = run_benchmark(
        tasks=tasks,
        models=models,
        repeats=args.repeats,
        temperature=args.temperature,
        dry_run=args.dry_run,
    )

    out_path = Path(args.output)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nWrote {out_path.resolve()}")
    print("This file's shape matches clm_vs_nl.json -- point your existing analyzer notebook at it directly.")


if __name__ == "__main__":
    main()
