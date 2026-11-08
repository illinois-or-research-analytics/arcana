# ARCANA, equal agent weights and a fit-weight OFAT study (2026-11-08)

Two parts. **(1)** Eighteen simulations that repeat the reference, control and generator-selection designs with the four mean scoring weights
(`pa_weight_mean`, `fit_weight_mean`, `na_weight_mean`, `ar_weight_mean`) at 0.25 each: six conditions, three replicates each. This is the reference set going forward.
**(2)** A one-factor-at-a-time (OFAT) study around one of those conditions: the fit weight at 0.10 and 0.90, `theta` at 50 and 1,000,000, and non-random generator selection at `theta` 50.

The earlier [reference set](../reference_set_2026-11-07/README.md) and [generator-selection study](../generator_selection_2026-11-07/README.md) were run at the earlier default weights (fit 0.70,
the other three 0.10 each) and are kept as the record of that campaign; they are not mixed into the tables below.

Scope: the study measures how scoring weights, a citing rule and generator selection shape tails and clustering for a given community partition, not how communities form or grow.

## Terms
- **Cluster-aware citing on / off:** as defined in the reference set (`theta=50` on; `theta=1000000` off, which is ordinary citing). The labels are the Leiden
  CPM resolution (0.1, 0.01 or 0.001) applied to the seed nodes.
- **Weights:** each agent draws its four scoring weights from a Dirichlet distribution with the given means (concentration 50); they sum to 1 per agent. The program normalises the means to sum to 1.
- **Uniform / non-random generators:** `non_random_generator_probability` 0 (uniform), or 0.5 with eligibility `and` or `or` and thresholds 5 / 20 / 10 (non-random).
- **Node coverage:** percentage of all nodes in the network that sit in a Leiden cluster whose size is in the band.
- **Within-label citing:** percentage of agent citations whose source and target share a seed-label cluster. With citing off it measures chance agreement with the labels, not a rule.

## Contents

| path | what it is |
|---|---|
| `data/master_table.csv`, `data/master_table.md` | master table of the equal-weights set (6 conditions, means over three replicates) |
| `data/ofat_table.csv`, `data/ofat_table.md` | OFAT table with every setting spelled out |
| `data/weights_summaries.csv`, `data/conductance_bands_weights.csv` | per-run simulation summaries and Leiden band measures of the 18 equal-weights runs (node coverage is a percentage) |
| `data/ofat_run_summaries.csv` | per-run simulation summaries of the 9 OFAT runs |
| `config/` | `config_equal_baseline_cpm0.01.ini` (the centre run) and `config_ofat_{fit_lo,fit_hi,nrg_and_theta50}.ini` (the `theta` 1,000,000 arms change only the `theta` line) |
| `scripts/` | `weights_summaries.py`, `weights_bands.py`, `ofat_summaries.py` (cluster side), `make_master_table.py`, `make_ofat_table.py` |

## How the data were generated
- **Code and inputs:** ARCANA `main` (tag `v1.0-frozen`), seed set `mf_seed_v3` (26,686 nodes, 273,490 citations; see `inputs/mf_seed_v3`), label files `seed_comm_cpm{0.1,0.01,0.001}_v3.csv`,
  GCC 13.3.0, OpenMPI 5.0.1, 32 OpenMP threads on one node, Illinois Campus Cluster `secondary` partition, node-local database. Settings as in the reference set except the weights.
- **Equal-weights runs (18, jobs 12248852 to 12248872):** cluster-aware citing on with labels 0.1, 0.01, 0.001 (9 runs); citing off (`theta=1000000`) with uniform generators, labels 0.01 (3 runs);
  non-random generators at probability 0.5, eligibility `and` or `or`, `theta=1000000`, labels 0.01 (6 runs). Agent weight means in every run's nodelist are 0.25 (sd of each weight about 0.06).
- **OFAT runs (9; jobs 12255779 to 12255781, 12256001 to 12256004, 12256102, 12256106):** the centre run is the equal-weights run with labels 0.01, uniform generators and `theta` 50 (three replicates).
  Each arm changes one setting. Fit 0.10 uses means 0.30 / 0.10 / 0.30 / 0.30 and fit 0.90 uses 0.0333 / 0.90 / 0.0333 / 0.0333 (pa / fit / na / ar). The `theta` 1,000,000 arm is the equal-weights control.
  The non-random generator arm at `theta` 50 uses probability 0.5, eligibility `and`, thresholds 5 / 20 / 10. The fit arms at `theta` 1,000,000 repeat the fit arms with only `theta` changed. Each config differs
  from its parent in exactly the lines described (checked with `diff`). `fit_hi` and `nrg_and_theta50` at `theta` 50 have three replicates; `fit_lo` at both `theta` values and `fit_hi` at `theta` 1,000,000 have one.
- **Summaries:** from each run's `nodelist.csv` and `edgelist.csv`; all 27 runs pass the integrity checks (no duplicate edges, no self-citations, no citation from an older to a newer node, edge count equals total in-degree).
- **Readout (equal-weights runs only):** the multiscale pipeline, Leiden CPM at resolution 0.1 on the whole output network, then `scripts/weights_bands.py`. Bands are half-open, Python style:
  [2, 10), [10, 100), [100, 1000), [1000, ∞). The OFAT runs were not put through the readout.

## Master table: the equal-weights set (mean of three replicates)

### Concentration and tails

| condition | Gini | top-10 share % | top-1% share % | top-0.1% median in-degree | max in-degree | agents > 50k |
|---|---|---|---|---|---|---|
| citing on, labels 0.1 | 0.76 | 1.33 | 33.8 | 1,984 | 45,893 | 0.3 |
| citing on, labels 0.01 | 0.80 | 1.13 | 40.6 | 2,503 | 33,863 | 0.0 |
| citing on, labels 0.001 | 0.84 | 1.77 | 50.4 | 2,982 | 47,587 | 0.3 |
| citing off, uniform generators | 0.76 | 1.45 | 39.5 | 2,480 | 43,357 | 0.0 |
| generators non-random, and | 0.79 | 2.34 | 42.5 | 2,306 | 66,651 | 5.7 |
| generators non-random, or | 0.77 | 1.71 | 41.5 | 2,598 | 52,360 | 1.3 |

### Citing, ages, seeds, uncited

| condition | within-label citing % | seed share of new citations % | citations aged 1-4 % | uncited % |
|---|---|---|---|---|
| citing on, labels 0.1 | 40.4 | 4.67 | 34.3 | 14.2 |
| citing on, labels 0.01 | 43.2 | 4.75 | 34.4 | 15.5 |
| citing on, labels 0.001 | 44.1 | 4.85 | 34.6 | 16.6 |
| citing off, uniform generators | 15.8 | 5.19 | 30.9 | 13.5 |
| generators non-random, and | 15.0 | 4.57 | 34.2 | 14.3 |
| generators non-random, or | 14.8 | 4.69 | 32.9 | 13.4 |

### Leiden readout (resolution 0.1): node coverage % and median conductance by cluster-size band

| condition | coverage 2-9 % | conductance 2-9 | coverage 10-99 % | conductance 10-99 | coverage 100-999 % | conductance 100-999 |
|---|---|---|---|---|---|---|
| citing on, labels 0.1 | 54.0 | 0.919 | 44.3 | 0.853 | 1.6 | 0.702 |
| citing on, labels 0.01 | 70.6 | 0.927 | 28.3 | 0.868 | 1.1 | 0.788 |
| citing on, labels 0.001 | 78.5 | 0.931 | 21.1 | 0.877 | 0.4 | 0.848 |
| citing off, uniform generators | 37.4 | 0.891 | 62.4 | 0.826 | 0.1 | 0.852 |
| generators non-random, and | 44.4 | 0.902 | 55.2 | 0.838 | 0.1 | 0.854 |
| generators non-random, or | 35.3 | 0.894 | 64.5 | 0.824 | 0.1 | 0.848 |

## OFAT: the fit weight, `theta` and generator selection

Centre: equal weights, uniform generators, `theta` 50, labels 0.01. Replicate sd of the centre: 0.52 points for the top-1% share, 68 for the top-0.1% median, 0.13 for the top-10 share
(the maximum in-degree is too noisy for single runs and is not read).

| arm | weights (pa / fit / na / ar) | generators | theta | reps | Gini | top-10 % | top-1% share % | top-0.1% median | uncited % | within-label % | seed share % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fit 0.10 | 0.30 / 0.10 / 0.30 / 0.30 | uniform | 50 | 1 | 0.80 | 1.23 | 40.1 | 2,312 | 15.2 | 43.3 | 4.78 |
| centre | 0.25 / 0.25 / 0.25 / 0.25 | uniform | 50 | 3 | 0.80 | 1.13 | 40.6 | 2,503 | 15.5 | 43.2 | 4.75 |
| fit 0.90 | 0.033 / 0.90 / 0.033 / 0.033 | uniform | 50 | 3 | 0.84 | 1.87 | 51.3 | 3,332 | 18.6 | 43.2 | 4.65 |
| fit 0.10 | 0.30 / 0.10 / 0.30 / 0.30 | uniform | 1,000,000 | 1 | 0.76 | 1.76 | 39.3 | 2,334 | 13.3 | 16.0 | 5.26 |
| fit 0.25 | 0.25 / 0.25 / 0.25 / 0.25 | uniform | 1,000,000 | 3 | 0.76 | 1.45 | 39.5 | 2,480 | 13.5 | 15.8 | 5.19 |
| fit 0.90 | 0.033 / 0.90 / 0.033 / 0.033 | uniform | 1,000,000 | 1 | 0.80 | 2.63 | 50.1 | 3,270 | 15.5 | 15.7 | 5.01 |
| generators | 0.25 / 0.25 / 0.25 / 0.25 | non-random and | 50 | 3 | 0.84 | 2.04 | 45.4 | 2,432 | 18.1 | 46.1 | 4.40 |
| generators | 0.25 / 0.25 / 0.25 / 0.25 | non-random and | 1,000,000 | 3 | 0.79 | 2.34 | 42.5 | 2,306 | 14.3 | 15.0 | 4.57 |

- **The fit weight is flat from 0.10 to 0.25 and large at 0.90.** The top-1% share goes 40.1, 40.6, 51.3 at `theta` 50 and 39.3, 39.5, 50.1 at `theta` 1,000,000. The Gini, the top-0.1% median and the uncited share move the same way.
  With three fit values the shape between 0.25 and 0.90 is not resolved.
- **Fit weight and `theta` add up.** The 0.25-to-0.90 step is +10.7 points at `theta` 50 and +10.6 at `theta` 1,000,000 (Gini +0.04 at both). Cluster-aware citing adds about 1 point to the top-1% share at all three fit values.
- **Generator selection interacts with cluster-aware citing, moderately.** Non-random `and` generators raise the top-1% share by 4.7 points at `theta` 50 and 3.0 at `theta` 1,000,000, the uncited share by 2.6 and 0.8 points,
  and within-label citing by 2.8 points against a 0.8-point fall. The top-10 share and the Gini do not interact. The replicate sd at `theta` 50 is 0.69 points for the top-1% share.
- A plausible reason for the fit effect is that fitness is permanent, so high-fitness nodes keep being cited and low-fitness ones never are; this was not tested.

## Reading the results, and limits
- Cluster-aware citing, at equal weights, replaces mid-size clusters with fragments and a few larger ones. The 10 to 99 band falls from 62% to 21 to 44% of nodes, and the 100 to 999 band grows from 0.1% to 0.4 to 1.6%,
  with lower conductance at the finest labels. No cluster reaches 1,000 nodes in any run. The Leiden readout at resolution 0.1 is a conservative lower bound on community structure; coarser readouts were not run.
- Non-random generators concentrate citations at the top (top-10 share and agents above 50k order uniform < `or` < `and`) and barely move the clustering.
- Limits: three replicates for the equal-weights set and the OFAT centre, one for several OFAT arms; one seed set; one readout resolution; weight concentration fixed at 50; fit weight at three values.

## Retention of the data
**On 2026-11-08 the raw networks (`nodelist.csv` and `edgelist.csv`) of all runs were deleted from the cluster, except one: the centre run, `weights_equal/baseline_cpm0.01/r0`.** The record is the configurations,
logs, per-run summary tables, the Leiden readout results and the scripts in this repository. A run takes about two minutes and the readout 17 to 30 minutes, so the networks can be regenerated, but the generator is
seeded from `std::random_device` and the seed is not logged: a regenerated network is statistically equivalent to the original, not identical.

## Where the data live
**These paths are on the Illinois Campus Cluster project storage and may stop being valid after some time: the data-retention policy will apply. The repository (tables, configs, scripts and this description) is the durable record.**

| what | path |
|---|---|
| Run folders (config, scripts, logs) of the 18 equal-weights runs | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/weights_equal/<group>/r{0,1,2}/` |
| Run folders of the 9 OFAT runs | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/ofat_2026-11-08/<arm>/r{0,1,2}/` |
| The one retained network (centre run) | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/weights_equal/baseline_cpm0.01/r0/output/` |
| Leiden readout of the 18 equal-weights runs | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/chackoge/deltacon_testing/multiscale_results/arcana_weights_equal/<group>/r{0,1,2}/` |
| Tables as written by the scripts | `.../arcana/weights_equal/weights_summaries.csv`, `.../arcana/ofat_2026-11-08/ofat_summaries.csv`, `.../multiscale_results/arcana_weights_equal/conductance_bands_weights.csv` |

`<group>` is one of `baseline_cpm0.1`, `baseline_cpm0.01`, `baseline_cpm0.001`, `control_cpm0.01`, `nrg_and_t1m_cpm0.01`, `nrg_or_t1m_cpm0.01`. The cluster-side scripts contain absolute paths at the top; edit them if the data move.
The cluster copy of `weights_summaries.csv` still holds the 36-run version with the earlier-default-weights rows; this repository's CSVs hold the 18 equal-weights runs.
