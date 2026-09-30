# Round 2 Spec: Jev vs. the Open Alternatives

_Started 2026-09-30. Builds on round 1 (`jev-closed-loop-spec-v0.2.md`), which found Jev beats Claude Sonnet 5 at the 70% auto-accept row on Banking77._

## Goal
Run the same head-to-head as round 1, with open "decision model" alternatives to Jev in the decide seat:

| Contender | Model | Size | Where it runs |
|---|---|---|---|
| G | **Laya** (`convaiinnovations/laya`, English, revision `55cf4c4`) | 421M encoder | This container's CPU (free) |
| H | **SemIf** (`Qwen/Qwen3.5-4B`, direct-logit readout) | 4B | GPU needed → Modal |
| I | **Bespoke Nimble** (`bespokelabs/Bespoke-Nimble-9B`) | 9B | GPU needed → Modal |

The question is the same as round 1: *which model, at the front of the same Python-gated pipeline, auto-accepts the most messages with the fewest confident-and-wrong answers, and at what cost?*

## Rules (pre-registered in `CHANGELOG.md`, 2026-09-30)
- **Nothing in the harness changes.** Same `data/tuning.csv` (500) and `data/test.csv` (1,000), same `gate.py`, keywords v1.
- **Headline = v2 descriptions** (same as Jev B / Sonnet C / Haiku D). v1 runs are secondary, like contender F.
- Each model gets **its own thresholds** from its own v2 tuning run (spec Section 8).
- Confidence = the model's own probability for its chosen answer × 100.
- **Win condition unchanged:** the 70% auto-accept row on test, compared with Jev (B).
- Only settings needed to make a model run at all are allowed. They are chosen on **tuning messages only** and written in `CHANGELOG.md` **before** test runs.
- Self-hosted models: API cost $0. We report compute time (and Modal GPU cost) instead.

## Pipeline for each contender
1. Add an `ask_<model>()` function to `run.py` that returns `(category, confidence, ms, cost, model_version)`. Laya is done.
2. `python run.py --model <m> --set tuning --categories v2`
3. `python run.py --model <m> --set test --categories v2 --confirm-test`
4. Repeat steps 2–3 with `--categories v1`.
5. `python analyze.py && python build_site_data.py`, then add the new contenders to the site.

## Per-model notes and findings so far

### Laya: running
- Defaults fail on 77 options: 0/20 correct. Its own docs say so, because option descriptions get cut off.
- Settings tried on the first 50 tuning messages: `head_max_len=512` got 22/50 at about 1.1 s per message. `head_max_len=1024` got 11/50, and `predict_shortlist k=20` got 17/50 at about 9 s per message. **Locked: `head_max_len=512, max_len=1024`.**
- v1 descriptions (label names only) with the same settings: 24/50, about the same.
- **Partial tuning run (v2, 372/500; paused at 427/500):** 45.6% correct on all answers, vs. Jev's 83.9% on the same messages. Median about 1.06 s per message on 4 CPU cores.
- Full runs (tuning and test × v2 and v1) were started in the background. `run.py` resumes where it stopped, so re-running the same command finishes the job:
  ```
  python run.py --model laya --set tuning --categories v2
  python run.py --model laya --set test --categories v2 --confirm-test
  python run.py --model laya --set tuning --categories v1
  python run.py --model laya --set test --categories v1 --confirm-test
  ```

### SemIf: blocked on a decision + GPU
- Repo: `github.com/TheoLeeCJ/SemIf-OpenJev` (MIT). One forward pass. It labels options A–P and reads those letters' probabilities.
- **Hard limit: 16 options** (`core.py` `LETTERS = "ABCDEFGHIJKLMNOP"`). Banking77 needs 77.
- **Decision for Dan:**
  - **A (recommended):** widen to 77 single-token answer labels. Same method; reported as "SemIf, widened to 77." Written into `CHANGELOG.md` before running.
  - **B:** report "can't do 77-way as shipped."
- A CPU path exists (llama.cpp GGUF), but with about 2,000-token prompts it would take many hours here. Use Modal instead.
- LangSmith Gateway hosts SemIf (`semif-qwen3.5-4b`), but its free period ended 2026-09-28 and it likely has the same 16-option limit.

### Bespoke Nimble: blocked on GPU
- Repo: `github.com/bespokelabsai/nimble`. It supports up to 255 choices and an 8,192-token context. Needs a BF16 GPU (about 18 GB of weights) or an Apple Silicon Mac.
- Its free public demo endpoint now returns `401 proxy auth required`, so it's closed.
- The repo ships a Modal deploy script (`deploy/modal_app.py`) that serves a **TypeSafe-shaped `/v1/systemone` endpoint**. `run.py` can then call it through the existing `TypeSafeClient` by changing `base_url`.
- Pin the revision when we deploy (the public deployment used `93ec5d6`).

## What Dan needs to do (about 10 min)
1. Sign up at **modal.com** (GitHub login is fine; about $30 a month of free credit).
2. In Modal: **Settings → API Tokens → New Token** gives a token ID and a secret.
3. Sign up at **huggingface.co**, then **Settings → Access Tokens**, and create a **Read** token.
4. In the cloud environment settings (title bar → environment menu → Edit), add the environment variables `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET`, and `HF_TOKEN`. Never paste them into chat.
5. Start a **new session** (only new sessions see new variables) and say "keys are in."
6. Answer the SemIf question: A or B.

## Then Claude does
1. Deploy Nimble on Modal (pinned revision), smoke-test one message with 77 options, add `ask_nimble()`, and run tuning → test.
2. Write the SemIf adaptation (if A) into `CHANGELOG.md`, deploy it on Modal, add `ask_semif()`, and run tuning → test.
3. Shut down the Modal apps when done, so they don't run up credit.
4. Analyze, update the site, write up the verdict.

## Links
- Laya: https://github.com/NandhaKishorM/laya
- SemIf: https://github.com/TheoLeeCJ/SemIf-OpenJev
- Nimble: https://github.com/bespokelabsai/nimble · https://huggingface.co/bespokelabs/Bespoke-Nimble-9B
- Overview list: https://github.com/mturac/awesome-jev-alternatives
