# Seed network `mf_seed_v3`

The seed set behind every result in `results/` (26,686 nodes, 273,490 citations).

| file | columns | rows |
|---|---|---|
| `seed_nodelist_v3.csv` | `node_id,year` | 26,686 |
| `seed_edgelist_v3.csv` | `source,target` (`source` cites `target`) | 273,490 |

**Provenance.** The network was derived from Dimensions (Digital Science) data. Dimensions publication identifiers were replaced by integer ids (`node_id`),
and only the citation edges and publication years were kept. The files contain no titles, abstracts, DOIs, author or journal information. The lookup table
from integer ids back to Dimensions identifiers is not released.

`MD5SUMS` holds the checksums of the files used for the runs on the Illinois Campus Cluster (`md5sum -c MD5SUMS`).

The community-label files in `results/reference_set_2026-11-07/labels/` (`node_id,cluster_id`) refer to these `node_id`s. `docs/inputs.tar.gz` is a different, older and larger
seed set (491,532 nodes) and is not the one behind these results.
