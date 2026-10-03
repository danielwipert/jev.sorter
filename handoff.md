# Handoff

_Rewritten at the end of every session. Keep it short._

**Last session:** 2026-10-03

## Where things stand
- **Round 1 is done and live:** Jev beat Sonnet 5 at the 70% row (91.4% vs 91.0%, 52× cheaper). Site: https://danielwipert.github.io/jev.sorter/
- **Round 2 started: Jev vs. open alternatives (Laya, SemIf, Bespoke Nimble).** The full plan, rules and findings so far are in **`planning/round2-open-alternatives-spec.md`**. It's pre-registered in `CHANGELOG.md` (2026-09-30).

## What we did this session
- **2026-10-02:** Dug into the confidence scores and drafted LinkedIn post 2: `promo/linkedin-post-2-confidence.md`. Settings between 50% and 90% automation: Jev 38, Sonnet 8, Haiku 3. Sonnet jumps from 45% to 65% automation (196 messages share the score 85). Honest caveat in the post: Sonnet's 90+ scores are more trustworthy (96% vs. 92.5%).

_From 2026-09-30:_
- Checked where each model can run. None are on OpenRouter.
- **Laya** added to `run.py` (`--model laya`). It runs on this container's CPU, and its settings are locked (`head_max_len=512`).
- Laya full runs started. Partial tuning result: **45.6% correct vs. Jev's 83.9%** on the same 372 messages. The log is committed as WIP.
- Found that **SemIf supports only 16 options** (Banking77 needs 77), and that **Nimble's public demo is closed**. Both need a GPU, so the plan is Modal.

## Next session
0. **DeepSeek V4 Flash (contender J) is done: Jev wins.** At the 70% row: 88.0% vs Jev's 91.4% on auto-accepted, 74.7% vs 81.6% on all answers, 8x cheaper ($0.013 vs $0.10 per 1,000). Details in `CHANGELOG.md` (2026-10-03). Not on the site yet; Dan decides whether to add it.
1. **Dan:** create Modal and Hugging Face accounts, add `MODAL_TOKEN_ID`, `MODAL_TOKEN_SECRET` and `HF_TOKEN` to the cloud environment, and start a new session. Steps are in the spec, "What Dan needs to do".
2. **Dan:** decide SemIf **A** (widen to 77 labels; recommended) or **B** (report "can't do 77 as shipped").
3. Finish the Laya runs if the container was reclaimed. The same commands resume where they stopped (listed in the spec).
4. Deploy Nimble and SemIf on Modal, run them, analyze, and update the site.
5. LinkedIn: post 1 (cost) is up. Post 2 (confidence) is drafted. Its image is `promo/confidence-60.png`. Post 3 (cheap model first, image `promo/cascade-1.png`) and post 4 (9-step build plan to 99%, image `promo/cascade-2.png`) are drafted in `promo/linkedin-post-3-cascade.md` and `promo/linkedin-post-4-road-to-99.md`. Dan should read the 8 top-score "errors" listed in the post 4 file before posting (rebuild: `python promo/build_post_images.py`). Headshot for the site is still optional.

## Notes
- Pin `typesafe/jev-1.13`; never `jev-latest` or `jev-router`.
- Key is in the `OPENROUTER_API_KEY` env var (cloud env) or `.env` locally.
- After any new log: `python analyze.py && python build_site_data.py` to refresh results and the site.
- Install with `python -m pip` (plain `pip` points at a different Python here). Laya needs `pip install laya`, which isn't in `requirements.txt` yet.
