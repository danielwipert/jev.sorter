# Handoff

_Rewritten at the end of every session. Keep it short._

**Last session:** 2026-09-27

## What we did
Week 1, steps 1.1–1.6 done.
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
- **1.6** `run.py` (Jev path; `ask_claude()` is a stub for step 2.4). Writes rows as it goes; re-running resumes and skips logged messages (`--fresh` restarts); `--limit N`; `--set test` needs `--confirm-test`.
  - Ran Jev v1 on all 500 tuning messages → `logs/decisions_jev_tuning_v1.csv`. **79.0% accuracy (all answers), $0.036 total, ~0.2 s/call, 0 invalid categories.**
  - `keyword_miss`: 1.5% of correct answers, 14.3% of wrong ones. Promising for step 2.1 (rule of thumb < 10%).
  - Biggest early confusion: `card_arrival` vs `card_delivery_estimate`.

## Next session: do these, in order
1. Step 1.7: `analyze.py` on `logs/decisions_jev_tuning_v1.csv`: accuracy, top ~8 confused pairs with 3 examples each, threshold curve (50/70/85%, via `gate()`, ties by message_id), calibration bands (50–59 … 90–100), spend per model.
2. Then week 2: step 2.1 (keyword flag vs block), 2.2 (tuning round 1).

## Notes
- Always pin `typesafe/jev-1.13`. Never `jev-latest` or `jev-router`.
- Don't look at test-set results during tuning.
- Code reads `OPENROUTER_API_KEY` from the environment, falls back to `.env` locally.
- Source for the OpenRouter setup: https://openrouter.ai/docs/guides/community/typesafe-sdk
