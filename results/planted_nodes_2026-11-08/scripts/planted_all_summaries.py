"""Per-node and per-run summaries of every planted-node experiment, and the control statistics, written before the networks are deleted.
Outputs (in the arcana run area): planted_nodes_per_node.csv, planted_runs_per_run.csv, controls_stats.csv."""
import numpy as np, pandas as pd
from multiprocessing import Pool
A = "/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/"
OUT = A + "planted_2026-11-08/"
R3 = ("r0", "r1", "r2")
ctl50 = [A + "weights_equal/baseline_cpm0.01/r0/output/"] + [A + f"control_regen_2026-11-08/r{i}/output/" for i in (1, 2)]
ctl1m = [A + f"control_t1m_regen_2026-11-08/r{i}/output/" for i in range(3)]
jobs = [("first run (3 nodes, random phenotype, out-degree random)", "theta 50", "r0", A + "planted_2026-11-08/centre_r0/output/")]
jobs += [("trio (3 nodes, equal phenotype, out-degree 15)", "theta 50", r, A + f"planted_equalized_2026-11-08/{r}/output/") for r in R3]
jobs += [(f"single node, out-degree 15, fitness {n}", "theta 50", r, A + f"planted_single_2026-11-08/f{n}/{r}/output/") for n in ("10k", "100k", "1M", "10M", "100M") for r in R3]
jobs += [(f"single node, out-degree 50, fitness {n}", "theta 50", r, A + f"planted_single_out50_2026-11-08/f{n}/{r}/output/") for n in ("10k", "100k", "1M", "10M") for r in R3]
jobs += [(f"single node, out-degree 50, fitness {n}", "theta 1M", r, A + f"planted_single_out50_t1m_2026-11-08/f{n}/{r}/output/") for n in ("10k", "100k", "1M", "10M") for r in R3]
jobs += [(f"out-degree ladder, fitness 10k, out-degree {d}", th, "r0", A + f"planted_outdeg_ladder_2026-11-08/t{ 'x' if False else ('50' if th == 'theta 50' else '1m')}/d{d}/r0/output/") for th in ("theta 50", "theta 1M") for d in (15, 30, 45, 60, 75, 90)]
cols = ["node_id", "type", "year", "in_degree", "out_degree", "fit_peak_value", "pa_weight", "fit_weight", "num_authors_weight", "author_reputation_weight", "alpha", "num_authors", "planted_nodes_line_number"]
def gini(x):
    x = np.sort(x.astype(np.float64)); n = len(x); c = np.cumsum(x); return (n + 1 - 2 * (c / c[-1]).sum()) / n
def run(job):
    exp, th, rep, d = job
    nl = pd.read_csv(d + "nodelist.csv", usecols=cols, low_memory=False); pl = nl.planted_nodes_line_number > 0
    tot = nl.in_degree.sum(); o = nl[~pl]; c = o[(o.year == 2027) & (o.type == "agent")]; x = nl.in_degree.values
    per_run = dict(experiment=exp, theta=th, rep=rep, nodes=len(nl), edges=int(tot), n_planted=int(pl.sum()), planted_in_degree_total=int(nl[pl].in_degree.sum()),
                   cohort2027_per_million=c.in_degree.sum() / tot * 1e6, gini=gini(x), top1pct_share=np.sort(x)[::-1][:int(len(x) * .01)].sum() / tot * 100, uncited_pct=(x == 0).mean() * 100)
    nodes = [dict(experiment=exp, theta=th, rep=rep, node_id=int(r.node_id), year=int(r.year), fitness=int(r.fit_peak_value), out_degree=int(r.out_degree), pa_weight=round(r.pa_weight, 3), fit_weight=round(r.fit_weight, 3),
                  na_weight=round(r.num_authors_weight, 3), ar_weight=round(r.author_reputation_weight, 3), alpha=round(r.alpha, 3), num_authors=int(r.num_authors), final_in_degree=int(r.in_degree),
                  per_million=r.in_degree / tot * 1e6) for r in nl[pl].itertuples()]
    return per_run, nodes
def ctl(job):
    th, rep, d = job; r, _ = run(("control (no planted nodes)", th, rep, d)); return r
if __name__ == "__main__":
    with Pool(12) as p:
        res = p.map(run, jobs, chunksize=1)
        cs = p.map(ctl, [("theta 50", f"c{i}", d) for i, d in enumerate(ctl50)] + [("theta 1M", f"c{i}", d) for i, d in enumerate(ctl1m)])
    runs = pd.DataFrame([r for r, _ in res]); nodes = pd.DataFrame([n for _, ns in res for n in ns]); C = pd.DataFrame(cs)
    for th, g in C.groupby("theta"):
        m, s = g.cohort2027_per_million.mean(), g.cohort2027_per_million.std(); sel = runs.theta == th
        runs.loc[sel, "cohort_deficit_per_million"] = runs.loc[sel, "cohort2027_per_million"] - m; runs.loc[sel, "deficit_in_control_sd"] = (runs.loc[sel, "cohort2027_per_million"] - m) / s
        print(f"{th}: control cohort2027 per million: {g.cohort2027_per_million.round(1).tolist()} mean {m:.1f} sd {s:.1f}")
    runs.round(3).to_csv(OUT + "planted_runs_per_run.csv", index=False); nodes.round(3).to_csv(OUT + "planted_nodes_per_node.csv", index=False); C.round(3).to_csv(OUT + "controls_stats.csv", index=False)
    pd.set_option("display.width", 220); print(len(runs), "runs,", len(nodes), "planted nodes,", len(C), "controls"); print("incomplete or unexpected node counts:", int((runs.nodes != 1208027).sum()))
    print(nodes[nodes.experiment.str.startswith("out-degree ladder")][["theta", "out_degree", "fitness", "final_in_degree", "per_million"]].round(1).to_string(index=False))
