from dataclasses import dataclass
from typing import Set, Any, Callable, List, Dict, Tuple, Literal
from .types import NodeId, NodePath


@dataclass
class Node():
  path: NodePath
  type: Literal['array', 'object', 'value']
  value: Any


@dataclass
class Graph():
  nodes: Dict[NodeId, Node]
  edges: Set[Tuple[NodeId, NodeId]]

  def predecessors(self, node_id: NodeId) -> Set[NodeId]:
    return set([source for (source, target) in self.edges if target == node_id])
  
  def successors(self, node_id: NodeId) -> Set[NodeId]:
    return set([target for (source, target) in self.edges if source == node_id])

def create_graph(
  value: Any,
  path: NodePath = ['$'],
) -> Graph:
  nodes: Dict[NodeId, Node] = {}
  edges: Set[Tuple[NodeId, NodeId]] = set()

  node_id = create_node_id(path)
  if isinstance(value, dict):
    node = Node(path=path, type='object', value=value)
    nodes[node_id] = node
    for key, val in value.items():
      sub_graph = create_graph(val, path + [key])
      child_node_id = next(iter(sub_graph.nodes.keys()))
      edges.add((node_id, child_node_id))
      nodes.update(sub_graph.nodes)
      edges.update(sub_graph.edges)
  elif isinstance(value, list):
    node = Node(path=path, type='array', value=value)
    nodes[node_id] = node
    for i, val in enumerate(value):
      sub_graph = create_graph(val, path + [i])
      child_node_id = next(iter(sub_graph.nodes.keys()))
      edges.add((node_id, child_node_id))
      nodes.update(sub_graph.nodes)
      edges.update(sub_graph.edges)
  else:
    node = Node(path=path, type='value', value=value)
    nodes[node_id] = node
  
  return Graph(nodes=nodes, edges=edges)

def create_node_id(path: NodePath) -> str:
  parts: List[str] = []
  for i, p in enumerate(path):
    if isinstance(p, int):
      parts.append(f'[{p}]')
    elif i == 0:
      parts.append(f'{p}')
    else:
      parts.append(f'.{p}')
  return ''.join(parts)
