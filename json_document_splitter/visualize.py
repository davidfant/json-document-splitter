from typing import Tuple, List, Callable, Any, Dict
from .types import NodeId
from .graph import Graph
from .cluster import Cluster, ClusterCandidate


def visualize(
  graph: Graph,
  clusters: List[Cluster] | None = None,
  calculate_weight: Callable[[Any], int] | None = None,
  label_objects_and_arrays: bool = True,
  figsize: Tuple[int, int] = (10, 10),
):
  import matplotlib.pyplot as plt
  import networkx as nx

  node_ids = list(graph.nodes.keys())

  G = nx.DiGraph()
  for node_id in node_ids:
    G.add_node(node_id)
  for source, target in graph.edges:
    G.add_edge(source, target)
  
  cluster_idx_by_node = (
    get_cluster_idx_by_node_id(graph, clusters)
    if clusters
    else {}
  )
  node_color = [
    cluster_idx_by_node.get(node_id)
    for node_id in node_ids
  ]

  node_weight_by_id: Dict[NodeId, int] = { id: 0 for id in node_ids }
  if calculate_weight:
    for node_id in node_ids:
      node = graph.nodes[node_id]
      if node.type == 'value':
        node_weight_by_id[node_id] = calculate_weight(ClusterCandidate(
          path=node.path,
          value=node.value,
        ))
  node_size = [
    max(node_weight_by_id[node_id], 50)
    for node_id in node_ids
  ]
  
  labels: Dict[str, str] = {}
  for node_id in node_ids:
    node = graph.nodes[node_id]
    weight = node_weight_by_id[node_id]
    cluster_idx = cluster_idx_by_node.get(node_id)
    if weight:
      labels[node_id] = str(weight)
    elif label_objects_and_arrays:
      labels[node_id] = node_id

  plt.figure(figsize=figsize)
  pos = nx.nx_agraph.graphviz_layout(G, prog="twopi", args="")
  nx.draw_networkx(
    G,
    pos=pos,
    edge_color='lightgray',
    node_color=node_color,
    node_size=node_size,
    labels=labels,
    cmap=plt.cm.rainbow, # type: ignore
  )
  plt.show()


def get_cluster_idx_by_node_id(graph: Graph, clusters: List[Cluster]) -> Dict[NodeId, int]:
  cluster_idx_by_node: Dict[NodeId, int] = {}
  for node_id, node in graph.nodes.items():
    for cluster_idx, cluster in enumerate(clusters or []):
      if len(node.path) < len(cluster.path):
        continue
      if node.path[:len(cluster.path)] != cluster.path:
        continue

      if not cluster.child_keys:
        cluster_idx_by_node[node_id] = cluster_idx
      else:
        for child_key in cluster.child_keys:
          if node.path[:len(cluster.path) + 1] == cluster.path + [child_key]:
            cluster_idx_by_node[node_id] = cluster_idx
            break
      
      if node_id in cluster_idx_by_node:
        break
  
  return cluster_idx_by_node
