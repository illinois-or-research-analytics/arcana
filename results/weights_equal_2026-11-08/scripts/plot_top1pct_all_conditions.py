"""Top-1% citation share for every condition tested (equal-weights set, fit OFAT, pa OFAT). Run from the results folder."""
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
w = pd.read_csv("data/weights_summaries.csv"); f = pd.read_csv("data/ofat_run_summaries.csv"); p = pd.read_csv("data/ofat_pa_run_summaries.csv")
v = lambda d, key: d[d.group == key].top1pct_share_pct.tolist()
# row label -> (cluster-aware citing on [theta 50], off [theta 1,000,000])
rows = [
 ("centre: all weights 0.25",               v(w,"citing on, labels 0.01"),  v(w,"citing off, uniform generators")),
 ("fit weight 0.10",                        v(f,"fit_lo"),                  v(f,"fit_lo_theta1m")),
 ("fit weight 0.90",                        v(f,"fit_hi"),                  v(f,"fit_hi_theta1m")),
 ("pa weight 0.10",                         v(p,"pa_lo"),                   v(p,"pa_lo_theta1m")),
 ("pa weight 0.90",                         v(p,"pa_hi"),                   v(p,"pa_hi_theta1m")),
 ("generators non-random, 'and'",           v(f,"nrg_and_theta50"),         v(w,"generators non-random, and")),
 ("generators non-random, 'or'",            [],                             v(w,"generators non-random, or")),
 ("labels at resolution 0.1 (coarser:\nfewer, larger clusters... see note)", v(w,"citing on, labels 0.1"), []),
 ("labels at resolution 0.001",             v(w,"citing on, labels 0.001"), []),
]
rows[7] = ("labels at resolution 0.1", rows[7][1], [])
BG, INK, MUT, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e7e6e2"
C_ON, C_OFF = "#2a78d6", "#eb6834"
fig, ax = plt.subplots(figsize=(9, 5.6), facecolor=BG); ax.set_facecolor(BG)
n = len(rows)
for i, (name, on, off) in enumerate(rows):
    y = n - 1 - i
    for vals, col, mk, dy in ((on, C_ON, "o", 0.16), (off, C_OFF, "D", -0.16)):
        if not vals: continue
        m = sum(vals) / len(vals); single = len(vals) == 1
        ax.plot([min(vals), max(vals)], [y + dy] * 2, color=col, lw=2, solid_capstyle="round", zorder=2)
        ax.scatter(vals, [y + dy] * len(vals), s=46, marker=mk, facecolor=BG if single else col, edgecolor=col, linewidth=1.5, zorder=3)
        ax.annotate(f"{m:.1f}", (max(vals), y + dy), xytext=(7, 0), textcoords="offset points", va="center", fontsize=9, color=INK)
ref_on, ref_off = sum(rows[0][1]) / 3, sum(rows[0][2]) / 3
ax.axvline(ref_on, color=C_ON, lw=0.8, ls=(0, (3, 3)), alpha=.5, zorder=1); ax.axvline(ref_off, color=C_OFF, lw=0.8, ls=(0, (3, 3)), alpha=.5, zorder=1)
ax.set_yticks(range(n)); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=10, color=INK)
ax.set_ylim(-0.7, n + 1.2); ax.set_xlim(30, 60)
ax.set_xlabel("share of all citations received by the top 1% of nodes (%)", fontsize=10, color=MUT)
ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID); ax.tick_params(axis="both", length=0, colors=MUT)
ax.tick_params(axis="y", colors=INK)
ax.scatter([], [], marker="o", color=C_ON, label="cluster-aware citing on (theta 50)")
ax.scatter([], [], marker="D", color=C_OFF, label="cluster-aware citing off (theta 1,000,000)")
ax.scatter([], [], marker="o", facecolor=BG, edgecolor=MUT, label="hollow = one run (others: three replicates, line spans them)")
ax.legend(loc="upper left", bbox_to_anchor=(0.0, 1.0), frameon=False, fontsize=9, labelcolor=INK)
ax.set_title("Top-1% share of citations, every condition tested", loc="left", fontsize=12, color=INK, pad=12)
fig.tight_layout(); fig.savefig("figures/top1pct_share_all_conditions.png", dpi=200, facecolor=BG)
print("ok")
