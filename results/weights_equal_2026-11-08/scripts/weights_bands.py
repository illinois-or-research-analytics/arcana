"""Leiden (resolution 0.1) cluster-size bands and conductance for the 18 equal-weights runs. node_coverage is a percentage."""
import numpy as np, pandas as pd, os
D = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/chackoge/deltacon_testing/multiscale_results/"
bands = [("2-9", 2, 10), ("10-99", 10, 100), ("100-999", 100, 1000), ("1000+", 1000, 10**9)]
groups = [("citing on, labels 0.1", "arcana_reference/cpm0.1", "baseline_cpm0.1"), ("citing on, labels 0.01", "arcana_reference/cpm0.01", "baseline_cpm0.01"),
          ("citing on, labels 0.001", "arcana_reference/cpm0.001", "baseline_cpm0.001"), ("citing off, uniform generators", "arcana_control/cpm0.01", "control_cpm0.01"),
          ("generators non-random, and", "arcana_nrg/and_t1m", "nrg_and_t1m_cpm0.01"), ("generators non-random, or", "arcana_nrg/or_t1m", "nrg_or_t1m_cpm0.01")]
rows = []
for g, orig, eq in groups:
    for w, sub in (("equal 0.25", "arcana_weights_equal/" + eq),):
        for rep in ("r0", "r1", "r2"):
            f = D + f"{sub}/{rep}/meso/leiden_clusters.csv"; assert os.path.exists(f), f
            lc = pd.read_csv(f); tot = lc["size"].sum()
            for b, lo, hi in bands:
                s = lc[(lc["size"] >= lo) & (lc["size"] < hi)]; c = s.conductance.dropna()
                rows.append(dict(group=g, weights=w, rep=rep, band=b, clusters=len(s), nodes=int(s["size"].sum()), node_coverage_pct=s["size"].sum() / tot * 100,
                                 median_conductance=c.median(), n_lt05=int((c < 0.5).sum()), largest=int(lc["size"].max())))
df = pd.DataFrame(rows); df.round(4).to_csv(D + "arcana_weights_equal/conductance_bands_weights.csv", index=False)
a = df.groupby(["group", "band", "weights"], sort=False).agg(clusters=("clusters", "mean"), coverage=("node_coverage_pct", "mean"), median=("median_conductance", "mean"), sd=("median_conductance", "std"), lt05=("n_lt05", "sum")).round(3)
print(a.to_string())
print("\nlargest cluster per run:")
print(df.drop_duplicates(["group", "weights", "rep"]).groupby(["group", "weights"], sort=False).largest.apply(list).to_string())
