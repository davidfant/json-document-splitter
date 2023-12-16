import math
from time import time
from random import Random
from typing import List, Set, cast, Dict, Callable, Any, Union, Optional
from dataclasses import dataclass
from .graph import Graph, NodeId
from .types import NodeId



@dataclass
class ClusterCandidate():
  path: List[Union[str, int]]
  value: Any
  child_keys: Optional[Set[Union[str, int]]] = None

@dataclass
class Cluster():
  path: List[Union[str, int]]
  value: Any
  weight: int
  child_keys: Optional[Set[Union[str, int]]] = None


def sample_clusters(
  graph: Graph,
  max_weight: int,
  calculate_weight: Callable[[ClusterCandidate], int],
  max_iterations: int = 1,
  timeout: Optional[int] = None,
  seed: Optional[int] = None,
) -> List[Cluster]:
  rand = Random(seed)

  attempts: List[List[Cluster]] = []
  for iteration in range(max_iterations):
    attempt = create_clusters(
      graph,
      max_weight,
      rand=rand if iteration > 0 else None,
      calculate_weight=calculate_weight,
      timeout=timeout / max_iterations if timeout else None,
    )
    attempts.append(attempt)
  
  mins = [(len(a), std([c.weight for c in a])) for a in attempts]
  return min(
    attempts,
    key=lambda clusters: (
      len(clusters),
      std([c.weight for c in clusters])
    )
  )


def create_clusters(
  graph: Graph,
  max_weight: int,
  calculate_weight: Callable[[ClusterCandidate], int],
  rand: Optional[Random] = None,
  timeout: Optional[int] = None,
) -> List[Cluster]:
  start_at = time()
  
  node_ids = list(graph.nodes.keys())
  if rand:
    rand.shuffle(node_ids)

  count = 0
  cluster_by_node: Dict[NodeId, int] = {}
  clusters: Dict[int, Cluster] = {}

  calculcate_weight_cache: Dict[str, int] = {}
  reconstruct_cache: Dict[str, ClusterCandidate] = {}
  
  def calculate_weight_cached(candidate: ClusterCandidate) -> int:
    cache_key = f'{candidate.path} {candidate.child_keys}'
    if cache_key in calculcate_weight_cache:
      return calculcate_weight_cache[cache_key]
    weight = calculate_weight(candidate)
    calculcate_weight_cache[cache_key] = weight
    return weight

  def reconstruct_cached(node_ids: List[NodeId]) -> ClusterCandidate:
    cache_key = str(sorted(node_ids))
    if cache_key in reconstruct_cache:
      return reconstruct_cache[cache_key]
    reconstructed = reconstruct(node_ids, graph)
    reconstruct_cache[cache_key] = reconstructed
    return reconstructed

  # 1. Create initial cluster for each leaf node
  for node_id in node_ids:
    has_children = any([source == node_id for (source, target) in graph.edges])
    if has_children:
      continue

    node = graph.nodes[node_id]
    cluster_id = len(clusters) + 1
    cluster_by_node[node_id] = cluster_id
    clusters[cluster_id] = Cluster(
      path=node.path,
      value=node.value,
      weight=calculate_weight(ClusterCandidate(path=node.path, value=node.value)),
    )
  
  changed = True
  while changed:
    if timeout and time() - start_at > timeout:
      raise TimeoutError('Timeout exceeded')

    changed = False

    for node_id in node_ids:
      if not node_id in cluster_by_node:
        continue

      # Get each node's parent and siblings (merging candidates)
      parent_id = next(iter(graph.predecessors(node_id)), None)
      if not parent_id or parent_id in cluster_by_node:
        continue
      parent = graph.nodes[parent_id]
      siblings = [n for n in graph.successors(parent_id) if n != node_id]

      if rand and not parent.type == 'array':
        rand.shuffle(siblings)
      
      node_cluster_id = cluster_by_node[node_id]

      for sibling_id in siblings:
        if not sibling_id in cluster_by_node:
          continue
        sibling_cluster_id = cluster_by_node[sibling_id]

        if node_cluster_id == sibling_cluster_id:
          continue
        
        if parent.type == 'array':
          node_array_idx = cast(int, graph.nodes[node_id].path[-1])
          sibling_array_idx = cast(int, graph.nodes[sibling_id].path[-1])
          if node_array_idx != sibling_array_idx - 1:
            continue

        combined_node_ids = [
          id
          for id, cluster_id in cluster_by_node.items()
          if cluster_id in [node_cluster_id, sibling_cluster_id]
        ]
        combined_candidate = reconstruct_cached(combined_node_ids)

        combined_weight = calculate_weight_cached(combined_candidate)
        if combined_weight > max_weight:
          continue

        clusters[node_cluster_id] = Cluster(
          path=combined_candidate.path,
          value=combined_candidate.value,
          child_keys=combined_candidate.child_keys,
          weight=combined_weight,
        )

        if sibling_cluster_id:
          del clusters[sibling_cluster_id]
          for id, cluster_id in cluster_by_node.items():
            if cluster_id == sibling_cluster_id:
              cluster_by_node[id] = node_cluster_id
        
        changed = True
      
      is_all_siblings_in_same_cluster = all([
        cluster_by_node.get(sibling_id) == node_cluster_id
        for sibling_id in siblings
      ])
      if is_all_siblings_in_same_cluster:
        combined_node_ids = [node_id, parent_id] + siblings
        combined_candidate = reconstruct_cached(combined_node_ids)
        combined_weight = calculate_weight_cached(combined_candidate)
        if combined_weight <= max_weight:
          clusters[node_cluster_id] = Cluster(
            path=combined_candidate.path,
            value=combined_candidate.value,
            child_keys=combined_candidate.child_keys,
            weight=combined_weight,
          )
          cluster_by_node[parent_id] = node_cluster_id
          changed = True

  return list(clusters.values())


def clean_child_nodes(node_ids: List[NodeId], graph: Graph) -> List[NodeId]:
  path_len_by_node_id = {
    node_id: len(graph.nodes[node_id].path)
    for node_id in node_ids
  }
  min_path_len = min(path_len_by_node_id.values())
  return [
    node_id
    for node_id, path_len in path_len_by_node_id.items()
    if path_len == min_path_len
  ]


def std(array: List[int]) -> float:
  mean = sum(array) / len(array)
  variance = sum([(x - mean) ** 2 for x in array]) / len(array)
  return math.sqrt(variance)


def reconstruct(
  node_ids: List[NodeId],
  graph: Graph,
) -> ClusterCandidate:
  node_ids = clean_child_nodes(node_ids, graph)

  if len(node_ids) == 1:
    node = graph.nodes[node_ids[0]]
    return ClusterCandidate(path=node.path, value=node.value)
  else:
    first_node_id = node_ids[0]
    parent_id = next(iter(graph.predecessors(first_node_id)))
    parent = graph.nodes[parent_id]

    if parent.type == 'array':
      cluster_node_ids = sorted(node_ids, key=lambda id: graph.nodes[id].path[-1])
      cluster_node_keys = set([graph.nodes[id].path[-1] for id in node_ids])
      value = [graph.nodes[id].value for id in cluster_node_ids]
      return ClusterCandidate(
        path=parent.path,
        value=value,
        child_keys=cluster_node_keys,
      )
    elif parent.type == 'object':
      child_keys = [graph.nodes[id].path[-1] for id in node_ids]
      value = {
        child_key: graph.nodes[child_id].value
        for child_key, child_id in zip(child_keys, node_ids)
      }
      return ClusterCandidate(
        path=parent.path,
        value=value,
        child_keys=set(child_keys),
      )
    else:
      raise Exception('Unexpected parent type: ' + parent.type)


