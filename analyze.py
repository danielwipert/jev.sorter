"""Analyze decision logs: accuracy, confused pairs, threshold curve, calibration, spend.

Examples:
  python analyze.py                                     # every log in logs/
  python analyze.py logs/decisions_jev_tuning_v1.csv    # one log

Thresholds (spec Section 8) always come from the model's TUNING log for the same
description version, and are applied unchanged to whichever log is being analyzed.
Every answer is re-gated with gate.py, so a change to the gate applies to old logs too.
"""

import json
import math
import sys
from pathlib import Path

import pandas as pd

from gate import gate

TARGETS = [50, 70, 85]  # auto-accept rates, in percent
BANDS = [(0, 49), (50, 59), (60, 69), (70, 79), (80, 89), (90, 100)]
TOP_PAIRS = 8
EXAMPLES_PER_PAIR = 3


def load_log(path):
    """Read a log and re-run gate checks 1-3 on every row."""
    # Read everything as text (so "true" stays "true" and an empty prediction stays ""), then convert.
    log = pd.read_csv(path, dtype=str, keep_default_na=False)
    log["confidence"] = pd.to_numeric(log["confidence"])
    log["cost_usd"] = pd.to_numeric(log["cost_usd"])
    log["is_correct"] = log["is_correct"] == "true"
    categories = json.loads(Path(f"categories/{log['categories_version'].iloc[0]}.json").read_text())
    keywords = json.loads(Path(f"keywords/{log['keywords_version'].iloc[0]}.json").read_text())
    gated = [gate(r.message_text, r.predicted, r.confidence, categories, keywords) for r in log.itertuples()]
    log["passes_checks"] = [result == "auto_accept" for result, _, _ in gated]
    log["reason"] = [reason for _, reason, _ in gated]
    log["keyword_miss"] = [miss for _, _, miss in gated]
    log.attrs.update(categories=categories, keywords=keywords)
    return log


def tuning_log_for(path):
    """logs/decisions_{model}_{set}_{categories}.csv -> the same model and version on tuning."""
    model, _, version = Path(path).stem.removeprefix("decisions_").split("_")
    return Path(f"logs/decisions_{model}_tuning_{version}.csv")


def thresholds_from(tuning):
    """Section 8: confidence at which 50/70/85% of ALL tuning messages would be auto-accepted."""
    passing = tuning[tuning["passes_checks"]].sort_values(["confidence", "message_id"], ascending=[False, True])
    result = {}
    for target in TARGETS:
        k = math.ceil(len(tuning) * target / 100)
        # If too few answers pass checks 1-3 to reach the target, accept every one that passes.
        result[target] = passing["confidence"].iloc[min(k, len(passing)) - 1] if len(passing) else math.inf
    return result


def curve(log, thresholds):
    rows = []
    for target, threshold in thresholds.items():
        accepted = [
            gate(r.message_text, r.predicted, r.confidence, log.attrs["categories"], log.attrs["keywords"], threshold)[0]
            == "auto_accept"
            for r in log.itertuples()
        ]
        accepted = log[accepted]
        accuracy = accepted["is_correct"].mean() if len(accepted) else float("nan")
        rows.append({
            "target_auto_accept": f"{target}%",
            "threshold": threshold,
            "realized_auto_accept": f"{len(accepted) / len(log):.1%}",
            "accuracy_on_auto_accepted": f"{accuracy:.1%}",
            "soft_hallucination_rate": f"{1 - accuracy:.1%}",
            "hard_hallucination_rate": f"{(log['reason'] == 'invalid_category').mean():.1%}",
        })
    return pd.DataFrame(rows)


def confused_pairs(log):
    wrong = log[~log["is_correct"] & (log["reason"] != "invalid_category")]
    pair = wrong.apply(lambda r: " <> ".join(sorted([r["correct"], r["predicted"]])), axis=1)
    return wrong.assign(pair=pair).groupby("pair", sort=False)


def calibration(log):
    rows = []
    for low, high in BANDS:
        band = log[(log["confidence"] >= low) & (log["confidence"] < high + 1)]
        rows.append({
            "confidence_band": f"{low}-{high}",
            "messages": len(band),
            "accuracy": f"{band['is_correct'].mean():.1%}" if len(band) else "-",
        })
    return pd.DataFrame(rows)


def report(path):
    log = load_log(path)
    print("=" * 80)
    print(f"{path}   model: {log['model'].iloc[0]}   descriptions: {log['categories_version'].iloc[0]}"
          f"   keywords: {log['keywords_version'].iloc[0]}")
    print("=" * 80)
    print(f"Messages: {len(log)}   Accuracy (all answers): {log['is_correct'].mean():.1%}   "
          f"Spend: ${log['cost_usd'].sum():.4f}   Cost per 1,000: ${log['cost_usd'].mean() * 1000:.4f}")

    valid = log[log["reason"] != "invalid_category"]
    print("\nKeyword check (check 3), false-alarm rate = share of CORRECT answers it flags:")
    print(f"  flags {valid.loc[valid['is_correct'], 'keyword_miss'].mean():.1%} of correct answers, "
          f"{valid.loc[~valid['is_correct'], 'keyword_miss'].mean():.1%} of wrong answers")

    tuning_path = tuning_log_for(path)
    print(f"\nThreshold curve (thresholds from {tuning_path}):")
    if tuning_path.exists():
        tuning = log if Path(path) == tuning_path else load_log(tuning_path)
        print(curve(log, thresholds_from(tuning)).to_string(index=False))
    else:
        print("  no tuning log yet for this model and description version")

    print("\nCalibration (does a confidence of 90 mean 90% right?):")
    print(calibration(log).to_string(index=False))

    groups = confused_pairs(log)
    counts = groups.size().sort_values(ascending=False, kind="stable")
    print(f"\nTop {TOP_PAIRS} confused pairs ({int(counts.sum())} wrong answers in {len(counts)} pairs):")
    for pair, count in counts.head(TOP_PAIRS).items():
        print(f"\n  {count}x  {pair}")
        for r in groups.get_group(pair).head(EXAMPLES_PER_PAIR).itertuples():
            print(f"      \"{r.message_text}\"")
            print(f"         correct: {r.correct}   model said: {r.predicted} ({r.confidence:g})")
    print()


def spend_summary(paths):
    logs = pd.concat([pd.read_csv(p, usecols=["model", "cost_usd"]) for p in paths])
    # Description-drafting calls (Learn stage) count too, failed ones included.
    # Each version's calls are in drafts/vN_calls.jsonl; v2 predates that file, so use its record.
    drafting = []
    for record_path in sorted(Path("drafts").glob("*_sonnet.json")):
        if not record_path.with_name(record_path.name.replace("_sonnet.json", "_calls.jsonl")).exists():
            drafting.append(json.loads(record_path.read_text()))
    for calls_path in sorted(Path("drafts").glob("*_calls.jsonl")):
        drafting += [json.loads(line) for line in calls_path.read_text().splitlines()]
    drafting = pd.DataFrame([{"model": d["model"] + " (drafting)", "cost_usd": d["cost_usd"]} for d in drafting])
    logs = pd.concat([logs, drafting])
    print("Running spend per model (all logs):")
    for model, cost in logs.groupby("model")["cost_usd"].sum().items():
        print(f"  {model}: ${cost:.4f}")
    print(f"  TOTAL: ${logs['cost_usd'].sum():.4f}")


def main():
    paths = sys.argv[1:] or sorted(str(p) for p in Path("logs").glob("decisions_*.csv"))
    for path in paths:
        report(path)
    spend_summary(paths)


if __name__ == "__main__":
    main()
