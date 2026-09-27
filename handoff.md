# Handoff

_Rewritten at the end of every session. Keep it short._

**Last session:** 2026-09-27

## What we did
Week 1, steps 1.1–1.5 done.
- **1.1** Pinned `requirements.txt`. `OPENROUTER_API_KEY` set in the cloud environment and verified. Reusing an existing key (Dan's choice, $50 limit, has other spend), so project spend comes from our logs' `cost_usd`, not the OpenRouter dashboard.
- **1.2** `sample_data.py` → `data/tuning.csv` (500) and `data/test.csv` (1,000), seed 42. Source: PolyAI's Banking77 CSVs pinned to commit `57ec275` (the Hugging Face copy no longer loads). Columns: `message_id`, `text`, `label`. Some tuning categories are thin (`contactless_not_working` has 1).
- **1.3** `explore/jev_first_call.py`: one Jev call works.
  - `TypeSafeClient(api_key=..., base_url="https://openrouter.ai/api")`, `system_one(model="typesafe/jev-1.13", state=text, questions={"category": Choice(instructions=..., criteria={label: description})})`.
  - Confidence is **0–1** → ×100. Response `model` is `typesafe/jev-1.13-20260917`; log that.
  - SDK drops cost; read `result.raw_http_response.json()["usage"]["cost"]`. ~$0.00007/call.
- **1.4** `build_categories.py` → `categories/v1.json` (`{name: description}`) and `keywords/v1.json` (`{name: [words]}`). Keywords learned from train **minus tuning messages**. Deterministic. `CHANGELOG.md` has the v1 line. Only 2.6% of tuning messages lack a keyword of their true category, but some keywords are generic ("help", "try").
- **1.5** `gate.py`: `gate(message, predicted, confidence, categories, keywords, threshold=None)` → `(gate_result, gate_reason, keyword_miss)`. `python test_gate.py`: 7 tests pass.
  - `threshold=None` = checks 1–3 only. `run.py` logs that; `analyze.py` calls the same `gate()` with each 50/70/85% threshold.
  - `KEYWORD_CHECK_BLOCKS = False` until step 2.1. `words()` (the keyword match rule) lives in `gate.py`.

## Next session: do these, in order
1. Step 1.6: `run.py --model jev --set tuning --categories v1`. `ask_jev()` returns `(category, confidence×100, ms, cost)`. Log columns per spec Section 12 → `logs/decisions_{model}_{set}_{categories}.csv`. 20 messages first, inspect by eye, then all 500 (~$0.04).
2. Step 1.7: `analyze.py` (accuracy, confusion pairs, threshold curve via `gate()`, calibration bands, spend).

## Notes
- Always pin `typesafe/jev-1.13`. Never `jev-latest` or `jev-router`.
- Don't look at test-set results during tuning.
- Code reads `OPENROUTER_API_KEY` from the environment, falls back to `.env` locally.
- Source for the OpenRouter setup: https://openrouter.ai/docs/guides/community/typesafe-sdk
