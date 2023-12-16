import json
from typing import Callable, Dict, List, Optional, Union
from .graph import create_graph
from .cluster import sample_clusters, ClusterCandidate, Cluster


def split(
  document: Union[Dict, List[Dict]],
  max_length: int,
  max_iterations: int = 10,
  timeout: Optional[int] = None,
  seed: int = 42,
  dumps: Callable[[ClusterCandidate], int] = lambda candidate: len(json.dumps(candidate.value)),
) -> List[Cluster]:
  graph = create_graph(document)
  clusters = sample_clusters(
    graph,
    max_weight=max_length,
    max_iterations=max_iterations,
    timeout=timeout,
    calculate_weight=dumps,
    seed=seed,
  )
  return clusters
