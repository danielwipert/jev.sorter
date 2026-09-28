"""Step 1.4: generate categories/v1.json and keywords/v1.json from Banking77 (run once).

categories/v1.json  {category: description}. v1 descriptions are just the name with spaces.
keywords/v1.json    {category: [keywords]}. Words from the name, plus the most distinctive
                    words for that category in the train split.

"Distinctive" = share of the category's messages containing the word, divided by the share
of all messages containing it. Keywords are learned from train messages that are NOT in
data/tuning.csv, so the keyword check isn't graded on the messages it was built from.
"""

import json
from pathlib import Path

import pandas as pd

from gate import words
from sample_data import SOURCE_URL

VERSION = "v1"
KEYWORDS_PER_CATEGORY = 10  # distinctive words added on top of the name words
MIN_SHARE = 0.05  # a word must appear in at least 5% of a category's messages to count
# Words in category names too common to be useful as keywords (e.g. "lost_or_stolen_card").
NAME_STOPWORDS = {"a", "and", "by", "for", "in", "is", "my", "not", "of", "or", "the", "to", "why"}


def distinctive_words(messages):
    """Top distinctive words per category, ranked by in-category share / overall share."""
    messages = messages.assign(words=messages["text"].map(words))
    overall = messages.explode("words")["words"].value_counts() / len(messages)
    result = {}
    for label, group in messages.groupby("label"):
        in_category = group.explode("words")["words"].value_counts() / len(group)
        in_category = in_category[in_category >= MIN_SHARE]
        ratio = (in_category / overall[in_category.index]).rename("ratio").rename_axis("word").reset_index()
        # Ties broken alphabetically so the output is identical on every run.
        ratio = ratio.sort_values(["ratio", "word"], ascending=[False, True])
        result[label] = list(ratio["word"][:KEYWORDS_PER_CATEGORY])
    return result


def main():
    train = pd.read_csv(SOURCE_URL.format(split="train")).rename(columns={"category": "label"})
    train["message_id"] = [f"train_{i:05d}" for i in train.index]
    tuning_ids = set(pd.read_csv("data/tuning.csv")["message_id"])
    keyword_source = train[~train["message_id"].isin(tuning_ids)]

    labels = sorted(train["label"].unique())
    categories = {label: label.replace("_", " ") for label in labels}

    learned = distinctive_words(keyword_source)
    keywords = {}
    for label in labels:
        name_words = [w for w in label.lower().split("_") if w not in NAME_STOPWORDS]
        keywords[label] = name_words + [w for w in learned[label] if w not in name_words]

    Path("categories").mkdir(exist_ok=True)
    Path("keywords").mkdir(exist_ok=True)
    Path(f"categories/{VERSION}.json").write_text(json.dumps(categories, indent=2) + "\n")
    Path(f"keywords/{VERSION}.json").write_text(json.dumps(keywords, indent=2) + "\n")
    print(f"categories/{VERSION}.json: {len(categories)} categories")
    print(f"keywords/{VERSION}.json: learned from {len(keyword_source)} train messages (tuning excluded)")


if __name__ == "__main__":
    main()
