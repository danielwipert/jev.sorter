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


def auto_accepted(log, threshold):
    """True/False per row: does the full gate (checks 1-4) auto-accept this answer?"""
    return pd.Series([
        gate(r.message_text, r.predicted, r.confidence, log.attrs["categories"], log.attrs["keywords"], threshold)[0]
        == "auto_accept"
        for r in log.itertuples()
    ], index=log.index)


def curve(log, thresholds):
    rows = []
    for target, threshold in thresholds.items():
        accepted = log[auto_accepted(log, threshold)]
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


# The contenders on the final test set (spec Section 7). E is computed from B and C.
CONTENDERS = {
    "A": ("Jev, descriptions v1", "logs/decisions_jev_test_v1.csv"),
    "B": ("Jev, final descriptions (v2)", "logs/decisions_jev_test_v2.csv"),
    "C": ("Sonnet 5, final descriptions (v2)", "logs/decisions_sonnet_test_v2.csv"),
    "D": ("Haiku 4.5, final descriptions (v2)", "logs/decisions_haiku_test_v2.csv"),
    # Secondary check on description tilt (v2 was tuned on Jev's mistakes). Does not affect the verdict.
    "F": ("Sonnet 5, descriptions v1", "logs/decisions_sonnet_test_v1.csv"),
}
VERDICT_ROW = 70  # Section 10: the 70% auto-accept row decides the headline
VERDICT_MAX_GAP = 3.0  # Jev within 3 accuracy points of Sonnet...
VERDICT_MIN_COST_RATIO = 10.0  # ...and at least 10x cheaper per 1,000 gated decisions


def final_results():
    """Results table, cascade (E), calibration and the pre-registered verdict. Saved to results/."""
    logs = {key: load_log(path) for key, (_, path) in CONTENDERS.items() if Path(path).exists()}
    if not logs:
        return
    Path("results").mkdir(exist_ok=True)

    rows, numbers = [], {}
    for key, log in logs.items():
        thresholds = thresholds_from(load_log(tuning_log_for(CONTENDERS[key][1])))
        cost_per_1000 = log["cost_usd"].mean() * 1000
        for target, threshold in thresholds.items():
            accepted = auto_accepted(log, threshold)
            accuracy = log.loc[accepted, "is_correct"].mean()
            numbers[key, target] = (accuracy * 100, cost_per_1000)
            rows.append({
                "contender": key, "model": CONTENDERS[key][0], "target_auto_accept": f"{target}%",
                "threshold": threshold, "realized_auto_accept": f"{accepted.mean():.1%}",
                "accuracy_on_auto_accepted": f"{accuracy:.1%}", "soft_hallucination_rate": f"{1 - accuracy:.1%}",
                "hard_hallucination_rate": f"{(log['reason'] == 'invalid_category').mean():.1%}",
                "accuracy_all_answers": f"{log['is_correct'].mean():.1%}", "cost_per_1000": f"${cost_per_1000:.2f}",
            })
    table = pd.DataFrame(rows)
    table.to_csv("results/results_table.csv", index=False)
    print("=" * 80 + "\nFINAL TEST SET RESULTS (thresholds from each model's tuning log)\n" + "=" * 80)
    print(table.drop(columns="model").to_string(index=False))

    calibration_rows = [{"contender": key, **row} for key, log in logs.items() for row in calibration(log).to_dict("records")]
    pd.DataFrame(calibration_rows).to_csv("results/calibration.csv", index=False)

    if "B" in logs and "C" in logs:
        cascade(logs["B"], logs["C"])
        verdict(numbers)
    if "C" in logs and "F" in logs:
        tilt(numbers)


def tilt(numbers):
    """Contender F vs C: did the Jev-tuned v2 descriptions help or hurt Sonnet? (pre-committed in CHANGELOG)"""
    print("\nDESCRIPTION TILT CHECK (Sonnet 5: v2 descriptions (C) minus v1 descriptions (F), accuracy on auto-accepted):")
    for target in TARGETS:
        c, f = numbers["C", target][0], numbers["F", target][0]
        print(f"  {target}% row: C {c:.1f}%, F {f:.1f}%, C - F = {c - f:+.1f} points")


def cascade(jev, sonnet):
    """Contender E: Jev's answer if Jev auto-accepts it, otherwise Sonnet's. No new API calls."""
    # Line up Sonnet's answers with Jev's, message by message.
    sonnet = sonnet.set_index("message_id").loc[jev["message_id"]].reset_index()
    attrs = dict(jev.attrs)  # categories/keywords the gate needs
    jev = jev.reset_index(drop=True)
    jev.attrs = attrs
    thresholds = thresholds_from(load_log(tuning_log_for(CONTENDERS["B"][1])))
    rows = []
    for target, threshold in thresholds.items():
        jev_keeps = auto_accepted(jev, threshold)
        correct = jev["is_correct"].where(jev_keeps, sonnet["is_correct"])
        cost = jev["cost_usd"].sum() + sonnet.loc[~jev_keeps, "cost_usd"].sum()
        rows.append({
            "jev_target": f"{target}%", "jev_threshold": threshold, "jev_handles": f"{jev_keeps.mean():.1%}",
            "accuracy_jev_slice": f"{jev.loc[jev_keeps, 'is_correct'].mean():.1%}",
            "accuracy_sonnet_slice": f"{sonnet.loc[~jev_keeps, 'is_correct'].mean():.1%}",
            "accuracy_overall": f"{correct.mean():.1%}",
            "cost_per_1000": f"${cost / len(jev) * 1000:.2f}",
        })
    table = pd.DataFrame(rows)
    table.to_csv("results/cascade.csv", index=False)
    print(f"\nCASCADE (E): Jev if auto-accepted, else Sonnet. Every message gets an answer.")
    print(f"For comparison, Sonnet alone on every message: accuracy {sonnet['is_correct'].mean():.1%}, "
          f"${sonnet['cost_usd'].mean() * 1000:.2f} per 1,000.")
    print(table.to_string(index=False))


def verdict(numbers):
    """Section 10, applied mechanically to the 70% row."""
    jev_accuracy, jev_cost = numbers["B", VERDICT_ROW]
    sonnet_accuracy, sonnet_cost = numbers["C", VERDICT_ROW]
    gap = sonnet_accuracy - jev_accuracy
    ratio = sonnet_cost / jev_cost
    close_enough = gap <= VERDICT_MAX_GAP
    cheap_enough = ratio >= VERDICT_MIN_COST_RATIO
    print(f"\nPRE-REGISTERED VERDICT (Section 10, {VERDICT_ROW}% row, Jev B vs Sonnet C):")
    print(f"  Accuracy: Jev {jev_accuracy:.1f}%, Sonnet {sonnet_accuracy:.1f}%. Sonnet minus Jev = {gap:+.1f} points "
          f"(Jev passes if <= {VERDICT_MAX_GAP:g}): {'PASS' if close_enough else 'FAIL'}")
    print(f"  Cost per 1,000: Jev ${jev_cost:.2f}, Sonnet ${sonnet_cost:.2f}. Sonnet costs {ratio:.0f}x more "
          f"(Jev passes if >= {VERDICT_MIN_COST_RATIO:g}x): {'PASS' if cheap_enough else 'FAIL'}")
    print(f"  => {'JEV WINS' if close_enough and cheap_enough else 'NOT YET'}")


def main():
    paths = sys.argv[1:] or sorted(str(p) for p in Path("logs").glob("decisions_*.csv"))
    for path in paths:
        report(path)
    spend_summary(paths)
    if not sys.argv[1:]:
        final_results()


if __name__ == "__main__":
    main()
