import unittest
from typing import Any, Dict, List
from ..graph import create_graph, Node
from ..cluster import sample_clusters, Cluster

class TestClusterGraph(unittest.TestCase):

  def cluster(
    self,
    document: Dict | List,
    max_weight: int,
    max_iterations: int = 1,
  ):
    def sum_of_leaf_values(value: Any):
      if isinstance(value, list):
        return sum(sum_of_leaf_values(v) for v in value)
      elif isinstance(value, dict):
        return sum(sum_of_leaf_values(v) for v in value.values())
      return int(value)

    graph = create_graph(document)
    return sample_clusters(
      graph,
      max_weight=max_weight,
      max_iterations=max_iterations,
      calculate_weight=lambda candidate: sum_of_leaf_values(candidate.value),
    )


  def test_creates_two_clusters_if_cannot_combine(self):
    clusters = self.cluster({ 'one': 1, 'two': 2 }, max_weight=2)
    self.assertEqual(len(clusters), 2)
    self.assertEqual(clusters[0].weight, 1)
    self.assertEqual(clusters[0].path, ['one'])
    self.assertEqual(clusters[1].weight, 2)
    self.assertEqual(clusters[1].path, ['two'])
    

  def test_creates_one_cluster_if_can_combine(self):
    clusters = self.cluster({ 'one': 1, 'two': 2 }, max_weight=3)
    self.assertEqual(len(clusters), 1)
    self.assertEqual(clusters[0].weight, 3)
    self.assertEqual(clusters[0].path, [])


  def test_returns_balanced_clusters(self):
    clusters = self.cluster({ 'one': 1, 'two': 2, 'three': 3 }, max_weight=4, max_iterations=100)

    expected_clusters = [
      Cluster(path=[], child_keys={'one', 'two'}, weight=3, value={'one': 1, 'two': 2}),
      Cluster(path=['three'], weight=3, value=3),
    ]
    self.assertEqual(len(clusters), len(expected_clusters))
    for expected in expected_clusters:
      self.assertIn(expected, clusters)


  def test_clusters_with_parent_if_all_children_are_clustered(self):
    value = {
      'a': 1,
      'nested': {
        'b': 2,
        'c': 3,
      },
    }
    clusters = self.cluster(value, max_weight=6)
    self.assertEqual(len(clusters), 1)
    self.assertIn(Cluster(path=[], weight=6, value=value), clusters)


  def test_doesnt_cluster_with_parent_if_not_all_children_are_clustered(self):
    """ $.1.a and $.1.2.b should not cluster because all children of $.1 are not clustered """
    value = {
      'a': 1,
      'nested': {
        'b': 2,
        'c': 3,
      },
    }
    clusters = self.cluster(value, max_weight=3)

    expected_clusters = [
      Cluster(path=['a'], weight=1, value=1),
      Cluster(path=['nested', 'b'], weight=2, value=2),
      Cluster(path=['nested', 'c'], weight=3, value=3),
    ]
    self.assertEqual(len(clusters), len(expected_clusters))
    for expected in expected_clusters:
      self.assertIn(expected, clusters)


  def test_keeps_array_order(self):
    # a & c shouldn't be clustered
    value = [
      { 'a': 1 },
      { 'b': 3 },
      { 'c': 2 },
    ]
    clusters = self.cluster(value, max_weight=3)

    expected_clusters = [
      Cluster(path=[0], weight=1, value={ 'a': 1 }),
      Cluster(path=[1], weight=3, value={ 'b': 3 }),
      Cluster(path=[2], weight=2, value={ 'c': 2 }),
    ]
    self.assertEqual(len(clusters), len(expected_clusters))
    for expected in expected_clusters:
      self.assertIn(expected, clusters)
  

  def test_array_with_dicts_with_multiple_keys(self):
    data = [
      { 'key1': 1, 'key2': 1 },
      { 'key3': 1, 'key4': 1 },
      { 'key4': 1, 'key6': 2 },
    ]
    clusters = self.cluster(data, max_weight=5) # either 2 clusters can cluster

    expected_clusters = [
      Cluster(path=[], weight=4, child_keys={0, 1}, value=data[0:2]),
      Cluster(path=[2], weight=3, value=data[2]),
    ]
    self.assertEqual(len(clusters), len(expected_clusters))
    for expected in expected_clusters:
      self.assertIn(expected, clusters)


if __name__ == '__main__':
  unittest.main()
