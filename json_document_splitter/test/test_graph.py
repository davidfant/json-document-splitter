import unittest
from typing import Any
from ..graph import create_graph, Node

class TestCreateGraph(unittest.TestCase):

  def test_create_graph_from_dict(self):
    graph = create_graph({
      'hello': 'world',
      'nested': {
        'key': 'value'
      }
    })
    self.assertEqual(len(graph.nodes), 4)
    self.assertEqual(len(graph.edges), 3)

    self.assertTrue('$.hello' in graph.nodes)
    self.assertTrue(('$', '$.hello') in graph.edges)
    self.assertEqual(
      graph.nodes['$.hello'],
      Node(path=['hello'], type='value', value='world')
    )

    self.assertTrue('$.nested' in graph.nodes)
    self.assertTrue(('$', '$.nested') in graph.edges)
    self.assertEqual(
      graph.nodes['$.nested'],
      Node(path=['nested'], type='object', value={'key': 'value'})
    )

    self.assertTrue('$.nested.key' in graph.nodes)
    self.assertTrue(('$.nested', '$.nested.key') in graph.edges)
    self.assertEqual(
      graph.nodes['$.nested.key'],
      Node(path=['nested', 'key'], type='value', value='value')
    )


  def test_create_graph_from_list(self):
    graph = create_graph([
      'hello',
      ['world'],
      { 'nested': 'value' }
    ])
    self.assertEqual(len(graph.nodes), 6)
    self.assertEqual(len(graph.edges), 5)

    self.assertTrue('$[0]' in graph.nodes)
    self.assertTrue(('$', '$[0]') in graph.edges)
    self.assertEqual(
      graph.nodes['$[0]'],
      Node(path=[0], type='value', value='hello')
    )

    self.assertTrue('$[1]' in graph.nodes)
    self.assertTrue(('$', '$[1]') in graph.edges)
    self.assertEqual(
      graph.nodes['$[1]'],
      Node(path=[1], type='array', value=['world'])
    )

    self.assertTrue('$[1][0]' in graph.nodes)
    self.assertTrue(('$[1]', '$[1][0]') in graph.edges)
    self.assertEqual(
      graph.nodes['$[1][0]'],
      Node(path=[1, 0], type='value', value='world')
    )

    self.assertTrue('$[2]' in graph.nodes)
    self.assertTrue(('$', '$[2]') in graph.edges)
    self.assertEqual(
      graph.nodes['$[2]'],
      Node(path=[2], type='object', value={'nested': 'value'})
    )

    self.assertTrue('$[2].nested' in graph.nodes)
    self.assertTrue(('$[2]', '$[2].nested') in graph.edges)
    self.assertEqual(
      graph.nodes['$[2].nested'],
      Node(path=[2, 'nested'], type='value', value='value')
    )


if __name__ == '__main__':
  unittest.main()
