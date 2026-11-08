"""Simulation summaries for the equal-weights set and the matching original-weights runs (36 runs), in parallel."""
import numpy as np, pandas as pd, sys
from multiprocessing import Pool
A = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/"
OUT = A + "weights_equal/weights_summaries.csv"
se = pd.read_csv("/projects/illinois/eng/cs/chackoge/mf_seed_v3/seed_edgelist_v3.csv"); init = se["target"].value_counts()
groups = [("citing on, labels 0.1", "baseline_cpm0.1"), ("citing on, labels 0.01", "baseline_cpm0.01"), ("citing on, labels 0.001", "baseline_cpm0.001"),
          ("citing off, uniform generators", "control_cpm0.01"), ("generators non-random, and", "nrg_and_t1m_cpm0.01"), ("generators non-random, or", "nrg_or_t1m_cpm0.01")]
jobs = [(w, g, folder, r, A + ("weights_equal/" if w == "equal 0.25" else "") + f"{folder}/{r}/output/")
        for w in ("equal 0.25",) for g, folder in groups for r in ("r0", "r1", "r2")]

def gini(x):
    x = np.sort(x.astype(np.float64)); n = len(x); c = np.cumsum(x)
    return (n + 1 - 2 * (c / c[-1]).sum()) / n
def tail(x, frac):
    t = np.sort(x)[::-1][: int(len(x) * frac)]
    return dict(min=t[-1], median=np.median(t), q99=np.quantile(t, .99), max=t[0])

def one(job):
    w, g, folder, r, d = job
    cols = ["node_id", "type", "year", "in_degree", "cluster_id", "pa_weight", "fit_weight", "num_authors_weight", "author_reputation_weight"]
    nl = pd.read_csv(d + "nodelist.csv", usecols=cols, low_memory=False)
    ed = pd.read_csv(d + "edgelist.csv", dtype=np.int64)
    tot = nl.in_degree.sum(); idx = nl.set_index("node_id"); sy, ty = ed.source.map(idx.year).values, ed.target.map(idx.year).values
    ok_int = (not ed.duplicated().any()) and (ed.source != ed.target).all() and (sy >= ty).all() and tot == len(ed)
    sd = nl[nl.type == "seed"].set_index("node_id").in_degree; gn = sd - init.reindex(sd.index).fillna(0)
    ag = nl[nl.type == "agent"]; x = nl.in_degree.values; age = sy - ty
    t1, t01 = tail(x, 0.01), tail(x, 0.001)
    cs, ct = ed.source.map(idx.cluster_id).values, ed.target.map(idx.cluster_id).values
    ok = (cs >= 0) & (ct >= 0) & (ed.source.map(idx.type).values == "agent")
    res = dict(weights=w, group=g, run=f"{folder}/{r}", integrity=bool(ok_int), nodes=len(nl), edges=len(ed), gini=gini(x),
        top10_share_pct=np.sort(x)[::-1][:10].sum() / tot * 100, top1pct_share_pct=np.sort(x)[::-1][:int(len(x) * .01)].sum() / tot * 100,
        uncited_pct=(x == 0).mean() * 100, seed_share_new_pct=gn.sum() / (tot - len(se)) * 100,
        top1pct_median=t1["median"], top01pct_median=t01["median"], top01pct_q99=t01["q99"], max_in_degree=t1["max"],
        agents_gt50k=int((ag.in_degree > 50000).sum()), age_1_4_pct=((age >= 1) & (age <= 4)).mean() * 100,
        age_20_29_pct=((age >= 20) & (age <= 29)).mean() * 100, within_label_pct=(cs[ok] == ct[ok]).mean() * 100,
        w_pa=ag.pa_weight.mean(), w_fit=ag.fit_weight.mean(), w_na=ag.num_authors_weight.mean(), w_ar=ag.author_reputation_weight.mean())
    print("done", w, folder, r, flush=True)
    return res

if __name__ == "__main__":
    with Pool(12) as p: rows = p.map(one, jobs, chunksize=1)
    df = pd.DataFrame(rows).round(4); df.to_csv(OUT, index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
    print(df.groupby(["group", "weights"], sort=False).mean(numeric_only=True).round(2).T.to_string())
    print("all integrity:", bool(df.integrity.all()), "| wrote", OUT, len(df), "runs")
