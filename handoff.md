# Handoff

_Rewritten at the end of every session. Keep it short._

**Last session:** 2026-09-30

## Where things stand
- **Round 1 is done and live:** Jev beat Sonnet 5 at the 70% row (91.4% vs 91.0%, 52× cheaper). Site: https://danielwipert.github.io/jev.sorter/
- **Round 2 started: Jev vs. open alternatives (Laya, SemIf, Bespoke Nimble).** The full plan, rules and findings so far are in **`planning/round2-open-alternatives-spec.md`**. It's pre-registered in `CHANGELOG.md` (2026-09-30).

## What we did this session
- Checked where each model can run. None are on OpenRouter.
- **Laya** added to `run.py` (`--model laya`). It runs on this container's CPU, and its settings are locked (`head_max_len=512`).
- Laya full runs started. Partial tuning result: **45.6% correct vs. Jev's 83.9%** on the same 372 messages. The log is committed as WIP.
- Found that **SemIf supports only 16 options** (Banking77 needs 77), and that **Nimble's public demo is closed**. Both need a GPU, so the plan is Modal.

## Next session
1. **Dan:** create Modal and Hugging Face accounts, add `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET` and `HF_TOKEN` to the cloud environment, and start a new session. Steps are in the spec, "What Dan needs to do".
2. **Dan:** decide SemIf **A** (widen to 77 labels; recommended) or **B** (report "can't do 77 as shipped").
3. Finish the Laya runs if the container was reclaimed. The same commands resume where they stopped (listed in the spec).
4. Deploy Nimble and SemIf on Modal, run them, analyze, and update the site.
5. On hold: the round 1 LinkedIn rollout (post + carousel `promo/jev-vs-the-frontier.pdf`), and an optional headshot for the site.

## Notes
- Pin `typesafe/jev-1.13`; never `jev-latest` or `jev-router`.
- Key is in the `OPENROUTER_API_KEY` env var (cloud env) or `.env` locally.
- After any new log: `python analyze.py && python build_site_data.py` to refresh results and the site.
- Install with `python -m pip` (plain `pip` points at a different Python here). Laya needs `pip install laya`, which isn't in `requirements.txt` yet.
