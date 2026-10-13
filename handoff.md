# Handoff

_Rewritten at the end of every session. Keep it short._

**Last session:** 2026-10-13

## Where things stand
- **Round 1 is done and live:** Jev beat Sonnet 5 at the 70% row (91.4% vs 91.0%, 52× cheaper). Site: https://danielwipert.github.io/jev.sorter/
- **Round 2 started: Jev vs. open alternatives (Laya, SemIf, Bespoke Nimble).** The full plan, rules and findings so far are in **`planning/round2-open-alternatives-spec.md`**. It's pre-registered in `CHANGELOG.md` (2026-09-30).

## What we did this session
- **2026-10-13:** Deep dive on DeepSeek, then a confused-pairs analysis (`python confusions.py`, output in `results/confusion_pairs.md`).
  - Jev's 85 tuning mistakes are spread over 62 different pairs. That's why v3 (rewriting the top pairs) was a wash.
  - On 38 of the 85, **all 4 models** made the same "wrong" pick. Most read as answer-key errors or messages that fit both categories.
  - On the test set, DeepSeek makes the same wrong pick on 56 of Jev's 63 confident mistakes, so a second model as a fact-checker won't help.
- _2026-10-03:_ DeepSeek V4 Flash (contender J) done: Jev wins at the 70% row (88.0% vs 91.4%). DeepSeek is 8x cheaper but ~45 more silent errors per 1,000. Details in `CHANGELOG.md`. Not on the site yet.

## Next session
0. **Dan:** read the 38 "all 4 models agree" messages at the bottom of `results/confusion_pairs.md` and decide: merge near-duplicate categories, report a cleaned-key score as a secondary number, or leave it. Also decide whether DeepSeek goes on the site.
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
