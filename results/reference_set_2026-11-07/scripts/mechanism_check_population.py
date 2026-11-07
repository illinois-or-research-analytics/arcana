"""Mechanism check for theta, from nodelist.csv and edgelist.csv. Sample: replicate r0 of each label set, cluster-aware citing on (theta=50) vs off (theta=1000000)."""
import numpy as np, pandas as pd
A = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/"
THETA = 50
edges_bins = [0, 10, 20, 30, 40, 50, 60, 80, 120, 200, 400, 10**9]
def agents_table(kind, res, rep="r0"):
    d = f"{A}{kind}_cpm{res}/{rep}/output/"
    nl = pd.read_csv(d + "nodelist.csv", usecols=["node_id", "type", "year", "alpha", "cluster_id"])
    ed = pd.read_csv(d + "edgelist.csv", dtype=np.int64).iloc[:, :2]
    g = nl.groupby(["cluster_id", "year"]).size().rename("n").reset_index()
    g["before"] = g.groupby("cluster_id").n.cumsum() - g.n          # members of the cluster published before year y
    nl = nl.merge(g[["cluster_id", "year", "before"]], on=["cluster_id", "year"], how="left")
    idx = pd.Index(nl.node_id); u, v = idx.get_indexer(ed.source), idx.get_indexer(ed.target)
    cid = nl.cluster_id.values; isagent = (nl.type.values == "agent")
    keep = isagent[u]
    tot = np.bincount(u[keep], minlength=len(nl)); inn = np.bincount(u[keep & (cid[u] == cid[v])], minlength=len(nl))
    a = nl[isagent].copy(); a["tot"] = tot[isagent]; a["inn"] = inn[isagent]
    return a
def by_bin(a):
    a = a.assign(bin=pd.cut(a.before, edges_bins, right=False))
    s = a.groupby("bin", observed=True).agg(agents=("tot", "size"), tot=("tot", "sum"), inn=("inn", "sum"))
    s["w"] = s.inn / s.tot * 100; return s
def alpha_slope(a):
    a = a.assign(ab=np.minimum((a.alpha * 10).astype(int), 9))
    s = a.groupby("ab").agg(tot=("tot", "sum"), inn=("inn", "sum")); w = s.inn / s.tot
    return np.polyfit((s.index.values + 0.5) / 10, w.values, 1)[0]    # change in within-cluster share per unit alpha
results = []
for res in ("0.1", "0.01", "0.001"):
    on, off = agents_table("baseline", res), agents_table("control", res)
    bon, boff = by_bin(on), by_bin(off); gap = bon.w - boff.w
    ok = (bon.tot > 20000) & (boff.tot > 20000)
    below = [b for b in bon.index if b.right <= THETA and ok[b]]; above = [b for b in bon.index if b.left >= THETA and b.left < 120 and ok[b]]
    p1 = (bon.w[pd.Interval(50, 60, closed="left")] - bon.w[pd.Interval(40, 50, closed="left")])
    p1b = abs(gap[pd.Interval(30, 40, closed="left")]) , abs(gap[pd.Interval(40, 50, closed="left")])
    p2 = boff.w[pd.Interval(50, 60, closed="left")] - boff.w[pd.Interval(40, 50, closed="left")]
    q1_on, q1_off = on[on.before >= THETA], off[off.before >= THETA]; q0_on, q0_off = on[on.before < THETA], off[off.before < THETA]
    s = dict(q1_on=alpha_slope(q1_on), q1_off=alpha_slope(q1_off), q0_on=alpha_slope(q0_on), q0_off=alpha_slope(q0_off))
    print(f"\n=== labels {res} (replicate r0) ===")
    t = pd.DataFrame({"agents_on": bon.agents, "w_on": bon.w, "w_off": boff.w, "gap": gap}).round(1); print(t.to_string())
    print(f"P1 jump of w at theta in ON ([50,60) minus [40,50)): {p1:.1f} points; control (P2): {p2:.1f} points")
    print(f"P3 gap below theta: " + ", ".join(f"{b}: {gap[b]:+.1f}" for b in below if b.left >= 20) + " | above: " + ", ".join(f"{b}: {gap[b]:+.1f}" for b in above))
    print(f"P4 slope of w per unit alpha: qualified ON {s['q1_on']:.2f} (OFF {s['q1_off']:.2f}); not qualified ON {s['q0_on']:.2f} (OFF {s['q0_off']:.2f})")
    res_ = dict(labels=res,
        P1=p1 >= 10, P2=abs(p2) < 2, P3=all(abs(gap[b]) <= 1.5 for b in below if b.left >= 20) and all(gap[b] >= 10 for b in above if b.left >= 50),
        P4=(s["q1_on"] - s["q1_off"] >= 0.3) and abs(s["q0_on"] - s["q0_off"]) <= 0.1)
    results.append(res_); print("verdict:", {k: ("PASS" if v else "FAIL") for k, v in res_.items() if k != "labels"})
print("\nSUMMARY", pd.DataFrame(results).to_string(index=False))
