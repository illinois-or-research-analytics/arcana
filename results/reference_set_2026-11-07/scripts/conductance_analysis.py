import numpy as np, pandas as pd
A = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/"
R = A + "chackoge/deltacon_testing/multiscale_results/arcana_reference/"
bands = [("2-9", 2, 10), ("10-99", 10, 100), ("100-999", 100, 1000), ("1000+", 1000, 10**9)]
band_rows, label_rows = [], []
for res in ("0.1", "0.01", "0.001"):
    for rep in ("r0", "r1", "r2"):
        run = f"cpm{res}/{rep}"
        lc = pd.read_csv(R + run + "/meso/leiden_clusters.csv")
        tot = lc["size"].sum()
        for name, lo, hi in bands:
            s = lc[(lc["size"] >= lo) & (lc["size"] < hi)]
            c = s.conductance.dropna()
            band_rows.append(dict(labels=res, rep=rep, band=name, clusters=len(s), papers=int(s["size"].sum()), paper_share=s["size"].sum() / tot,
                median=c.median(), q1=c.quantile(.25), q3=c.quantile(.75), min=c.min() if len(c) else np.nan, n_lt05=int((c < 0.5).sum())))
        # conductance of the label clusters themselves (seeds + the agents that joined them) in the output network
        d = A + f"arcana/baseline_cpm{res}/{rep}/output/"
        nl = pd.read_csv(d + "nodelist.csv", usecols=["node_id", "type", "cluster_id"])
        ed = pd.read_csv(d + "edgelist.csv", dtype=np.int64).iloc[:, :2]
        E = len(ed); idx = pd.Index(nl.node_id)
        u, v = idx.get_indexer(ed.source), idx.get_indexer(ed.target)
        cid = nl.cluster_id.values; k = cid.max() + 1
        cu, cv = cid[u], cid[v]; cross = cu != cv
        cut = np.bincount(cu[cross][cu[cross] >= 0], minlength=k) + np.bincount(cv[cross][cv[cross] >= 0], minlength=k)
        deg = np.bincount(u, minlength=len(nl)) + np.bincount(v, minlength=len(nl))
        ok = cid >= 0
        vol = np.bincount(cid[ok], weights=deg[ok], minlength=k)
        size = np.bincount(cid[ok], minlength=k)
        seeds = np.bincount(cid[ok & (nl.type.values == "seed")], minlength=k)
        denom = np.minimum(vol, 2 * E - vol); cond = np.where(denom > 0, cut / np.maximum(denom, 1), np.nan)
        for c in np.where(seeds >= 50)[0]:
            label_rows.append(dict(labels=res, rep=rep, cluster=int(c), seed_papers=int(seeds[c]), size=int(size[c]), cut=int(cut[c]), volume=float(vol[c]), conductance=cond[c]))
        print("done", run, flush=True)
pd.DataFrame(band_rows).round(4).to_csv(R + "conductance_bands.csv", index=False)
pd.DataFrame(label_rows).round(4).to_csv(R + "label_cluster_conductance.csv", index=False)
print("wrote", R)
