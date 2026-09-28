# Handoff

_Rewritten at the end of every session. Keep it short._

**Last session:** 2026-09-27 → 28

## What we did
- Built the whole spec (weeks 1–2, steps 1.1–2.7): sampling, categories/keywords, `gate.py`, `run.py` (Jev + Claude via OpenRouter), `analyze.py`, `draft_rewrites.py`, two tuning rounds, final test runs, results page.
- **Verdict (pre-registered, 70% row): Jev wins.** Jev 91.4% vs Sonnet 5 91.0% accuracy on auto-accepted, $0.10 vs $5.25 per 1,000 (52×). Final descriptions = v2 (round 2/v3 was a wash). Total spend $16.05.
- **Results page is live:** https://danielwipert.github.io/jev.sorter/ (GitHub Pages from `main` `/docs`). All links checked.
- Repo cleanup: `main` is the default branch; PR [danielwipert/jev.sorter#1](https://github.com/danielwipert/jev.sorter/pull/1) merged. `CLAUDE.md` holds the working rules (session branch → PR → merge to `main` every session).
- Full detail lives in `CHANGELOG.md`, `results/`, and the site's technical report (`docs/methods.html`).
- **Site redesign (v2):** title "Jev vs. the Frontier", more accent color (blue→violet→pink gradient; chart colors unchanged). Byline + bio + LinkedIn waiting on Dan.
- **Site redesign (v1):** custom 3-layer site in `docs/`: `index.html` (story + expandable evidence), `methods.html` (technical report), `app.js` (charts/tables), `styles.css`, `data.json` (built from logs by `build_site_data.py`). Light/dark, mobile-checked. Dan wants to iterate on the look.
- **Step 2.7 done (contender F, Sonnet 5 + v1 descriptions):** pre-committed in `CHANGELOG.md` before running. Result: v2 helped Sonnet about as much as Jev (+0.9 pts each at the 70% row), so no measurable tilt toward Jev. Page updated.

## Next session
1. Iterate on the site design with Dan's feedback (then the LinkedIn post).
2. Optional: add an author byline to the site if Dan wants one.

## Notes
- Pin `typesafe/jev-1.13`; never `jev-latest` or `jev-router`.
- Key is in the `OPENROUTER_API_KEY` env var (cloud env) or `.env` locally.
- After any new log: `python analyze.py && python build_site_data.py` to refresh results and the site.
