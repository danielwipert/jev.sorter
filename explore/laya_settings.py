"""Compare Laya settings on the first 50 TUNING messages (never test). Prints accuracy + speed."""
import json, time
import pandas as pd
import laya

cats = json.loads(open("categories/" + __import__("sys").argv[1] + ".json").read())
q = {"category": {"type": "choice", "instructions": "Which category best describes this bank customer's message?", "criteria": cats}}
msgs = pd.read_csv("data/tuning.csv").head(50)
agent = laya.load("convaiinnovations/laya", device="cpu")
embed = laya.embed_fn_from_agent(agent)
runs = {k: v for k, v in {
    "head512": lambda t: agent.predict(t, q, head_max_len=512, max_len=1024),
    "head1024": lambda t: agent.predict(t, q, head_max_len=1024, max_len=2048),
    "shortlist20": lambda t: laya.predict_shortlist(agent, t, q, embed_fn=embed, k=20),
}.items() if k in __import__("sys").argv[2:]}
for name, fn in runs.items():
    ok, t0 = 0, time.perf_counter()
    for r in msgs.itertuples():
        ok += fn(r.text)["answers"]["category"]["choice"] == r.label
    print(f"{name}: {ok}/50 correct, {(time.perf_counter()-t0)/50*1000:.0f} ms/msg", flush=True)
