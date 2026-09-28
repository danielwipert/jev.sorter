"""Step 1.3: one Jev call by hand, to see the raw response.

One tuning message, all 77 categories as options. Prints the raw JSON so we can see
exactly what comes back (confidence scale, probabilities, usage, cost).
"""

import json
import os

import pandas as pd
from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

load_dotenv()  # only used when running locally; does not override an existing env variable

MODEL = "typesafe/jev-1.13"  # pinned. Never jev-latest or jev-router.

tuning = pd.read_csv("data/tuning.csv")
message = tuning.iloc[0]
labels = sorted(tuning["label"].unique())

client = TypeSafeClient(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api",
)
result = client.system_one(
    model=MODEL,
    state=message["text"],
    questions={
        "category": Choice(
            instructions="Which category best describes this bank customer's message?",
            # Placeholder descriptions (name with spaces), same idea as categories/v1.json.
            criteria={label: label.replace("_", " ") for label in labels},
        ),
    },
)

print("Message: ", message["text"])
print("Correct: ", message["label"])
print()
raw = result.raw_http_response.json()
answer = raw["answers"]["category"]
top5 = dict(sorted(answer["probabilities"].items(), key=lambda kv: -kv[1])[:5])
answer["probabilities"] = f"<{len(labels)} values, top 5 shown below>"
print("Raw response (probabilities shortened):")
print(json.dumps(raw, indent=2))
print()
print("Top 5 probabilities:", json.dumps(top5, indent=2))
