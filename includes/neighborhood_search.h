#ifndef NEIGHBORHOOD_SEARCH_H
#define NEIGHBORHOOD_SEARCH_H

#include "graph.h"
#include "utils.h"
#include <string>
#include <unordered_map>
#include <vector>

class NeighborhoodSearch {
public:
  /*
  Input: std::string recency_bins_str, bool use_alpha, int neighborhood_sample
  Output: NeighborhoodSearch object
  Description: Constructs a NeighborhoodSearch object and initializes recency
  bins for time-aware co-author network exploration.
  */
  NeighborhoodSearch(std::string recency_bins_str, bool use_alpha,
                     int neighborhood_sample);

  /*
  Input: Graph *graph, int current_year, const std::vector<int>
  &generator_nodes, int num_hops Output: std::vector<std::vector<int>>
  (vector indexed by distance 1..num_hops) Description:
  Main entry point for gathering neighborhood nodes. Defers to specific N-hop
               strategies based on the configuration of the search instance.
  */
  std::vector<std::vector<int>>
  GetNeighborhoodMap(Graph *graph, int current_year,
                     const std::vector<int> &generator_nodes, int num_hops);
  /*
  Input: Graph *graph, int current_year, const std::vector<int>
  &generator_nodes, int num_hops Output: std::vector<std::vector<int>>
  (vector indexed by distance 1..2) Description:
  Specifically computes the union of the 1-hop and 2-hop co-author network for
  the given generator nodes, filtering by the current year.
  */
  std::vector<std::vector<int>>
  GetOneAndTwoDistanceNeighborhoods(Graph *graph, int current_year,
                                    const std::vector<int> &generator_nodes,
                                    int num_hops);
  /*
  Input: Graph *graph, int current_year, const std::vector<int>
  &generator_nodes, int num_hops Output: std::vector<std::vector<int>>
  (vector indexed by distance 1..num_hops) Description: Computes
  the N-hop co-author network recursively or iteratively, expanding outward up
  to num_hops distances.
  */
  std::vector<std::vector<int>>
  GetNHopNeighborhood(Graph *graph, int current_year,
                      const std::vector<int> &generator_nodes, int num_hops);

  /*
  Input: int year_diff
  Output: int (index of the corresponding recency bin)
  Description: Maps an absolute year difference to the appropriate index in the
  configured time bins (e.g., [0-1], [2-5], [6+]).
  */
  int GetBinIndex(int year_diff);
  /*
  Input: Graph *graph, int current_node, int current_year
  Output: int (index of the corresponding recency bin)
  Description: Extracts the publication year of a node from the graph and
  calculates its age relative to the current year, mapping it to a bin index.
  */
  int GetBinIndex(Graph *graph, int current_node, int current_year);
  /*
  Input: Graph *graph, int current_year, const std::vector<int> &n_hop_list
  Output: std::vector<std::vector<int>> (bin index mapped to nodes
  in that age bin) Description: Partitions a flat list of neighborhood nodes
  into separate buckets depending on how recently the papers were published.
  */
  std::vector<std::vector<int>>
  BinNeighborhood(Graph *graph, int current_year, const std::vector<int> &n_hop_list);
  /*
  Input: const std::vector<std::vector<int>> &binned_neighborhood,
         int total_outdegree, const std::vector<double>&
  binned_recency_probabilities Output: std::vector<int> (number of
  citations allocated per bin) Description: Allocates a quota of out-degree
  (citations) across different age bins based on the configured probability
  distribution for recency.
  */
  std::vector<int> BinOutdegrees(
      const std::vector<std::vector<int>> &binned_neighborhood,
      int total_outdegree,
      const std::vector<double> &binned_recency_probabilities);
  std::vector<int> BinOutdegrees(
      const std::vector<int> &bin_sizes,
      int total_outdegree,
      const std::vector<double> &binned_recency_probabilities);
  /*
  Input: double alpha, int total_num_citations_neighborhood,
         const std::vector<std::vector<int>> &n_hop_map
  Output: std::vector<int> (target distance index mapped to its allocated
  citation count) Description: Determines the precise number of citations to
  distribute across various distances or groups in the neighborhood based on an
  alpha bias factor.
  */
  std::vector<int> GetNumCitationsPerNeighborhood(
      double alpha, int total_num_citations_neighborhood,
      const std::vector<std::vector<int>> &n_hop_map);
  std::vector<int> GetNumCitationsPerNeighborhood(
      double alpha, int total_num_citations_neighborhood,
      size_t hop1_size, size_t hop2_size);

  /*
  Input: Graph *graph, int current_year, const std::vector<int> &nodes, size_t k
  Output: std::vector<int> of at most k nodes sampled without replacement
  Description: Weighted sample where a node of age a has weight
  exp(-a / recency_lambda) (Efraimidis-Spirakis). Returns nodes unchanged if
  there are at most k.
  */
  std::vector<int> RecencyBiasedSample(Graph *graph, int current_year,
                                       const std::vector<int> &nodes, size_t k);

  std::string recency_bins_str;
  bool use_alpha;
  int neighborhood_sample;
  // Recency bias for the neighborhood down-sampling. recency_lambda <= 0 keeps
  // uniform sampling. Otherwise a node of age a is kept with weight
  // exp(-a / recency_lambda). prepool_factor >= 1 widens the 2-hop pool that is
  // collected before the biased down-sampling to neighborhood_sample nodes.
  double recency_lambda = -1.0;
  // Nodes older than max_citable_age years are dropped from the candidates
  // (-1 keeps all).
  int max_citable_age = -1;
  int prepool_factor = 1;
  int num_bins;
  std::vector<int> bin_boundaries;
  std::vector<int> recency_bin_lut;
  /*
  Input: None
  Output: void
  Description: Parses the recency_bins_str (e.g. "0-2,3-5,6-10") to establish
  internal integer boundary vectors for rapid bin lookups.
  */
  void InitializeBinBoundaries();
  void BuildBinLUT();
};

#endif
