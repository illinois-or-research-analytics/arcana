# ARCANA

**A**ge-**R**esolved **C**ommunity-**A**ware **N**etwork **A**gents: an agent-based model of citation-network growth,
derived from [CantataS](https://github.com/illinois-or-research-analytics/cantatas). Status: research prototype, private,
single-node runs only.

## Relationship to CantataS

CantataS is the reference model: it must run in shared-memory and distributed (MPI) mode, and fixes to the core model
are made there first and then brought into ARCANA. ARCANA is an experimental extension that may be merged back into
CantataS one day. To keep that possible, every ARCANA change is gated by a config option that is off by default and sits
in its own commit (see [PROVENANCE.md](PROVENANCE.md)).

## What is different from CantataS

1. **Unbinned age sampling** (`unbinned_age_sampling=true`). Each citation draws the age of the cited paper from the
   recency table used as a per-year distribution, restricted to ages that still have candidates in the pool, then
   scores the candidates of that age and samples without replacement. This replaces the recency bins, the rounding of
   per-bin quotas and the sweep that moved the quota of an empty bin to its nearest younger bin. An age with no
   candidates passes its probability to the other ages in proportion to the table.
2. **Expected-value agent weights** (`pa_weight_mean`, `fit_weight_mean`, `na_weight_mean`, `ar_weight_mean`,
   `weight_concentration`). Each agent draws its four score weights from a Dirichlet distribution with the given means
   (rescaled to sum to 1) and total concentration. Larger concentration keeps agents closer to the means; a mean of 0
   keeps that weight at exactly 0.

3. **Bounded random alpha** (`minimum_alpha`, `maximum_alpha`, only with `alpha=-1`). Each agent's alpha is drawn uniformly
   on `[minimum_alpha, maximum_alpha]` (3 decimals) instead of on [0, 1]. With the cluster route on, the within-cluster
   citation fraction is about the mean alpha, so `0.55` to `0.95` emphasizes intra-cluster citations. Setting either bound
   with a fixed alpha is an error.

All three are off by default, so a CantataS config runs as before. Experimental options that did not help (age damping of the
PA score, recency-biased neighborhood sampling, a hard `max_citable_age`) are kept, off by default, for provenance. See
[PROVENANCE.md](PROVENANCE.md).

## Agent life cycle (as run here)

1. A generator node is chosen (uniformly over all papers, or from the eligible set) and cited.
2. The agent gets an out-degree quota. One edge cites the generator, up to one is a same-year citation, and 5% is
   reserved for fully random citations.
3. Of the remainder, `alpha` goes to distance-1 candidates and the rest to distance 2. If the generator's cluster has at
   least `theta` members, distance 1 is replaced by the whole cluster and distance 2 is pruned to papers outside it.
   Otherwise each distance is the generator's neighborhood, down-sampled to `neighborhood_sample` (10,000).
4. Candidates are scored on in-degree, fitness, author count and author reputation with the agent's own weights, and
   chosen without replacement. Unfilled quota cascades from distance 1 to distance 2 to random.

## Building and running

Same build as CantataS (CMake, GCC 13, OpenMPI). The runs reported in [PROVENANCE.md](PROVENANCE.md) use
`use_distributed=false`, the LadyBugDB backend and 32 OpenMP threads on one node. See `experiments/configs/` and
`experiments/batch_script.run.example`; paths in the configs point at the Illinois Campus Cluster.

**Distributed (MPI) mode is not verified for the ARCANA changes.** The changes sit in code shared by both modes. A 4-node
MPI run completes and passes integrity checks, but with `theta=50` its within-cluster citation fraction is 40.7% against
49.7% on one node. This is traced to per-rank cluster member lists (see issue #1); the fix is being made in CantataS first.

## Caveat

All results so far use one seed set (26,686 seed papers, 10% growth for 40 cycles). A setup with a 13.9M-paper seed
network, where seeds are most of the graph and the generator is usually a seed, has not been tested with these changes.

## License

MIT, inherited from CantataS (see `LICENSE`).
