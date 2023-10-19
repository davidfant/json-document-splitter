import json
from transformers import AutoTokenizer
from typing import Set, Any, Callable, Dict, List
from dataclasses import dataclass
from .graph import create_graph, Graph
from .cluster import sample_clusters, ClusterCandidate, Cluster


class JSONDocumentSplitter:
  @dataclass
  class Options():
    tokenizer: AutoTokenizer
    max_length: int
    max_iterations: int = 10
    seed: int = 42
    dumps: Callable[[ClusterCandidate], str] = lambda chunk: json.dumps(chunk.value)
  options: Options


  def __init__(self, options: Options):
    self.options = options


  def split(self, document: Dict | List[Dict]) -> List[Cluster]:
    graph = create_graph(document)
    clusters = sample_clusters(
      graph,
      max_weight=self.options.max_length,
      max_iterations=self.options.max_iterations,
      calculate_weight=self.calculate_tokens,
      seed=self.options.seed,
    )
    return clusters
  

  def calculate_tokens(self, candidate: ClusterCandidate) -> int:
    stringified = self.options.dumps(candidate)
    encoded = self.options.tokenizer.encode(stringified, add_special_tokens=False) # type: ignore
    return len(encoded)
