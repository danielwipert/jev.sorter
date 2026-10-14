"""Make the cleaned-key re-check auditable (suggested by a reader, 2026-10-14; exploratory).

Writes:
  results/label_changes.csv     every reviewed test label, unblinded: original label, the
                                alternative, the verdict, what each model said, who decided
  results/gap_decomposition.csv Jev minus DeepSeek accuracy at matched coverage (each model's
                                n most confident answers), on the original key and on both
                                corrected keys, with paired bootstrap 95% intervals

The bootstrap resamples the 1,000 test messages (2,000 times, seed 0) with each model's
accepted set held fixed, so it measures how much the gap depends on which messages happened
to be in the test set. It does not measure run-to-run variation of the models.

  python label_audit.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

from analyze import load_log
from cleaned_scores import accepted_labels

RUNS = {"jev": "B", "sonnet": "C", "haiku": "D", "deepseek": "J"}  # v2 test logs
PAIR = ("B", "J")  # Jev vs DeepSeek
COVERAGE_N = [300, 400, 500, 600, 731, 850]  # 731 = Jev's auto-accepted count at the 70% setting
KEYS = {"original": "Original key", "strict": "Corrected (clear relabels only)",
        "cleaned": "Corrected (either label where both fit)"}
BOOTSTRAPS, SEED = 2000, 0


def label_changes():
    """One row per reviewed message, with the verdict unblinded."""
    sheet = pd.read_csv("review/relabel_test.csv", dtype=str, keep_default_na=False).set_index("message_id")
    key = pd.read_csv("review/relabel_test_key.csv", dtype=str, keep_default_na=False).set_index("message_id")
    labels, verdict, _, draft = accepted_labels()
    preds = {name: pd.read_csv(f"logs/decisions_{name}_test_v2.csv", dtype=str, keep_default_na=False)
             .set_index("message_id")["predicted"] for name in RUNS}
    rows = []
    for message_id in sheet.index:
        original, alternative = key.loc[message_id, "answer_key"], key.loc[message_id, "alternative"]
        accepted = labels[message_id]
        if verdict[message_id] == "unclear":
            outcome = "unclear (original kept)"
        elif accepted == {original, alternative}:
            outcome = "both fit"
        elif accepted == {original}:
            outcome = "original kept"
        else:
            outcome = "changed"
        rows.append({
            "message_id": message_id, "message": sheet.loc[message_id, "message"],
            "original_label": original, "alternative_label": alternative, "outcome": outcome,
            "strict_key": alternative if outcome == "changed" else original,
            "cleaned_key": " | ".join(sorted(accepted)),
            **{f"{name}_said": preds[name][message_id] for name in RUNS},
            "decided_by": "Claude draft (blind), approved by Dan" if not draft else "Claude draft (blind), not yet approved",
            "note": sheet.loc[message_id, "note"],
        })
    return pd.DataFrame(rows)


def correctness(log, key_name, labels):
    """True/False per row of a log under one answer key."""
    if key_name == "original":
        return log["is_correct"].to_numpy()
    return np.array([p in labels.get(m, {c}) for m, p, c in zip(log["message_id"], log["predicted"], log["correct"])])


def top_n_mask(log, n):
    """Each model's n most confident answers that pass gate checks 1-3 (same rule as the same-volume check)."""
    passing = log[log["passes_checks"]].sort_values(["confidence", "message_id"], ascending=[False, True])
    return log["message_id"].isin(passing["message_id"].head(n)).to_numpy()


def gap_decomposition(logs):
    a, b = (logs[k].sort_values("message_id").reset_index(drop=True) for k in PAIR)
    assert (a["message_id"].values == b["message_id"].values).all()
    labels = {"cleaned": accepted_labels()[0], "strict": accepted_labels(strict=True)[0]}
    rng = np.random.default_rng(SEED)
    weights = np.stack([np.bincount(rng.integers(0, len(a), len(a)), minlength=len(a)) for _ in range(BOOTSTRAPS)])
    rows = []
    for n in COVERAGE_N + ["all"]:
        ma = np.ones(len(a), bool) if n == "all" else top_n_mask(a, n)
        mb = np.ones(len(b), bool) if n == "all" else top_n_mask(b, n)
        for key_name in KEYS:
            ca, cb = correctness(a, key_name, labels.get(key_name)), correctness(b, key_name, labels.get(key_name))
            acc = lambda c, m, w: (w * (c & m)).sum(axis=-1) / (w * m).sum(axis=-1)
            boot = 100 * (acc(ca, ma, weights) - acc(cb, mb, weights))
            rows.append({
                "answers_per_model": n, "key": key_name,
                "jev": round(100 * ca[ma].mean(), 1), "deepseek": round(100 * cb[mb].mean(), 1),
                "gap": round(100 * (ca[ma].mean() - cb[mb].mean()), 1),
                "gap_ci_low": round(float(np.percentile(boot, 2.5)), 1),
                "gap_ci_high": round(float(np.percentile(boot, 97.5)), 1),
            })
    return pd.DataFrame(rows)


def main():
    changes = label_changes()
    changes.to_csv("results/label_changes.csv", index=False)
    print(f"Wrote results/label_changes.csv ({len(changes)} reviewed labels):")
    print(changes["outcome"].value_counts().to_string())

    logs = {k: load_log(f"logs/decisions_{name}_test_v2.csv") for name, k in RUNS.items() if k in PAIR}
    gaps = gap_decomposition(logs)
    gaps.to_csv("results/gap_decomposition.csv", index=False)
    print("\nJev minus DeepSeek, accuracy points (95% bootstrap interval), each model's n most confident answers:")
    print(gaps.pivot(index="answers_per_model", columns="key", values="gap").reindex(COVERAGE_N + ["all"])[list(KEYS)].to_string())
    print("\nWrote results/gap_decomposition.csv")


if __name__ == "__main__":
    main()
