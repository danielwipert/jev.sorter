# Handoff

_Rewritten at the end of every session. Keep it short._

**Last session:** 2026-09-27

## What we did
- Set up the repo: `planning/` (spec), `.gitignore` (`.env` ignored), this file.
- Step 1.1 (code side): added `requirements.txt` with pinned versions and confirmed everything installs and imports on Python 3.11.
  - Jev SDK is **`typesafe-sdk`** (official, by TypeSafe AI). Import name: `typesafe_sdk`. Do **not** use `typesafe` (unrelated) or `typesafe-ai` (third-party shim).

- API key: `OPENROUTER_API_KEY` is set in the cloud environment and verified working with OpenRouter.
  - **Spec deviation (Dan's choice):** reusing an existing key instead of a new $25 one. At check time: limit $50, ~$29.94 lifetime usage from other work. So OpenRouter's dashboard totals won't isolate this project; use the `cost_usd` column in our logs for project spend.

## Where we are
Step 1.1 is done.

## Next session: do these, in order
1. Step 1.2: load Banking77, draw `data/tuning.csv` (500, train, seed 42) and `data/test.csv` (1,000, test, seed 42), commit them.
2. Step 1.3: one Jev call by hand. Write down whether confidence is 0–1 or 0–100.
3. Step 1.4: `build_categories.py` → `categories/v1.json` and `keywords/v1.json`.
- Key setup reminder: code reads the `OPENROUTER_API_KEY` environment variable first, then falls back to `.env` (via `python-dotenv`) when running locally.

## Notes / open questions
- Always pin `typesafe/jev-1.13`. Never `jev-latest` or `jev-router`.
- Don't look at test-set results during tuning.
