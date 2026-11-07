import numpy as np, pandas as pd, glob, os
base = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/"
runs = [f"control_cpm{b}/{r}" for b in ("0.1", "0.01", "0.001") for r in ("r0", "r1", "r2")]
se = pd.read_csv("/projects/illinois/eng/cs/chackoge/mf_seed_v3/seed_edgelist_v3.csv")
init = se["target"].value_counts()
cols = ["node_id", "type", "year", "in_degree", "cluster_id", "pa_weight", "fit_weight", "num_authors_weight", "author_reputation_weight"]
rows = []
for r in runs:
    d = base + r + "/output/"
    try:
        nl = pd.read_csv(d + "nodelist.csv", usecols=cols, low_memory=False)
        ed = pd.read_csv(d + "edgelist.csv", dtype=np.int64)
    except Exception as e:
        rows.append(dict(run=r, error=str(e)[:80])); continue
    tot = nl.in_degree.sum()
    yr = nl.set_index("node_id").year
    sy, ty = ed.source.map(yr).values, ed.target.map(yr).values
    ok_int = (not ed.duplicated().any()) and (ed.source != ed.target).all() and (sy >= ty).all() and tot == len(ed)
    sd = nl[nl.type == "seed"].set_index("node_id").in_degree
    gn = sd - init.reindex(sd.index).fillna(0)
    ag = nl[nl.type == "agent"]
    ai = ag.in_degree
    t01 = ai.nlargest(int(len(ai) * 0.001))
    t1 = ai.nlargest(int(len(ai) * 0.01))
    age = sy - ty
    cl = nl.set_index("node_id").cluster_id
    tp = nl.set_index("node_id").type
    cs, ct = ed.source.map(cl).values, ed.target.map(cl).values
    ok = (cs >= 0) & (ct >= 0) & (ed.source.map(tp).values == "agent")
    w = ag[["pa_weight", "fit_weight", "num_authors_weight", "author_reputation_weight"]]
    rows.append(dict(run=r, papers=len(nl), edges=len(ed), integrity=bool(ok_int),
        seed_share_new_pct=gn.sum() / (tot - len(se)) * 100, seeds_ge1000=int((sd >= 1000).sum()),
        agents_gt50k=int((ai > 50000).sum()), agents_gt100k=int((ai > 100000).sum()), agent_max=int(ai.max()),
        agent_top1pct_median=t1.median(), agent_top01pct_median=t01.median(), uncited_pct=(nl.in_degree == 0).mean() * 100,
        age_1_4_pct=((age >= 1) & (age <= 4)).mean() * 100, age_20_29_pct=((age >= 20) & (age <= 29)).mean() * 100,
        within_cluster_pct=(cs[ok] == ct[ok]).mean() * 100, w_pa=w.pa_weight.mean(), w_fit=w.fit_weight.mean()))
    print("done", r, flush=True)
out = base + "control_set_summaries.csv"
pd.DataFrame(rows).round(3).to_csv(out, index=False)
print("wrote", out, len(rows), "runs")
