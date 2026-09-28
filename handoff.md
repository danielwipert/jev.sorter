# Handoff

_Rewritten at the end of every session. Keep it short._

**Last session:** 2026-09-27 → 28

## What we did
- Built the whole spec (weeks 1–2, steps 1.1–2.7): sampling, categories/keywords, `gate.py`, `run.py` (Jev + Claude via OpenRouter), `analyze.py`, `draft_rewrites.py`, two tuning rounds, final test runs, results page.
- **Verdict (pre-registered, 70% row): Jev wins.** Jev 91.4% vs Sonnet 5 91.0% accuracy on auto-accepted, $0.10 vs $5.25 per 1,000 (52×). Final descriptions = v2 (round 2/v3 was a wash). Total spend $16.05.
- **Results page is live:** https://danielwipert.github.io/jev.sorter/ (GitHub Pages from `main` `/docs`). All links checked.
- Repo cleanup: `main` is the default branch; PR [danielwipert/jev.sorter#1](https://github.com/danielwipert/jev.sorter/pull/1) merged. `CLAUDE.md` holds the working rules (session branch → PR → merge to `main` every session).
- Full detail lives in `CHANGELOG.md`, `results/`, and `docs/index.md`.
- **Step 2.7 done (contender F, Sonnet 5 + v1 descriptions):** pre-committed in `CHANGELOG.md` before running. Result: v2 helped Sonnet about as much as Jev (+0.9 pts each at the 70% row), so no measurable tilt toward Jev. Page updated.

## Next session
1. Nothing required: every step in the spec is done. Phase 2 (real emails) is in the spec and on the page (section 7).

## Notes
- Pin `typesafe/jev-1.13`; never `jev-latest` or `jev-router`.
- Key is in the `OPENROUTER_API_KEY` env var (cloud env) or `.env` locally.
- `make_chart.py` redraws `docs/calibration.svg` from `results/calibration.csv`.
