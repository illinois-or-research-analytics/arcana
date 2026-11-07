# ARCANA reference set (2026-11-07)

Nine simulations: ARCANA main with three different community-label files (Leiden CPM at resolutions 0.1, 0.01 and 0.001 of the seed
network), three replicates each. This folder holds the data behind the tables below, the inputs that are specific to this set, the
scripts that produced the numbers, and a description of every step, so the tables can be checked or regenerated.

The runs are an abstract-model reference point for later sensitivity tests, not a calibration to a real network. Read patterns by
presence and direction, not by the absolute numbers.

## Terms

- **Cluster-aware citing:** a new paper (agent) is modeled on a generator paper. When the generator's cluster has at least `theta` papers (here 50),
  the agent draws its distance-1 citations from that whole cluster, and a share set by `alpha` stays inside it.
- **Ordinary citing:** otherwise the agent cites from the generator's usual neighborhood in the citation network, with no special weight on its cluster.
  `theta=1000000` turns cluster-aware citing off. New papers inherit their generator's cluster label either way. See `docs/USER_MANUAL.md`, section 5.1.

## Contents

| path | what it is |
|---|---|
| `data/reference_set_summaries.csv` | one row per simulation (9): size, integrity check, hubs, tail, age profile, within-cluster citation fraction |
| `data/conductance_bands.csv` | Leiden-readout conductance by cluster-size band, per run (36 rows) |
| `data/label_cluster_conductance.csv` | conductance of each label cluster (at least 50 seed papers) in each run's output network (297 rows) |
| `labels/seed_comm_cpm{0.1,0.01,0.001}_v3.csv` | the three community-label files (`node_id,cluster_id`, 26,686 seed papers); `MD5SUMS.labels_and_scripts` has checksums |
| `config/` | the configuration of one run (resolution 0.01) and the run scripts; the other eight differ only in the labels line |
| `scripts/` | `make_seed_labels_v3.py` (labels), `run_summaries.py` (simulation summaries), `conductance_analysis.py` (both conductance tables) |

## How the data were generated

### 1. Seed network and labels
- Seed set `mf_seed_v3`: 26,686 papers and 273,490 citations (multifield seed; files `seed_nodelist_v3.csv`, `seed_edgelist_v3.csv`;
  MD5 `886ab386...` and `e0b8b92f...`). Recency table `multifield_reccount_v3.csv`, out-degree bag `multifield_out_degree_bag_v3.csv`
  (median out-degree 15), author-count bag `pubmed_2025_english_journals_v3.csv`. The inputs are described in `docs/inputs.tar.gz`
  (edgelist and tables are identical in content to the v2 seed).
- Labels: `scripts/make_seed_labels_v3.py` builds the undirected graph from `seed_edgelist_v3.csv` and runs `leidenalg` 0.12.0
  (`CPMVertexPartition`, igraph 1.0.0) with `seed=1` at resolution 0.1, 0.01 and 0.001 (the 0.1 file is the pre-existing one, which
  the script reproduces exactly). Cluster statistics:

| labels | clusters | singletons | clusters ≥ 50 papers | papers in them | largest |
|---|---|---|---|---|---|
| 0.1 | 7,454 | 4,146 | 27 | 2,216 | 194 |
| 0.01 | 5,602 | 4,496 | 57 | 12,027 | 1,314 |
| 0.001 | 4,842 | 4,220 | 15 | 20,239 | 6,024 |

  Leiden is stochastic: an earlier unseeded 0.01 clustering (`simready_comm.csv`) agrees with the seeded 0.01 file at an adjusted
  Rand index of 0.66, and gave nearly identical simulation summaries (within-cluster 43.3% vs 43.2%, uncited 16.9% vs 17.0%).

### 2. Simulations
- Code: ARCANA `main` at commit b3e8ef0 (this repository). Build: GCC 13.3.0, OpenMPI 5.0.1, `-DCMAKE_BUILD_TYPE=Release`, on node-local
  storage; 32 OpenMP threads on one exclusive node, Illinois Campus Cluster `secondary` partition. Storage backend `ladybug`, database
  on node-local `/tmp`. `use_distributed=false`.
- Configuration (`config/config_cpm0.01.ini`; `docs/USER_MANUAL.md` explains each option): `growth_rate=0.1`, `num_cycles=40`
  (seed set grows to 1,208,027 papers); `alpha=-1` (random per agent, uniform on [0, 1]); `theta=50`; `unbinned_age_sampling=true`;
  Dirichlet weights 0.10 / 0.70 / 0.10 / 0.10 for preferential attachment, fitness, author count and author reputation, concentration 50;
  `same_year_citations=0.12`; `fully_random_citations=0.05`; fitness 1 to 1000, permanent (peak duration 1000, no lag);
  `non_random_generator_probability=0`; INSTAR options at their defaults. The only line that differs between the three label sets is
  `community_assignment`.
- Replicates `r0`, `r1`, `r2` use identical configs; each run seeds its random generator from `std::random_device`, so the
  replicates differ only by chance. Jobs 12214453 to 12214461 (labels 0.1: 12214453-55, 0.01: 12214456-58, 0.001: 12214459-61).
  Run times were about 1:15 (0.1), 1:24 (0.01) and 3:26 (0.001) per job.
- `scripts/run_summaries.py` reads each run's `nodelist.csv` and `edgelist.csv` and writes `data/reference_set_summaries.csv`. Checks:
  no duplicate edges, no self-citations, no citation from an older paper to a newer one, and edge count equals total in-degree
  (column `integrity`). "Seed share of new citations" is the seed papers' in-degree gain divided by all new citations. "Within-cluster"
  is the share of agent citations whose source and target carry the same `cluster_id` (each run's own labels).

### 3. Multiscale readout
The `SASCA-ReSA-INSTAR-multiscale` pipeline (commit 4c856a6, `slurm/run_pipeline.sh`) ran micro, IKC, Leiden and macro stages and a merge
job for each run. Leiden stage: CPM on the undirected citation graph of the whole output network at **resolution 0.1**, `seed=1`
(`mesoscale_readout.py leiden`), giving `meso/leiden_clusters.csv` with each cluster's size, cut, volume and conductance. The readout
resolution is 0.1 for all nine runs, whichever labels were used as input. CPM resolution is a minimum internal edge density, so 0.1
is the strictest of the three scales.

### 4. Conductance tables (`scripts/conductance_analysis.py`)
Conductance of a cluster = cut / min(volume, 2E − volume), with cut the number of edges leaving the cluster, volume the sum of its
members' degrees, and E the number of edges; 0 means no edges leave and 1 means fully mixed with the rest (the definition used in
`mesoscale_readout.py`).
- **Bands.** Leiden-readout clusters are grouped by size into half-open bands [2, 10), [10, 100), [100, 1000) and [1000, ∞)
  (a cluster of 10 papers is in the second band). Per run and band the table gives the number of clusters, papers, share of papers,
  median and quartiles of conductance, minimum, and the number below 0.5.
- **Label clusters.** For each label cluster with at least 50 seed papers (the clusters cluster-aware citing acts on), take all papers whose
  `cluster_id` equals it, seeds plus the agents that joined, and compute the same conductance in that run's output network.

## Results

### Simulations (mean of three replicates; spread across replicates is small)

| labels | within-cluster | uncited | seed share of new citations | agent top-0.1% in-degree median | agents > 50k in-degree | agent max |
|---|---|---|---|---|---|---|
| Leiden 0.1 | 40.3% (sd 0.05) | 15.1% | 4.54% | 2,320 (sd 62) | 2.0 | 55.6k |
| Leiden 0.01 | 43.2% (sd 0.05) | 17.0% | 4.67% | 2,914 (sd 84) | 2.0 | 57.9k |
| Leiden 0.001 | 44.1% (sd 0.02) | 18.5% | 4.78% | 3,778 (sd 94) | 7.3 | 68.1k |

The within-cluster column is measured against each run's own labels, so it is not comparable across label sets.

### Leiden readout (resolution 0.1) by cluster-size band (mean of three replicates)

| input labels | band | clusters | share of papers | median conductance | clusters < 0.5 (all replicates) |
|---|---|---|---|---|---|
| 0.1 | 2–9 | 132,909 | 55% | 0.919 | 0 |
| 0.1 | 10–99 | 20,269 | 43% | 0.847 | 5 |
| 0.1 | 100–999 | 162 | 1.4% | 0.716 | 0 |
| 0.01 | 2–9 | 180,363 | 72% | 0.926 | 0 |
| 0.01 | 10–99 | 14,932 | 27% | 0.859 | 0 |
| 0.01 | 100–999 | 134 | 1.3% | 0.835 | 0 |
| 0.001 | 2–9 | 205,240 | 79% | 0.929 | 0 |
| 0.001 | 10–99 | 13,312 | 21% | 0.869 | 0 |
| 0.001 | 100–999 | 38 | 0.4% | 0.906 | 0 |

No run has a cluster of 1000 or more papers. The replicate-to-replicate sd of each median is 0.001 or less (0.027 for the 38 clusters at 0.001).

### Label clusters in the output networks

| labels | label clusters (≥ 50 seeds) | median conductance | minimum | below 0.5 (pooled over replicates) | median size (all papers) |
|---|---|---|---|---|---|
| 0.1 | 27 | 0.524 | 0.456 | 25 of 81 | 3,116 |
| 0.01 | 57 | 0.504 | 0.448 | 74 of 171 | 4,681 |
| 0.001 | 15 | 0.511 | 0.475 | 14 of 45 | 24,903 |

The per-replicate medians agree to within about 0.01.

## Reading the results, and limits
- Finer input labels give better-separated communities in the readout: more papers in clusters of 10 to 99 papers and lower
  conductance in the 100 to 999 band. Coarser labels give more within-cluster citing, a heavier agent tail and more uncited papers.
- The label clusters are far better separated (conductance about 0.5) than the clusters Leiden finds at 0.1 (about 0.85). Leiden at 0.1
  cannot report communities of thousands of papers, because they are not dense enough to qualify, so it does not see the structure the
  cluster-aware citing builds at a coarse scale.
- Limits: one seed set; three replicates per condition; one seeded clustering per resolution; one readout resolution; no control run
  without cluster-aware citing, so the contribution of cluster-aware citing to the conductance of the label clusters is not separated out here.
  Conductance of small clusters is noisy and close to its floor.
- The raw networks (`edgelist.csv`, `nodelist.csv`, about 450 MB per run) are kept on the cluster, not in this repository (see
  "Where the data live" below).

## Where the data live

**These paths are on the Illinois Campus Cluster project storage. They may stop being valid after some time: the data-retention policy
will apply, and raw networks may be deleted. The repository (tables, labels, configs, scripts and this description) is the durable
record; the paths below are a convenience for as long as the files exist.** Every number in the tables can be regenerated from the
steps above.

| what | path |
|---|---|
| Raw networks and logs of the nine runs | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/baseline_cpm{0.1,0.01,0.001}/r{0,1,2}/output/` (`edgelist.csv`, `nodelist.csv`, `log.txt`, `abm.err`) |
| Run folders (config, scripts, Slurm log) | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/baseline_cpm{0.1,0.01,0.001}/r{0,1,2}/` |
| Multiscale readout per run (`micro/`, `meso/`, `macro/`, `summary_all.csv`) | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/chackoge/deltacon_testing/multiscale_results/arcana_reference/cpm{0.1,0.01,0.001}/r{0,1,2}/` |
| The three tables as written by the scripts | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/reference_set_summaries.csv` and `.../chackoge/deltacon_testing/multiscale_results/arcana_reference/{conductance_bands,label_cluster_conductance}.csv` |
| Label files and their scripts and checksums | `/projects/illinois/eng/cs/chackoge/mf_seed_v3/leiden_cpm/` (read-only) |
| Seed set `mf_seed_v3` | `/projects/illinois/eng/cs/chackoge/mf_seed_v3/` |
| ARCANA source used (as an archive) | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/archive_2026-11-07/arcana_code.tar.gz` (this repository at commit b3e8ef0 is the same code) |
| Multiscale pipeline | GitHub `illinois-or-research-analytics/SASCA-ReSA-INSTAR-multiscale` at commit 4c856a6; cluster clone `.../chackoge/deltacon_testing/multiscale_repo` |
| Pipeline settings | `/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/multiscale_ref_cpm{0.1,0.01,0.001}.env` |

The scripts in `scripts/` contain these absolute paths at the top; edit them if the data move.

## Regenerating
1. Labels: `python scripts/make_seed_labels_v3.py OUTDIR 0.1 0.01 0.001` (paths inside the script point to the cluster seed folder).
2. Simulations: for each label file, set `community_assignment` in a copy of `config/config_cpm0.01.ini`, build ARCANA at b3e8ef0, and run
   `abm --config config.ini --db-path <node-local dir>` three times.
3. Readout: the multiscale pipeline at commit 4c856a6 with `LEIDEN_RES=0.1`.
4. Tables: `scripts/run_summaries.py` and `scripts/conductance_analysis.py` (cluster paths at the top of each file).
