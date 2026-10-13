# Answer-key review (cleaned-key secondary score)

Rules: `CHANGELOG.md`, 2026-10-13 pre-registration.

## How to review
1. Open `review/relabel_test.csv` (Excel or Google Sheets is fine). **Don't open `relabel_test_key.csv`**, which says which label is the official one.
2. For each row, read the message and the two labels (descriptions are in the next columns).
3. Look at `claude_draft`. If you agree, copy it into `dan_verdict`. If not, write your own:
   - `1`: label 1 is right
   - `2`: label 2 is right
   - `both`: either label is a fair answer
   - `unclear`: can't tell (the official label is kept)
4. Use `note` for anything worth remembering.
5. Save as CSV, then run `python cleaned_scores.py`. The output says DRAFT until every row has a `dan_verdict`.

Shortcut: if you only want to check some rows, fill in the ones you disagree with and tell Claude "approve the rest of the drafts".
