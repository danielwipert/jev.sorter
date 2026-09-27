# Handoff

_Rewritten at the end of every session. Keep it short._

**Last session:** 2026-09-27

## What we did
- Set up the repo: `planning/` (spec), `.gitignore` (`.env` ignored), this file.
- Step 1.1 (code side): added `requirements.txt` with pinned versions and confirmed everything installs and imports on Python 3.11.
  - Jev SDK is **`typesafe-sdk`** (official, by TypeSafe AI). Import name: `typesafe_sdk`. Do **not** use `typesafe` (unrelated) or `typesafe-ai` (third-party shim).

## Where we are
Step 1.1 is almost done. Still waiting on the API key (Dan's action).

## Next session: do these, in order
1. Finish step 1.1. Dan needs to:
   - Create an OpenRouter key and set its credit limit to $25.
   - Add it as the environment variable `OPENROUTER_API_KEY` in the cloud environment settings (title bar → environment → Edit). It takes effect in a new session.
   - If running locally instead: put `OPENROUTER_API_KEY=...` in `.env` (already git-ignored).
   - Code reads the environment variable first, then falls back to `.env` (via `python-dotenv`).
2. Step 1.2: load Banking77, draw `data/tuning.csv` (500, train, seed 42) and `data/test.csv` (1,000, test, seed 42), commit them. (Doesn't need the key.)
3. Step 1.3: one Jev call by hand. Write down whether confidence is 0–1 or 0–100. (Needs the key.)

## Notes / open questions
- Always pin `typesafe/jev-1.13`. Never `jev-latest` or `jev-router`.
- Don't look at test-set results during tuning.
