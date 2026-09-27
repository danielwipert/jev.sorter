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

## Where we are
Ready for step 1.3.

## Next session: do these, in order
1. Step 1.3: one Jev call by hand (`typesafe/jev-1.13` via OpenRouter). Look at the raw response. Write down whether confidence is 0–1 or 0–100.
2. Step 1.4: `build_categories.py` → `categories/v1.json` and `keywords/v1.json`.
3. Step 1.5: `gate.py`.

## Notes
- Always pin `typesafe/jev-1.13`. Never `jev-latest` or `jev-router`.
- Don't look at test-set results during tuning.
- Code reads `OPENROUTER_API_KEY` from the environment, falls back to `.env` locally.
