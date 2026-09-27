# Handoff

_Rewritten at the end of every session. Keep it short._

**Last session:** 2026-09-27

## What we did
- Set up the repo: `planning/` (spec), `.gitignore` (`.env` ignored), this file.
- **Step 1.1 done.** Pinned `requirements.txt`; `OPENROUTER_API_KEY` set in the cloud environment and verified.
  - Jev SDK is **`typesafe-sdk`** (import `typesafe_sdk`). Not `typesafe` or `typesafe-ai`.
  - Key: reusing an existing key (Dan's choice), limit $50, has spend from other work. Use our logs' `cost_usd` for project spend.
- **Step 1.2 done.** `sample_data.py` → `data/tuning.csv` (500 from train) and `data/test.csv` (1,000 from test), seed 42, reproducible.
  - Loaded Banking77 from PolyAI's GitHub CSVs, pinned to commit `57ec275`. The Hugging Face copy no longer loads with current `datasets`, so `datasets` was dropped from requirements.
  - Columns: `message_id` (e.g. `train_00003`, original row number), `text`, `label`.
  - All 77 categories in both files. Tuning is thin for a few (e.g. `contactless_not_working` has 1 message, 9 others have 2–3). Keep in mind when reading confusion pairs.

- **Step 1.3 done.** `explore/jev_first_call.py` = one Jev call, prints raw response.
  - How to call: `TypeSafeClient(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api")`, `system_one(model="typesafe/jev-1.13", state=text, questions={"category": Choice(instructions=..., criteria={label: description})})`.
  - **Confidence is 0–1** → multiply by 100 (open question 4 closed). Answer also has `probabilities` for all 77 labels.
  - Response `model` comes back dated: `typesafe/jev-1.13-20260917`. Log that exact string.
  - **Cost:** SDK's parsed `usage` drops `cost`; read it from `result.raw_http_response.json()["usage"]["cost"]`. ~$0.00007/call (input tokens × $0.042/M; output is free). 500 messages ≈ $0.04.
  - First result: "Can I track my card while it is in the process of delivery?" → `card_delivery_estimate` (0.65), correct is `card_arrival` (0.34). Expected confusion pair with v1 descriptions.

- **Step 1.4 done.** `build_categories.py` → `categories/v1.json` (`{name: description}`, description = name with spaces) and `keywords/v1.json` (`{name: [words]}`, 10–15 each). Output is deterministic (ties broken alphabetically). `CHANGELOG.md` started with the v1 line.
  - Keywords = name words (minus filler like "or", "not", "why") + top 10 distinctive words from train, **excluding the 500 tuning messages** (so check 3 isn't graded on its own source data).
  - Keyword match rule: lowercase whole words, `re.findall(r"[a-z]+", text.lower())`. `gate.py` must use the same rule (`words()` in `build_categories.py`).
  - Category names kept exactly as Banking77 has them, including capital `Refund_not_showing_up`.
  - Preview: 2.6% of tuning messages contain no keyword of their *true* category (well under the 10% rule of thumb). Some keywords are generic ("help", "here", "try"), so the check may be too permissive. Judge at step 2.1 with real predictions.

- **Step 1.5 done.** `gate.py`: `gate(message, predicted, confidence, categories, keywords, threshold=None)` → `(gate_result, gate_reason, keyword_miss)`. Checks in spec order; first failure wins. `test_gate.py` (run `python test_gate.py`): 7 tests pass.
  - `threshold=None` runs checks 1–3 only. **Design:** `run.py` logs with no threshold (log's `gate_result`/`gate_reason` = checks 1–3); `analyze.py` calls the same `gate()` with each model's 50/70/85% thresholds.
  - `KEYWORD_CHECK_BLOCKS = False` in `gate.py`. Step 2.1 flips it if the false-alarm rate is low enough.
  - `keyword_miss` is blank (None) when check 1 fails (no valid category to check).
  - `words()` moved into `gate.py`; `build_categories.py` imports it (v1 files unchanged).

## Where we are
Ready for step 1.6.

## Next session: do these, in order
1. Step 1.6: `run.py --model jev --set tuning --categories v1`. `ask_jev()` returns `(category, confidence×100, ms, cost)`; cost from `result.raw_http_response.json()["usage"]["cost"]`. Log columns per spec Section 12, to `logs/decisions_{model}_{set}_{categories}.csv`. Run 20 messages first, inspect by eye, then all 500 (~$0.04).
2. Step 1.7: `analyze.py` (accuracy, confusion pairs, threshold curve via `gate()`, calibration bands, spend).

## Notes
- Always pin `typesafe/jev-1.13`. Never `jev-latest` or `jev-router`.
- Don't look at test-set results during tuning.
- Code reads `OPENROUTER_API_KEY` from the environment, falls back to `.env` locally.
- Sources: OpenRouter TypeSafe SDK guide https://openrouter.ai/docs/guides/community/typesafe-sdk
