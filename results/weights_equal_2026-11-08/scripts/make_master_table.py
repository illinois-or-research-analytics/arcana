"""Master table: one row per condition and weight setting (12 rows), means over three replicates.
Reads data/weights_summaries.csv and data/conductance_bands_weights.csv; writes data/master_table.csv and data/master_table.md."""
import pandas as pd
s = pd.read_csv("data/weights_summaries.csv"); b = pd.read_csv("data/conductance_bands_weights.csv")
order = list(dict.fromkeys(s.group)); keys = ["group", "weights"]
m = s.groupby(keys, sort=False).agg(runs=("run", "count"), gini=("gini", "mean"), top10_share_pct=("top10_share_pct", "mean"), top1pct_share_pct=("top1pct_share_pct", "mean"),
    top01pct_median=("top01pct_median", "mean"), max_in_degree=("max_in_degree", "mean"), agents_gt50k=("agents_gt50k", "mean"), uncited_pct=("uncited_pct", "mean"),
    seed_share_new_pct=("seed_share_new_pct", "mean"), age_1_4_pct=("age_1_4_pct", "mean"), within_label_pct=("within_label_pct", "mean")).reset_index()
for band in ("2-9", "10-99", "100-999"):
    x = b[b.band == band].groupby(keys, sort=False).agg(**{f"cov_{band}_pct": ("node_coverage_pct", "mean"), f"cond_{band}": ("median_conductance", "mean")}).reset_index()
    m = m.merge(x, on=keys)
m["weights"] = pd.Categorical(m.weights, ["original", "equal 0.25"]); m["group"] = pd.Categorical(m.group, order)
m = m.sort_values(["group", "weights"]).reset_index(drop=True); m.round(3).to_csv("data/master_table.csv", index=False)
t = m.copy(); t.insert(0, "weights (pa/fit/na/ar)", t.weights.map({"original": "0.10/0.70/0.10/0.10", "equal 0.25": "0.25/0.25/0.25/0.25"}))
t = t.drop(columns=["weights", "runs"]).rename(columns={"group": "condition"})
fmt = {"gini": "{:.2f}", "top10_share_pct": "{:.2f}", "top1pct_share_pct": "{:.1f}", "top01pct_median": "{:,.0f}", "max_in_degree": "{:,.0f}", "agents_gt50k": "{:.1f}", "uncited_pct": "{:.1f}",
       "seed_share_new_pct": "{:.2f}", "age_1_4_pct": "{:.1f}", "within_label_pct": "{:.1f}"}
for c in t.columns:
    if c.startswith("cov_"): fmt[c] = "{:.1f}"
    if c.startswith("cond_"): fmt[c] = "{:.3f}"
for c, f in fmt.items(): t[c] = t[c].map(f.format)
blocks = [("Concentration and tails", ["gini", "top10_share_pct", "top1pct_share_pct", "top01pct_median", "max_in_degree", "agents_gt50k"]),
          ("Citing, ages, seeds, uncited", ["within_label_pct", "seed_share_new_pct", "age_1_4_pct", "uncited_pct"]),
          ("Leiden readout (resolution 0.1): node coverage % and median conductance by cluster-size band", [c for c in t.columns if c.startswith(("cov_", "cond_"))])]
names = {"gini": "Gini", "top10_share_pct": "top-10 share %", "top1pct_share_pct": "top-1% share %", "top01pct_median": "top-0.1% median in-degree", "max_in_degree": "max in-degree",
         "agents_gt50k": "agents > 50k", "within_label_pct": "within-label citing %", "seed_share_new_pct": "seed share of new citations %", "age_1_4_pct": "citations aged 1-4 %", "uncited_pct": "uncited %"}
for band in ("2-9", "10-99", "100-999"): names[f"cov_{band}_pct"] = f"coverage {band} %"; names[f"cond_{band}"] = f"conductance {band}"
out = []
for title, cols in blocks:
    cs = ["condition", "weights (pa/fit/na/ar)"] + cols
    out += [f"### {title}", "", "| " + " | ".join(names.get(c, c) for c in cs) + " |", "|" + "---|" * len(cs)]
    out += ["| " + " | ".join(str(r[c]) for c in cs) + " |" for _, r in t.iterrows()] + [""]
open("data/master_table.md", "w").write("\n".join(out)); print("\n".join(out))
