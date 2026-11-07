"""Leiden CPM labels for the mf_seed_v3 seed network.
Usage: make_seed_labels_v3.py OUTDIR RESOLUTION [RESOLUTION ...]
Same procedure as deltacon_testing/cantatas_c1/make_seed_labels.py: undirected graph built from seed_edgelist_v3.csv,
leidenalg CPMVertexPartition, seed=1. Writes OUTDIR/seed_comm_cpm<RES>_v3.csv with columns node_id,cluster_id and prints
cluster statistics. Checks that the labelled nodes are exactly the nodes of seed_nodelist_v3.csv."""
import sys, os, numpy as np, pandas as pd, igraph as ig, leidenalg
S = "/projects/illinois/eng/cs/chackoge/mf_seed_v3"
out = sys.argv[1]; resolutions = sys.argv[2:]
el = pd.read_csv(f"{S}/seed_edgelist_v3.csv")
nodes = set(pd.read_csv(f"{S}/seed_nodelist_v3.csv").node_id)
g = ig.Graph.DataFrame(el, directed=False, use_vids=False)
assert set(g.vs["name"]) == nodes, "graph nodes differ from the v3 nodelist"
print(f"leidenalg {leidenalg.version}, igraph {ig.__version__}; graph: {g.vcount()} nodes, {g.ecount()} edges")
for r in resolutions:
    p = leidenalg.find_partition(g, leidenalg.CPMVertexPartition, resolution_parameter=float(r), seed=1)
    d = pd.DataFrame({"node_id": g.vs["name"], "cluster_id": p.membership}).sort_values("node_id")
    f = os.path.join(out, f"seed_comm_cpm{r}_v3.csv"); d.to_csv(f, index=False)
    s = d.groupby("cluster_id").size()
    print(f"res {r}: {len(d):,} papers, {len(s):,} clusters; singletons {(s==1).sum()}; >=10: {(s>=10).sum()}; >=50: {(s>=50).sum()}; "
          f"papers in clusters >=50: {s[s>=50].sum():,}; largest {s.max():,}; median {s.median():.0f}  -> {f}")
