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
   on `[minimum_alpha, maximum_alpha]` (3 decimals) instead of on [0, 1]. With cluster-aware citing on, the within-cluster
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

## Results

The first reference set (nine runs: three Leiden label resolutions, three replicates each) is documented in
[results/reference_set_2026-11-07](results/reference_set_2026-11-07/README.md), with its data, scripts and a description of how the numbers were
generated.

The effect of non-random generator selection (six further runs, with a uniform-generator control) is in
[results/generator_selection_2026-11-07](results/generator_selection_2026-11-07/README.md).

The same designs repeated with equal scoring weights (0.25 each; 18 runs, the reference set going forward), with a master table and a one-factor-at-a-time study of the fit weight,
`theta` and generator selection, are in [results/weights_equal_2026-11-08](results/weights_equal_2026-11-08/README.md). The two earlier folders above were run at the earlier default weights (fit 0.70).

Experiments that plant one or three extremely fit nodes (supernodes) and ask where their citations come from, with the 87 planted nodes and the controls tabulated, are in
[results/planted_nodes_2026-11-08](results/planted_nodes_2026-11-08/README.md).

## Data provenance

The seed network used for all results is in [inputs/mf_seed_v3](inputs/mf_seed_v3/README.md): integer node ids, citation edges and publication years, derived
from Dimensions data. No titles, abstracts, DOIs or author information are included, and the table mapping the integer ids back to Dimensions identifiers is not released.

## Building and running

Every configuration option, the input file formats and how the options interact are described in the
[user manual](docs/USER_MANUAL.md); `config.sample.ini` carries no comments.

Same build as CantataS (CMake, GCC 13, OpenMPI). The runs reported in [PROVENANCE.md](PROVENANCE.md) use
`use_distributed=false`, the LadyBugDB backend and 32 OpenMP threads on one node. See `experiments/configs/` and
`experiments/batch_script.run.example`; paths in the configs point at the Illinois Campus Cluster.

**Distributed (MPI) mode:** with the CantataS fix for rank-0 attribute synchronization merged in (issue #1), a 4-node MPI run
reproduces single-node behavior with `theta=50`: within-cluster citation fraction 49.6% and 49.7% in two replicates against
49.7% on one node, and the same agent tail, age profile and weights. Both unmerged MPI and single-node were checked on one seed
set only; `theta` above the largest cluster (cluster-aware citing off) under MPI has not been tested. When `unbinned_age_sampling` is on,
the cached-bin cluster fast path from CantataS is switched off.

## Caveat

All results so far use one seed set (26,686 seed papers, 10% growth for 40 cycles). A setup with a 13.9M-paper seed
network, where seeds are most of the graph and the generator is usually a seed, has not been tested with these changes.

## License

MIT, inherited from CantataS (see `LICENSE`).
