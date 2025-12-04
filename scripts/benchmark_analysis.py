"""
Benchmark Analyzer: CLM vs Natural Language (NL)
------------------------------------------------
This script compares CLM and NL performance across models,
showing quantitative and qualitative insights for:
- Latency
- Cost
- Accuracy
- Token efficiency

It produces:
1. Summary statistics table
2. Visual comparison charts
3. Relative efficiency improvement percentages
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# === Configuration ===
BENCHMARK_FILE = Path("clm_vs_nl.json")  # update path if needed

# === Load and prepare data ===
with open(BENCHMARK_FILE, "r") as f:
    raw_data = json.load(f)

# Filter out empty entries
data = {k: v for k, v in raw_data.items() if v.get("clm") or v.get("nl")}

# Flatten into DataFrame
records = []
for model, results in data.items():
    for approach, samples in results.items():
        for s in samples:
            s = {k.lower(): v for k, v in s.items()}
            s.update({"model": model, "approach": approach})
            records.append(s)

if not records:
    raise ValueError("No non-empty benchmark data found in file.")

df = pd.DataFrame(records)

# === Compute summary stats ===
metrics = ["latency_ms", "cost_usd", "accuracy", "tokens_used"]
summary = (
    df.groupby(["model", "approach"])[metrics]
    .mean()
    .reset_index()
    .pivot(index="model", columns="approach")
)

# Flatten multiindex columns
summary.columns = [f"{a}_{b}" for a, b in summary.columns]
summary.reset_index(inplace=True)


# === Efficiency Gains (CLM vs NL) ===
def pct_diff(nl, clm):
    try:
        return round((nl - clm) / nl * 100, 2)
    except ZeroDivisionError:
        return None


summary["latency_gain_%"] = summary.apply(
    lambda x: pct_diff(x.get("latency_ms_nl", 0), x.get("latency_ms_clm", 0)), axis=1
)
summary["cost_gain_%"] = summary.apply(
    lambda x: pct_diff(x.get("cost_usd_nl", 0), x.get("cost_usd_clm", 0)), axis=1
)
summary["accuracy_delta"] = summary.get("accuracy_clm", 0) - summary.get(
    "accuracy_nl", 0
)
summary["token_efficiency_%"] = summary.apply(
    lambda x: pct_diff(x.get("tokens_used_nl", 0), x.get("tokens_used_clm", 0)), axis=1
)

print("\n=== Quantitative Summary (per model) ===")
print(summary.round(3))

# === Global Averages ===
global_means = (
    summary[[c for c in summary.columns if any(m in c for m in metrics)]]
    .mean()
    .round(3)
)
print("\n=== Global Averages (CLM vs NL) ===")
print(global_means)

# === Visual Comparisons ===
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
plt.suptitle("CLM vs Natural Language Benchmark Results", fontsize=14, weight="bold")

# Plot latency, cost, accuracy averages
for i, metric in enumerate(["latency_ms", "cost_usd", "accuracy"]):
    means = df.groupby("approach")[metric].mean()
    means.plot(
        kind="bar", ax=axes[i], title=f"Average {metric.replace('_', ' ').title()}"
    )
    axes[i].set_ylabel(metric.split("_")[0].title())

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# === Qualitative Summary (printed) ===
print("\n=== Qualitative Insights ===")
if summary["accuracy_delta"].mean() >= 0:
    print(
        "✅ CLM maintains or slightly improves output quality compared to Natural Language."
    )
else:
    print(
        "⚠️ CLM shows slight degradation in quality, depending on model or test domain."
    )

if summary["latency_gain_%"].mean() > 0:
    print(f"⚡ Average latency improvement: {summary['latency_gain_%'].mean():.2f}%")
if summary["cost_gain_%"].mean() > 0:
    print(f"💰 Average cost reduction: {summary['cost_gain_%'].mean():.2f}%")
if summary["token_efficiency_%"].mean() > 0:
    print(
        f"🔹 Average token efficiency gain: {summary['token_efficiency_%'].mean():.2f}%"
    )

print("\nDone ✅ — All results computed and visualized.")
