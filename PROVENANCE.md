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

## Results so far (single replicate unless noted; replicates r1 and r2 of the last two rows were still running)

Seed share is of new citations (final in-degree minus the in-degree from the seed network), against a paper share of 2.21%.

| run | seed share | seeds with in-degree >= 1000 | agent max in-degree |
|---|---|---|---|
| baseline (original bins `1,2,3,4,5,10,20,30`) | 3.05% | 63 | 281,954 |
| revised bins | 3.05% | 59 | 207,718 |
| revised bins, max age 10 | 1.64% | 42 | 191,327 |
| revised bins, soft table cutoff | 2.22% | 38 | 238,607 |
| unbinned | 4.51% | 92 | 81,784 |
| unbinned, weights (pa 0.05, fit 0.95, concentration 50) | 4.46% | 33 | 148,062 |
| unbinned, weights, theta 1,000,000 | 5.03% | 24 | 72,052 |

Seed hubs are suppressed by fitness-heavy weights; the seed share is not. Theta 1,000,000 turns off the cluster route and
ran in 42 s against about 590 s.

## Authorship

Model design and direction: George Chacko. Base simulator: Hemank Kohli and OR Research Analytics. Implementation of
the changes above was done with Claude (Anthropic).
