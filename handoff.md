# Handoff

_Rewritten at the end of every session. Keep it short._

**Last session:** 2026-09-27 → 28

## What we did
- Built the whole spec (weeks 1–2, steps 1.1–2.6): sampling, categories/keywords, `gate.py`, `run.py` (Jev + Claude via OpenRouter), `analyze.py`, `draft_rewrites.py`, two tuning rounds, final test runs, results page.
- **Verdict (pre-registered, 70% row): Jev wins.** Jev 91.4% vs Sonnet 5 91.0% accuracy on auto-accepted, $0.10 vs $5.25 per 1,000 (52×). Final descriptions = v2 (round 2/v3 was a wash). Total spend $11.20.
- **Results page is live:** https://danielwipert.github.io/jev.sorter/ (GitHub Pages from `main` `/docs`). All links checked.
- Repo cleanup: `main` is the default branch; PR [danielwipert/jev.sorter#1](https://github.com/danielwipert/jev.sorter/pull/1) merged. `CLAUDE.md` holds the working rules (session branch → PR → merge to `main` every session).
- Full detail lives in `CHANGELOG.md`, `results/`, and `docs/index.md`.

## Next session
1. Optional step 2.7: contender F = Sonnet 5 with **v1** descriptions on the test set (~$5.25). Checks how much tuning on Jev's mistakes tilted things. If run: add a row to `analyze.py` `CONTENDERS`, re-run `python analyze.py`, update `docs/index.md` (table + the tilt caveat).
2. Otherwise the project is done. Phase 2 (real emails) is in the spec and the page's section 7.

## Notes
- Pin `typesafe/jev-1.13`; never `jev-latest` or `jev-router`.
- Key is in the `OPENROUTER_API_KEY` env var (cloud env) or `.env` locally.
- `make_chart.py` redraws `docs/calibration.svg` from `results/calibration.csv`.
