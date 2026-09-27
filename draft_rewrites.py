"""Learn stage (spec Section 9): Sonnet 5 drafts better descriptions, Dan approves.

Two passes:
  1. python draft_rewrites.py --from v1
       Finds the top confused pairs in Jev's tuning log for v1, sends them to Sonnet 5 in
       one call, and saves:
         drafts/v2_sonnet.json    Sonnet's drafts, never edited (the record)
         drafts/v2_approved.json  a copy for Dan to edit. To reject a draft, put the old
                                  description back.
  2. python draft_rewrites.py --from v1 --apply
       Builds categories/v2.json (v1 with the approved descriptions swapped in) and adds a
       line to CHANGELOG.md saying which drafts were accepted as-is, edited, or rejected.
       Keywords are not changed.
"""

import argparse
import json
import os
import shutil
from datetime import date
from pathlib import Path

import openai
from dotenv import load_dotenv

from analyze import TOP_PAIRS, confused_pairs, load_log
from run import CLAUDE_MODELS, OPENROUTER_CHAT_URL

load_dotenv()

EXAMPLES_PER_PAIR = 3

PROMPT = """You are improving category descriptions for a bank customer-message classifier.

The classifier is a decision model. It picks one category for each customer message by
reading the category descriptions. It reads them literally and knows nothing beyond what
is written in them. Right now each description is just the category name with spaces.

Below are the category pairs it confuses most often on a tuning set, with real messages it
got wrong. Write a new description for EVERY category listed under "Categories to rewrite".

Rules:
- One or two sentences each, in plain English.
- Say what the customer's message is about, and what separates this category from the one
  it gets confused with. Name the other category if that helps ("...not X, which is ...").
- Describe the intent in general terms. Do not quote or closely copy the example messages.
- Keep each description true for its whole category, not just these examples.

Reply with a JSON object only: {{"<category name>": "<new description>", ...}} using the
exact category names below.

Categories to rewrite (current description in brackets):
{categories}

Confused pairs, with messages the classifier got wrong:
{pairs}
"""


def paths(from_version):
    next_version = f"v{int(from_version.removeprefix('v')) + 1}"
    return next_version, Path(f"drafts/{next_version}_sonnet.json"), Path(f"drafts/{next_version}_approved.json")


def top_pairs(from_version):
    log = load_log(f"logs/decisions_jev_tuning_{from_version}.csv")
    groups = confused_pairs(log)
    counts = groups.size().sort_values(ascending=False, kind="stable").head(TOP_PAIRS)
    return {pair: groups.get_group(pair).head(EXAMPLES_PER_PAIR) for pair in counts.index}, counts


def draft(from_version):
    next_version, sonnet_path, approved_path = paths(from_version)
    if sonnet_path.exists():
        raise SystemExit(f"{sonnet_path} already exists. Delete it to draft again (costs another call).")
    current = json.loads(Path(f"categories/{from_version}.json").read_text())
    pairs, counts = top_pairs(from_version)
    affected = sorted({name for pair in pairs for name in pair.split(" <> ")})

    pair_text = []
    for pair, examples in pairs.items():
        lines = [f"\n{pair}  ({counts[pair]} mistakes)"]
        for r in examples.itertuples():
            lines.append(f'  - "{r.message_text}"  correct: {r.correct}, classifier said: {r.predicted}')
        pair_text.append("\n".join(lines))
    prompt = PROMPT.format(
        categories="\n".join(f"- {name} [{current[name]}]" for name in affected),
        pairs="\n".join(pair_text),
    )

    client = openai.OpenAI(api_key=os.environ["OPENROUTER_API_KEY"], base_url=OPENROUTER_CHAT_URL)
    response = client.chat.completions.create(
        model=CLAUDE_MODELS["sonnet"],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        response_format={"type": "json_object"},
    )
    drafts = json.loads(response.choices[0].message.content)
    missing = set(affected) - set(drafts)
    extra = set(drafts) - set(affected)
    if missing or extra:
        raise SystemExit(f"Sonnet's reply didn't match the categories. Missing: {missing}. Unexpected: {extra}.")

    record = {
        "from_version": from_version,
        "model": response.model,
        "cost_usd": response.model_dump()["usage"].get("cost"),
        "pairs": {pair: int(counts[pair]) for pair in pairs},
        "prompt": prompt,
        "drafts": {name: drafts[name] for name in affected},
    }
    sonnet_path.parent.mkdir(exist_ok=True)
    sonnet_path.write_text(json.dumps(record, indent=2) + "\n")
    shutil.copy(sonnet_path, approved_path)
    print(f"Saved {sonnet_path} and {approved_path}. Cost ${record['cost_usd']:.4f}\n")
    for name in affected:
        print(f"{name}\n  old: {current[name]}\n  new: {drafts[name]}\n")
    print(f"Next: review {approved_path} (edit the 'drafts' values), then run with --apply.")


def apply(from_version):
    next_version, sonnet_path, approved_path = paths(from_version)
    out_path = Path(f"categories/{next_version}.json")
    if out_path.exists():
        raise SystemExit(f"{out_path} already exists.")
    current = json.loads(Path(f"categories/{from_version}.json").read_text())
    record = json.loads(sonnet_path.read_text())
    approved = json.loads(approved_path.read_text())["drafts"]

    accepted, edited, rejected = [], [], []
    for name, text in approved.items():
        if text == current[name]:
            rejected.append(name)
        elif text == record["drafts"][name]:
            accepted.append(name)
        else:
            edited.append(name)
    out_path.write_text(json.dumps({**current, **approved}, indent=2) + "\n")

    summary = (f"{len(accepted)} accepted as-is; {len(edited)} edited ({', '.join(edited) or 'none'}); "
               f"{len(rejected)} rejected ({', '.join(rejected) or 'none'})")
    row = (f"| {next_version} | {date.today()} | Sonnet 5 drafted new descriptions for the {len(approved)} categories "
           f"in the top {len(record['pairs'])} confused pairs on Jev {from_version} tuning "
           f"({'; '.join(record['pairs'])}). Keywords unchanged. Drafts: `{sonnet_path}`, approved: `{approved_path}`. "
           f"| Separate the most-confused pairs. | {summary} |")
    changelog = Path("CHANGELOG.md")
    text = changelog.read_text()
    marker = "\n## Gate decisions"
    changelog.write_text(text.replace(marker, row + "\n" + marker, 1) if marker in text else text + row + "\n")
    print(f"Wrote {out_path}: {summary}")
    print("Added a line to CHANGELOG.md.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from", dest="from_version", required=True, help="description version to improve, e.g. v1")
    parser.add_argument("--apply", action="store_true", help="build the next version from the approved drafts")
    args = parser.parse_args()
    apply(args.from_version) if args.apply else draft(args.from_version)


if __name__ == "__main__":
    main()
