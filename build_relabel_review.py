"""Build the blind review sheet for the cleaned-key secondary score (pre-registered 2026-10-13).

A test message is a candidate when at least 2 of the 4 v2 test runs picked the same
category that is NOT the answer key. The sheet shows the key and that alternative as
"label 1" and "label 2" in random order, so the reviewer can't tell which is official.

Writes:
  review/relabel_test.csv      the sheet to fill in (verdict: 1, 2, both or unclear)
  review/relabel_test_key.csv  which label is the answer key (don't open while reviewing)

Re-running keeps any verdicts already filled in.

  python build_relabel_review.py
"""

import json
import random
from collections import Counter
from pathlib import Path

import pandas as pd

RUNS = ["jev", "sonnet", "haiku", "deepseek"]  # v2 test logs: contenders B, C, D, J
MIN_AGREE = 2
SEED = 13
SHEET = Path("review/relabel_test.csv")
KEY = Path("review/relabel_test_key.csv")
VERDICT_COLUMNS = ["claude_draft", "dan_verdict", "note"]


def main():
    logs = {r: pd.read_csv(f"logs/decisions_{r}_test_v2.csv", dtype=str, keep_default_na=False)
            .set_index("message_id") for r in RUNS}
    categories = json.loads(Path("categories/v2.json").read_text())
    base = logs["jev"]

    rng = random.Random(SEED)
    sheet, key = [], []
    for message_id, row in base.iterrows():
        answer_key = row["correct"]
        picks = Counter(logs[r].loc[message_id, "predicted"] for r in RUNS)
        picks = {label: n for label, n in picks.items() if label not in ("", answer_key)}
        if not picks or max(picks.values()) < MIN_AGREE:
            continue
        top = max(picks.values())
        alternative = sorted(label for label, n in picks.items() if n == top)[0]
        labels = [answer_key, alternative]
        rng.shuffle(labels)
        sheet.append({
            "row": len(sheet) + 1, "message_id": message_id, "message": row["message_text"],
            "label_1": labels[0], "label_2": labels[1],
            "label_1_description": categories[labels[0]], "label_2_description": categories[labels[1]],
        })
        key.append({"message_id": message_id, "answer_key": answer_key, "alternative": alternative,
                    "key_is_label": 1 if labels[0] == answer_key else 2, "runs_agreeing": top})

    sheet = pd.DataFrame(sheet)
    if SHEET.exists():  # keep verdicts already filled in
        old = pd.read_csv(SHEET, dtype=str, keep_default_na=False).set_index("message_id")
        for col in VERDICT_COLUMNS:
            sheet[col] = sheet["message_id"].map(old[col]).fillna("") if col in old else ""
    else:
        for col in VERDICT_COLUMNS:
            sheet[col] = ""
    SHEET.parent.mkdir(exist_ok=True)
    sheet.to_csv(SHEET, index=False)
    pd.DataFrame(key).to_csv(KEY, index=False)
    print(f"{len(sheet)} candidates. Wrote {SHEET} and {KEY}.")


if __name__ == "__main__":
    main()
