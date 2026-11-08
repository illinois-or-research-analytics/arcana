"""Summaries of the out-degree-ladder replicates r1 and r2, scored against the saved control statistics (the control networks were deleted).
Reads controls_stats.csv (cohort 2027 per million, three controls per theta); writes ladder_reps_per_run.csv and ladder_reps_per_node.csv."""
import pandas as pd
from multiprocessing import Pool
import planted_all_summaries as pas
A = pas.A; OUT = pas.OUT
jobs = [(f"out-degree ladder, fitness 10k, out-degree {d}", th, r, A + f"planted_outdeg_ladder_2026-11-08/t{'50' if th == 'theta 50' else '1m'}/d{d}/{r}/output/")
        for th in ("theta 50", "theta 1M") for d in (15, 30, 45, 60, 75, 90) for r in ("r1", "r2")]
if __name__ == "__main__":
    C = pd.read_csv(OUT + "controls_stats.csv"); st = C.groupby("theta").cohort2027_per_million.agg(["mean", "std"])
    with Pool(12) as p: res = p.map(pas.run, jobs, chunksize=1)
    runs = pd.DataFrame([r for r, _ in res]); nodes = pd.DataFrame([n for _, ns in res for n in ns])
    runs["cohort_deficit_per_million"] = runs.cohort2027_per_million - runs.theta.map(st["mean"]); runs["deficit_in_control_sd"] = runs.cohort_deficit_per_million / runs.theta.map(st["std"])
    runs.round(3).to_csv(OUT + "ladder_reps_per_run.csv", index=False); nodes.round(3).to_csv(OUT + "ladder_reps_per_node.csv", index=False)
    pd.set_option("display.width", 220); print(len(runs), "runs;", "unexpected node counts:", int((runs.nodes != 1208027).sum()), "| runs with exactly one planted node:", int((runs.n_planted == 1).sum()))
    nodes["od"] = nodes.experiment.str.extract(r"out-degree (\d+)$")[0].astype(int)
    ok = (nodes.fitness == 10000) & (nodes.out_degree == nodes.od) & (nodes.pa_weight == 0.25) & (nodes.fit_weight == 0.25) & (nodes.na_weight == 0.25) & (nodes.ar_weight == 0.25) & (nodes.alpha == 0.5) & (nodes.num_authors == 6) & (nodes.year == 2027)
    print("planted-node attribute check:", int(ok.sum()), "of", len(nodes))
    print(nodes[["theta", "od", "rep", "final_in_degree"]].sort_values(["theta", "od", "rep"]).to_string(index=False))
