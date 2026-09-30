"""Run one model over a message set, gate every answer, and log one row per message.

Examples:
  python run.py --model jev --set tuning --categories v1 --limit 20
  python run.py --model jev --set tuning --categories v1
  python run.py --model sonnet --set tuning --categories v2 --limit 5
  python run.py --model laya --set tuning --categories v2

Rows are written as they come in. Re-running the same command skips messages already in
the log, so an interrupted run picks up where it stopped (and paid calls aren't repeated).
Use --fresh to start the log over.
"""

import argparse
import csv
import json
import os
import re
import time
from pathlib import Path

import openai
import pandas as pd
from dotenv import load_dotenv
from typesafe_sdk import Choice, TypeSafeClient

from gate import gate

load_dotenv()  # only used when running locally; an existing env variable wins

JEV_MODEL = "typesafe/jev-1.13"  # pinned. Never jev-latest or jev-router.
JEV_INPUT_PRICE = 0.042 / 1_000_000  # $ per input token; used only if OpenRouter omits cost
# Copied from OpenRouter's model list (2026-09-27), not typed from memory.
CLAUDE_MODELS = {"sonnet": "anthropic/claude-sonnet-5", "haiku": "anthropic/claude-haiku-4.5"}
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1"
# Open alternatives (round 2). Run on our own machine, so API cost is $0.
LAYA_MODEL = "convaiinnovations/laya"
LAYA_REVISION = "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851"  # pinned, from laya.PINNED_REVISIONS
LAYA_SETTINGS = {"head_max_len": 512, "max_len": 1024}  # pre-registered in CHANGELOG.md (2026-09-30)
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


_laya_agent = None


def ask_laya(message, categories):
    """Return (category, confidence 0-100, milliseconds, cost_usd, model_version). Runs locally."""
    global _laya_agent
    if _laya_agent is None:
        import laya  # only needed for this model; it pulls in PyTorch
        _laya_agent = laya.load(LAYA_MODEL, revision=LAYA_REVISION)
    question = {"category": {"type": "choice", "instructions": INSTRUCTIONS, "criteria": categories}}
    start = time.perf_counter()
    result = _laya_agent.predict(message, question, **LAYA_SETTINGS)
    ms = round((time.perf_counter() - start) * 1000)
    answer = result["answers"]["category"]
    # answer_confidence = Laya's probability for the chosen option (after its own calibration).
    return answer["choice"], answer["answer_confidence"] * 100, ms, 0.0, f"{LAYA_MODEL}@{LAYA_REVISION[:7]}"


CLAUDE_PROMPT = """Classify this bank customer's message into exactly one of the categories below.

Categories (name: description):
{categories}

Message:
{message}

Reply with JSON only, in this form: {{"category": "<exact category name>", "confidence": <0-100>}}
"category" must be copied exactly from the list. "confidence" is how sure you are, 0 to 100."""

_claude_client = None


def ask_claude(message, categories, model):
    """Return (category, confidence 0-100, milliseconds, cost_usd, model_version).

    One call, self-reported confidence (spec Section 7). A reply that can't be read returns the
    raw text as the category, so gate check 1 counts it as a hard hallucination.
    """
    global _claude_client
    if _claude_client is None:
        _claude_client = openai.OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url=OPENROUTER_CHAT_URL)
    prompt = CLAUDE_PROMPT.format(
        categories="\n".join(f"- {name}: {description}" for name, description in categories.items()),
        message=message,
    )
    start = time.perf_counter()
    response = _claude_client.chat.completions.create(
        model=CLAUDE_MODELS[model],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        response_format={"type": "json_object"},
        # No extended thinking: one plain answer per message (Sonnet 5 thinks by default).
        extra_body={"reasoning": {"enabled": False}},
    )
    ms = round((time.perf_counter() - start) * 1000)
    reply = response.choices[0].message.content or ""
    cost = response.model_dump()["usage"]["cost"]
    # Haiku sometimes wraps the JSON in ```json ... ```. Strip that packaging only.
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", reply.strip())
    try:
        answer = json.loads(text)
        return str(answer["category"]), float(answer["confidence"]), ms, cost, response.model
    except (ValueError, KeyError, TypeError):
        return reply, 0.0, ms, cost, response.model


def fmt_bool(value):
    return "" if value is None else str(value).lower()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True, choices=["jev", "sonnet", "haiku", "laya"])
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
            elif args.model == "laya":
                predicted, confidence, ms, cost, model_name = ask_laya(row.text, categories)
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
