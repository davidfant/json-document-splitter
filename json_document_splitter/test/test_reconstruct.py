import unittest
from typing import Any
from ..graph import create_graph, Node
from ..cluster import reconstruct

class TestReconstruct(unittest.TestCase):

  def test_reconstruct_cluster_of_one(self):
    graph = create_graph({
      'hello': 'world',
    })

    reconstructed = reconstruct(['$'], graph)
    self.assertEqual(reconstructed.path, [])
    self.assertEqual(reconstructed.value, {
      'hello': 'world',
    })
    self.assertEqual(reconstructed.child_keys, None)
  

  def test_reconstruct_partial_array(self):
    graph = create_graph([
      'one',
      'two',
      'three',
    ])

    reconstructed = reconstruct(['$[1]', '$[2]'], graph)
    self.assertEqual(reconstructed.path, [])
    self.assertEqual(reconstructed.value, ['two', 'three'])
    self.assertEqual(reconstructed.child_keys, {1, 2})
  
  def test_reconstruct_partial_object(self):
    graph = create_graph({
      'one': 1,
      'two': 2,
      'three': { 'nested': 3 },
    })

    reconstructed = reconstruct(['$.two', '$.three'], graph)
    self.assertEqual(reconstructed.path, [])
    self.assertEqual(reconstructed.value, {
      'two': 2,
      'three': { 'nested': 3 },
    })
    self.assertEqual(reconstructed.child_keys, {'two', 'three'})
    
  
if __name__ == '__main__':
  unittest.main()
