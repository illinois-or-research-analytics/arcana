"""Single planted node at five fitness levels: final in-degree and the 2027-cohort deficit against three controls."""
import numpy as np, pandas as pd
A = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/"
control = [A + "weights_equal/baseline_cpm0.01/r0/output/"] + [A + f"control_regen_2026-11-08/r{i}/output/" for i in (1, 2)]
levels = [("10k", 10_000), ("100k", 100_000), ("1M", 1_000_000), ("10M", 10_000_000), ("100M", 100_000_000)]
def row(d):
    nl = pd.read_csv(d + "nodelist.csv", usecols=["node_id", "type", "year", "in_degree", "planted_nodes_line_number"], low_memory=False)
    pl = nl.planted_nodes_line_number > 0; o = nl[~pl]; tot = nl.in_degree.sum()
    c = o[(o.year == 2027) & (o.type == "agent")]
    return dict(edges=tot, planted=int(nl[pl].in_degree.sum()), cohort2027=c.in_degree.sum(), other=o[(o.year != 2027)].in_degree.sum())
C = pd.DataFrame([row(d) for d in control]); cm = (C.cohort2027 / C.edges * 1e6)
print(f"controls: 2027 cohort per million citations: {cm.round(0).tolist()} mean {cm.mean():.0f} sd {cm.std():.1f}")
rows = []
for n, f in levels:
    for r in ("r0", "r1", "r2"):
        x = row(A + f"planted_single_2026-11-08/f{n}/{r}/output/")
        x.update(level=n, rep=r, cohort_pm=x["cohort2027"] / x["edges"] * 1e6, planted_pm=x["planted"] / x["edges"] * 1e6); rows.append(x)
R = pd.DataFrame(rows); R["cohort_deficit_pm"] = R.cohort_pm - cm.mean(); R["deficit_in_control_sd"] = R.cohort_deficit_pm / cm.std()
pd.set_option("display.width", 200)
print(R[["level", "rep", "planted", "planted_pm", "cohort_pm", "cohort_deficit_pm", "deficit_in_control_sd"]].round(1).to_string(index=False))
g = R.groupby("level", sort=False).agg(planted_mean=("planted", "mean"), planted_median=("planted", "median"), deficit_mean=("cohort_deficit_pm", "mean"), planted_pm_mean=("planted_pm", "mean")).round(1)
print("\nby level:\n", g.to_string())
R.round(3).drop(columns=["other"]).to_csv(A + "planted_single_2026-11-08/single_node_summary.csv", index=False)
