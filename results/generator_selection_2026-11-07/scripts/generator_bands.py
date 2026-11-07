import numpy as np, pandas as pd, os
D = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/chackoge/deltacon_testing/multiscale_results/"
bands = [("2-9", 2, 10), ("10-99", 10, 100), ("100-999", 100, 1000), ("1000+", 1000, 10**9)]
src = [("uniform (control)", "arcana_control/cpm0.01"), ("non-random 0.5, and", "arcana_nrg/and_t1m"), ("non-random 0.5, or", "arcana_nrg/or_t1m")]
rows = []
for name, sub in src:
    for rep in ("r0", "r1", "r2"):
        f = D + f"{sub}/{rep}/meso/leiden_clusters.csv"
        assert os.path.exists(f), f
        lc = pd.read_csv(f); tot = lc["size"].sum()
        for b, lo, hi in bands:
            s = lc[(lc["size"] >= lo) & (lc["size"] < hi)]; c = s.conductance.dropna()
            rows.append(dict(generators=name, rep=rep, band=b, clusters=len(s), paper_share=s["size"].sum() / tot * 100, median=c.median(), n_lt05=int((c < 0.5).sum())))
df = pd.DataFrame(rows); df.round(4).to_csv(D + "arcana_nrg/conductance_bands_nrg.csv", index=False)
g = df.groupby(["band", "generators"], sort=False).agg(clusters=("clusters", "mean"), share=("paper_share", "mean"), median=("median", "mean"), sd=("median", "std"), lt05=("n_lt05", "sum")).round(3)
print(g.to_string())
print("\nlargest cluster per run:")
for name, sub in src:
    print(name.ljust(22), [int(pd.read_csv(D + f"{sub}/{r}/meso/leiden_clusters.csv")["size"].max()) for r in ("r0", "r1", "r2")])
