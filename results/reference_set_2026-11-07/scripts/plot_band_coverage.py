import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
d = pd.read_csv("data/conductance_bands_control.csv")
bands = ["2-9", "10-99", "100-999"]
cols = ["#bdbdbd", "#3182bd", "#e6550d"]
conds = [("off (control)", None)] + [("cluster-aware citing on", l) for l in (0.001, 0.01, 0.1)]
rows = []
for c, l in conds:
    s = d[d.citing == c] if l is None else d[(d.citing == c) & (d.labels == l)]
    # citing off: the label set plays no part, so all 9 control runs are pooled
    m = s.groupby("band").node_coverage.mean() * 100
    rows.append(m.reindex(bands).fillna(0))
names = ["off", "on, labels\nCPM 0.001", "on, labels\nCPM 0.01", "on, labels\nCPM 0.1"]
fig, ax = plt.subplots(figsize=(7, 4.8))
bottom = [0] * 4
for b, col in zip(bands, cols):
    v = [r[b] for r in rows]
    ax.bar(names, v, bottom=bottom, color=col, label=f"{b} nodes", width=0.6)
    for i, (x, y) in enumerate(zip(v, bottom)):
        if x > 4: ax.text(i, y + x / 2, f"{x:.0f}%", ha="center", va="center", color="white" if col != cols[0] else "black")
    bottom = [a + c for a, c in zip(bottom, v)]
ax.set_ylabel("node coverage (% of nodes)")
ax.set_title("Cluster sizes in the output network (Leiden CPM 0.1)\nmean of 3 replicates", fontsize=10)
ax.legend(title="cluster size", frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.01, 0.01, "off = ordinary citing (theta = 1,000,000): new nodes cite the generator's direct neighbors only.\n"
         "on = cluster-aware citing (theta = 50): when the generator's cluster has >= 50 members, new nodes cite within that cluster;\n"
         "the label set (Leiden CPM 0.001, 0.01 or 0.1 on the seed nodes) defines the clusters.", fontsize=7, va="bottom", ha="left")
plt.tight_layout(rect=(0, 0.14, 1, 1))
plt.savefig("figures/band_coverage.png", dpi=200)
print([r.round(1).to_dict() for r in rows])
