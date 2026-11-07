# ARCANA: 4-node MPI run vs single-node run (theta 50)

Date: 2026-11-03. Code: `illinois-or-research-analytics/arcana`, `main` at b088a2b (built from
`illinoiscomputes/arcana/arcana_code`). Status: the hypothesis in the last section is from reading the code and has not been tested.

## Setup

Same `config.ini` for every run (copied; checked with `cmp`): seed set `mf_seed_v3` (26,686 papers), 40 cycles at 10% growth,
`theta=50`, `alpha=-1` (random per agent), `unbinned_age_sampling=true`, expected-value weights pa 0.10 / fit 0.70 /
author count 0.10 / author reputation 0.10, `weight_concentration=50`, `use_distributed=false` in the file (MPI turns on
automatically with more than one rank). Single node: 1 node, 32 OpenMP threads, no `mpirun`. MPI: 4 nodes, `mpirun -n 4`.
Three independent replicates each (the generator is seeded from `std::random_device`). Directories under
`/projects/illinois/eng/cs/chackoge/illinoiscomputes/arcana/`: `small_sim_test_baseline_single[_r1,_r2]` and
`small_sim_test_baseline_mpi[_r1,_r2]`.

## Results

All six runs: 1,208,027 papers, integrity checks pass (unique ids, no duplicate edges, no self loops, no edge pointing
forward in time, in-degree matches the edge list, seed edges present), agent weight means 0.1 / 0.7 / 0.1 / 0.1 with every
agent's weights summing to 1. Edge counts differ between runs, as expected for stochastic runs.

| run | job time | seed share of new citations | seeds ≥ 1,000 | agents > 50,000 | agent top 0.1% median | agent max | within-cluster fraction |
|---|---|---|---|---|---|---|---|
| single r0 | 10:01 | 4.50% | 56 | 16 | 3,727 | 131,306 | 49.65% |
| single r1 | 6:36 | 4.48% | 48 | 30 | 3,516 | 117,446 | 49.68% |
| single r2 | 10:38 | 4.45% | 50 | 25 | 3,547 | 121,549 | 49.66% |
| MPI r0 | 7:00 | 4.55% | 46 | 18 | 2,907 | 117,299 | 40.57% |
| MPI r1 | 3:20 | 4.56% | 53 | 17 | 2,823 | 115,441 | 40.57% |
| MPI r2 | 7:43 | 4.57% | 57 | 17 | 2,755 | 108,954 | 40.87% |

Mean ± standard deviation over the three replicates:

| measure | single node | 4-node MPI | verdict |
|---|---|---|---|
| **within-cluster citation fraction (agent sources)** | 49.66 ± 0.02% | **40.67 ± 0.17%** | real difference |
| **agent top 0.1% median in-degree** | 3,597 ± 114 | **2,828 ± 76** | real difference (about 21% lower) |
| seeds with in-degree ≥ 1,000 | 51.3 ± 4.2 | 52.0 ± 5.6 | same |
| seed share of new citations | 4.48 ± 0.02% | 4.56 ± 0.01% | tiny gap (0.08 points) |
| agents with in-degree > 50,000 | 23.7 ± 7.1 | 17.3 ± 0.6 | overlapping |
| agent maximum in-degree | 123,434 ± 7,120 | 113,898 ± 4,381 | overlapping |
| citations to ages 1–4 | 36.01 ± 0.08% | 35.93 ± 0.05% | very close |
| citations to ages 20–29 | 8.12 ± 0.06% | 8.34 ± 0.02% | small but consistent gap |
| job time | 6.6 to 10.6 min | 3.3 to 7.7 min | MPI about 1.5× faster on average (wide range) |

The seed-hub gap seen in the first pair (56 vs 46) did not hold up across replicates. The within-cluster fraction is
the clearest difference: with theta 50 and alpha random it should be near the mean alpha (about 50%, the single-node value),
and the MPI value is about 9 points lower. It is also below the value with cluster-aware citing off (about 64%, theta 1,000,000, single node), so it is not
a simple on/off switch.

## Hypothesis (from reading the code; not tested)

Cluster-aware citing (`src/abm.cpp:1281`) replaces distance 1 with all members of the generator's cluster and prunes distance 2
to papers outside it. Its pool comes from per-rank cluster member lists. Under MPI those lists look inconsistent on ranks 1–3:

1. On every rank, each new paper's generator is drawn from that rank's own random stream, and
   `UpdateGraphAttributesGeneratorNodes` (`src/abm.cpp:317`) sets the paper's cluster from that generator and calls
   `AddNodeToCluster(new_node, cluster_id)` (`src/abm.cpp:335`).
2. Rank 0's generator, cluster and author assignments are then broadcast (`BroadcastNewNodeMetadata`, `src/abm.cpp:1130`).
   Ranks 1–3 overwrite the paper's cluster with rank 0's and call `AddNodeToCluster(n, cluster_ids[i])` again
   (`src/abm.cpp:1141`), without removing the paper from the cluster its own draw chose.
3. So on ranks 1–3 a new paper is a member of two clusters' lists, usually different ones (the generator is uniform over all
   papers). Agents are simulated only on the rank that owns their cluster (`src/abm.cpp:1239`), so most agents are simulated
   on ranks with polluted pools.
4. Final cluster labels come from rank 0, so citations that go to the wrongly listed papers count as cross-cluster. That would
   lower the within-cluster fraction, as observed.

A second, related effect: each rank draws its own agent weights, and the weight columns in the output come from rank 0. For
agents simulated on other ranks, the recorded weights may not be the ones used. The distribution is the same, so the
weight statistics above do not reveal it.

## Proposed test

On non-master ranks, skip the member-list update in `UpdateGraphAttributesGeneratorNodes` until the broadcast has arrived
(or remove the stale entry before adding the broadcast cluster), then rerun the MPI configuration with three replicates.
If the within-cluster fraction returns to about 49.7% (and the agent tail median to about 3,600), the explanation holds. A
second check: log the member count of a few clusters on each rank after the broadcast and compare with rank 0.

## Not checked

Theta 1,000,000 (cluster-aware citing off) under MPI; larger networks; whether ghost-cell and in-degree synchronization across ranks
has other effects; the nodelist weight columns under MPI.
