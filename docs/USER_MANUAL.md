# ARCANA user manual

ARCANA (Age-Resolved Community-Aware Network Agents) is an agent-based model that grows a citation network from a seed
network. It is an experimental extension of CantataS: every ARCANA option is off by default, so a CantataS configuration
runs as before. This manual documents the configuration file, the input files, the options and how they interact. The
sample configuration, [`config.sample.ini`](../config.sample.ini), carries no comments; everything it used to say is here.

Contents: [1 Running](#1-running) · [2 Configuration file rules](#2-configuration-file-rules) ·
[3 Input files](#3-input-files) · [4 Option reference](#4-option-reference) · [5 How the options interact](#5-how-the-options-interact) ·
[6 Output files](#6-output-files) · [7 Recipes](#7-recipes) · [8 Verification status](#8-verification-status)

## 1. Running

```sh
./build/bin/abm --config ./config.ini --db-path <fast local directory>
```

| Argument | Meaning |
|---|---|
| `--config` | Path to the `.ini` file (required). |
| `--db-path` | Directory for the LadyBugDB storage; overrides `db_path` in the file. Use fast node-local storage (for example `/tmp/$USER/ladybug_data` on a compute node), not a shared filesystem. |
| `--storage-backend` | `ladybug` (out-of-core, memory-mapped) or `legacy` (in memory); overrides the file. |

Under MPI (`mpirun` or `srun` with more than one rank), distributed mode is switched on automatically, each rank gets
its own `db_path` and log file (suffix `_rank_N`), and only rank 0 writes the final output files. Build and cluster notes
are in the [README](../README.md) and [`experiments/batch_script.run.example`](../experiments/batch_script.run.example).

Every run is independent: the random generator is seeded from `std::random_device`, so two runs of the same file differ.
The model is stochastic; judge a setting by its pattern across replicates, not by one run.

## 2. Configuration file rules

- Three sections: `[Environment]`, `[Agent]`, `[General]`.
- **Comments.** A line starting with `;` is a comment, and `;` after a value (with a space before it) starts an inline
  comment. The sample file has none; this manual replaces them.
- **Line length.** The parser (inih) reads at most **200 characters per line**. A longer line fails at startup with
  `parse error on line N` and the run exits within a second. Long paths plus an inline comment are the usual cause, so
  keep long paths on lines without comments. Slurm reports such a job as COMPLETED, so check for the output files.
- **Required keys.** The program stops at startup if any of these is missing (a key may be given an empty value where the
  table says so):
  - `[Environment]`: `edgelist`, `nodelist`, `out_degree_bag`, `recency_table`, `planted_nodes`, `growth_rate`,
    `num_cycles`, `recency_bins`, `start_from_checkpoint`.
  - `[Agent]`: `fully_random_citations`, `preferential_weight`, `fitness_weight`, `num_authors_weight`,
    `author_reputation_weight`, `fitness_value_min`, `fitness_value_max`, `fitness_lag_duration_min`,
    `fitness_lag_duration_max`, `fitness_peak_duration_min`, `fitness_peak_duration_max`, `same_year_citations`,
    `neighborhood_sample`, `num_authors_bag`, `author_max_lifetime`, `cartel_outdegree_proportion`, `null_cartel`,
    `clonal_cartel_agent_file`, `alpha`, `use_alpha`, `in_degree_threshold`, `fitness_threshold`, `recency_threshold`,
    `non_random_generator_probability`.
  - `[General]`: `output_file`, `auxiliary_information_file`, `log_file`, `num_processors`, `log_level`.
- Boolean values are written `true` or `false` exactly.
- The settings need tuning for each seed set and each set of running conditions. The sample is an example, not a
  recommended default.

## 3. Input files

All are CSV with a header row. The ID column in every node-level file is `node_id`.

| Option | Columns | Meaning |
|---|---|---|
| `nodelist` | `node_id,year` | Seed papers and their publication years. |
| `edgelist` | `source,target` | Seed citations (`source` cites `target`). |
| `community_assignment` | `node_id,cluster_id` | Community label for each seed paper, used by the cluster route (see `theta`). Field labels, or a clustering such as Leiden CPM. May be empty when `theta` turns the route off. |
| `recency_table` | `diff,count` | Number of citations at each age in years. Age 0 is ignored (same-year citations are a separate quota). With `unbinned_age_sampling=true` it is used as a per-year probability table. |
| `out_degree_bag` | `node_id,out_degree` | Empirical out-degrees; each new paper draws its number of references from this bag. |
| `num_authors_bag` | `pubmed_id,author_count` | Empirical author counts; each new paper draws its number of authors from this bag. |
| `planted_nodes` | see [CantataS README](CANTATAS_README.md) | Optional hand-specified agents. Empty for none. |
| `clonal_cartel_agent_file` | see [CantataS README](CANTATAS_README.md) | Optional attributes for clonal cartel agents. Empty for none. |

## 4. Option reference

Defaults in the tables are those applied when the key is absent. "Required" keys have no default.

### 4.1 `[Environment]`

| Key | Default | Meaning |
|---|---|---|
| `nodelist`, `edgelist`, `community_assignment`, `recency_table`, `out_degree_bag`, `planted_nodes` | required (`community_assignment` optional) | Input files, section 3. |
| `growth_rate` | required | Fraction of the current number of papers added each year, for example 0.1 for 10%. |
| `num_cycles` | required | Number of simulated years. |
| `recency_bins` | required | Comma-separated upper bounds of the age bins used by the binned age sampler, for example `1,2,3,4,5,10,15,20,25,30,35,40,45,50`. Still read and validated when `unbinned_age_sampling=true`, but not used then. |
| `start_from_checkpoint` | required | `true` resumes from the checkpoint in `db_path` (the run continues from the year after the last committed one); `false` starts fresh. |

### 4.2 `[Agent]`: citation behavior

| Key | Default | Meaning |
|---|---|---|
| `alpha` | required | Share of an agent's citation quota that goes to distance-1 candidates (its generator's direct neighborhood, or its whole cluster on the cluster route). A fixed value in [0, 1], or `-1` to draw a value at random for each agent. |
| `minimum_alpha`, `maximum_alpha` | unset (0 and 1) | Bounds of the random alpha. Only valid with `alpha=-1`; the draw is uniform on [minimum, maximum] and rounded to 3 decimals. Either bound may be given alone. Need 0 ≤ minimum ≤ maximum ≤ 1, else the program stops. With the cluster route on, the within-cluster citation fraction is about the mean alpha, so `minimum_alpha=0.55` and `maximum_alpha=0.95` emphasizes intra-cluster citations. |
| `use_alpha` | required | `true` applies alpha to split the quota between distance-1 and distance-2 candidates; `false` disables the split. |
| `theta` | required | Minimum cluster size for the cluster route. A value above the largest cluster (for example `1000000`) turns the cluster route off. See 5.1. |
| `same_year_citations` | required | Fraction of new papers that are same-year citation sources, for example 0.12. |
| `fully_random_citations` | required | Fraction of each paper's references drawn uniformly at random from all papers, for example 0.05. |
| `neighborhood_sample` | required | Maximum number of candidates sampled from each neighborhood when the cluster route is not used. |
| `preferential_weight`, `fitness_weight`, `num_authors_weight`, `author_reputation_weight` | required | Fixed weights of the four scoring components (preferential attachment on in-degree, fitness, author count, author reputation). `-1` for all four draws them at random for each agent (CantataS behavior). Ignored when the `*_weight_mean` options below are set. |

### 4.3 `[Agent]`: scoring (INSTAR options)

Each candidate's score for a component is `max(x^exponent, 1) + score_offset`. These options are off by default: the
defaults reproduce the original scoring (exponent 3, offset 1).

| Key | Default | Meaning |
|---|---|---|
| `score_exponent` | 3 | Exponent applied to all four components unless overridden below. |
| `pa_exponent`, `fitness_exponent`, `num_authors_exponent`, `author_reputation_exponent` | `score_exponent` | Per-component exponents. Each must be in [0, 10]. |
| `score_offset` | 1 | Added to every score. Must be non-negative. |

### 4.4 `[Agent]`: fitness

| Key | Default | Meaning |
|---|---|---|
| `fitness_value_min`, `fitness_value_max` | required | Range (inclusive) of the peak fitness an agent draws. A few extreme draws produce the hubs in the agent population. |
| `fitness_lag_duration_min`, `fitness_lag_duration_max` | required | Years of dormancy before peak fitness. `0` means no lag. |
| `fitness_peak_duration_min`, `fitness_peak_duration_max` | required | Years at peak fitness. `1000` means fitness is permanent. |

### 4.5 `[Agent]`: generator selection

The generator is the existing paper a new paper starts from; its neighborhood supplies the distance-1 and distance-2
candidates, and a new paper inherits its generator's cluster.

| Key | Default | Meaning |
|---|---|---|
| `non_random_generator_probability` | required | Probability that a new paper's generator is drawn from the eligible set instead of uniformly from all papers. `0` draws always uniformly. |
| `in_degree_threshold`, `fitness_threshold` | required | Percentages. Within the recency window, a paper passes the in-degree (fitness) criterion if it is in the top this-many percent by in-degree (fitness). A value of 90 keeps the top 90%, a weak filter; 5 keeps the top 5%. |
| `recency_threshold` | required | Width in years of the recency window: only papers published within this many years of the current year are candidates. |
| `generator_eligibility` | `and` | `and`: a paper must pass both criteria. `or`: either is enough. (INSTAR option.) |
| `generator_pool` | `all` | `all`: any paper can be a generator. `agents_eligible`: the eligible set is restricted to agents. `agents`: eligible set restricted to agents, and the random draw also uses agents only. (INSTAR option.) |
| `generator_pool_min_agent_share` | 0.1 | With an agents-restricted pool, the unfiltered eligible set is used until agents are at least this share of it (always so in the first simulated year, when there are no agents). (INSTAR option.) |

If the eligible set is empty in a year, the random draw is used instead. Seeds are ranked by their own fitness (1 unless
the nodelist says otherwise) when the eligible set is built, as in citation scoring.

### 4.6 `[Agent]`: authors and cartels

| Key | Default | Meaning |
|---|---|---|
| `num_authors_bag` | required | See section 3. |
| `author_max_lifetime` | required | Maximum career length of an author in years. |
| `cartel_outdegree_proportion` | required | Share of a cartel member's references directed within the cartel. |
| `null_cartel` | required | `true`: cartel members cite each other at random (random-cartel model); `false`: by score (preferential-cartel model). |
| `clonal_cartel_agent_file` | required (may be empty) | Section 3. |

### 4.7 `[Agent]`: ARCANA options (all off by default)

| Key | Default | Meaning |
|---|---|---|
| `unbinned_age_sampling` | `false` | Draw each citation's age from `recency_table` year by year, restricted to ages that have candidates, then score within the age. The binned sampler is not used. |
| `pa_weight_mean`, `fit_weight_mean`, `na_weight_mean`, `ar_weight_mean` | -1 (off) | Expected values of the four component weights. Each agent draws its weights from a Dirichlet distribution with these means, rescaled to sum to 1. A mean of 0 keeps that weight at 0. Leave all four unset to use the weights from 4.2. |
| `weight_concentration` | 20 | Concentration of the Dirichlet draw. Larger values keep an agent's weights closer to the means; at 50, the preferential-attachment weight has a standard deviation of about 0.03 around a mean of 0.05. |
| `minimum_alpha`, `maximum_alpha` | unset | Bounded random alpha, 4.2. |

### 4.8 `[Agent]`: experimental options kept for provenance (no benefit shown; leave off)

| Key | Default | Meaning and finding |
|---|---|---|
| `max_citable_age` | -1 (off) | Papers older than this many years cannot be cited. It piles citations on the oldest allowed age. |
| `age_damping_start` | -1 (off) | Damp the in-degree score for papers older than this many years. No measurable effect. |
| `age_damping_tau`, `age_damping_min_exponent` | 10, 0 | Shape of the damping: the exponent decays from the scoring exponent towards `age_damping_min_exponent` with time constant `age_damping_tau`. The score offset is not applied on this path. |
| `neighborhood_recency_lambda` | -1 | Bias neighborhood down-sampling towards recent papers (≤ 0 means uniform). Never run. |
| `neighborhood_prepool_factor` | 1 | Pre-pool size factor for that down-sampling. |

### 4.9 `[General]`

| Key | Default | Meaning |
|---|---|---|
| `output_file` | required | Output edgelist (`source,target`). |
| `auxiliary_information_file` | required | Output nodelist with per-paper attributes (section 6). |
| `log_file` | required | Log file; per-rank suffix under MPI. |
| `log_level` | required | 0 silent, 1 info, 2 verbose. |
| `num_processors` | required | Maximum parallelism (OpenMP threads per node). |
| `storage_backend` | `ladybug` | `ladybug` (out-of-core memory-mapped) or `legacy` (in memory). |
| `db_path` | `./ladybug_data` | Storage directory; use fast node-local storage. |
| `use_distributed` | `false` | Distributed mode; switched on automatically under MPI with more than one rank. |
| `ghost_hub_threshold` | 100 | In-degree at or above which a paper's data is replicated on every rank as a read-only ghost cell (distributed mode). |
| `wall_clock_limit` | 0 | Slurm limit in seconds, 0 for none. With a limit set, the run finishes the current year, commits a checkpoint and exits cleanly when time runs short. |

## 5. How the options interact

### 5.1 The cluster route

If `alpha` is above 0 and the generator's cluster has at least `theta` members, distance 1 is the whole cluster
(uncapped) and distance 2 is pruned to papers outside the cluster. The fraction of citations that stay inside a cluster
is then about the mean alpha. Clusters smaller than `theta` use the ordinary neighborhood rule. Only labelled clusters of
`theta` or more seed papers (and the agents that join them) use the route, so the number of such clusters limits its
reach: 64 of the 5,542 Leiden clusters in the tested label file have 50 or more papers. New papers inherit their
generator's cluster.

With `unbinned_age_sampling=true`, the CantataS cached-bin fast path for clusters is switched off, so the cluster route
works on the unfiltered cluster pool.

### 5.2 Age

Binned sampling (the default) assigns each citation to a recency bin; an empty bin's quota moves to the nearest younger
bin. Unbinned sampling draws exact ages from the table, which reproduces the table's age profile closely. The recency
table sets only the age distribution; it is not used to dampen preferential attachment (a factor shared by every
candidate in an age bin cancels on normalization).

### 5.3 Weights

With the four fixed weights, or `-1` for random, behavior is that of CantataS. With the `*_weight_mean` options, each
agent's weights come from a Dirichlet distribution, so the population has a controlled average mix and a spread set by
`weight_concentration`. Raising `fit_weight_mean` breaks the dominance of old seed hubs but increases inequality and the
number of uncited papers and of very high in-degree agents.

### 5.4 Choosing `theta`, alpha and the labels

- Choose `theta` so that clusters with at least `theta` papers cover roughly 35 to 45% of the seed papers.
- Labels from a network clustering (Leiden CPM) gave much more community structure in the output than field labels did,
  and a bounded alpha (0.55 to 0.95) strengthened this only with the network-derived labels.
- Keep `theta` below the size of the clusters you want to act on and above the noise floor of tiny clusters.

## 6. Output files

- `output_file`: the generated edgelist, seed edges included; no duplicate edges, no self-citations, and a source is never
  older than its target.
- `auxiliary_information_file`: one row per paper with, among other columns, `node_id`, `type` (`seed` or `agent`),
  `year`, `in_degree`, `cluster_id` and the four weights (`pa_weight`, `fit_weight`, `num_authors_weight`,
  `author_reputation_weight`). Agents also carry their drawn fitness parameters.
- `log_file`: per-year timings and, at `log_level=1`, the settings in effect (exponents, offset, generator eligibility and
  pool, generator-mode line).
- A checkpoint (`manifest.json` plus the memory-mapped files) is committed in `db_path` after each year.

## 7. Recipes

**CantataS behavior.** Leave every ARCANA and INSTAR option unset: `unbinned_age_sampling` false, no `*_weight_mean`, no
alpha bounds, exponents and offset at their defaults, `generator_eligibility=and`, `generator_pool=all`.

**ARCANA as tested.** `unbinned_age_sampling=true`; `pa_weight_mean=0.05`, `fit_weight_mean=0.95`, `na_weight_mean=0`,
`ar_weight_mean=0`, `weight_concentration=50`; `alpha=-1`; `theta=50`; `community_assignment` pointing at a Leiden CPM
label file.

**Emphasize within-cluster citing.** Add `minimum_alpha=0.55` and `maximum_alpha=0.95`.

**Turn the cluster route off.** `theta=1000000`.

**Non-random generators.** `non_random_generator_probability=0.5` with `generator_eligibility=or` or `and`, and
`generator_pool` as wanted.

**Size matching.** The sample runs 40 cycles at 10% growth from a 26,686-paper seed set and ends near 1.2 million papers.

## 8. Verification status

- Single-node runs are the verified path. With the CantataS fix for rank-0 attribute synchronization merged in, two
  4-node MPI replicates at `theta=50` reproduce single-node behavior (within-cluster citation fraction 49.6% and 49.7%
  against 49.7%). `theta` above the largest cluster under MPI is untested.
- The INSTAR options (4.3 and 4.5) were merged from the archived CANTATAS-INSTAR repository. At their defaults they
  reproduce the single-node replicates (within-cluster fraction 49.69% against 49.66%, seed share of new citations 4.49%
  against 4.48%); a run with non-random generators at 0.5, `generator_eligibility=or` and `generator_pool=agents_eligible`
  shows the options taking effect. Each was one replicate; see [PROVENANCE.md](../PROVENANCE.md).
- All results use one seed set (26,686 papers). A setup with a 13.9M-paper seed network has not been tested.
