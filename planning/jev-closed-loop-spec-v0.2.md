# Project Spec: Jev as the Decision Model in a Closed-Loop Gate

**Status:** v0.2 — decisions locked, nothing built yet
**Language:** Python 3.11
**Date:** September 27, 2026
**Supersedes:** v0.1 (Sept 2026)

---

## 1. The idea in one paragraph

Build a light closed-loop harness in Python — decide, gate, check, learn — and put **Jev** (TypeSafe's decision model) in the "decide" seat. Then keep the harness exactly the same and swap in **Claude Sonnet 5** and **Claude Haiku 4.5**. Test on the **Banking77** dataset (77 customer-message intents). The comparison is not "Jev vs. LLMs at labeling." It is: *which model, sitting at the front of the same Python-gated pipeline, auto-accepts the most messages with the fewest confident-and-wrong answers, and at what cost?*

**What changed from v0.1:** the harness is now held constant and the model is the variable. Every contender gets the same gate, the same confidence threshold procedure, the same logs. GPT-6 Luna and Opus are dropped. Results are a public GitHub Pages site.

---

## 2. Goals

1. Build a working Jev classifier for Banking77's 77 categories.
2. Wrap it in a closed loop where every decision passes through deterministic Python checks before confidence gets a say.
3. Run Claude Sonnet 5 and Claude Haiku 4.5 through the *identical* harness.
4. Report, for each model, accuracy on auto-accepted messages at 50 / 70 / 85% auto-accept rates, plus cost per 1,000 gated decisions.
5. Answer a pre-registered question (Section 10) without moving the goalposts.
6. Publish the build and results as a public GitHub Pages site.

## 3. Non-goals

- No real email inbox. Phase 2.
- No UI. Results are CSVs, a printed summary, and a markdown page.
- No fine-tuning. Jev improves only through category descriptions, keyword lists, and thresholds.
- No production deployment.
- No designed HTML page. GitHub's default Pages theme on a markdown file is the deliverable.

---

## 4. Background

### Jev
- A decision model, not a text generator. Send it a message ("state") and a question; it returns a typed answer plus a confidence score. Its **Choice** question type picks one of up to 255 options, so all 77 categories fit in one question.
- Jev *cannot* return a label that isn't in the option list. That is a structural property, and it matters for Section 6.
- Accessed here through **OpenRouter**, model ID `typesafe/jev-1.13`. Never use `jev-latest` (moves) or `jev-router` (a different product that picks a model per request).
- OpenRouter exposes Jev through a separate Decisions API surface, not the ordinary chat endpoint. The TypeSafe Python SDK can be pointed at OpenRouter with a base-URL change.
- Listed price: about $0.042 per million input tokens, $0 output. Every Jev run in this project costs cents.
- Weaknesses to watch: reads descriptions literally; no knowledge beyond what is in the request. Jev launched mid-September 2026 and is marked beta on OpenRouter, so pricing, limits, and versions may change.

### Banking77
- ~13,000 short customer messages to a bank, each labeled with 1 of 77 intents (e.g. `card_arrival`, `lost_or_stolen_card`).
- Pre-split: train ~10,000, test ~3,000.
- Caveat: these are short chat-style messages, not emails with subjects, signatures, and threads. Findings are a proxy for email triage, not a proof.

---

## 5. The closed loop

```
   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
   │ 1.DECIDE │ ──> │ 2. GATE  │ ──> │ 3. CHECK │ ──> │ 4. LEARN │
   └──────────┘     └──────────┘     └──────────┘     └──────────┘
        ^                                                   │
        └───────────────────────────────────────────────────┘
```

| Stage | What happens | Who does it |
|---|---|---|
| 1. Decide | The model returns a category and a confidence 0–100 | Jev, Sonnet 5, or Haiku 4.5 — the only thing that changes |
| 2. Gate | Deterministic checks, then the confidence threshold. Pass → auto-accept. Fail → review pile, with the reason logged | `gate.py` (Section 6) |
| 3. Check | Compare the answer to the correct label | Banking77 labels (a human, in phase 2) |
| 4. Learn | Find the most-confused category pairs, rewrite their descriptions, save as a new version | Claude drafts, Dan approves (Section 9) |

---

## 6. The gate (`gate.py`)

Four checks, in this order. The first three involve no model. Any failure sends the message to review with the reason written to the log.

| # | Check | Fail reason | Notes |
|---|---|---|---|
| 1 | Is the returned category *exactly* one of the 77 names in `categories/vN.json`? | `invalid_category` | Catches every hard hallucination. Jev cannot fail this by construction; Claude can. |
| 2 | Is the message non-empty after stripping whitespace? | `empty_input` | Will almost never fire on Banking77. It exists because this gate is meant to be lifted unchanged into phase 2. |
| 3 | Does the message contain at least one keyword from the predicted category's list? | `keyword_miss` | **Round 1: flag only** — logged as `keyword_miss = true`, does not block. Promoted to a blocking check only after its false-alarm rate on the tuning set is known. See open question 1. |
| 4 | Is confidence ≥ this model's threshold for the chosen auto-accept rate? | `low_confidence` | Threshold procedure in Section 8. |

**Keyword lists** (`keywords/vN.json`) are generated, not hand-written: the words in the category name, plus the most distinctive words per category from the *train* split (highest ratio of in-category frequency to overall frequency). Saved as an editable file and versioned like descriptions.

**Why this order:** a model can be 95% confident in a broken answer. Running the deterministic checks first means a confident-but-invalid answer can never be auto-accepted. This is the "Python gates before model confidence" principle in code, and `gate.py` is the file that carries it.

---

## 7. Contenders

All contenders see the **same 1,000 test messages** and the **same final category descriptions**.

| ID | Setup | What it answers |
|---|---|---|
| A | Jev, descriptions v1 | Baseline. Where Jev starts before any tuning. |
| B | Jev, final tuned descriptions | Does the loop improve Jev? (B vs. A) |
| C | Claude Sonnet 5, final descriptions | The strong general model in the same seat |
| D | Claude Haiku 4.5, final descriptions | The cheap general model in the same seat |
| E | Cascade: Jev if auto-accepted, else Sonnet 5 | The practical pipeline shape. **Computed from B and C's logs — no new API calls.** Cost = Jev on all + Sonnet on the non-accepted slice only. |
| F *(optional)* | Sonnet 5, descriptions v1 | Did description tuning help Claude too, or only Jev? Run only if week 2 has slack (~$5). |

**Confidence sources**
- Jev: the confidence it returns natively. If Jev reports on a 0–1 scale, multiply by 100 so all models share one scale.
- Claude models: the prompt asks for JSON `{"category": "<exact name>", "confidence": <0-100>}`. One call per message. No sampling, no top-2. If self-reported confidence turns out poorly calibrated, that is a finding, not a bug to engineer around.

**Fairness notes**
- The final descriptions are tuned on Jev's confusions, then handed to Claude. This tilts slightly toward Jev. Contender F is the check on that tilt.
- Claude gets a fixed, simple prompt: the 77 names and descriptions, the message, and the JSON instruction. Any output that fails check 1 counts as a hard hallucination.
- All versions pinned. Claude model slugs copied from OpenRouter's model pages at setup, never typed from memory.

---

## 8. Threshold procedure and reporting

Each model gets its own thresholds, because a "90" from Jev and a "90" from Claude do not mean the same thing.

**Procedure, per model:**
1. Run the model on the **tuning set** (500 messages). Apply gate checks 1–3.
2. Among messages that passed checks 1–3, sort by confidence, highest first. Ties broken by message id (ascending) so runs are reproducible.
3. Read off the confidence value at the point where 50%, 70%, and 85% of *all* tuning messages would be auto-accepted. Those three values are the model's thresholds.
4. Apply those exact thresholds, unchanged, to the **final test set** (1,000 messages).
5. Report what actually happened on the test set: the realized auto-accept rate (may land at 68% or 72%, report the real number), and the accuracy of the auto-accepted pile.

**The results table** (one row per model per cutoff):

| Model | Target auto-accept | Threshold | Realized auto-accept | Accuracy on auto-accepted | Soft hallucination rate | Hard hallucination rate |

Soft hallucination rate = 1 − accuracy on auto-accepted. Hard hallucination rate = share of all answers that failed check 1.

**Why a curve, not a point:** nobody has seen the data yet. Picking "95% accuracy" or "70% volume" in advance is a guess. The curve costs no extra code and lets the single-sentence finding be lifted from whichever row matters afterward.

---

## 9. The Learn stage

What can change between runs, in order of leverage:
1. **Category descriptions** — the main lever. v1 is auto-generated from names (`card_arrival` → "card arrival"). Rewrites add the detail that separates confused pairs.
2. **Keyword lists** — regenerated or hand-edited alongside descriptions.
3. **Thresholds** — recomputed every run by the Section 8 procedure; never hand-set.

**Procedure, per round:**
1. `analyze.py` prints the top ~8 confused pairs on the tuning set, with 3 example messages each.
2. `draft_rewrites.py` packages those pairs and examples into one Sonnet 5 call and prints proposed new descriptions for the 16 affected categories.
3. Dan edits or accepts each one. The script records which drafts were changed.
4. Save as `categories/v{N+1}.json`. Append to `CHANGELOG.md`: version, which pairs were rewritten, why, and whether the draft was accepted as-is.
5. Re-run Jev on the tuning set. Compare to the previous version.

Two rounds, maximum. Every version stays in the repo; any version can be re-run.

**Disclosure:** `findings.md` states that description drafts came from Claude Sonnet 5 and were human-approved.

---

## 10. Success criteria — pre-registered

Written before the first run. The headline of the results page is constrained by this section.

**Jev wins** if, at the 70% auto-accept row on the final test set:
- its accuracy on auto-accepted messages is within **3 points** of Sonnet 5's, **and**
- its cost per 1,000 gated decisions is at least **10x lower** than Sonnet 5's.

The 50% and 85% rows are supporting evidence: they show whether the gap widens or narrows as each model is pushed into its less-confident answers.

**"Not yet"** if Jev misses either condition. The headline then reads "not yet the right gate for this task," and the cascade (contender E) is reported alongside as the practical alternative.

Secondary claims, reported regardless of the headline:
- B vs. A: how many points the loop added to Jev.
- Hard hallucination rate per model (expected: Jev 0% by construction).
- Calibration: for each model, accuracy within confidence bands (50–59, 60–69, ... 90–100). This is the "does 90 mean 90" chart.

---

## 11. Data plan

| Set | Source | Size | Seed | Used for |
|---|---|---|---|---|
| Tuning | Banking77 train split | 500 | 42 | Running the loop, finding confusions, rewriting descriptions, choosing thresholds |
| Final test | Banking77 test split | 1,000 | 42 | Final comparison only. **Not opened during tuning.** |

Both samples are drawn once, saved to `data/tuning.csv` and `data/test.csv`, and committed. Every model reads the same files.

---

## 12. Repository layout

Public repo. Suggested name: `jev-gate-bench`.

```
jev-gate-bench/
├── README.md              # what this is, how to run it, link to the results page
├── docs/
│   └── index.md           # the GitHub Pages site: build story + results (Section 15)
├── run.py                 # --model jev|sonnet|haiku --set tuning|test --categories vN
├── gate.py                # the four checks from Section 6; ~20 lines; reused in phase 2
├── analyze.py             # scores, curve table, confusion pairs, calibration, spend, cascade
├── draft_rewrites.py      # packages confused pairs → one Sonnet call → proposed descriptions
├── build_categories.py    # generates categories/v1.json and keywords/v1.json from Banking77
├── categories/
│   ├── v1.json            # 77 names + auto-generated descriptions
│   ├── v2.json
│   └── v3.json
├── keywords/
│   └── v1.json            # generated keyword lists, editable
├── data/
│   ├── tuning.csv         # 500 rows, seed 42
│   └── test.csv           # 1,000 rows, seed 42
├── logs/
│   └── decisions_{model}_{set}_{categories}.csv
├── CHANGELOG.md           # one line per description version: what, why, accepted as-is?
├── requirements.txt
├── .env                   # OPENROUTER_API_KEY — git-ignored from the first commit
└── .gitignore
```

`run.py` has two small functions, `ask_jev()` and `ask_claude()`, each returning `(category, confidence, milliseconds, cost)`. Everything else — loading, gating, logging — is shared code, so the logs are guaranteed identical in shape.

### Log columns (one row per message per run)

| Column | Notes |
|---|---|
| `message_id` | From the saved CSV |
| `message_text` | |
| `model` | `typesafe/jev-1.13`, or the exact Claude slug |
| `categories_version` | `v1`, `v2`, ... |
| `keywords_version` | |
| `predicted` | Raw string the model returned |
| `confidence` | 0–100 |
| `gate_result` | `auto_accept` or `review` |
| `gate_reason` | blank, `invalid_category`, `empty_input`, `keyword_miss`, `low_confidence` |
| `keyword_miss` | `true`/`false`, logged even while check 3 is flag-only |
| `correct` | The Banking77 label |
| `is_correct` | `true`/`false` |
| `ms` | Wall-clock for the call |
| `cost_usd` | From OpenRouter's usage/cost field, or tokens × list price if absent |

---

## 13. Cost

| Item | Estimate |
|---|---|
| Jev, all runs (tuning ×3, test ×2) | cents |
| Sonnet 5, 1,000 test messages (~2,500 in / ~20 out tokens each, ~30% tokenizer padding) | ~$5–7 |
| Haiku 4.5, 1,000 test messages | ~$3 |
| Sonnet 5 draft-rewrite calls (2 rounds) | cents |
| Contender F, optional | ~$5–7 |
| **Worst case, everything** | **~$20** |

Controls: every call's cost goes in the log; `analyze.py` prints running spend per model; the OpenRouter key carries a $25 credit limit. No cap enforced in code.

---

## 14. Build plan — two weeks, ~5.5 hours each

### Week 1 — a working Jev loop

| Step | What you do | Hours |
|---|---|---|
| 1.1 | Create the public repo. Add `.gitignore` with `.env` **before** anything else. Create the OpenRouter key, set its limit to $25, put it in `.env`. `pip install` the TypeSafe SDK, `openai` (for OpenRouter's chat endpoint), `pandas`, `datasets`. | 0.5 |
| 1.2 | Load Banking77. Draw and commit `data/tuning.csv` and `data/test.csv` with seed 42. Look at 10 examples per category to get a feel. | 0.5 |
| 1.3 | One Jev call by hand, following OpenRouter's Jev tutorial: one message, the 77 options, look at the raw response. Note the exact confidence scale. | 0.5 |
| 1.4 | `build_categories.py` → `categories/v1.json` and `keywords/v1.json`. | 0.5 |
| 1.5 | `gate.py` — the four checks, check 3 flag-only. | 0.5 |
| 1.6 | `run.py`, Jev path only. Run 20 tuning messages, inspect the log by eye, then all 500. | 1.5 |
| 1.7 | `analyze.py` — accuracy, confusion pairs, curve table, calibration bands, spend. | 1.5 |
| | **Week 1 total** | **5.5** |

End of week 1: Jev running on the tuning set with a full log and a printed curve. Descriptions still v1.

### Week 2 — tune, compare, publish

| Step | What you do | Hours |
|---|---|---|
| 2.1 | Read `keyword_miss` false-alarm rate from week 1's log. Decide: promote check 3 to blocking, or leave as flag. Log the decision in `CHANGELOG.md`. | 0.25 |
| 2.2 | Tuning round 1: `draft_rewrites.py` → approve → `v2.json` → re-run Jev on tuning. | 0.75 |
| 2.3 | Tuning round 2 → `v3.json` → re-run. | 0.75 |
| 2.4 | Add `ask_claude()` to `run.py`. Test on 5 messages. Run Sonnet 5 and Haiku 4.5 on the tuning set (for their thresholds), then on the test set. | 1.25 |
| 2.5 | Run Jev v1 (A) and Jev v3 (B) on the test set. `analyze.py` computes the cascade (E) from B and C's logs. Produce the final table. | 0.5 |
| 2.6 | Write `docs/index.md`: the build story, the table, the pre-registered verdict, caveats, phase-2 plan. Enable GitHub Pages on `/docs`. Finish `README.md`. | 1.5 |
| 2.7 | Buffer. If unused: contender F. | 0.5 |
| | **Week 2 total** | **5.5** |

Target: page live **Sunday, October 11, 2026**.

If week 2 slips, drop in this order: contender F, the second tuning round, Haiku.

---

## 15. Deliverable — the public page

`docs/index.md`, rendered by GitHub Pages with the default theme. Sections:
1. The question, in two sentences.
2. The harness diagram and the four gate checks.
3. What was tested: data, contenders, versions, the pre-registered bar (copied verbatim from Section 10).
4. The results table and the calibration chart.
5. The verdict, constrained by Section 10.
6. Caveats: Banking77 ≠ email; descriptions tuned on Jev's mistakes; Jev is a beta product with vendor-run benchmarks; Claude's confidence is self-reported.
7. Phase 2.
8. Links to the logs and every description version, so any number in the table can be checked.

---

## 16. Risks and limitations

- **Banking77 ≠ email.** Findings need a second test on real emails before any claim about email triage.
- **Overfitting to the tuning set.** Guarded by the untouched test set and by thresholds chosen on tuning only.
- **Genuinely overlapping categories** (several card and transfer intents). A ceiling for every model.
- **Jev is new and beta.** Pricing, rate limits, API shape, and versions may change mid-project. Pinning `jev-1.13` protects the comparison, not the schedule.
- **Self-reported LLM confidence** may be clustered and overconfident. This is measured, not assumed, and it is part of the finding either way.
- **Description tilt toward Jev.** Contender F is the check; if F is skipped, the caveat is stated on the page.
- **Public repo.** A leaked key is the one real security risk; `.env` is ignored before the first commit.
- **Two-week momentum.** Week 1 ends with a working loop and a visible curve on purpose, so week 2 starts from a result, not a to-do list.

---

## 17. Decisions log

Each decision was made explicitly, one at a time, with options considered.

| # | Decision | Options considered | Chosen | Rationale |
|---|---|---|---|---|
| 1 | API access | Direct vendor keys; one OpenRouter key; mixed | **One OpenRouter key** | One signup, one bill, no TypeSafe waitlist; cost difference is a rounding error. Jev pinned to `typesafe/jev-1.13`. Vercel AI Gateway is the fallback if OpenRouter's beta Jev endpoint misbehaves. |
| 2 | Spend control | Hard cap in code; log + key-level limit; log only | **Log + $25 key limit** | OpenRouter is prepaid so the downside is already bounded; 15 lines of cap code buys little. Spend column feeds cost-per-1,000. |
| 3 | Hallucination definition | Soft headline; hard headline; both equal; soft only | **Soft headline, hard secondary** | Soft (confident-and-wrong) is what a gate exists to prevent and maps to downstream harm. Hard stays as a row because "typed output can't invent a label" is a real structural point for Jev. |
| 4 | Gate checks | Confidence only; validity + non-empty + confidence; plus keyword rule | **All four, keyword as flag first** | Deterministic checks before confidence is the project's philosophy. Keyword rule accepted at +2 hours; runs as a logged flag until its false-alarm rate is known. |
| 5 | Threshold rule | Fix accuracy at 95%; fix volume at 70%; curve | **Curve at 50/70/85%** | No data seen yet; a curve keeps the guess out of the spec and costs no extra code. Thresholds chosen on tuning, applied to test. |
| 6 | Claude confidence | Self-reported; sampled agreement; top-2 gap | **Self-reported, one call** | Tests whether LLM confidence is usable as-is, which is the honest form of "swap the model, keep the harness." Sampling is a phase-2 experiment. |
| 7 | Who rewrites descriptions | Dan by hand; Claude drafts + Dan approves; fully automatic | **Claude drafts, Dan approves** | The approval step and the version log are where the trust lives, not the drafter. Cuts each round from ~1 hour to ~15 minutes. Disclosed in findings. |
| 8 | Win condition | Strict parity; tolerance band; beat Haiku; cost per correct | **Within 3 pts of Sonnet 5 at 70% + ≥10x cheaper** | Keeps the claim strong by measuring against Sonnet, respects the cost reality, and the "not yet" outcome is defined in advance. |
| 9 | Deliverable and home | README + findings; plus public post; Chorus doc / new repo; existing repo; no git | **Public GitHub Pages site, new standalone repo** | Public claims need checkable logs; a standalone repo is shareable by link; description versions need git history because they are what the loop improves. |
| 10 | Timeline | 1 week full scope; 2 weeks full scope; 1 week minus keyword rule | **Two weeks, ~5.5 hrs/week** | Only option that keeps every decision above and fits stated capacity. Page live Oct 11. |

---

## 18. Open questions (remaining)

1. **Keyword rule: flag or block?** Decided at step 2.1 from week 1's false-alarm rate. Rule of thumb: promote to blocking only if fewer than ~10% of *correct* answers trip it.
2. **Contender F.** Run only if step 2.7's buffer is unused.
3. **Phase 2 email source.** Which real inbox, who labels, how many messages. Not needed to start.
4. **Jev's confidence scale.** Confirm at step 1.3 whether it is 0–1 or 0–100 and normalize once.
