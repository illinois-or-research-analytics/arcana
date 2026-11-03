# Provenance

## Base

- Upstream: `illinois-or-research-analytics/cantatas`, branch `hkohli/optimizations`, commit `c69b316`
  ("[Optimizations] Tweaked data structures for faster execution", Hemank Kohli, 2026-11-01).
- License: MIT (copyright OR_Research_Analytics), unchanged.
- The `includes/` and `src/` trees on the cluster build used for all baseline runs
  (`/u/chackoge/scratch/cantatas`) were identical to this commit.

## Changes, in order (one commit each)

Each change was made in its own copy of the source on the Illinois Campus Cluster and used for the runs listed.
Commits here are the diffs between those copies; the final tree equals the `cantatas_weights` copy.

| commit | cluster source copy | option (default off) | used for | outcome |
|---|---|---|---|---|
| 1 | `cantatas_damp` | `age_damping_start`, `age_damping_tau` | `small_sim_test_baseline_bins_damp` | no effect (a shared factor cancels within an age bin) |
| 2 | `cantatas_recency` | `age_damping_min_exponent`, `neighborhood_recency_lambda`, `neighborhood_prepool_factor` | `..._bins_expdamp` (the sampling option was never run) | exponent damping: no effect on seed share |
| 3 | `cantatas_maxage` | `max_citable_age` | `..._bins_maxage10` | seed share of new citations 3.05% to 1.64%, with a pile-up at age 10 |
| 4 | `cantatas_unbinned` | `unbinned_age_sampling` | `..._unbinned` | age profile matches the table |
| 5 | `cantatas_weights` | `pa/fit/na/ar_weight_mean`, `weight_concentration` | `..._unbinned_w5`, `..._w5_t1m` | see below |

Run directories are in `/u/chackoge/scratch` on the cluster (prefix `small_sim_test_baseline`); configs are in
`experiments/configs/`. The `soft10` run used the original code with a modified recency table
(`recency_table` counts for ages over 10 multiplied by exp(-(age-10)/5)).

## Common run settings

Seed set `mf_seed_v3` (26,686 papers, 273,490 edges), `growth_rate=0.1`, `num_cycles=40`,
`recency_bins=1,2,3,4,5,10,15,20,25,30,35,40,45,50` (binned runs), `theta=50`, alpha random, `neighborhood_sample=10000`,
`use_distributed=false`. Runs are independent: the generator is seeded from `std::random_device`.

## Results

Seed share is of new citations (final in-degree minus the in-degree from the seed network), against a paper share of
2.21%. Replicated rows are mean ± standard deviation over three independent replicates (r0, r1, r2; the generator is
seeded from `std::random_device`, so replicates are independent but a run cannot be reproduced bit for bit). Stochastic
runs agree on the major trends; micro-level details such as the single most-cited paper differ between replicates and
should not be interpreted.

### Replicated (3 runs each)

| measure | unbinned | unbinned + weights (theta 50) | unbinned + weights, theta 1,000,000 |
|---|---|---|---|
| seed share of new citations | 4.51 ± 0.01% | 4.44 ± 0.03% | 5.04 ± 0.01% |
| seeds with in-degree >= 1000 | 93.7 ± 2.9 | 35.0 ± 2.0 | 24.3 ± 1.5 |
| seed top 0.1% median in-degree | 5,025 ± 320 | 1,690 ± 50 | 1,569 ± 51 |
| agents with in-degree > 50,000 | 18.3 ± 1.2 | 36.3 ± 1.5 | 7.7 ± 4.6 (13, 5, 5) |
| agent top 0.1% median in-degree | 2,890 ± 61 | 4,187 ± 102 | 3,820 ± 85 |
| agent maximum in-degree | 83,303 ± 1,374 | 138,963 ± 7,899 | 98,874 ± 29,079 |
| citations to ages 1-4 / 20-29 / 30+ | 35.7 / 8.3 / 1.1% | 36.4 / 7.9 / 1.1% | 30.1 / 10.4 / 2.0% |
| within-cluster citation fraction (agent sources) | 49.7% | 49.7% | 64.4 ± 0.6% |
| run time | about 10 min | about 10 min | about 1 min |

Multiscale readout (`multiscale.py report`, ranges over three replicates; full table in the cluster file
`deltacon_testing/multiscale_results/report_arcana_unbinned_w5.md`; all integrity checks pass):

| measure | unbinned | + weights | + weights, theta 1M |
|---|---|---|---|
| Gini of citations | 0.862 to 0.866 | 0.915 | 0.824 to 0.826 |
| top 1% of cited papers' share of citations | 54 to 56% | 69% | 53% |
| tail exponent | 2.0 | 1.8 | 1.85 |
| never cited | 18.2 to 18.4% | 24.5% | 16.5% |
| uncited after 2 years | 26% | 41.5% | 24.7% |
| old papers (age 10+) still cited | 33 to 34% | 25% | 47.7% |
| higher fitness wins head-to-head | 0.64 | 0.83 | 0.76 |
| citation variation explained by traits | 31 to 33% | 24.7% | 16% |
| Leiden clusters of 10+ papers (papers in them) | about 1,200 (2%) | about 1,350 (2.3%) | about 50,000 (63%) |
| median conductance of those clusters | 0.916 | 0.916 | 0.805 |
| mean local clustering | 0.02 | 0.04 | 0.127 |

Reading: the fitness-heavy weights (pa 0.05, fitness 0.95, concentration 50) cut the number of seed hubs roughly in
three but also increase inequality and the share of uncited papers. Theta 1,000,000 turns off the cluster route:
it is about ten times faster, less concentrated, has more local closure and far more detectable Leiden communities, but a
higher seed share. No setting gives well-separated communities (no cluster has conductance below 0.5).

### Single replicate (earlier runs)

| run | seed share | seeds with in-degree >= 1000 | agent max in-degree |
|---|---|---|---|
| baseline (original bins `1,2,3,4,5,10,20,30`) | 3.05% | 63 | 281,954 |
| revised bins | 3.05% | 59 | 207,718 |
| revised bins, max age 10 | 1.64% | 42 | 191,327 |
| revised bins, soft table cutoff | 2.22% | 38 | 238,607 |

## Authorship

Model design and direction: George Chacko. Base simulator: Hemank Kohli and OR Research Analytics. Implementation of
the changes above was done with Claude (Anthropic).
