# ARCANA, equal agent weights (2026-11-08)

Eighteen simulations that repeat yesterday's reference, control and generator-selection designs with one change: the four mean scoring weights
(`pa_weight_mean`, `fit_weight_mean`, `na_weight_mean`, `ar_weight_mean`) are 0.25 each instead of 0.10 / 0.70 / 0.10 / 0.10. Three replicates per
condition. The master table below puts these runs next to the matching original-weight runs of the
[reference set](../reference_set_2026-11-07/README.md) and the [generator-selection study](../generator_selection_2026-11-07/README.md).

Scope: the study measures how the mix of scoring weights changes tails and clustering for a given citing rule and partition, not how communities form or grow.

## Terms
- **Cluster-aware citing on / off:** as defined in the reference set (`theta=50` on; `theta=1000000` off, which is ordinary citing). Labels are the Leiden
  CPM resolution (0.1, 0.01 or 0.001) applied to the seed nodes.
- **Weights:** each agent draws its four scoring weights from a Dirichlet distribution with the given means (concentration 50); they sum to 1 per agent.
  Original means 0.10 (preferential attachment, `pa`) / 0.70 (fitness, `fit`) / 0.10 (number of authors, `na`) / 0.10 (author reputation, `ar`); equal means 0.25 each.
- **Node coverage:** percentage of all nodes in the network that sit in a Leiden cluster whose size is in the band.
- **Within-label citing:** percentage of agent citations whose source and target share a seed-label cluster. With citing off it measures chance agreement with the labels, not a rule.

## Contents

| path | what it is |
|---|---|
| `data/master_table.csv`, `data/master_table.md` | the master table (12 rows: 6 conditions × 2 weight settings), means over three replicates |
| `data/weights_summaries.csv` | per-run simulation summaries for all 36 runs (18 equal-weight, 18 original-weight) |
| `data/conductance_bands_weights.csv` | per-run Leiden-readout band measures for the same 36 runs (node coverage is a percentage) |
| `config/config_equal_baseline_cpm0.01.ini` | configuration of one run (equal weights, labels 0.01, cluster-aware citing on); the others differ only in labels, `theta`, and generator lines |
| `scripts/` | `weights_summaries.py`, `weights_bands.py`, `make_master_table.py` |

## How the data were generated
- **Code and inputs:** ARCANA `main`, seed set `mf_seed_v3` (26,686 nodes, 273,490 citations), label files `seed_comm_cpm{0.1,0.01,0.001}_v3.csv`, GCC 13.3.0, OpenMPI 5.0.1,
  32 OpenMP threads on one node, Illinois Campus Cluster `secondary` partition, node-local database. Settings as in the reference set except the four weight means.
- **Runs (18, jobs 12248852 to 12248872):** cluster-aware citing on with labels 0.1, 0.01, 0.001 (9 runs); citing off (`theta=1000000`) with uniform generators,
  labels 0.01 (3 runs; also the control for the generator study); non-random generators at probability 0.5 with eligibility `and` or `or`, thresholds 5 / 20 / 10, `theta=1000000`, labels 0.01 (6 runs).
  Each config differs from its original-weight twin in exactly four lines (checked with `diff`). Agent weight means in every run's nodelist are 0.25 (sd of each weight about 0.06).
- **Original-weight rows** are the runs of the reference set (nine on), the three control runs at labels 0.01, and the six generator-selection runs. Only three of the nine reference controls are used, because with citing off the labels play no part.
- **Summaries** (`scripts/weights_summaries.py`): from each run's `nodelist.csv` and `edgelist.csv`; all 36 pass the integrity checks (no duplicate edges, no self-citations,
  no citation from an older to a newer node, edge count equals total in-degree).
- **Readout:** the multiscale pipeline, Leiden CPM at resolution 0.1 on the whole output network, then `scripts/weights_bands.py`. Bands are half-open, Python style:
  [2, 10), [10, 100), [100, 1000), [1000, ∞). The master table is built by `scripts/make_master_table.py` from the two CSVs.

## Master table (mean of three replicates)

### Concentration and tails

| condition | weights (pa/fit/na/ar) | Gini | top-10 share % | top-1% share % | top-0.1% median in-degree | max in-degree | agents > 50k |
|---|---|---|---|---|---|---|---|
| citing on, labels 0.1 | 0.10/0.70/0.10/0.10 | 0.77 | 1.91 | 38.6 | 2,301 | 55,592 | 2.0 |
| citing on, labels 0.1 | 0.25/0.25/0.25/0.25 | 0.76 | 1.33 | 33.8 | 1,984 | 45,893 | 0.3 |
| citing on, labels 0.01 | 0.10/0.70/0.10/0.10 | 0.82 | 1.75 | 46.1 | 2,892 | 57,897 | 2.0 |
| citing on, labels 0.01 | 0.25/0.25/0.25/0.25 | 0.80 | 1.13 | 40.6 | 2,503 | 33,863 | 0.0 |
| citing on, labels 0.001 | 0.10/0.70/0.10/0.10 | 0.85 | 2.46 | 56.1 | 3,712 | 68,136 | 7.3 |
| citing on, labels 0.001 | 0.25/0.25/0.25/0.25 | 0.84 | 1.77 | 50.4 | 2,982 | 47,587 | 0.3 |
| citing off, uniform generators | 0.10/0.70/0.10/0.10 | 0.78 | 2.02 | 45.2 | 2,978 | 69,642 | 2.3 |
| citing off, uniform generators | 0.25/0.25/0.25/0.25 | 0.76 | 1.45 | 39.5 | 2,480 | 43,357 | 0.0 |
| generators non-random, and | 0.10/0.70/0.10/0.10 | 0.80 | 3.30 | 47.1 | 2,634 | 102,367 | 17.7 |
| generators non-random, and | 0.25/0.25/0.25/0.25 | 0.79 | 2.34 | 42.5 | 2,306 | 66,651 | 5.7 |
| generators non-random, or | 0.10/0.70/0.10/0.10 | 0.79 | 2.88 | 47.5 | 3,000 | 107,683 | 9.7 |
| generators non-random, or | 0.25/0.25/0.25/0.25 | 0.77 | 1.71 | 41.5 | 2,598 | 52,360 | 1.3 |

### Citing, ages, seeds, uncited

| condition | weights (pa/fit/na/ar) | within-label citing % | seed share of new citations % | citations aged 1-4 % | uncited % |
|---|---|---|---|---|---|
| citing on, labels 0.1 | 0.10/0.70/0.10/0.10 | 40.3 | 4.54 | 34.4 | 15.1 |
| citing on, labels 0.1 | 0.25/0.25/0.25/0.25 | 40.4 | 4.67 | 34.3 | 14.2 |
| citing on, labels 0.01 | 0.10/0.70/0.10/0.10 | 43.2 | 4.67 | 34.5 | 17.0 |
| citing on, labels 0.01 | 0.25/0.25/0.25/0.25 | 43.2 | 4.75 | 34.4 | 15.5 |
| citing on, labels 0.001 | 0.10/0.70/0.10/0.10 | 44.1 | 4.78 | 34.8 | 18.5 |
| citing on, labels 0.001 | 0.25/0.25/0.25/0.25 | 44.1 | 4.85 | 34.6 | 16.6 |
| citing off, uniform generators | 0.10/0.70/0.10/0.10 | 15.5 | 5.03 | 30.8 | 14.4 |
| citing off, uniform generators | 0.25/0.25/0.25/0.25 | 15.8 | 5.19 | 30.9 | 13.5 |
| generators non-random, and | 0.10/0.70/0.10/0.10 | 15.5 | 4.46 | 34.3 | 14.8 |
| generators non-random, and | 0.25/0.25/0.25/0.25 | 15.0 | 4.57 | 34.2 | 14.3 |
| generators non-random, or | 0.10/0.70/0.10/0.10 | 14.7 | 4.54 | 33.0 | 14.3 |
| generators non-random, or | 0.25/0.25/0.25/0.25 | 14.8 | 4.69 | 32.9 | 13.4 |

### Leiden readout (resolution 0.1): node coverage % and median conductance by cluster-size band

| condition | weights (pa/fit/na/ar) | coverage 2-9 % | conductance 2-9 | coverage 10-99 % | conductance 10-99 | coverage 100-999 % | conductance 100-999 |
|---|---|---|---|---|---|---|---|
| citing on, labels 0.1 | 0.10/0.70/0.10/0.10 | 55.0 | 0.919 | 43.4 | 0.847 | 1.4 | 0.716 |
| citing on, labels 0.1 | 0.25/0.25/0.25/0.25 | 54.0 | 0.919 | 44.3 | 0.853 | 1.6 | 0.702 |
| citing on, labels 0.01 | 0.10/0.70/0.10/0.10 | 71.6 | 0.926 | 27.1 | 0.859 | 1.3 | 0.835 |
| citing on, labels 0.01 | 0.25/0.25/0.25/0.25 | 70.6 | 0.927 | 28.3 | 0.868 | 1.1 | 0.788 |
| citing on, labels 0.001 | 0.10/0.70/0.10/0.10 | 78.8 | 0.929 | 20.7 | 0.869 | 0.4 | 0.906 |
| citing on, labels 0.001 | 0.25/0.25/0.25/0.25 | 78.5 | 0.931 | 21.1 | 0.877 | 0.4 | 0.848 |
| citing off, uniform generators | 0.10/0.70/0.10/0.10 | 37.4 | 0.889 | 62.4 | 0.820 | 0.1 | 0.835 |
| citing off, uniform generators | 0.25/0.25/0.25/0.25 | 37.4 | 0.891 | 62.4 | 0.826 | 0.1 | 0.852 |
| generators non-random, and | 0.10/0.70/0.10/0.10 | 42.3 | 0.902 | 57.2 | 0.835 | 0.1 | 0.847 |
| generators non-random, and | 0.25/0.25/0.25/0.25 | 44.4 | 0.902 | 55.2 | 0.838 | 0.1 | 0.854 |
| generators non-random, or | 0.10/0.70/0.10/0.10 | 34.9 | 0.893 | 64.8 | 0.817 | 0.1 | 0.836 |
| generators non-random, or | 0.25/0.25/0.25/0.25 | 35.3 | 0.894 | 64.5 | 0.824 | 0.1 | 0.848 |

## Reading the results, and limits
- Equal weights lower concentration in every condition: top-1% share by 4.6 to 6.0 points, maximum in-degree by 17 to 51%, and the number of agents above 50k to near zero in the cluster-aware and uniform runs.
  Preferential attachment has more weight (0.10 to 0.25) yet the tail gets lighter, so the 0.70 fitness weight is the more concentrating ingredient. This has not been tested directly.
- Cluster-aware citing is unchanged by the weights: within-label citing is 40.4 / 43.2 / 44.1% (equal) against 40.3 / 43.2 / 44.1% (original), and the size-band shift from ordinary citing keeps its size and order across the label sets.
- Non-random generators still concentrate citations (top-10 share and agents above 50k order uniform < `or` < `and`) at both weight settings, and still barely move the clustering.
- Equal weights raise the median conductance of the 10 to 99 band slightly (by 0.003 to 0.009 in every condition) and lower that of the 100 to 999 band in the cluster-aware runs; the 100 to 999 bands hold few clusters, so those medians are noisy.
- Limits: three replicates; one seed set; one alternative weight setting; weight concentration fixed at 50; one readout resolution.
- The raw networks stay on the cluster (below); they are not in this repository.

## Where the data live
**These paths are on the Illinois Campus Cluster project storage and may stop being valid after some time: the data-retention policy will apply and raw networks may be deleted. The repository (tables, config, scripts and this description) is the durable record.**

| what | path |
|---|---|
| Raw networks, logs of the 18 runs | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/weights_equal/<group>/r{0,1,2}/output/` |
| Readout of the 18 runs | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/chackoge/deltacon_testing/multiscale_results/arcana_weights_equal/<group>/r{0,1,2}/` |
| Tables as written by the scripts | `.../arcana/weights_equal/weights_summaries.csv` and `.../multiscale_results/arcana_weights_equal/conductance_bands_weights.csv` |
| Pipeline settings | `.../arcana/weights_equal/multiscale_<group>.env` |

`<group>` is one of `baseline_cpm0.1`, `baseline_cpm0.01`, `baseline_cpm0.001`, `control_cpm0.01`, `nrg_and_t1m_cpm0.01`, `nrg_or_t1m_cpm0.01`. The scripts contain absolute paths at the top; edit them if the data move.
