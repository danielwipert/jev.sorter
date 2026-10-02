"""First look at DeepSeek V4 Flash on 20 tuning messages, before anything is pre-registered.

Checks three things: does it answer in the right format, what does one call really cost,
and what do its two possible confidence scores look like?
  - self-reported: the number it writes, like Claude in round 1
  - logprob: its own probability for the category it wrote (from the tokens' logprobs)

Uses the same prompt as Claude in run.py, v2 descriptions, reasoning off, one pinned provider.
Writes explore/deepseek_first_call.csv. Costs about a cent.
  python explore/deepseek_first_call.py
"""

import csv
import json
import math
import os
import re
import sys
import time
from pathlib import Path

import openai
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from run import CLAUDE_PROMPT, OPENROUTER_CHAT_URL  # noqa: E402

load_dotenv()

MODEL = "deepseek/deepseek-v4-flash"  # copied from OpenRouter's model list (2026-10-02)
PROVIDER = "streamlake/fp8"  # cheapest listed provider that returns logprobs ($0.028 / $0.056 per M)
N = 20


def logprob_confidence(logprobs, reply):
    """Probability (0-100) of the category text, from the logprobs of the tokens that spell it."""
    match = re.search(r'"category"\s*:\s*"([^"]*)"', reply)
    if not match or not logprobs:
        return None
    start, end = match.span(1)
    pos, total = 0, 0.0
    for t in logprobs:
        t_start, t_end = pos, pos + len(t.token)
        if t_end > start and t_start < end:  # token overlaps the category text
            total += t.logprob
        pos = t_end
    return math.exp(total) * 100


def main():
    client = openai.OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url=OPENROUTER_CHAT_URL)
    categories = json.loads(Path("categories/v2.json").read_text())
    messages = pd.read_csv("data/tuning.csv").head(N)
    rows = []
    for row in messages.itertuples():
        prompt = CLAUDE_PROMPT.format(
            categories="\n".join(f"- {name}: {d}" for name, d in categories.items()), message=row.text
        )
        start = time.perf_counter()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            response_format={"type": "json_object"},
            logprobs=True,
            extra_body={"reasoning": {"enabled": False},
                        "provider": {"order": [PROVIDER], "allow_fallbacks": False}},
        )
        ms = round((time.perf_counter() - start) * 1000)
        data = response.model_dump()
        reply = response.choices[0].message.content or ""
        lp = response.choices[0].logprobs.content if response.choices[0].logprobs else None
        try:
            answer = json.loads(re.sub(r"^```(?:json)?\s*|\s*```$", "", reply.strip()))
            predicted, self_conf = str(answer["category"]), float(answer["confidence"])
        except (ValueError, KeyError, TypeError):
            predicted, self_conf = reply, None
        lp_conf = logprob_confidence(lp, reply)
        usage = data["usage"]
        rows.append({
            "message_id": row.message_id, "text": row.text, "correct": row.label, "predicted": predicted,
            "is_correct": predicted == row.label, "valid_category": predicted in categories,
            "self_confidence": self_conf, "logprob_confidence": None if lp_conf is None else round(lp_conf, 2),
            "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
            "cost_usd": usage.get("cost"), "ms": ms, "provider": data.get("provider"), "model": response.model,
        })
        r = rows[-1]
        print(f"{len(rows):2}. {'OK ' if r['is_correct'] else 'X  '} self={r['self_confidence']} "
              f"lp={r['logprob_confidence']} ${r['cost_usd']} {ms}ms  {predicted}")

    out = Path("explore/deepseek_first_call.csv")
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    df = pd.DataFrame(rows)
    print(f"\nCorrect: {df.is_correct.sum()}/{len(df)}  Valid categories: {df.valid_category.sum()}/{len(df)}")
    print(f"Spend: ${df.cost_usd.sum():.5f}  (${df.cost_usd.mean() * 1000:.3f} per 1,000 messages)")
    print(f"Tokens per call: {df.prompt_tokens.mean():.0f} in, {df.completion_tokens.mean():.0f} out")
    print(f"Providers seen: {sorted(set(df.provider.dropna()))}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
