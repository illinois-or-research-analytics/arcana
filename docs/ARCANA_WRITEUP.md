# ARCANA: Age-Resolved Community-Aware Network Agents

Draft, 2026-11-03. Status: research prototype. All results are from single-node runs on one seed set; see
[Limitations](#limitations-and-scope) before relying on any number here.

## Summary

ARCANA extends CantataS, an agent-based model of citation-network growth, with two changes: citations are placed by
drawing the age of the cited paper from an empirical recency distribution (no recency bins), and each agent's score
weights are drawn around user-specified expected values. With the tested settings ARCANA reproduces the target
citation-age profile and lets a fitness-heavy weighting break up the hub effect of old, highly cited seed papers. It
does not generate community structure of high quality, and its settings have to be tuned for each seed set and for the
conditions of the run.

## 1. Motivation

In earlier CantataS runs a handful of old seed papers kept receiving a large share of citations, because in-degree drives
preferential attachment and the oldest, most cited papers keep appearing in candidate pools. Dampening the in-degree
score by age did not help (Section 4), and the recency bins made the age profile depend on rounding and on a sweep that
moved the quota of an empty bin to its nearest younger bin. ARCANA separates two jobs that the bins mixed: the age
distribution decides how many citations land at each age, and the score decides which paper at that age is cited.

## 2. The model

Each new paper (agent) is built in this order.

1. A generator paper is chosen (uniformly over all papers by default) and cited.
2. The agent gets an out-degree quota. One edge cites the generator, up to one is a same-year citation, and 5% is
   reserved for fully random citations anywhere in the graph.
3. Of the remainder, a fraction `alpha` goes to distance-1 candidates and the rest to distance 2. If the generator's
   cluster has at least `theta` members, distance 1 is the whole cluster and distance 2 is restricted to papers outside it;
   otherwise each distance is the generator's neighborhood, down-sampled to `neighborhood_sample` (10,000).
4. Candidates are scored on in-degree, fitness, author count and author reputation using the agent's own weights, and
   chosen without replacement. Quota that cannot be filled at a distance cascades to distance 2 and then to random.

### What ARCANA changes

- **Unbinned age sampling.** Each citation draws an age from the recency table used as a per-year distribution, restricted
  to ages that still have unused candidates; candidates of that age are then scored. An age with no candidates passes its
  probability to the other ages in proportion to the table, so nothing piles up at one age.
- **Expected-value weights.** The four score weights (preferential attachment, fitness, author count, author reputation)
  are drawn per agent from a Dirichlet distribution with specified means and a concentration. The weights sum to 1, each
  has the specified expected value, and a mean of 0 keeps a weight at 0.

## 3. Setup

Seed set: 26,686 papers and 273,490 edges (`mf_seed_v3`), 40 cycles at 10% growth, 1,208,027 papers at the end. Three
configurations with three independent replicates each: unbinned age sampling with the original random weights;
unbinned with weights (pa 0.05, fitness 0.95, author count 0, author reputation 0, concentration 50); and the same with
`theta = 1,000,000`, which turns off the cluster route. Multiscale readout: micro (papers), meso (Leiden clusters at
resolution 0.1, IKC cores at k = 20) and macro (inequality, clustering, triangles). Mean ± standard deviation over
replicates unless stated. Stochastic runs agree on the major trends; micro-level details such as the single most-cited
paper differ between replicates and are not interpreted.

## 4. Results

**Recency.** Citations to ages 1–4, 20–29 and 30+ are 35.7%, 8.3% and 1.1% (target table 35.2%, 9.0% and 0.8%). The binned
runs gave 39.5% at ages 1–4 and 5.0% at ages 20–29.

**Negative results that shaped the design.** Scaling the in-degree by age had no effect, because a factor shared by every
candidate at an age cancels inside the age quota. Lowering the preferential-attachment exponent with age also had no
measurable effect on seed share. A hard cutoff on citable age lowered the seed share of new citations (3.05% to 1.64%,
one run) but piled 24.9% of all citations onto papers exactly 10 years old.

**Weights and hubs.** Seeds with in-degree of 1,000 or more fall from 93.7 ± 2.9 (original weights) to 35.0 ± 2.0 (pa 0.05)
and 24.3 ± 1.5 (pa 0.05, theta 1M). The seed share of new citations does not change (4.51% to 4.44% at theta 50). The
costs are visible at every scale:

| measure | unbinned | + weights | + weights, theta 1M |
|---|---|---|---|
| Gini of citations | 0.862 to 0.866 | 0.915 | 0.824 to 0.826 |
| uncited after 2 years | 26% | 41.5% | 24.7% |
| agents with in-degree > 50,000 | 18.3 ± 1.2 | 36.3 ± 1.5 | 7.7 ± 4.6 |
| old papers (age 10+) still cited | 33 to 34% | 25% | 47.7% |
| citation variation explained by traits | 31 to 33% | 24.7% | 16% |

**Community structure.** No setting yields a Leiden cluster with conductance below 0.5; the median conductance of
clusters of 10 or more papers is 0.92 (theta 50) and 0.81 (theta 1M). At theta 50 about half of agent citations stay
inside the model's own cluster labels, yet only 2% of papers fall in a Leiden cluster of 10 or more, against 63% at theta 1M.
The labelled communities are barely recoverable from the resulting network. We have not established why.

## Limitations and scope

**Settings must be optimized for each seed set and each set of running conditions.** Nothing here should be read as a
recommended default. The values used (weights, concentration, theta, alpha, the neighborhood cap, the fitness
range, the recency table, the growth rate and the number of cycles) interact, and the evidence that they matter is already
in the results: moving from theta 50 to theta 1M changes the seed share, the age profile, the within-cluster fraction,
the inequality and the number of detectable communities, and the fitness-heavy weights trade fewer hubs for more
inequality and more uncited papers. Specifically:

- **Seed set.** Everything was run on one seed set in which seeds are 2.2% of papers at the end. In a setup with a
  13.9M-paper seed network and 15 cycles at 3% growth, seeds are about 64% of papers and the generator is usually a seed,
  so the generator route alone would anchor most new papers in the old literature. These results do not transfer to
  that case. It has not been run with ARCANA.
- **Growth and size.** The recency table gives a share of citations per age, not a per-paper rate, so the age profile that
  results depends on how fast the network grows. Changing growth rate or the number of cycles requires re-checking it.
- **Calibration.** The weights, concentration, theta and alpha should be chosen for each application by sweeping them,
  running at least three replicates per setting, and judging on the multiscale readout against the properties that
  matter for that application, not on one outcome measure.
- **Verified mode.** Only single-node (shared-memory) runs have been verified. The MPI distributed mode shares the code
  but has not been checked for the ARCANA changes.

## Planned work

Sensitivity testing of the settings listed above; ARCANA on the large seed network; a closer look at why labelled
communities are not recoverable; verification of distributed mode; and a data-retention manifest so that the protocol
and results of a run can be kept while raw networks are deleted.

## Provenance

Built on the upstream CantataS branch `hkohli/optimizations` at commit c69b316, with one commit per change; see
[PROVENANCE.md](../PROVENANCE.md) for the changes, run directories and configs. Model design and direction: George
Chacko. Base simulator: Hemank Kohli and OR Research Analytics. Implementation and analysis support: Claude (Anthropic).
