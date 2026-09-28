# jev.sorter: Jev as the decision model in a closed-loop gate

A light Python harness (decide, gate, check, learn) with TypeSafe's **Jev** in the "decide" seat, then the same harness with **Claude Sonnet 5** and **Claude Haiku 4.5** swapped in. The test data is Banking77 (77 bank customer-message intents).

**Results page:** https://danielwipert.github.io/jev.sorter/ (source: [`docs/index.md`](docs/index.md))

**Headline (pre-registered rule, test set):** at the 70% auto-accept row, Jev scored 91.4% accuracy on auto-accepted messages against Sonnet 5's 91.0%, at $0.10 vs $5.25 per 1,000 messages. **Jev wins.**

## How it fits together

| File | What it does |
|---|---|
| `sample_data.py` | Draws `data/tuning.csv` (500) and `data/test.csv` (1,000) from Banking77, seed 42 |
| `build_categories.py` | Makes `categories/v1.json` (descriptions) and `keywords/v1.json` |
| `gate.py` | The four gate checks: valid category, non-empty, keyword, confidence threshold |
| `run.py` | Runs one model over a message set, gates every answer and logs one row per message to `logs/` |
| `analyze.py` | Accuracy, confused pairs, threshold curve, calibration, spend, the final results table, the cascade and the verdict |
| `draft_rewrites.py` | The Learn stage: Sonnet 5 drafts better descriptions and a human approves them |
| `make_chart.py` | Draws `docs/calibration.svg` from `results/calibration.csv` |
| `test_gate.py` | Tests for the gate |
| `CHANGELOG.md` | Every description version and gate decision, and why |
| `planning/` | The project spec |

## Run it yourself

1. Install Python 3.11 and the packages:
   ```
   pip install -r requirements.txt
   ```
2. Put your OpenRouter key in a file called `.env` in this folder (git ignores it):
   ```
   OPENROUTER_API_KEY=your-key-here
   ```
3. Check the gate:
   ```
   python test_gate.py
   ```
4. Re-run the analysis on the committed logs. This costs nothing and makes no API calls:
   ```
   python analyze.py
   ```
5. Or run a model yourself (this costs money; Sonnet is about $5 per 1,000 messages):
   ```
   python run.py --model jev --set tuning --categories v2
   python run.py --model sonnet --set test --categories v2 --confirm-test
   ```
   Re-running the same command resumes where it stopped. `--limit 20` runs just 20 messages.

## Notes

- Jev is called as `typesafe/jev-1.13` through OpenRouter, using the official `typesafe-sdk` package (import name `typesafe_sdk`).
- Total spend for the whole project: $11.20.
