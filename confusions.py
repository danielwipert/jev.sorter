"""Which category pairs do the models confuse, and do they make the SAME mistake?

Reads the v2 logs (final descriptions) for Jev, DeepSeek, Sonnet and Haiku,
on the tuning set and the test set, and writes:
  results/confusion_pairs.csv   one row per confused pair, with counts
  results/confusion_pairs.md    the top pairs with example messages, for reading

A "shared" mistake is a message where Jev and DeepSeek both picked the same wrong category.
When very different models agree on the "wrong" answer, the problem is usually the
categories (overlapping meanings) or the answer key, not the model.

Rank pairs by the TUNING set. The test set is held out: look at it to confirm, never to
choose description changes, or the final scores stop being fair.

  python confusions.py
"""

import json
from pathlib import Path

import pandas as pd

MODELS = ["jev", "deepseek", "sonnet", "haiku"]
SPLITS = ["tuning", "test"]
TOP_PAIRS = 15
EXAMPLES_PER_PAIR = 4

# Categories whose descriptions were rewritten in v3 (tried, and it was a wash).
V3_TRIED = {
    "card_arrival", "card_delivery_estimate", "pending_transfer", "transfer_timing",
    "declined_card_payment", "reverted_card_payment?", "order_physical_card",
    "card_about_to_expire", "card_payment_wrong_exchange_rate", "exchange_rate",
    "exchange_charge", "extra_charge_on_statement", "pending_card_payment",
    "declined_transfer", "failed_transfer",
}


def load(model, split):
    log = pd.read_csv(f"logs/decisions_{model}_{split}_v2.csv", dtype=str, keep_default_na=False)
    log["is_correct"] = log["is_correct"] == "true"
    return log.set_index("message_id")


def pair_of(a, b):
    """The same pair whichever way round the mistake went."""
    return " <> ".join(sorted([a, b]))


def main():
    categories = json.loads(Path("categories/v2.json").read_text())
    has_description = {k for k, v in categories.items() if v.lower() != k.replace("_", " ").lower()}

    rows = []      # one row per (split, message, model) mistake
    shared = []    # one row per (split, message) where Jev and DeepSeek made the same mistake
    for split in SPLITS:
        logs = {m: load(m, split) for m in MODELS}
        for model, log in logs.items():
            wrong = log[~log["is_correct"] & (log["predicted"] != "")]
            for mid, r in wrong.iterrows():
                rows.append({"split": split, "model": model, "pair": pair_of(r["correct"], r["predicted"])})
        jev, ds = logs["jev"], logs["deepseek"].reindex(logs["jev"].index)
        same = (~jev["is_correct"]) & (jev["predicted"] == ds["predicted"])
        for mid, r in jev[same].iterrows():
            others = [m for m in ["sonnet", "haiku"] if logs[m].loc[mid, "predicted"] == r["predicted"]]
            shared.append({
                "split": split, "pair": pair_of(r["correct"], r["predicted"]), "message": r["message_text"],
                "answer_key": r["correct"], "models_said": r["predicted"],
                "also_sonnet": "sonnet" in others, "also_haiku": "haiku" in others,
            })

    mistakes = pd.DataFrame(rows)
    shared = pd.DataFrame(shared)

    table = mistakes.pivot_table(index="pair", columns=["split", "model"], aggfunc="size", fill_value=0)
    table.columns = [f"{split}_{model}" for split, model in table.columns]
    for split in SPLITS:
        s = shared[shared["split"] == split]
        table[f"{split}_shared"] = s.groupby("pair").size()
        table[f"{split}_all4_agree"] = s[s["also_sonnet"] & s["also_haiku"]].groupby("pair").size()
    table = table.fillna(0).astype(int)

    def status(pair):
        a, b = pair.split(" <> ")
        if a in V3_TRIED and b in V3_TRIED:
            return "tried in v3"
        if a in has_description or b in has_description:
            return "partly described"
        return "not yet tried"

    table["status"] = [status(p) for p in table.index]
    table = table.sort_values(["tuning_shared", "tuning_jev"], ascending=False)
    cols = ["status", "tuning_jev", "tuning_deepseek", "tuning_shared", "tuning_all4_agree",
            "test_jev", "test_deepseek", "test_shared", "test_all4_agree"]
    table = table[cols]
    Path("results").mkdir(exist_ok=True)
    table.to_csv("results/confusion_pairs.csv")

    # Readable report: top pairs with examples, tuning set only (test set stays held out).
    lines = [
        "# Confused category pairs (v2 descriptions)",
        "",
        "Built by `python confusions.py`. Ranked by **shared** mistakes on the tuning set:",
        "messages where Jev and DeepSeek both picked the same wrong category.",
        "\"All 4\" = Sonnet and Haiku made that same pick too.",
        "Examples are from the tuning set only. The test set is held out.",
        "",
        "| # | Pair | Status | Jev wrong | DeepSeek wrong | Shared | All 4 agree | Test: shared |",
        "|---|---|---|---|---|---|---|---|",
    ]
    top = table.head(TOP_PAIRS)
    for i, (pair, r) in enumerate(top.iterrows(), 1):
        lines.append(f"| {i} | `{pair}` | {r['status']} | {r['tuning_jev']} | {r['tuning_deepseek']} | "
                     f"{r['tuning_shared']} | {r['tuning_all4_agree']} | {r['test_shared']} |")
    lines.append("")
    tuning_shared = shared[shared["split"] == "tuning"]
    for i, pair in enumerate(top.index, 1):
        ex = tuning_shared[tuning_shared["pair"] == pair].head(EXAMPLES_PER_PAIR)
        if ex.empty:
            continue
        lines += [f"## {i}. `{pair}`", ""]
        for r in ex.itertuples():
            tag = " (all 4 models)" if r.also_sonnet and r.also_haiku else ""
            lines.append(f"- \"{r.message}\": answer key `{r.answer_key}`, models said `{r.models_said}`{tag}")
        lines.append("")
    all4 = tuning_shared[tuning_shared["also_sonnet"] & tuning_shared["also_haiku"]]
    lines += [
        f"## All {len(all4)} tuning messages where all 4 models made the same \"wrong\" pick",
        "",
        "Four different models agreeing against the answer key usually means the key is wrong",
        "or the message really fits both categories. Worth a human read.",
        "",
    ]
    for r in all4.sort_values("pair").itertuples():
        lines.append(f"- \"{r.message}\": answer key `{r.answer_key}`, models said `{r.models_said}`")
    lines.append("")
    Path("results/confusion_pairs.md").write_text("\n".join(lines))

    for split in SPLITS:
        s = shared[shared["split"] == split]
        n_jev = len(mistakes[(mistakes["split"] == split) & (mistakes["model"] == "jev")])
        print(f"{split}: Jev wrong {n_jev}, same wrong pick as DeepSeek {len(s)}, "
              f"all 4 models same wrong pick {int((s['also_sonnet'] & s['also_haiku']).sum())}")
    print(table.head(TOP_PAIRS).to_string())
    print("\nWrote results/confusion_pairs.csv and results/confusion_pairs.md")


if __name__ == "__main__":
    main()
