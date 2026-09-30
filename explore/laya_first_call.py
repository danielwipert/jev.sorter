"""First look at Laya: 20 tuning messages, a few settings, accuracy + speed. No logging."""
import json, time, sys
import pandas as pd
import laya

cats = json.loads(open("categories/v2.json").read())
q = {"category": {"type": "choice", "instructions": "Which category best describes this bank customer's message?", "criteria": cats}}
msgs = pd.read_csv("data/tuning.csv").head(20)
for name in sys.argv[1:]:
    model, hml, ml = name.split(":")
    agent = laya.load(*(("convaiinnovations/laya",) if model == "english" else ("convaiinnovations/laya",)),
                      subfolder=None if model == "english" else model, device="cpu")
    ok, t0 = 0, time.perf_counter()
    for r in msgs.itertuples():
        a = agent.predict(r.text, q, head_max_len=int(hml), max_len=int(ml))["answers"]["category"]
        ok += a["choice"] == r.label
    print(name, f"acc {ok}/20", f"{(time.perf_counter()-t0)/20*1000:.0f} ms/msg", "sample:", {k: a[k] for k in a if k != 'probs'} if True else "")
