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

## Where we are
Ready for step 1.4.

## Next session: do these, in order
1. Step 1.4: `build_categories.py` → `categories/v1.json` (77 names + descriptions from names) and `keywords/v1.json` (name words + distinctive train words).
2. Step 1.5: `gate.py` (four checks, check 3 flag-only).
3. Step 1.6: `run.py`, Jev path. 20 messages first, then 500.

## Notes
- Always pin `typesafe/jev-1.13`. Never `jev-latest` or `jev-router`.
- Don't look at test-set results during tuning.
- Code reads `OPENROUTER_API_KEY` from the environment, falls back to `.env` locally.
- Sources: OpenRouter TypeSafe SDK guide https://openrouter.ai/docs/guides/community/typesafe-sdk
