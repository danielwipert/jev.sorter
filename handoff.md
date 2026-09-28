# Handoff

_Rewritten at the end of every session. Keep it short._

**Last session:** 2026-09-27

## What we did
**Week 1 done** (steps 1.1–1.7).
- **1.1** Pinned `requirements.txt`. `OPENROUTER_API_KEY` set in the cloud environment and verified. Reusing an existing key (Dan's choice, $50 limit, has other spend), so project spend comes from our logs' `cost_usd`, not the OpenRouter dashboard.
- **1.2** `sample_data.py` → `data/tuning.csv` (500) and `data/test.csv` (1,000), seed 42. Source: PolyAI's Banking77 CSVs pinned to commit `57ec275` (the Hugging Face copy no longer loads). Columns: `message_id`, `text`, `label`. Some tuning categories are thin (`contactless_not_working` has 1).
- **1.3** `explore/jev_first_call.py`: one Jev call works.
  - `TypeSafeClient(api_key=..., base_url="https://openrouter.ai/api")`, `system_one(model="typesafe/jev-1.13", state=text, questions={"category": Choice(instructions=..., criteria={label: description})})`.
  - Confidence is **0–1** → ×100. Response `model` is `typesafe/jev-1.13-20260917`; log that.
  - SDK drops cost; read `result.raw_http_response.json()["usage"]["cost"]`. ~$0.00007/call.
- **1.4** `build_categories.py` → `categories/v1.json` (`{name: description}`) and `keywords/v1.json` (`{name: [words]}`). Keywords learned from train **minus tuning messages**. Deterministic. `CHANGELOG.md` has the v1 line. Only 2.6% of tuning messages lack a keyword of their true category, but some keywords are generic ("help", "try").
- **1.5** `gate.py`: `gate(message, predicted, confidence, categories, keywords, threshold=None)` → `(gate_result, gate_reason, keyword_miss)`. `python test_gate.py`: 7 tests pass.
  - `threshold=None` = checks 1–3 only. `run.py` logs that; `analyze.py` calls the same `gate()` with each 50/70/85% threshold.
  - `KEYWORD_CHECK_BLOCKS = False` until step 2.1. `words()` (the keyword match rule) lives in `gate.py`.
- **1.6** `run.py` (Jev path; `ask_claude()` is a stub for step 2.4). Writes rows as it goes; re-running resumes and skips logged messages (`--fresh` restarts); `--limit N`; `--set test` needs `--confirm-test`.
  - Ran Jev v1 on all 500 tuning messages → `logs/decisions_jev_tuning_v1.csv`. **79.0% accuracy (all answers), $0.036 total, ~0.2 s/call, 0 invalid categories.**
  - `keyword_miss`: 1.5% of correct answers, 14.3% of wrong ones. Promising for step 2.1 (rule of thumb < 10%).
  - Biggest early confusion: `card_arrival` vs `card_delivery_estimate`.
- **1.7** `analyze.py` (`python analyze.py` = all logs). Re-gates every row with `gate()`; thresholds always from the model's tuning log for the same description version. Cascade (contender E) not built yet (step 2.5).
  - Jev v1 on tuning: thresholds 97 / 85 / 66 → realized auto-accept 52.4 / 70.6 / 85.4%, accuracy on auto-accepted **93.9 / 90.1 / 85.0%**. (Realized overshoots target because Jev's confidences are whole numbers and tie at the threshold.)
  - Calibration: 90–100 band is 91.7% right (325 msgs); lower bands are noisy and small.
  - Keyword false-alarm rate: 1.5% of correct answers.
  - Top confused pairs: card_arrival/card_delivery_estimate (5), card_payment_wrong_exchange_rate/exchange_rate (5), verify_my_identity/why_verify_identity (4), change_pin/get_physical_card (4), get_physical_card/order_physical_card (4), card_payment/direct_debit_payment_not_recognised (3), card_not_working/declined_card_payment (3), beneficiary_not_allowed/declined_transfer (3).
- **2.1** Keyword check promoted to **blocking** (`KEYWORD_CHECK_BLOCKS = True`), logged in `CHANGELOG.md` (Dan's decision). Jev v1 tuning accuracy on auto-accepted now **94.2 / 90.3 / 85.4%** at 50/70/85% (was 93.9 / 90.1 / 85.0). The `gate_result` column in `decisions_jev_tuning_v1.csv` was written flag-only; `analyze.py` re-gates, so that's fine.
- **2.2** `draft_rewrites.py` (two passes: draft → Dan edits `drafts/vN_approved.json` → `--apply` builds `categories/vN.json` + CHANGELOG row). Sonnet 5 slug `anthropic/claude-sonnet-5`, Haiku `anthropic/claude-haiku-4.5` (in `run.py` `CLAUDE_MODELS`, copied from OpenRouter).
  - v2: 15 categories rewritten; 14 accepted as-is, 1 edited by Dan (`get_physical_card` → about the PIN). Draft cost $0.03.
  - **Jev v2 on tuning: 83.0% overall (v1: 79.0%); auto-accepted accuracy 97.0 / 93.4 / 87.8% at 50/70/85% (v1: 94.2 / 90.3 / 85.4).** 29 fixed, 9 broken. Rewritten categories 66.4% → 83.2%; others unchanged (82.9%).
  - Caveat: improvement is measured on the same tuning messages the rewrites were based on; the test set is the real check.
  - Cost per 1,000 Jev calls up $0.07 → $0.10 (longer descriptions = more input tokens).
  - New side effect: `declined_transfer`'s new wording ("technical issues") now pulls in `failed_transfer` messages (2 broken).
- **2.3** Round 2. `draft_rewrites.py` hardened (logs every call incl. failed to `drafts/vN_calls.jsonl`, counted in spend; low reasoning effort + 16k budget; `--also PAIR`). 3 failed Sonnet calls first (~$0.09). v3: 15 categories, 11 accepted as-is, 4 edited by Dan (card_arrival, declined_transfer, failed_transfer, reverted_card_payment?).
  - **Jev tuning, v1 / v2 / v3:** all answers 79.0 / 83.0 / 82.6%; auto-accepted accuracy @50: 94.2 / 97.0 / 96.4; **@70: 90.3 / 93.4 / 93.8**; @85: 85.4 / 87.8 / 88.1. $/1000: 0.071 / 0.100 / 0.121.
  - v2→v3: 16 fixed, 18 broken. Rewritten categories 75.4→82.3%, but others fell 85.7→82.7%. Side effects: new `extra_charge_on_statement` ("unfamiliar/unexplained charge") pulls in card_payment_not_recognised (6) + direct_debit (1); broader `pending_transfer` pulls in transfer_not_received_by_recipient (3); edited `card_arrival` pulls 2 card_delivery_estimate.
  - **Decision (Dan): final descriptions = v2.** Round 2 was a wash; v2 is cheaper with fewer side effects. Logged in `CHANGELOG.md`. v3 kept in repo, unused. Round 2 is reported as "tried, no net gain".
- **2.4** `ask_claude()` in `run.py`: fixed prompt (77 names + descriptions, message, JSON instruction), one call, extended thinking off, `response_format=json_object`, strips ```json fences (Haiku adds them). Unreadable reply → raw text as category → fails check 1.
  - Tuning, v2 descriptions (Jev / Sonnet 5 / Haiku 4.5): all answers **83.0 / 79.4 / 76.4%**; hard hallucinations 0 / 0 / 0; auto-accepted accuracy @70% target **93.4 / 89.4 / 84.9%**; $/1000 **0.10 / 5.26 / 1.90**; median ms 220 / 1856 / 879.
  - Claude confidences cluster on round numbers (Sonnet: 90, 85, 95...; Haiku: 95, 85, 92...), so realized auto-accept overshoots badly: @70% target Sonnet accepts 75.2%, Haiku 80.8% (Jev 70.0%). Rows are not at equal volume. Flag this on the results page; don't move the goalposts.
  - Calibration 90–100 band: Jev 93.6%, Sonnet 96.6%, Haiku 88.3%.
  - Caveat: v2 descriptions were tuned on Jev's tuning mistakes (tilt toward Jev); test set is the real check.
- **2.5** Test set opened. All 4 test logs complete (1,000 each). `python analyze.py` prints and saves `results/results_table.csv`, `results/cascade.csv`, `results/calibration.csv`, plus the verdict.
  - **Verdict (Section 10, 70% row): JEV WINS.** Jev B 91.4% vs Sonnet C 91.0% on auto-accepted (Jev +0.4); $0.10 vs $5.25 per 1,000 (52x).
  - Test, @50/70/85 accuracy on auto-accepted: A 96.0/90.5/85.7; B 97.0/91.4/87.4; C 93.8/91.0/87.4; D 89.4/84.6/81.6. All answers: A 79.3, B 81.6, C 82.3, D 76.9%.
  - Realized auto-accept @70% target: B 73.1%, C 75.3%, D 81.4% (Claude's round-number confidences). Supporting check at equal volume (top 730 answers): Jev 91.4 vs Sonnet 91.8, so the verdict holds at matched volume too (not part of the pre-registered rule).
  - B vs A (the loop): +0.9 pts @70, +2.3 pts all answers (smaller than on tuning: tuning lead partly overfit).
  - Cascade E @70: Jev handles 73.1%, overall 82.8% at $1.51/1,000 vs Sonnet alone 82.3% at $5.25.
  - Hard hallucinations: Jev 0, Sonnet 0, Haiku 2 (0.2%): both were valid JSON followed by extra commentary ("Wait, let me reconsider…"), unreadable → counted per spec. Neither would have been auto-accepted.
  - Calibration 90–100 band: Jev B 92.5%, Sonnet 96.0%, Haiku 89.3%.
  - **Total spend: $11.20** (Sonnet $7.88, Haiku $2.86, Jev $0.32, drafting $0.14).
- **2.6** Results page `docs/index.md` (Section 15's 8 parts; pre-registered bar verbatim; links to logs/versions on GitHub), `docs/calibration.svg` from `make_chart.py` (plain SVG, hover tooltips, hollow = < 20 msgs), `docs/_config.yml` (default Primer theme), `README.md`. Page numbers cross-checked against `results/*.csv`.
  - This branch (`claude/practical-noether-o2xtat`) is the repo's default branch, so page links point to it.

## Next session: do these, in order
1. Dan: turn on GitHub Pages (repo Settings → Pages → Source "Deploy from a branch", branch `claude/practical-noether-o2xtat`, folder `/docs`). Page URL: https://danielwipert.github.io/jev.sorter/. Check that the chart and tables render.
2. Step 2.7 (optional): contender F = Sonnet with v1 descriptions on test (~$5.25) to check the description tilt. If run, add it to the page's caveats and table.

## Notes
- Always pin `typesafe/jev-1.13`. Never `jev-latest` or `jev-router`.
- Don't look at test-set results during tuning.
- Code reads `OPENROUTER_API_KEY` from the environment, falls back to `.env` locally.
- Source for the OpenRouter setup: https://openrouter.ai/docs/guides/community/typesafe-sdk
