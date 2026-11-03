# CantataS: Community-Aware Agent-Based Citation Simulator

The **Community-aware agent-based citation Simulator (CantataS)** is a high-performance network growth model built on top of SASCA-ReSA. CantataS simulates large-scale scientific citation dynamics, author lifecycles, and research community formation over decades of simulated time.

Version 8.0 introduces **LadyBugDB** (an embedded, out-of-core memory-mapped columnar storage engine), **SIMD AVX2 vectorized preference scoring**, **O(1) Vose Alias random sampling**, and **Distributed Multi-Node MPI Execution** designed specifically for high-performance supercomputing clusters (such as the Illinois Campus Cluster / NCSA).

---

## Recent Changelogs

### 8.0.0 (High-Performance HPC & Distributed Engine)
- **LadyBugDB Storage Engine**: Replaced in-memory pointer graphs with contiguous NVMe memory-mapped Struct-of-Arrays (SoA) columnar tables (`nodes/`, `graph/`, `clusters/`, `authors/`), eliminating RAM exhaustion for 100M+ node graphs with zero page-cache bloat.
- **Lock-Free Bidirectional CSR**: Forward CSR ($u \to v$) for $O(1)$ out-neighbor traversals, backward CSR ($v \leftarrow u$) for fast in-degree and reputation tracking, and thread-local lock-free delta incoming citation accumulation during the active simulation year.
- **Distributed MPI Execution**: Shards citation networks across compute nodes along dense Leiden community boundaries (`DistributedPartitioner`). Keeps ~90% of intra-field citation generation purely local.
- **Ghost Cell & Halo Caching**: Replicates top in-degree foundational papers locally as read-only ghost cells (`GhostCellManager`), eliminating network round-trips for high-traffic citation hubs.
- **BSP Annual Supersteps via RDMA**: Routes cross-partition citations at annual boundaries using batched non-blocking `MPI_Alltoallv` and columnar buffers (`ActorExchange`).
- **Zero-Bloat Transactional Checkpointing & Slurm Supervisor**: Wall-clock supervisor and POSIX signal trapping (`SIGTERM`, `SIGUSR1`, `SIGINT`) via `SignalSupervisor`, guaranteeing clean annual checkpoint commits (`manifest.json`) before Slurm wall-time expiration.
- **SIMD AVX2 Scoring & Vose Alias Sampling**: Multi-component preference calculation vectorized with AVX2/FMA, coupled with $O(1)$ Vose Alias weighted random sampling tables and fast bitset rejection tracking.
- **Comprehensive Test Suite**: 100% pass rate across 9 standalone CTest targets verifying memory mapping, node stores, CSR, database commits, partitioning, and distributed exchange.

### 7.0.4
- Fixes current year nodes leaking into the alpha intra-cluster citations.

### 7.0.3
- Fixes removal of duplicate edges within cluster.

### 7.0.2
- Fixes alpha value not showing correctly in auxiliary file.

### 7.0.1
- Fixes a memory management issue causing abrupt exit codes.

### 7.0.0
- Allows for cluster-based citations (CantataS).

---

## High-Performance Architecture Overview

CantataS 8.0 decomposes the simulation lifecycle into modular, zero-copy components:

```
                          +-------------------------------------------------+
                          |             ClusterCoordinator (MPI)            |
                          |  - Manages rank topology & collective barriers  |
                          |  - Executes annual BSP superstep reductions     |
                          +-----------------------+-------------------------+
                                                  |
           +--------------------------------------+--------------------------------------+
           |                                                                             |
           v                                                                             v
+-----------------------+                                                     +-----------------------+
|     Compute Rank 0    |                                                     |     Compute Rank 1    |
| (Leiden Partition A)  |                                                     | (Leiden Partition B)  |
|                       |                                                     |                       |
| LadyBugDB (Mmap SoA): |                                                     | LadyBugDB (Mmap SoA): |
| - LadyBugNodeStore    | <========== MPI_Alltoallv (ActorExchange) =========>| - LadyBugNodeStore    |
| - LadyBugCSR (Fwd/Bwd)|   Annual Cross-Partition Citation Edge Exchange     | - LadyBugCSR (Fwd/Bwd)|
| - GhostCellManager    |                                                     | - GhostCellManager    |
| - SignalSupervisor    |                                                     | - SignalSupervisor    |
| - Atomic Checkpoint   |                                                     | - Atomic Checkpoint   |
+-----------------------+                                                     +-----------------------+
```

### 1. LadyBugDB Embedded Storage Engine
- **`LadyBugNodeStore`**: Contiguous columnar memory-mapped files for node attributes (publication year, node type, author ID, community cluster ID, in/out degrees, preference weights, and fitness decay parameters). Provides zero-copy `std::span` access for SIMD kernels.
- **`LadyBugBidirectionalCSR`**: 
  - Forward CSR: Enables dynamic $O(1)$ appends of outgoing citations per newly injected paper.
  - Backward CSR: Stores incoming citations for fast in-degree evaluation and dynamic author reputation calculations.
  - Delta Buffer: Thread-local lock-free buffers accumulate incoming citations during the active year and merge in parallel at the annual superstep boundary.
- **`LadyBugClusterIndex`**: Inverted index of Leiden community partitions supporting fast $O(\log K)$ year-bounded cluster size lookups for $\theta$ thresholding.
- **`LadyBugAuthorStore`**: Tracks author publication histories, birth years, and dynamic $h$-index reputations governed by Lotka's Law and cartel syndicates.
- **`LadyBugJournal`**: Binary delta journal capturing all mutations with zero-bloat automatic truncation upon successful annual commit.

### 2. Distributed MPI Coordination
- **`DistributedPartitioner`**: Assigns Leiden research communities to MPI compute ranks to balance node counts while minimizing inter-partition boundary edges.
- **`GhostCellManager`**: Replicates foundational high-degree papers (in-degree $\ge$ `ghost_hub_threshold`) locally as read-only ghost cells, eliminating cross-rank RPCs for universal citation hubs.
- **`ActorExchange`**: Conducts batched columnar transfers via `MPI_Alltoallv` and implements low-alpha remote pre-sampling ($k = 10{,}000$) to bound candidate generation traffic to $\sim 40\text{ KB}$ per boundary agent.
- **`ClusterCoordinator`**: Orchestrates annual Bulk Synchronous Parallel (BSP) supersteps, collective barriers, and parallel checkpoint commits.

### 3. Slurm Wall-Clock Supervisor & Atomic Recovery
- **`SignalSupervisor`**: Automatically registers POSIX signal handlers (`SIGTERM`, `SIGUSR1`, `SIGINT`) and tracks elapsed Slurm wall-clock time against a user-configured limit with a safety margin (default 20 minutes). If triggered, the simulator gracefully pauses at the next annual boundary, flushes all buffers, commits the checkpoint, and exits cleanly with exit code 0.
- **Atomic Checkpointing**: Checkpoints update columnar files and write an atomic `manifest.json`. Simulations can seamlessly resume across multiple Slurm job allocations by setting `start_from_checkpoint = true`.

### 4. Algorithmic Kernels
- **Vectorized Scoring (`VectorizedScoring`)**: Computes multi-component preference scores (Preferential Attachment, Fitness, Number of Authors, Author Reputation) across candidate arrays using AVX2 SIMD FMA instructions.
- **Vose Alias Method (`VoseAliasTable`)**: Generates exact $O(1)$ weighted random samples with $O(N)$ table initialization and a cache-aligned `FastBitset` rejection tracking structure.

### 5. LadyBugDB On-Disk Columnar Layout

LadyBugDB stores graph state in zero-deserialization binary Struct-of-Arrays (SoA) format inside `db_path` (default `./ladybug_data` or `./ladybug_data_rank_N`):

```
ladybug_data/
├── manifest.json              # Atomic state metadata (year, node/edge counts, author ID, status)
├── delta_journal.bin          # Binary Write-Ahead Log (WAL); auto-truncated on commit
├── nodes/                     # Memory-mapped columnar attribute arrays (Span<T>)
│   ├── publication_year.bin   # int32_t per node
│   ├── node_type.bin          # int32_t per node (e.g. 0: regular, 1: planted)
│   ├── author_id.bin          # int64_t per node
│   ├── cluster_id.bin         # int32_t per node (Leiden community ID)
│   ├── in_degree.bin          # int32_t per node
│   ├── out_degree.bin         # int32_t per node
│   ├── preference_weight.bin  # double per node
│   ├── fitness.bin            # double per node
│   ├── fitness_lag.bin        # int32_t per node
│   └── fitness_peak.bin       # int32_t per node
├── graph/                     # Bidirectional Compressed Sparse Row (CSR) arrays
│   ├── forward_row_offsets.bin       # uint64_t row pointers (0 to N)
│   ├── forward_column_indices.bin    # int64_t target node IDs
│   ├── backward_row_offsets.bin      # uint64_t row pointers (0 to N)
│   └── backward_column_indices.bin   # int64_t source node IDs
├── clusters/                  # Inverted Leiden community indices
│   ├── cluster_offsets.bin    # uint64_t offsets per cluster
│   ├── cluster_nodes.bin      # int64_t member node IDs
│   └── cluster_years.bin      # int32_t publication years (for fast binary search)
└── authors/                   # Dynamic author lifecycle and publication rosters
    ├── author_offsets.bin     # uint64_t offsets per author
    ├── author_papers.bin      # int64_t paper IDs authored
    ├── author_birth_years.bin # int32_t author career inception year
    └── author_reputations.bin # double dynamic reputation / h-index
```

All columnar files are expanded via sparse resizing (`ftruncate`) and mapped via `mmap(MAP_SHARED)`. SIMD and sampling routines obtain raw pointers directly through zero-copy `std::span<T>`, ensuring CPU cache line alignment and immediate hardware prefetching.

---

## Architectural Comparison: LadyBugDB vs. Legacy SASCA

| Feature | Legacy Engine (v7.x) | LadyBugDB Engine (v8.0) | Technical Rationale |
| :--- | :--- | :--- | :--- |
| **Graph Representation** | Array of pointer-heavy `std::vector<int>` objects | Contiguous Memory-Mapped SoA Forward & Backward CSR | Eliminates 8x pointer overhead; enables direct SIMD vectorization and cache locality |
| **Memory Footprint (50M nodes)** | ~120 GB RAM (frequent OOM crashes on shared nodes) | < 4 GB Resident RAM (out-of-core mmap working set) | OS kernel automatically pages inactive historical graph segments to NVMe storage |
| **Preference Scoring** | Scalar loop over candidates | 256-bit AVX2 / FMA Vectorized Kernels | Computes multi-term preferences in 4x fewer CPU cycles |
| **Random Sampling** | Linear scan or binary search $O(\log N)$ alias | $O(1)$ Vose Alias Method with `FastBitset` | Constant-time random selection with zero-allocation duplicate rejection tracking |
| **Distributed Scaling** | Single compute node only | Distributed MPI across $P$ nodes via Leiden Sharding | Distributes memory and compute across supercomputer cluster nodes |
| **Inter-Node Traffic** | N/A | Low-alpha remote pre-sampling ($k = 10{,}000$) | Reduces candidate generation network traffic to $\sim 40\text{ KB}$ per boundary agent |
| **Checkpoint Duration** | 20–30 minutes full CSV serialization | **< 1.2 seconds** atomic sync & manifest commit | `msync()` flushes modified dirty pages; atomic `manifest.json` write commits state |
| **Transaction Journal** | Unbounded append logs or none | Zero-bloat WAL auto-truncated to 0 bytes on commit | Guarantees zero disk expansion over 30+ simulated years |
| **HPC Wall-Clock Handling** | Abrupt kill by Slurm (losing full year progress) | Real-time `SignalSupervisor` (`SIGTERM` / timer) | Completes active superstep and cleanly commits checkpoint before job timeout |

---

## Dependencies

- **C++ Compiler**: GCC $\ge 12.0$ or Clang $\ge 15.0$ with full **C++20** support
- **OpenMP**: $\ge 4.0$
- **CMake**: $\ge 3.23$
- **MPI**: OpenMPI $\ge 4.0$ or MPICH (compiled with C++ bindings; auto-detected)
- **Eigen3**: $\ge 3.4$ (can be installed via `setup.sh`)
- **PCG Random**: (can be installed via `setup.sh`)
- **inih**: (can be installed via `setup.sh`)
- **argparse**: (can be installed via `setup.sh`)

---

## Installation & Build

### 1. One-Time Setup of Header Libraries
Run [`setup.sh`](setup.sh) to locally install Eigen, PCG, inih, and argparse:
```bash
./setup.sh
```

### 2. Compiling the Project
CantataS is a standard CMake project. To compile in Release mode with native hardware vectorization (`-O3 -march=native`):

```bash
mkdir -p build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . -j$(nproc)
cd ..
```

The resulting executable will be located at `build/bin/abm`.

### 3. Running the Verification Test Suite
To run all 9 automated unit tests verifying the LadyBugDB engine, SIMD scoring, Vose alias sampling, and distributed coordination:

```bash
ctest --test-dir build --output-on-failure
```

---

## Usage Instructions

### Basic Execution (Single-Node / Multi-Threaded)
Run the simulation using a configuration file:
```bash
./build/bin/abm --config docs/default_experiment.ini
```

You can optionally override storage settings via CLI flags:
```bash
./build/bin/abm --config docs/default_experiment.ini --storage-backend ladybug --db-path ./my_ladybug_data
```

### Multi-Node Distributed Execution (MPI / HPC Supercomputing)
When running on an HPC cluster with OpenMPI or under Slurm, launch using `mpirun` or `srun`. The coordinator automatically shards database storage directories (`./ladybug_data_rank_N`) and log files (`log.txt_rank_N`) per compute rank to ensure zero NVMe lock contention:

```bash
# Direct OpenMPI run across 4 ranks:
mpirun -n 4 ./build/bin/abm --config docs/default_experiment.ini

# Slurm multi-node job step across 16 ranks:
srun -n 16 ./build/bin/abm --config docs/default_experiment.ini
```

### CLI Arguments
| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `-h`, `--help` | Flag | - | Display usage information and exit |
| `-v`, `--version` | Flag | - | Display version information and exit |
| `--config` | String | **Required** | Path to the `.ini` simulation configuration file |
| `--storage-backend` | String | `"ladybug"` | Storage backend: `"ladybug"` (out-of-core mmap) or `"legacy"` (in-memory) |
| `--db-path` | String | `""` (uses INI) | Directory path for the persistent LadyBugDB database files |

---

## Configuration Reference

An example configuration file is provided at [`docs/default_experiment.ini`](docs/default_experiment.ini).

```ini
[Environment]
nodelist=/path/to/seed_nodelist.csv
edgelist=/path/to/seed_edgelist.csv
community_assignment=/path/to/seed_field_labels.csv ; CSV mapping node_id -> cluster_id
recency_table=/path/to/multifield_reccount.csv      ; CSV of empirical citation recency counts
out_degree_bag=/path/to/out_degree_bag.csv          ; CSV of empirical out-degree distribution
growth_rate=0.03                                    ; Annual exponential node growth rate (e.g. 0.03 for 3%)
num_cycles=30                                       ; Number of simulation years
recency_bins=1,2,3,4,5,6,7,8,9,10,11,16,21,26,31,36,41,46,51 ; Comma-separated bin boundaries
planted_nodes=                                      ; Optional CSV of planted agents
start_from_checkpoint=false                         ; true to resume from checkpoint

[Agent]
alpha=-1                                ; 1-hop / intra-cluster citation proportion (-1 for uniform random)
use_alpha=true                          ; Enable/disable alpha intra-cluster dynamics
theta=0                                 ; Minimum cluster size threshold for cluster-based citations
same_year_citations=0.12                ; Proportion of citations directed to same-year papers
fully_random_citations=0.05             ; Proportion of citations allocated globally at random
preferential_weight=-1                  ; Preferential attachment weight (-1 for random per agent)
fitness_weight=-1                       ; Intrinsic paper fitness weight (-1 for random per agent)
num_authors_weight=-1                   ; Team size weight (-1 for random per agent)
author_reputation_weight=-1             ; Author historical reputation weight (-1 for random per agent)
fitness_value_min=1                     ; Minimum baseline fitness
fitness_value_max=1000                  ; Maximum baseline fitness
fitness_lag_duration_min=0              ; Minimum dormant lag before peak fitness (years)
fitness_lag_duration_max=0              ; Maximum dormant lag before peak fitness (years)
fitness_peak_duration_min=1000          ; Minimum peak fitness duration (years)
fitness_peak_duration_max=1000          ; Maximum peak fitness duration (years)
neighborhood_sample=10000               ; Maximum candidate sample size per neighborhood
in_degree_threshold=5                   ; Minimum in-degree for non-random generator selection
fitness_threshold=20                    ; Minimum fitness for non-random generator selection
recency_threshold=10                    ; Recency horizon (years) for generator selection
non_random_generator_probability=0.0    ; Probability of choosing generator non-randomly
author_max_lifetime=30                  ; Maximum career publishing span for an author (years)
cartel_outdegree_proportion=0.50        ; Out-degree proportion directed within cartel syndicate
null_cartel=true                        ; true for cartel-r (random), false for cartel-p (preferential)
clonal_cartel_agent_file=               ; Optional CSV defining clonal cartel agent attributes
num_authors_bag=/path/to/pubmed_authors.csv ; Bag for sampling paper author counts

[General]
output_file=./output/edgelist.csv                    ; Output CSV edgelist
auxiliary_information_file=./output/nodelist.csv    ; Output CSV node attributes
log_file=./output/log.txt                           ; Output log file
num_processors=32                                   ; OpenMP worker threads per compute node
log_level=1                                         ; 0: silent, 1: info, 2: verbose
storage_backend=ladybug                             ; ladybug (mmap SoA) or legacy (in-memory)
db_path=./ladybug_data                              ; Storage directory for LadyBugDB
use_distributed=false                               ; true/false (auto-enabled if run with MPI world_size > 1)
ghost_hub_threshold=100                             ; In-degree threshold to replicate ghost hub cells
wall_clock_limit=0.0                                ; Slurm wall-clock limit in seconds (0 = disabled)
```

---

## Zero-Bloat Checkpointing & Slurm Job Chaining

### How LadyBugDB Checkpointing Works
At the conclusion of each simulated year, the simulation executes an annual superstep commit:
1. Merges local and received remote delta citations into the backward CSR.
2. Updates author reputations across all active authors.
3. Synchronizes NVMe memory-mapped SoA files to disk.
4. Atomically writes `manifest.json`:
   ```json
   {
     "version": 1,
     "current_year": 2027,
     "node_count": 26954,
     "edge_count": 278436,
     "next_author_id": 10044,
     "last_commit_timestamp": 1791830942283,
     "status": "valid"
   }
   ```
5. Prunes the delta transaction log (`delta_journal.bin`) back to zero bytes (zero-bloat guarantee).

### Resuming from Checkpoints
To resume an interrupted simulation:
1. In your configuration file, set:
   ```ini
   [Environment]
   start_from_checkpoint=true
   ```
2. Set `db_path` to the existing database directory (or leave as default `./ladybug_data`).
3. Launch `abm`. The simulator will read `manifest.json`, verify file integrity, recover node counts and degrees, and resume execution starting from `current_year + 1`.

### Example Slurm Job Submission Script
Below is an example Slurm batch script configured for a 4-hour allocation with automatic wall-clock safety margins:

```bash
#!/bin/bash
#SBATCH --job-name=cantatas_sim
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --cpus-per-task=16
#SBATCH --time=04:00:00
#SBATCH --partition=secondary
#SBATCH --output=slurm-%j.out

module load gcc/13.3.0
module load openmpi/5.0.1

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# 4-hour wall clock limit (14400s) with 20-minute safety buffer configured in INI:
# wall_clock_limit = 14400.0

srun --mpi=pmi2 ./build/bin/abm --config docs/default_experiment.ini
```

If the 4-hour limit approaches or Slurm issues `SIGTERM`, `SignalSupervisor` catches the event, ensures the ongoing simulated year completes its full BSP commit, updates `manifest.json`, and exits cleanly with exit code 0. A subsequent job with `start_from_checkpoint=true` can immediately resume where the prior job left off.

---

## HPC Performance Tuning & Best Practices

### 1. Storage: Local NVMe Scratch vs. Shared Lustre/NFS
For maximum throughput on supercomputing clusters (such as the Illinois Campus Cluster, NCSA Delta, or TACC Stampede):
- **Set `db_path` to local NVMe scratch**: Point `db_path` to the local high-speed SSD scratch path (e.g., `/tmp`, `/scratch/local`, or `$TMPDIR`). Memory-mapped I/O on node-local NVMe achieves millions of IOPS without generating metadata locking contention on shared cluster filesystems (Lustre/GPFS/NFS).
- **Persistent Output on Shared Filesystem**: Keep `output_file`, `auxiliary_information_file`, and `log_file` pointing to your persistent project directory. Only Rank 0 writes the final CSV files at the conclusion of the simulation.

### 2. Thread Affinity & NUMA Topology
CantataS combines MPI inter-node communication with OpenMP intra-node multi-threading. For optimal cache efficiency:
- Allocate **1 MPI rank per compute node** (or 1 rank per NUMA socket).
- Match `num_processors` in `[General]` to the number of physical CPU cores per rank:
  ```bash
  export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
  export OMP_PROC_BIND=spread
  export OMP_PLACES=threads
  ```

### 3. OpenMPI Network Transports (InfiniBand vs. Login Nodes)
- **HPC Compute Nodes**: OpenMPI automatically selects UCX / InfiniBand fabrics (`rc`, `ud`, or `sm` for intra-node shared memory).
- **Login Nodes (`cc-login`)**: On login nodes, user-space InfiniBand device access is restricted. CantataS includes automated launcher detection: when launched directly via `./build/bin/abm` without `mpirun`/`srun`, it safely bypasses UCX fabric initialization to prevent hardware probe warnings while retaining full multi-threaded performance.

---

## Output Data Formats & Direct Binary Access

### Final CSV Exports
At the end of the simulation, the primary node (Rank 0) exports the complete graph into standard CSV formats:

1. **`edgelist.csv`** (`output_file`):
   ```csv
   source,target,year
   0,142,2025
   0,89,2025
   ...
   ```
2. **`nodelist.csv`** (`auxiliary_information_file`):
   ```csv
   node_id,author_id,birth_year,cluster_id,fitness,fitness_lag,fitness_peak,preference_weight
   0,1024,2025,12,42.5,0,1000,0.33
   ...
   ```
3. **`log.txt`** (or `log.txt_rank_N`): Detailed per-year operational logs, detailing edge creation counts, ghost cell hits, cross-partition edge transfer volumes, and superstep sync latency.

### Direct Zero-Copy Python Analysis (NumPy Memmap)
Because LadyBugDB maintains contiguous binary SoA arrays, you do not need to wait for or parse gigabytes of CSV data to analyze results. You can inspect arrays directly from Python in microseconds:

```python
import numpy as np
import json

# Read checkpoint manifest
with open("ladybug_data/manifest.json") as f:
    manifest = json.load(f)
N = manifest["node_count"]

# Zero-copy memory-mapped access to node attributes:
years = np.memmap("ladybug_data/nodes/publication_year.bin", dtype=np.int32, mode="r", shape=(N,))
in_degrees = np.memmap("ladybug_data/nodes/in_degree.bin", dtype=np.int32, mode="r", shape=(N,))
clusters = np.memmap("ladybug_data/nodes/cluster_id.bin", dtype=np.int32, mode="r", shape=(N,))

print(f"Total papers: {N}")
print(f"Average in-degree: {in_degrees.mean():.2f}")
print(f"Top 5 most cited papers: {np.argsort(in_degrees)[-5:]}")
```

---

## Citation Methodology

Each simulated paper fulfills its assigned out-degree quota across five sequential phases:

1. **Quota Reservation**: Portions of the citation quota are reserved for same-year papers (`same_year_citations`) and globally uniform random citations (`fully_random_citations`).
2. **Cartel Syndicates**: If the paper's author belongs to a cartel, quota is directed toward co-members (randomly under `null_cartel=true`, or score-weighted under `null_cartel=false`).
3. **Primary Citations (1-Hop vs. Intra-Cluster)**: The `alpha` parameter governs primary citations. If the paper's assigned community cluster meets or exceeds `theta`, citations target nodes within that cluster. Otherwise, citations target the standard 1-hop neighborhood of parent generator nodes.
4. **Secondary Citations (2-Hop)**: Remaining neighborhood quota is fulfilled by sampling from 2-hop neighbor candidates.
5. **Deficit Compensation**: Any remaining deficit (arising from duplicate edge rejection or small neighborhood candidate pools) is fulfilled by uniform random selection from the global network.

---

## Generating Community Clusters (Leiden Algorithm)

CantataS includes a Python utility ([`leiden_clustering.py`](leiden_clustering.py)) to detect community structures from empirical seed networks using the Leiden algorithm:

```bash
python leiden_clustering.py \
  --nodelist /path/to/seed_nodelist.csv \
  --edgelist /path/to/seed_edgelist.csv \
  --output /path/to/seed_field_labels.csv \
  --resolution 0.01 \
  --objective CPM
```

Point `community_assignment` in `[Environment]` to the generated output CSV to enable cluster-aware simulation dynamics.

---

## Citation & References

If you use CantataS in your research, please cite:

1. Chacko, George, Minhyuk Park, Vikram Ramavarapu, Ananth Grama, Pablo Robles-Granda, and Tandy Warnow. *"An agent-based model of citation behavior."* Applied Network Science 11, no. 1 (2026): 10.
