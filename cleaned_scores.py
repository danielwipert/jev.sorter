"""Cleaned-key secondary score (pre-registered in CHANGELOG.md, 2026-10-13).

Re-scores every test-set contender against a cleaned answer key built from the blind
review in review/relabel_test.csv. Thresholds are unchanged (they come from the tuning
logs and depend only on confidence). The official results do not change.

Two versions: "strict" counts only clear relabels; "cleaned" also accepts either label
where the reviewer said both fit. Verdicts: Dan's (dan_verdict) count. Where Dan hasn't
filled one in, Claude's draft is used and the output is labelled DRAFT.

  python cleaned_scores.py
"""

from pathlib import Path

import pandas as pd

from analyze import CONTENDERS, TARGETS, auto_accepted, load_log, thresholds_from, tuning_log_for

SHEET = Path("review/relabel_test.csv")
KEY = Path("review/relabel_test_key.csv")


def accepted_labels(strict=False):
    """message_id -> set of labels that count as correct after review.

    strict=True treats "both" as the original key only, so only clear relabels count."""
    sheet = pd.read_csv(SHEET, dtype=str, keep_default_na=False).set_index("message_id")
    key = pd.read_csv(KEY, dtype=str, keep_default_na=False).set_index("message_id")
    verdict = sheet["dan_verdict"].where(sheet["dan_verdict"] != "", sheet["claude_draft"])
    draft = (sheet["dan_verdict"] == "").any()
    labels = {}
    for message_id, v in verdict.items():
        one, two = sheet.loc[message_id, "label_1"], sheet.loc[message_id, "label_2"]
        if v == "1":
            labels[message_id] = {one}
        elif v == "2":
            labels[message_id] = {two}
        elif v == "both" and not strict:
            labels[message_id] = {one, two}
        elif v in ("both", "unclear"):
            labels[message_id] = {key.loc[message_id, "answer_key"]}
        else:
            raise ValueError(f"{message_id}: verdict must be 1, 2, both or unclear, got {v!r}")
    return labels, verdict, key, draft


def main():
    labels, verdict, key, draft = accepted_labels()
    strict_labels = accepted_labels(strict=True)[0]
    sides = []
    for message_id, accepted in labels.items():
        k, alt = key.loc[message_id, "answer_key"], key.loc[message_id, "alternative"]
        sides.append("both" if accepted == {k, alt} else "key" if accepted == {k} else "alternative")
    sides = pd.Series(sides).value_counts()
    status = "DRAFT (not yet approved by Dan)" if draft else "approved by Dan"
    print(f"Cleaned key, {status}: {len(labels)} reviewed messages. Accepted label is the original key: "
          f"{sides.get('key', 0)}, the alternative: {sides.get('alternative', 0)}, both: {sides.get('both', 0)}")

    rows = []
    for name, (model, path) in CONTENDERS.items():
        if not Path(path).exists():
            continue
        log = load_log(path)
        clean = [r.predicted in labels[r.message_id] if r.message_id in labels else r.is_correct
                 for r in log.itertuples()]
        log["is_correct_clean"] = clean
        log["is_correct_strict"] = [r.predicted in strict_labels[r.message_id] if r.message_id in strict_labels
                                    else r.is_correct for r in log.itertuples()]
        thresholds = thresholds_from(load_log(tuning_log_for(path)))
        for target, threshold in thresholds.items():
            accepted = auto_accepted(log, threshold)
            rows.append({
                "contender": name, "model": model, "target_auto_accept": f"{target}%",
                "realized_auto_accept": f"{accepted.mean():.1%}",
                "accuracy_on_auto_accepted": f"{log.loc[accepted, 'is_correct'].mean():.1%}",
                "strict_accuracy_on_auto_accepted": f"{log.loc[accepted, 'is_correct_strict'].mean():.1%}",
                "cleaned_accuracy_on_auto_accepted": f"{log.loc[accepted, 'is_correct_clean'].mean():.1%}",
                "accuracy_all_answers": f"{log['is_correct'].mean():.1%}",
                "cleaned_accuracy_all_answers": f"{log['is_correct_clean'].mean():.1%}",
                "status": "draft" if draft else "approved",
            })
    table = pd.DataFrame(rows)
    Path("results").mkdir(exist_ok=True)
    table.to_csv("results/results_table_cleaned.csv", index=False)
    print("\nSECONDARY: original vs cleaned answer key (official results unchanged)")
    print("strict = only clear relabels count; cleaned = also accept either label where both fit")
    print(table.drop(columns=["model", "status"]).to_string(index=False))
    print("\nWrote results/results_table_cleaned.csv")


if __name__ == "__main__":
    main()
