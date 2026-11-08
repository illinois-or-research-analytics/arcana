"""OFAT table: centre run, the fit-weight arms and the theta and generator arms, with settings spelled out.
Reads data/weights_summaries.csv (equal-weight runs) and data/ofat_run_summaries.csv (OFAT runs); writes data/ofat_table.csv and data/ofat_table.md."""
import pandas as pd
n = pd.read_csv("data/ofat_run_summaries.csv"); s = pd.read_csv("data/weights_summaries.csv")
cols = ["gini", "top10_share_pct", "top1pct_share_pct", "top01pct_median", "uncited_pct", "within_label_pct", "seed_share_new_pct"]
def agg(df): return df[cols].mean(), len(df), df.top1pct_share_pct.std()
G = lambda g: s[s.group == g]
rows = [("fit 0.10", "0.30 / 0.10 / 0.30 / 0.30", "uniform", "50", *agg(n[n.group == "fit_lo"])),
        ("centre", "0.25 / 0.25 / 0.25 / 0.25", "uniform", "50", *agg(G("citing on, labels 0.01"))),
        ("fit 0.90", "0.033 / 0.90 / 0.033 / 0.033", "uniform", "50", *agg(n[n.group == "fit_hi"])),
        ("fit 0.10", "0.30 / 0.10 / 0.30 / 0.30", "uniform", "1,000,000", *agg(n[n.group == "fit_lo_theta1m"])),
        ("fit 0.25", "0.25 / 0.25 / 0.25 / 0.25", "uniform", "1,000,000", *agg(G("citing off, uniform generators"))),
        ("fit 0.90", "0.033 / 0.90 / 0.033 / 0.033", "uniform", "1,000,000", *agg(n[n.group == "fit_hi_theta1m"])),
        ("generators", "0.25 / 0.25 / 0.25 / 0.25", "non-random and", "50", *agg(n[n.group == "nrg_and_theta50"])),
        ("generators", "0.25 / 0.25 / 0.25 / 0.25", "non-random and", "1,000,000", *agg(G("generators non-random, and")))]
t = pd.DataFrame([dict(arm=a, weights_pa_fit_na_ar=w, generators=g, theta=th, reps=r, top1pct_share_sd=(round(sd, 2) if r > 1 else None), **{k: round(m[k], 3) for k in cols}) for a, w, g, th, m, r, sd in rows])
t.to_csv("data/ofat_table.csv", index=False)
fmt = {"gini": "{:.2f}", "top10_share_pct": "{:.2f}", "top1pct_share_pct": "{:.1f}", "top01pct_median": "{:,.0f}", "uncited_pct": "{:.1f}", "within_label_pct": "{:.1f}", "seed_share_new_pct": "{:.2f}"}
hdr = ["arm", "weights (pa / fit / na / ar)", "generators", "theta", "reps", "Gini", "top-10 %", "top-1% share %", "top-0.1% median", "uncited %", "within-label %", "seed share %"]
out = ["| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)]
for _, r in t.iterrows():
    out.append("| " + " | ".join([r.arm, r.weights_pa_fit_na_ar, r.generators, r.theta, str(r.reps)] + [fmt[k].format(r[k]) for k in cols]) + " |")
open("data/ofat_table.md", "w").write("\n".join(out) + "\n"); print("\n".join(out))
