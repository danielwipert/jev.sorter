"""Run one model over a message set, gate every answer, and log one row per message.

Examples:
  python run.py --model jev --set tuning --categories v1 --limit 20
  python run.py --model jev --set tuning --categories v1

Rows are written as they come in. Re-running the same command skips messages already in
the log, so an interrupted run picks up where it stopped (and paid calls aren't repeated).
Use --fresh to start the log over.
"""

import argparse
import csv
import json
import os
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

from gate import gate

load_dotenv()  # only used when running locally; an existing env variable wins

JEV_MODEL = "typesafe/jev-1.13"  # pinned. Never jev-latest or jev-router.
JEV_INPUT_PRICE = 0.042 / 1_000_000  # $ per input token; used only if OpenRouter omits cost
INSTRUCTIONS = "Which category best describes this bank customer's message?"

LOG_COLUMNS = [
    "message_id", "message_text", "model", "categories_version", "keywords_version",
    "predicted", "confidence", "gate_result", "gate_reason", "keyword_miss",
    "correct", "is_correct", "ms", "cost_usd",
]

_jev_client = None


def ask_jev(message, categories):
    """Return (category, confidence 0-100, milliseconds, cost_usd, model_version)."""
    global _jev_client
    if _jev_client is None:
        _jev_client = TypeSafeClient(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api",
            timeout=60,
        )
    start = time.perf_counter()
    result = _jev_client.system_one(
        model=JEV_MODEL,
        state=message,
        questions={"category": Choice(instructions=INSTRUCTIONS, criteria=categories)},
    )
    ms = round((time.perf_counter() - start) * 1000)
    # The SDK's parsed response drops OpenRouter's cost field, so read the raw JSON.
    raw = result.raw_http_response.json()
    answer = raw["answers"]["category"]
    usage = raw.get("usage", {})
    cost = usage.get("cost")
    if cost is None:
        cost = usage.get("input_tokens", 0) * JEV_INPUT_PRICE
    return answer["choice"], answer["confidence"] * 100, ms, cost, raw["model"]


def ask_claude(message, categories, model):
    raise NotImplementedError("Claude models are added in step 2.4.")


def fmt_bool(value):
    return "" if value is None else str(value).lower()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True, choices=["jev", "sonnet", "haiku"])
    parser.add_argument("--set", required=True, choices=["tuning", "test"], dest="message_set")
    parser.add_argument("--categories", required=True, help="description version, e.g. v1")
    parser.add_argument("--keywords", default="v1", help="keyword version (default v1)")
    parser.add_argument("--limit", type=int, help="only the first N messages")
    parser.add_argument("--fresh", action="store_true", help="delete the existing log and start over")
    parser.add_argument("--confirm-test", action="store_true", help="required for --set test")
    args = parser.parse_args()

    if args.message_set == "test" and not args.confirm_test:
        parser.error("the test set is for the final comparison only. Add --confirm-test if tuning is finished.")

    categories = json.loads(Path(f"categories/{args.categories}.json").read_text())
    keywords = json.loads(Path(f"keywords/{args.keywords}.json").read_text())
    messages = pd.read_csv(f"data/{args.message_set}.csv")
    if args.limit:
        messages = messages.head(args.limit)

    log_path = Path(f"logs/decisions_{args.model}_{args.message_set}_{args.categories}.csv")
    log_path.parent.mkdir(exist_ok=True)
    if args.fresh and log_path.exists():
        log_path.unlink()
    done = set()
    if log_path.exists():
        existing = pd.read_csv(log_path, dtype=str)
        if (existing["keywords_version"] != args.keywords).any():
            parser.error(f"{log_path} was made with different keywords. Use --fresh to start over.")
        done = set(existing["message_id"])
    todo = messages[~messages["message_id"].isin(done)]
    print(f"{log_path}: {len(done)} already logged, {len(todo)} to run")

    new_file = not log_path.exists()
    with log_path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_COLUMNS)
        if new_file:
            writer.writeheader()
        for n, row in enumerate(todo.itertuples(), start=1):
            if args.model == "jev":
                predicted, confidence, ms, cost, model_name = ask_jev(row.text, categories)
            else:
                predicted, confidence, ms, cost, model_name = ask_claude(row.text, categories, args.model)
            # No threshold here: checks 1-3 only. analyze.py applies each model's thresholds.
            gate_result, gate_reason, keyword_miss = gate(row.text, predicted, confidence, categories, keywords)
            writer.writerow({
                "message_id": row.message_id,
                "message_text": row.text,
                "model": model_name,
                "categories_version": args.categories,
                "keywords_version": args.keywords,
                "predicted": predicted,
                "confidence": round(confidence, 2),
                "gate_result": gate_result,
                "gate_reason": gate_reason,
                "keyword_miss": fmt_bool(keyword_miss),
                "correct": row.label,
                "is_correct": fmt_bool(predicted == row.label),
                "ms": ms,
                "cost_usd": cost,
            })
            f.flush()
            if n % 25 == 0 or n == len(todo):
                print(f"  {n}/{len(todo)} done")

    log = pd.read_csv(log_path)
    print(f"Logged {len(log)} rows. Accuracy (all answers): {log['is_correct'].mean():.1%}. "
          f"Spend: ${log['cost_usd'].sum():.4f}")


if __name__ == "__main__":
    main()
