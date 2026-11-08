# ARCANA, non-random generator selection (2026-11-07)

Six simulations that change only how the generator node of a new node is chosen: uniform (the control), or non-random with probability
0.5 and eligibility `and` or `or`. Three replicates per condition. Cluster-aware citing is off in all of them (`theta=1000000`), so the
only difference between a run and its control is the generator selection. The control is the `control_cpm0.01` set of the
[reference set](../reference_set_2026-11-07/README.md).

**Weights.** These runs use the earlier default scoring weights (fit 0.70, the other three 0.10 each). The equal-weights set and a fit-weight sweep are in [weights_equal_2026-11-08](../weights_equal_2026-11-08/README.md), which is the reference set going forward; the two sets are not mixed.

**Retention.** On 2026-11-08 the raw networks (`nodelist.csv` and `edgelist.csv`) of these runs were deleted from the cluster. The tables, readout results, configs and scripts remain; see "Where the data live" below.

Scope: the study measures the effect of a generator-selection rule on tails and on clustering, not how communities form or grow.

## Terms
- **Generator:** the existing node a new node is modeled on. Its neighborhood supplies the candidates for the new node's citations and the
  new node inherits its cluster label.
- **Uniform generators:** `non_random_generator_probability=0`; the generator is drawn uniformly from all nodes.
- **Non-random generators:** with probability 0.5 the generator is drawn uniformly from the *eligible set*, otherwise uniformly from all nodes.
  The eligible set holds the nodes published within `recency_threshold` years that are in the top `in_degree_threshold`% by in-degree
  (`and`: and also in the top `fitness_threshold`% by fitness; `or`: or in that top group). If the eligible set were empty, the draw would fall
  back to uniform; this never happened here (see below).

## Contents

| path | what it is |
|---|---|
| `data/nrg_t1m_summaries.csv` | one row per simulation (9: the three control replicates and the six generator runs): size, integrity check, tail and concentration measures, age profile, sizes of the eligible set |
| `data/conductance_bands_nrg.csv` | Leiden-readout conductance by cluster-size band, per run (36 rows); `node_coverage` is a percentage (0 to 100) |
| `config/` | `config_control_uniform.ini`, `config_nrg_and.ini`, `config_nrg_or.ini` (replicate r0 of each; the other replicates are identical) |
| `scripts/` | `generator_summaries.py` (simulation summaries and eligible-set sizes), `generator_bands.py` (band table) |

## How the data were generated

- **Code and inputs:** ARCANA `main` at commit b3e8ef0 (the code of this repository), seed set `mf_seed_v3` (26,686 nodes, 273,490 citations),
  Leiden CPM 0.01 labels (`seed_comm_cpm0.01_v3.csv`; the labels play no part in citing because `theta=1000000`, but nodes still inherit
  them). Build and runtime as in the reference set: GCC 13.3.0, OpenMPI 5.0.1, 32 OpenMP threads on one node, Illinois Campus Cluster
  `secondary` partition, node-local database.
- **Settings:** those of the reference set (`growth_rate=0.1`, `num_cycles=40`, `alpha=-1`, unbinned age sampling, Dirichlet weights
  0.10 / 0.70 / 0.10 / 0.10 with concentration 50, same-year 0.12, `fully_random_citations=0.05`, fitness 1 to 1000 and permanent), with
  `theta=1000000`. Generator lines for the six runs:

| | control | `and` | `or` |
|---|---|---|---|
| `non_random_generator_probability` | 0 | 0.5 | 0.5 |
| `generator_eligibility` | and | and | or |
| `generator_pool` | all | all | all |
| `in_degree_threshold` / `fitness_threshold` / `recency_threshold` | 90 / 50 / 10 (inactive at probability 0) | 5 / 20 / 10 | 5 / 20 / 10 |

  Diffs of each generator config against the control show only these lines. The thresholds 5 / 20 / 10 and the probability 0.5 are those
  of the earlier INSTAR experiments. `fully_random_citations` stays at 0.05, as in the reference set (the INSTAR experiments used 0.01).
- **Runs:** jobs 12220099 to 12220104 (`and`: 12220099 to 12220101; `or`: 12220102 to 12220104), about 50 seconds each.
- **Summaries** (`scripts/generator_summaries.py`): from each run's `nodelist.csv` and `edgelist.csv`. Integrity: no duplicate edges, no
  self-citations, no citation from an older to a newer node, edge count equals total in-degree (all nine pass). Concentration measures are
  over all nodes; "top 1%" and "top 0.1%" are the 1% and 0.1% of nodes with the highest in-degree. The sizes of the eligible set come from
  the run log, one line per simulated year.
- **Readout:** the multiscale pipeline (commit 4c856a6), Leiden CPM at resolution 0.1 on the whole output network, `seed=1`, then
  `scripts/generator_bands.py`. Bands are half-open, Python style: [2, 10), [10, 100), [100, 1000), [1000, ∞). Conductance is
  cut / min(volume, 2E − volume).

## Results (mean of three replicates)

### Simulations

| measure | uniform (control) | non-random 0.5, `and` | non-random 0.5, `or` |
|---|---|---|---|
| Gini of in-degree | 0.78 | 0.80 | 0.79 |
| top-10 nodes' share of citations | 2.02% | 3.30% | 2.88% |
| top 1% nodes' share | 45.2% | 47.1% | 47.5% |
| top 1%: median in-degree | 269 | 273 | 266 |
| top 0.1%: median in-degree | 2,978 | 2,634 | 2,999 |
| top 0.1%: 99th percentile of in-degree | 34.2k | 56.9k | 43.6k |
| most-cited node | 69.6k | 102.4k | 107.7k |
| agents above 50k in-degree | 2.3 | 17.7 | 9.7 |
| seed share of new citations | 5.03% | 4.46% | 4.54% |
| citations aged 1–4 years | 30.8% | 34.3% | 33.0% |
| uncited nodes | 14.40% | 14.75% | 14.32% |
| eligible set, smallest / median size over the 40 years | | 197 to 318 / about 3,480 | about 5,050 to 6,150 / about 28,350 |

Replicate spread (sd): top 1% share 0.07 to 0.12 points; seed share 0.00 to 0.02; most-cited node 8k to 17k (so the `and` and `or` maxima are
indistinguishable); top-0.1% median 60 to 86.

### Leiden readout (resolution 0.1) by cluster-size band

**Node coverage** in a band table is the percentage of all nodes in the network that sit in a Leiden cluster whose size is in that band: the nodes in the band's clusters divided by all nodes (about 1.21 million). It is not the share of clusters. Coverage across bands sums to about 100%, apart from nodes left alone in a one-node cluster.

| generators | band | clusters | node coverage | median conductance |
|---|---|---|---|---|
| uniform | 2–9 | 77,847 | 37.4% | 0.889 |
| uniform | 10–99 | 50,417 | 62.4% | 0.820 |
| uniform | 100–999 | 5 | 0.07% | 0.835 |
| `and` | 2–9 | 95,406 | 42.3% | 0.902 |
| `and` | 10–99 | 42,361 | 57.2% | 0.835 |
| `and` | 100–999 | 5.3 | 0.07% | 0.847 |
| `or` | 2–9 | 75,038 | 34.9% | 0.893 |
| `or` | 10–99 | 50,986 | 64.8% | 0.817 |
| `or` | 100–999 | 5.7 | 0.07% | 0.836 |

No cluster in any run has conductance below 0.5 or reaches 1000 nodes; the largest cluster has 211 to 225 nodes. The replicate sd of each
band median is 0.001 or less (up to 0.010 for the five or six clusters in the 100–999 band).

## Reading the results, and limits
- Non-random generators concentrate citations at the top. The order uniform < `or` < `and` holds for the top-10 share, the 99th percentile of
  the top 0.1% and the number of agents above 50k, and agrees with the earlier INSTAR experiments (growth 5% for 76 years, 12% for 33 years,
  13.4% for 30 years). The body of the distribution does not move: the top-1% median is 266 to 273 in all three.
- They also lower the seed share of new citations (5.03% to about 4.5%) and raise the share of citations aged 1 to 4 years.
- The clustering at 0.1 barely changes: `or` is essentially the control; `and` moves about 5 points of nodes from the 10–99 band to the 2–9
  band and raises the 10–99 median conductance from 0.820 to 0.835. This is a small effect next to that of cluster-aware citing, which moved
  the 10–99 share from 62% to 21–43% (reference set).
- The `and` set was never empty (smallest size 197 nodes in any year of any replicate), so the fallback to uniform never applied.
- Limits: three replicates; one seed set; one label set (inactive here); one probability (0.5); one set of thresholds (5 / 20 / 10); one
  readout resolution. With `pool = all` only; the pool options (`agents_eligible`, `agents`) were not run in this set.
- The raw networks were deleted from the cluster on 2026-11-08 (see below); they were never in this repository.

## Where the data live
**These paths are on the Illinois Campus Cluster project storage. They may stop being valid after some time: the data-retention policy will apply. On 2026-11-08 the raw networks (`nodelist.csv` and `edgelist.csv`) of every run listed here were deleted; the run folders (config, scripts, logs) and the readout results remain. A run takes about two minutes, so the networks can be regenerated, but the random seed is not logged: a regenerated network is statistically equivalent, not identical. The repository (tables, labels, configs, scripts and this description) is the durable record.**

| what | path |
|---|---|
| Raw networks, logs of the six runs | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/nrg_{and,or}_t1m_cpm0.01/r{0,1,2}/output/` |
| Run folders (config, scripts) | same, one level up |
| Control runs | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/control_cpm0.01/r{0,1,2}/` |
| Multiscale readout | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/chackoge/deltacon_testing/multiscale_results/arcana_nrg/{and_t1m,or_t1m}/r{0,1,2}/` (control: `.../arcana_control/cpm0.01/`) |
| Tables as written by the scripts | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/nrg_t1m_summaries.csv` and `.../multiscale_results/arcana_nrg/conductance_bands_nrg.csv` |
| Pipeline settings | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/multiscale_nrg_{and,or}_t1m.env` |

The scripts contain these absolute paths at the top; edit them if the data move.
