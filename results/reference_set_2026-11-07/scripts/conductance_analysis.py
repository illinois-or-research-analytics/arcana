"""Conductance of the Leiden-readout clusters by size band, for the nine baseline runs (cluster-aware citing on) and the nine control runs
(theta=1000000, off); labels 0.1, 0.01, 0.001; replicates r0, r1, r2. Reads meso/leiden_clusters.csv (cluster, size, cut, volume, conductance)
written by the multiscale pipeline. Bands are half-open, Python style: [2, 10), [10, 100), [100, 1000), [1000, inf).
Writes conductance_bands.csv (on) and conductance_bands_control.csv (off). Paths are cluster paths; edit them if the data move."""
import numpy as np, pandas as pd
D = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/chackoge/deltacon_testing/multiscale_results/"
bands = [("2-9", 2, 10), ("10-99", 10, 100), ("100-999", 100, 1000), ("1000+", 1000, 10**9)]
for sub, out in (("arcana_reference", "conductance_bands.csv"), ("arcana_control", "conductance_bands_control.csv")):
    rows = []
    for res in ("0.1", "0.01", "0.001"):
        for rep in ("r0", "r1", "r2"):
            lc = pd.read_csv(D + f"{sub}/cpm{res}/{rep}/meso/leiden_clusters.csv"); tot = lc["size"].sum()
            for name, lo, hi in bands:
                s = lc[(lc["size"] >= lo) & (lc["size"] < hi)]; c = s.conductance.dropna()
                rows.append(dict(labels=res, rep=rep, band=name, clusters=len(s), papers=int(s["size"].sum()), node_coverage=s["size"].sum() / tot,
                    median=c.median(), q1=c.quantile(.25), q3=c.quantile(.75), min=c.min() if len(c) else np.nan, n_lt05=int((c < 0.5).sum())))
    pd.DataFrame(rows).round(4).to_csv(D + f"{sub}/{out}", index=False)
