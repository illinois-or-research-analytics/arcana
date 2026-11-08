"""Where do the citations of the planted nodes come from? Total in-degree of ordinary nodes by publication-year group, planted runs vs controls (3 each)."""
import numpy as np, pandas as pd
A = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/"
planted = [A + f"planted_equalized_2026-11-08/r{i}/output/" for i in range(3)]
control = [A + "weights_equal/baseline_cpm0.01/r0/output/"] + [A + f"control_regen_2026-11-08/r{i}/output/" for i in (1, 2)]
groups = [("seeds (to 2026)", -1, 2026), ("2027", 2027, 2027), ("2028-2029", 2028, 2029), ("2030-2034", 2030, 2034), ("2035-2044", 2035, 2044), ("2045-2066", 2045, 2066)]
def load(d):
    nl = pd.read_csv(d + "nodelist.csv", usecols=["node_id", "type", "year", "in_degree", "fit_peak_value", "planted_nodes_line_number"], low_memory=False)
    pl = nl.planted_nodes_line_number > 0
    ordn = nl[~pl]; tot = nl.in_degree.sum()
    row = {"edges": tot, "planted_total": int(nl[pl].in_degree.sum())}
    for g, lo, hi in groups:
        sel = ordn[(ordn.year >= lo) & (ordn.year <= hi)] if lo >= 0 else ordn[ordn.type == "seed"]
        row[g] = sel.in_degree.sum()
    c = ordn[(ordn.year == 2027) & (ordn.type == "agent")]
    row["2027 fit 11+"] = c[c.fit_peak_value >= 11].in_degree.sum(); row["2027 fit 2-10"] = c[(c.fit_peak_value >= 2) & (c.fit_peak_value <= 10)].in_degree.sum(); row["2027 fit 1"] = c[c.fit_peak_value == 1].in_degree.sum()
    row["2027 n11+"] = int((c.fit_peak_value >= 11).sum())
    return row
P = pd.DataFrame([load(d) for d in planted]); C = pd.DataFrame([load(d) for d in control])
print("planted nodes' total in-degree per run:", P.planted_total.tolist(), "| edges planted runs", P.edges.astype(int).tolist(), "| controls", C.edges.astype(int).tolist())
cols = [g for g, _, _ in groups] + ["2027 fit 11+", "2027 fit 2-10", "2027 fit 1"]
Pn = P[cols].div(P.edges, axis=0) * 1e6; Cn = C[cols].div(C.edges, axis=0) * 1e6   # citations per million, so runs of different size compare
out = pd.DataFrame({"planted mean": Pn.mean(), "control mean": Cn.mean(), "diff": Pn.mean() - Cn.mean(), "control sd": Cn.std(), "planted sd": Pn.std()})
out["diff / control sd"] = out["diff"] / out["control sd"]
pd.set_option("display.width", 200); print("\ntotal in-degree of ordinary nodes, as citations per million citations in the network:\n", out.round(1).to_string())
mean_edges = pd.concat([P.edges, C.edges]).mean()
print(f"\nplanted nodes captured {P.planted_total.mean():.0f} citations on average = {P.planted_total.mean()/mean_edges*1e6:.0f} per million; the summed deficit across the groups above is {out['diff'][[g for g,_,_ in groups]].sum():.0f} per million (conservation check: should be about {-P.planted_total.mean()/mean_edges*1e6:.0f}).")
print("per-run 2027 cohort total (excluding planted), planted:", P["2027"].astype(int).tolist(), " control:", C["2027"].astype(int).tolist())
print("fit-11+ nodes in the 2027 cohort, count per run:", P["2027 n11+"].tolist(), C["2027 n11+"].tolist())
