"""Planted-node run vs the matching run without planted nodes: trajectories of the planted nodes and the in-degree of the 2027 cohort by fitness."""
import sys, numpy as np, pandas as pd
A = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/"
RUNS = {"control (no planted nodes)": A + "weights_equal/baseline_cpm0.01/r0/output/", "planted 10k/100k/1M in 2027": A + "planted_2026-11-08/centre_r0/output/"}
def gini(x):
    x = np.sort(x.astype(np.float64)); n = len(x); c = np.cumsum(x); return (n + 1 - 2 * (c / c[-1]).sum()) / n
res = {}
for name, d in RUNS.items():
    nl = pd.read_csv(d + "nodelist.csv", usecols=["node_id", "type", "year", "in_degree", "fit_peak_value", "planted_nodes_line_number"], low_memory=False)
    ed = pd.read_csv(d + "edgelist.csv", dtype=np.int64)
    yr = nl.set_index("node_id").year
    planted = nl[nl.planted_nodes_line_number > 0]
    coh = nl[(nl.type == "agent") & (nl.year == 2027) & ~(nl.planted_nodes_line_number > 0)].copy()
    ag = nl[nl.type == "agent"]
    print(f"\n=== {name}: nodes {len(nl)}, edges {len(ed)}, planted {len(planted)}")
    x = nl.in_degree.values; srt = np.sort(x)[::-1]
    print(f"gini {gini(x):.4f} | top-1% share {srt[:int(len(x)*.01)].sum()/x.sum()*100:.2f}% | uncited {(x==0).mean()*100:.2f}% | max in-degree {x.max()}")
    if len(planted):
        for _, r in planted.sort_values("fit_peak_value").iterrows():
            e = ed[ed.target == r.node_id]; per = e.source.map(yr).value_counts().sort_index()
            cum = per.cumsum()
            print(f"planted fitness {int(r.fit_peak_value):>8}: final in-degree {r.in_degree}, rank {int((x > r.in_degree).sum()+1)} of {len(x)}; cumulative in-degree at 2030/2035/2045/2066: " +
                  " / ".join(str(int(cum[cum.index <= y].iloc[-1]) if (cum.index <= y).any() else 0) for y in (2030, 2035, 2045, 2066)))
    coh["fq"] = pd.cut(coh.fit_peak_value, [0, 1, 3, 10, 10**9], labels=["fitness 1", "fitness 2-3", "fitness 4-10", "fitness 11+"])
    g = coh.groupby("fq", observed=True).in_degree.agg(["count", "mean", "median"]).round(1)
    print(f"2027 cohort excluding planted (n={len(coh)}): mean in-degree {coh.in_degree.mean():.2f}, median {coh.in_degree.median():.0f}, share of all citations {coh.in_degree.sum()/x.sum()*100:.3f}%")
    print(g.to_string())
    res[name] = (coh.in_degree.sum(), x.sum())
