import re, numpy as np, pandas as pd
A = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/"
se = pd.read_csv("/projects/illinois/eng/cs/chackoge/mf_seed_v3/seed_edgelist_v3.csv"); init = se["target"].value_counts()
def gini(x):
    x = np.sort(x.astype(np.float64)); n = len(x); c = np.cumsum(x)
    return (n + 1 - 2 * (c / c[-1]).sum()) / n
def tail(x, frac):
    t = np.sort(x)[::-1][: int(len(x) * frac)]
    return dict(min=t[-1], median=np.median(t), q90=np.quantile(t, .9), q99=np.quantile(t, .99), max=t[0])
rows = []
sets = [("control (uniform generators)", f"control_cpm0.01/{r}") for r in ("r0", "r1", "r2")] + [("non-random 0.5, and", f"nrg_and_t1m_cpm0.01/{r}") for r in ("r0", "r1", "r2")] + [("non-random 0.5, or", f"nrg_or_t1m_cpm0.01/{r}") for r in ("r0", "r1", "r2")]
for name, run in sets:
    d = A + run + "/output/"
    nl = pd.read_csv(d + "nodelist.csv", usecols=["node_id", "type", "year", "in_degree", "cluster_id"], low_memory=False)
    ed = pd.read_csv(d + "edgelist.csv", dtype=np.int64)
    tot = nl.in_degree.sum(); yr = nl.set_index("node_id").year; sy, ty = ed.source.map(yr).values, ed.target.map(yr).values
    ok_int = (not ed.duplicated().any()) and (ed.source != ed.target).all() and (sy >= ty).all() and tot == len(ed)
    sd = nl[nl.type == "seed"].set_index("node_id").in_degree; gn = sd - init.reindex(sd.index).fillna(0)
    x = nl.in_degree.values; ag = nl[nl.type == "agent"].in_degree.values; age = sy - ty
    t1, t01 = tail(x, 0.01), tail(x, 0.001)
    log = open(d + "log.txt").read(); m = re.findall(r"eligible generator nodes \((\w+)\): (\d+) of (\d+)", log)
    elig = [int(a[1]) for a in m]
    rows.append(dict(set=name, run=run, integrity=bool(ok_int), edges=len(ed), gini=gini(x), top10_share=np.sort(x)[::-1][:10].sum() / tot * 100,
        top1pct_share=np.sort(x)[::-1][:int(len(x) * .01)].sum() / tot * 100, uncited=(x == 0).mean() * 100, seed_share_new=gn.sum() / (tot - len(se)) * 100,
        top1_min=t1["min"], top1_median=t1["median"], top1_q99=t1["q99"], top01_median=t01["median"], top01_q99=t01["q99"], maxdeg=t1["max"],
        agents_gt50k=int((ag > 50000).sum()), age_1_4=((age >= 1) & (age <= 4)).mean() * 100,
        elig_years=len(elig), elig_zero_years=int(sum(e == 0 for e in elig)), elig_lt20_years=int(sum(e < 20 for e in elig)), elig_min=min(elig) if elig else np.nan, elig_median=float(np.median(elig)) if elig else np.nan))
    print("done", run, flush=True)
df = pd.DataFrame(rows).round(3); df.to_csv(A + "nrg_t1m_summaries.csv", index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(df.groupby("set", sort=False).mean(numeric_only=True).round(2).T.to_string())
print("\nper-replicate sd of key measures (control / and / or):")
for k in ("gini", "top1pct_share", "top01_median", "maxdeg", "seed_share_new", "uncited"):
    print(k.ljust(16), " | ".join(f"{s[:12]:12s} mean {g[k].mean():9.2f} sd {g[k].std():7.2f}" for s, g in df.groupby("set", sort=False)))
print("\nall integrity:", bool(df.integrity.all()))
