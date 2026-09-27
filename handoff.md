# Handoff

_Rewritten at the end of every session. Keep it short._

**Last session:** 2026-09-27

## What we did
- Set up the repo.
- Added `planning/jev-closed-loop-spec-v0.2.md` (the project spec).
- Added `.gitignore` with `.env` in it, so the API key can never be committed (spec step 1.1).
- Added this `handoff.md`.

## Where we are
Nothing built yet. We are at the start of **Week 1, step 1.1** in the spec (Section 14).

## Next session: do these, in order
1. Finish step 1.1:
   - Create an OpenRouter key, set its credit limit to $25.
   - Create `.env` in the repo root with `OPENROUTER_API_KEY=...` (it is already git-ignored).
   - Create `requirements.txt` (TypeSafe SDK, `openai`, `pandas`, `datasets`) and `pip install -r requirements.txt`.
2. Step 1.2: load Banking77, draw `data/tuning.csv` (500, train, seed 42) and `data/test.csv` (1,000, test, seed 42), commit them.
3. Step 1.3: one Jev call by hand. Write down whether confidence is 0–1 or 0–100.

## Notes / open questions
- Always pin `typesafe/jev-1.13`. Never `jev-latest` or `jev-router`.
- Do not open `data/test.csv` results during tuning.
