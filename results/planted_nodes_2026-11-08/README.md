# ARCANA, planted supernodes (2026-11-08)

Do a few extremely fit nodes take citations away from ordinary nodes, and does it depend on how fit they are, on how many references they make, and on whether cluster-aware citing is on?
The experiments plant one or three nodes with fitness 10,000 to 100,000,000 in the first simulated year (2027) of the equal-weights centre run and compare with the same run without planted nodes.

**This is a trend-based comparison with an earlier model, not a replication.** The earlier results came from a different model in which recency was a scoring weight and out-degrees ran from 10 to 249.
In ARCANA recency is not a weight (the age of a citation is drawn from an empirical distribution before scoring), the four weights are preferential attachment, fitness, number of authors and author reputation,
and out-degrees come from an empirical bag. Compare directions, not magnitudes.

## Terms
- **Planted node, supernode:** a node whose attributes are overridden through the `planted_nodes` file. In the file, `year` is the simulated year counted from 0 (0 is 2027, the first cohort of 2,669 agents); a random agent of that year is overwritten. Unspecified attributes keep their random draws.
- **Ordinary fitness:** fitness is drawn from a power law on [1, 1000] (density about x^-3, `fitness_alpha = -3`), truncated to integers: 75% of agents have fitness 1, the 99th percentile is 10, the mean is 1.64 and the maximum in a run is a few hundred to about 1,000. Planted values are therefore 10^4 to 10^8 times a typical agent.
- **Cohort deficit:** the total in-degree of the ordinary (non-planted) agents published in 2027, as citations per million citations in the network, in a planted run minus the mean of three runs without planted nodes. Out-degrees are fixed per node, so the citations a planted node gains must come from someone: the deficit says from whom.
- **Control:** three runs without planted nodes at the same `theta`, equal weights, uniform generators, labels 0.01. For `theta` 50 these are the centre run and two regenerated runs; for `theta` 1,000,000 three regenerated runs. Regenerated runs are statistically equivalent to the original, not identical (the random seed is not logged).
- `theta` 50 means cluster-aware citing is on; `theta` 1,000,000 means it is off (ordinary citing). See the [reference set](../reference_set_2026-11-07/README.md).

## Experiments
All runs: centre configuration of the [equal-weights set](../weights_equal_2026-11-08/README.md) (equal weights 0.25, uniform generators, labels 0.01), one config line changed (`planted_nodes=./planted_nodes.csv`), plus `theta` where stated. Each run took about 1 to 2 minutes; all 55 runs have the full 1,208,027 nodes, and every planted node was checked in the nodelist (fitness, out-degree, weights, alpha, number of authors, year).

| experiment | planted nodes | phenotype of the planted node(s) | `theta` | runs |
|---|---|---|---|---|
| first run | 10k, 100k and 1M fitness in one run | random (weights, out-degree, alpha, authors) | 50 | 1 |
| trio | 10k, 100k and 1M in one run | equal weights, out-degree 15, alpha 0.5, six authors | 50 | 3 |
| single node, out-degree 15 | one node at 10k, 100k, 1M, 10M or 100M | as the trio | 50 | 15 |
| single node, out-degree 50 | one node at 10k, 100k, 1M or 10M | as the trio but out-degree 50 | 50 and 1,000,000 | 12 + 12 |
| out-degree ladder | one node at 10k with out-degree 15, 30, 45, 60, 75 or 90 | equal weights, alpha 0.5, six authors | 50 and 1,000,000 | 6 + 6 (one replicate) |

## Results

### Final in-degree of the planted nodes
First run (random phenotype): 481 (10k), 2,566 (100k) and 971 (1M).
Trio (equal phenotype, out-degree 15), replicates r0 / r1 / r2:

| fitness | in-degree |
|---|---|
| 10k | 843 / 697 / 585 |
| 100k | 430 / 17,211 / 2,868 |
| 1M | 10,896 / 9,509 / 19,425 |

Single node, out-degree 15, `theta` 50 (r0 / r1 / r2, median):

| fitness | in-degree | median |
|---|---|---|
| 10k | 2,015 / 20,185 / 2,413 | 2,413 |
| 100k | 2,183 / 1,701 / 1,173 | 1,701 |
| 1M | 3,704 / 3,526 / 1,915 | 3,526 |
| 10M | 1,646 / 19,759 / 2,866 | 2,866 |
| 100M | 1,689 / 448 / 7,158 | 1,689 |

Single node, out-degree 50, `theta` 50:

| fitness | in-degree | median |
|---|---|---|
| 10k | 8,592 / 3,377 / 7,743 | 7,743 |
| 100k | 20,894 / 20,172 / 7,692 | 20,172 |
| 1M | 20,928 / 7,731 / 4,991 | 7,731 |
| 10M | 17,952 / 2,481 / 20,742 | 17,952 |

Single node, out-degree 50, `theta` 1,000,000:

| fitness | in-degree | median |
|---|---|---|
| 10k | 8,992 / 2,777 / 26,247 | 8,992 |
| 100k | 8,468 / 9,428 / 14,047 | 9,428 |
| 1M | 2,731 / 14,335 / 8,938 | 8,938 |
| 10M | 27,212 / 26,751 / 29,015 | 27,212 |

Out-degree ladder, one replicate, fitness 10k:

| out-degree | `theta` 50 | `theta` 1,000,000 |
|---|---|---|
| 15 | 6,249 | 8,412 |
| 30 | 19,106 | 2,542 |
| 45 | 1,407 | 15,833 |
| 60 | 20,722 | 29,372 |
| 75 | 6,297 | 24,581 |
| 90 | 20,647 | 8,989 |

### Where the citations come from
Controls, 2027 cohort in citations per million:

| `theta` | controls | mean | sd |
|---|---|---|---|
| theta 1M | 8,321, 8,291, 8,272 | 8,295 | 24.4 |
| theta 50 | 7,365, 7,369, 7,330 | 7,354 | 21.5 |

The deficit in the 2027 cohort matches what the planted nodes gained, in every experiment (citations per million; sds are of the controls):

| experiment | `theta` | runs | planted nodes gained | cohort lost | deficit in control sds |
|---|---|---|---|---|---|
| first run (3 nodes, random phenotype) | theta 50 | 1 | 177 | 157 | 7 to 7 |
| trio (3 nodes, equal phenotype, out-degree 15) | theta 50 | 3 | 918 | 932 | 27 to 56 |
| single node, out-degree 15 | theta 50 | 15 | 213 | 216 | -2 to 42 |
| single node, out-degree 50 | theta 50 | 12 | 527 | 538 | 6 to 44 |
| single node, out-degree 50 | theta 1M | 12 | 658 | 643 | 4 to 52 |
| out-degree ladder (fitness 10k) | theta 50 | 6 | 547 | 534 | 2 to 41 |
| out-degree ladder (fitness 10k) | theta 1M | 6 | 659 | 662 | 5 to 53 |

For the trio, the other publication-year groups net to zero within noise (seeds −72, 2028–2029 −5, 2030–2034 +39, 2035–2044 +150, 2045–2066 −98 per million; control sd 21.5 or less) and the loss in the 2027 cohort is concentrated, in relative terms,
in the highest-fitness ordinary agents (fitness 11 or more: 1,239 to 682 per million, −45%; fitness 1: 4,362 to 4,034, −7.5%; fitness 2 to 10: 1,753 to 1,706).

## Reading the results
- **Quenching reproduces in direction, and it is local.** Planted supernodes take citations from ordinary, sub-1,000-fitness nodes, essentially one for one, and the loss falls on the nodes of their own publication year. This holds with cluster-aware citing on and off, for one or three planted nodes.
- **More fitness does not buy more citations above about 10k.** In the out-degree 15 and 50 ladders the median in-degree does not rise with fitness from 10k to 100M. One exception: at `theta` 1,000,000 and out-degree 50, the three 10M nodes all reached 26,700 to 29,000, above the 10k to 1M groups (medians 8,900 to 9,400). This is consistent with saturation of the fitness share (a node of fitness f in a pool of N candidates of mean fitness 1.64 holds f/(f + 1.64 N) of the fitness mass), but I have not traced which pool the scoring normalises over.
- **Single-node outcomes are heavy-tailed and mostly luck.** The same design gives 2,777 to 26,247 (10k, `theta` 1M, out-degree 50). At `theta` 50 several nodes end between 18,000 and 21,000 (a ceiling, unexplained), and others between 1,000 and 8,000.
- **Out-degree:** with out-degree 50 the median supernode gets more than with out-degree 15 (7,700 to 20,200 against 1,700 to 3,500 at `theta` 50), but the one-replicate ladder from 15 to 90 shows no monotone trend (`theta` 50: 6,249 / 19,106 / 1,407 / 20,722 / 6,297 / 20,647). The out-degree effect is therefore suggested, not established; it needs replicates.
- **The trio is not the sum of single nodes.** At out-degree 15, the 10k node got 585 to 843 in the trio and 2,015 to 20,185 alone; the 1M node got 9,509 to 19,425 in the trio and 1,915 to 3,704 alone. Three replicates each; I do not have an explanation for the second.
- Limits: three replicates or fewer per cell; regenerated controls; one seed set, one set of weights; one planting year (2027); the planted node's generator and cluster are random.

## Retention of the data
**On 2026-11-08 the raw networks (`nodelist.csv` and `edgelist.csv`) of every run were deleted from the cluster, except the centre run `weights_equal/baseline_cpm0.01/r0`.** The record is the per-run, per-node and control tables in `data/`, the configurations and planted files in `config/`, and the scripts. Runs take about two minutes and can be regenerated, statistically equivalent to the originals but not identical. The 24 unrun replicate folders of the out-degree ladder remain on the cluster as configs only.

## Contents

| path | what it is |
|---|---|
| `data/planted_runs_per_run.csv` | one row per run: nodes, edges, planted in-degree total, 2027 cohort per million, deficit against the controls, Gini, top-1% share, uncited share |
| `data/planted_nodes_per_node.csv` | one row per planted node: fitness, out-degree, weights, alpha, number of authors, final in-degree |
| `data/controls_stats.csv` | the six control runs (three per `theta`) |
| `config/` | example planted-node files: `planted_nodes_first_run.csv`, `planted_nodes_trio.csv`, `planted_nodes_single_example.csv` |
| `scripts/` | `planted_all_summaries.py` (writes the three CSVs; cluster side), `planted_analysis.py`, `planted_cohort_analysis.py`, `planted_single_analysis.py`, `planted_ladder_analysis.py` (the analyses as run) and their `.sbatch` files |

## Where the data live
**These paths are on the Illinois Campus Cluster project storage and may stop being valid after some time. The repository is the durable record.**
Run folders (configs, logs): `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/` in `planted_2026-11-08`, `planted_equalized_2026-11-08`, `planted_single_2026-11-08`, `planted_single_out50_2026-11-08`, `planted_single_out50_t1m_2026-11-08`, `planted_outdeg_ladder_2026-11-08`, `control_regen_2026-11-08` and `control_t1m_regen_2026-11-08`. The retained network: `.../arcana/weights_equal/baseline_cpm0.01/r0/output/`.
