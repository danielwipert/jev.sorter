"""Step 1.2: draw the tuning and test samples from Banking77 (run once).

Writes data/tuning.csv (500 rows from train) and data/test.csv (1,000 rows from test),
both with seed 42. The CSVs are committed, so every model reads the same messages.
"""

from pathlib import Path

import pandas as pd

# Banking77's original source, pinned to one commit so the data can never change.
SOURCE_COMMIT = "57ec275d8078af65b7731c2a98be812d844a6d6b"
SOURCE_URL = (
    "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/"
    f"{SOURCE_COMMIT}/banking_data/{{split}}.csv"
)
SEED = 42
SAMPLES = [
    # (source split, number of rows, output file)
    ("train", 500, "data/tuning.csv"),
    ("test", 1000, "data/test.csv"),
]


def draw_sample(split, n):
    df = pd.read_csv(SOURCE_URL.format(split=split))
    # message_id keeps the original row number, so any message can be traced back to the source.
    df["message_id"] = [f"{split}_{i:05d}" for i in df.index]
    df = df.rename(columns={"category": "label"})
    sample = df.sample(n=n, random_state=SEED)
    return sample.sort_values("message_id")[["message_id", "text", "label"]]


def main():
    Path("data").mkdir(exist_ok=True)
    for split, n, out_path in SAMPLES:
        sample = draw_sample(split, n)
        sample.to_csv(out_path, index=False)
        counts = sample["label"].value_counts()
        print(
            f"{out_path}: {len(sample)} rows, {counts.size} of 77 categories, "
            f"{counts.min()}-{counts.max()} messages per category"
        )


if __name__ == "__main__":
    main()
