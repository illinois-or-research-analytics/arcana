"""Single planted supernode (out-degree 50, equal weights) at fitness 10k..10M, theta 50 and theta 1,000,000: verification, final in-degree and cohort deficit vs matched controls."""
import numpy as np, pandas as pd
A = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/"
sets = {"theta 50": (A + "planted_single_out50_2026-11-08/", [A + "weights_equal/baseline_cpm0.01/r0/output/"] + [A + f"control_regen_2026-11-08/r{i}/output/" for i in (1, 2)]),
        "theta 1M": (A + "planted_single_out50_t1m_2026-11-08/", [A + f"control_t1m_regen_2026-11-08/r{i}/output/" for i in range(3)])}
levels = [("10k", 10_000), ("100k", 100_000), ("1M", 1_000_000), ("10M", 10_000_000)]
cols = ["node_id", "type", "year", "in_degree", "fit_peak_value", "pa_weight", "fit_weight", "num_authors_weight", "author_reputation_weight", "out_degree", "alpha", "num_authors", "planted_nodes_line_number"]
def row(d):
    nl = pd.read_csv(d + "nodelist.csv", usecols=cols, low_memory=False); pl = nl.planted_nodes_line_number > 0
    o = nl[~pl]; c = o[(o.year == 2027) & (o.type == "agent")]; tot = nl.in_degree.sum(); p = nl[pl]
    r = dict(nodes=len(nl), edges=tot, n_planted=int(pl.sum()), cohort_pm=c.in_degree.sum() / tot * 1e6)
    if len(p) == 1:
        x = p.iloc[0]; r.update(fit=int(x.fit_peak_value), out=int(x.out_degree), w=(round(x.pa_weight, 3), round(x.fit_weight, 3), round(x.num_authors_weight, 3), round(x.author_reputation_weight, 3)), alpha=round(x.alpha, 2), auth=int(x.num_authors), yr=int(x.year), in_degree=int(x.in_degree), planted_pm=x.in_degree / tot * 1e6)
    return r
out = []
for name, (base, ctl) in sets.items():
    C = pd.DataFrame([row(d) for d in ctl]); print(f"\n##### {name}: controls nodes {C.nodes.tolist()}, 2027 cohort per million {C.cohort_pm.round(0).tolist()} (mean {C.cohort_pm.mean():.0f}, sd {C.cohort_pm.std():.1f}); planted in controls: {C.n_planted.tolist()}")
    for n, f in levels:
        for r in ("r0", "r1", "r2"):
            x = row(base + f"f{n}/{r}/output/"); x.update(theta=name, level=n, rep=r, expect_fit=f); x["deficit_pm"] = x["cohort_pm"] - C.cohort_pm.mean(); x["deficit_sd"] = x["deficit_pm"] / C.cohort_pm.std(); out.append(x)
R = pd.DataFrame(out)
ok = (R.nodes == 1208027) & (R.n_planted == 1) & (R.fit == R.expect_fit) & (R.out == 50) & (R.alpha == 0.5) & (R.auth == 6) & (R.yr == 2027) & R.w.map(lambda w: w == (0.25, 0.25, 0.25, 0.25))
print(f"\nverification: {int(ok.sum())} of {len(R)} runs have 1,208,027 nodes, exactly one planted node, the intended fitness, out-degree 50, weights 0.25, alpha 0.5, six authors, year 2027")
pd.set_option("display.width", 220)
print(R[["theta", "level", "rep", "in_degree", "planted_pm", "cohort_pm", "deficit_pm", "deficit_sd"]].round(1).to_string(index=False))
g = R.groupby(["theta", "level"], sort=False).agg(in_degree_median=("in_degree", "median"), in_degree_mean=("in_degree", "mean"), in_degree_min=("in_degree", "min"), in_degree_max=("in_degree", "max"), planted_pm_mean=("planted_pm", "mean"), deficit_pm_mean=("deficit_pm", "mean")).round(1)
print("\nby theta and level:\n", g.to_string())
R.drop(columns=["w"]).round(3).to_csv(A + "planted_single_out50_2026-11-08/ladder_out50_summary.csv", index=False)
