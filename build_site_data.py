"""Build docs/data.json for the results site, straight from the decision logs.

Every number the site's charts show comes from this file, so nothing on the charts is typed
by hand. Re-run after any new log: python build_site_data.py
"""

import json
from pathlib import Path

import pandas as pd

from analyze import (BANDS, CONTENDERS, TARGETS, auto_accepted, load_log, thresholds_from,
                     tuning_log_for)

SERIES = {"B": "Jev", "C": "Sonnet 5", "D": "Haiku 4.5"}  # the three models on the final descriptions


def pct(x):
    return round(float(x) * 100, 1)


def sweep(log):
    """Every operating point a threshold can reach on this log: (share auto-accepted, accuracy).

    Only answers that pass gate checks 1-3 can be accepted. A threshold can't split a tie, so
    each distinct confidence value is one achievable point.
    """
    passing = log[log["passes_checks"]]
    points = []
    for threshold in sorted(passing["confidence"].unique(), reverse=True):
        accepted = passing[passing["confidence"] >= threshold]
        points.append({"threshold": float(threshold), "share": pct(len(accepted) / len(log)),
                       "accuracy": pct(accepted["is_correct"].mean()), "n": int(len(accepted))})
    return points


def main():
    logs = {key: load_log(path) for key, (_, path) in CONTENDERS.items()}
    data = {"contenders": {}, "curves": {}, "calibration": {}, "gate": {}}

    for key, log in logs.items():
        thresholds = thresholds_from(load_log(tuning_log_for(CONTENDERS[key][1])))
        rows = []
        for target, threshold in thresholds.items():
            accepted = auto_accepted(log, threshold)
            rows.append({"target": target, "threshold": float(threshold), "realized": pct(accepted.mean()),
                         "accuracy": pct(log.loc[accepted, "is_correct"].mean())})
        valid = log[log["reason"] != "invalid_category"]
        data["contenders"][key] = {
            "name": CONTENDERS[key][0], "model": log["model"].iloc[0], "rows": rows,
            "accuracy_all": pct(log["is_correct"].mean()),
            "hard_hallucinations": int((log["reason"] == "invalid_category").sum()),
            "cost_per_1000": round(float(log["cost_usd"].mean() * 1000), 2),
            "cost_per_million": int(round(float(log["cost_usd"].mean() * 1_000_000))),
            "median_ms": int(pd.to_numeric(log["ms"]).median()),
        }
        data["calibration"][key] = [
            {"band": f"{low}-{high}", "n": int(len(band)), "accuracy": pct(band["is_correct"].mean()) if len(band) else None}
            for low, high in BANDS
            for band in [log[(log["confidence"] >= low) & (log["confidence"] < high + 1)]]
        ]
        data["gate"][key] = {
            "keyword_flags_correct": pct(valid.loc[valid["is_correct"], "keyword_miss"].astype(bool).mean()),
            "keyword_flags_wrong": pct(valid.loc[~valid["is_correct"], "keyword_miss"].astype(bool).mean()),
        }
        if key in SERIES:
            data["curves"][key] = sweep(log)

    # Cascade (E): Jev's answer if Jev auto-accepts it, else Sonnet's.
    jev, sonnet = logs["B"].reset_index(drop=True), logs["C"].set_index("message_id").loc[logs["B"]["message_id"]].reset_index()
    jev.attrs = logs["B"].attrs
    cascade = []
    for target, threshold in thresholds_from(load_log(tuning_log_for(CONTENDERS["B"][1]))).items():
        keeps = auto_accepted(jev, threshold)
        correct = jev["is_correct"].where(keeps, sonnet["is_correct"])
        cost = jev["cost_usd"].sum() + sonnet.loc[~keeps, "cost_usd"].sum()
        cascade.append({"target": target, "jev_share": pct(keeps.mean()),
                        "jev_accuracy": pct(jev.loc[keeps, "is_correct"].mean()),
                        "sonnet_accuracy": pct(sonnet.loc[~keeps, "is_correct"].mean()),
                        "overall": pct(correct.mean()), "cost_per_1000": round(float(cost / len(jev) * 1000), 2),
                        "cost_per_million": int(round(float(cost / len(jev) * 1_000_000)))})
    data["cascade"] = cascade

    # Supporting check: the same number of accepted answers for Jev and Sonnet (top 730).
    matched = {}
    for key in ("B", "C"):
        p = logs[key][logs[key]["passes_checks"]].sort_values(["confidence", "message_id"], ascending=[False, True])
        matched[key] = pct(p.head(730)["is_correct"].mean())
    data["matched_volume_730"] = matched
    data["targets"] = TARGETS
    # Sonnet vs Jev cost per decision, from unrounded means (the verdict's ratio).
    data["cost_ratio_sonnet_jev"] = round(float(logs["C"]["cost_usd"].mean() / logs["B"]["cost_usd"].mean()), 1)

    Path("docs/data.json").write_text(json.dumps(data, indent=1) + "\n")
    print("Wrote docs/data.json")


if __name__ == "__main__":
    main()
