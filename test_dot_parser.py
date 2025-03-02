import unittest
from dot_parser import DotParser

class TestDotParser(unittest.TestCase):
    def test_simple_graph_with_nodes_and_edges(self):
        """Test parsing a simple graph with nodes and edges."""
        dot_string = '''
        strict digraph {
            Start -> Process1;
            Process1 -> End;
        }
        '''
        parser = DotParser()
        graph = parser.parse(dot_string)
        
        self.assertEqual(len(graph['nodes']), 3)
        self.assertIn('Start', graph['nodes'])
        self.assertIn('Process1', graph['nodes'])
        self.assertIn('End', graph['nodes'])
        self.assertEqual(len(graph['edges']), 2)
    
    def test_edge_label(self):
        """Test parsing edge label."""
        dot_string = '''
        strict digraph {
            Start -> End [label = "Test Label"];
        }
        '''
        parser = DotParser()
        graph = parser.parse(dot_string)
        
        self.assertEqual(len(graph['edges']), 1)
        edge = graph['edges'][0]
        self.assertEqual(edge['label'], "Test Label")
    
    def test_edge_without_label(self):
        """Test edge without label."""
        dot_string = '''
        strict digraph {
            Start -> End;
        }
        '''
        parser = DotParser()
        graph = parser.parse(dot_string)
        
        self.assertEqual(len(graph['edges']), 1)
        edge = graph['edges'][0]
        self.assertIsNone(edge['label'])
    
    def test_node_with_attributes(self):
        """Test node definition with attributes."""
        dot_string = '''
        strict digraph {
            Node1 [label="Test Node", data="something here"];
        }
        '''
        parser = DotParser()
        graph = parser.parse(dot_string)
        
        self.assertEqual(len(graph['nodes']), 1)
        self.assertIn('Node1', graph['nodes'])
        node = graph['nodes']['Node1']
        self.assertEqual(node['data'], "something here")
    
    def test_parse_simple_graph(self):
        """Test parsing a simple graph with a single node and edge."""
        simple_dot = '''
        strict digraph {
            node1[data="some string here"]
            node1 -> node2[label="connection"];
        }
        '''
        parser = DotParser()
        graph = parser.parse(simple_dot)
        
        # Check graph properties
        self.assertTrue(graph['strict'])
        self.assertTrue(graph['directed'])
        
        # Check nodes
        self.assertEqual(len(graph['nodes']), 2)  # node1 and node2 (implicitly created)
        self.assertIn('node1', graph['nodes'])
        self.assertIn('node2', graph['nodes'])
        
        # Check node1 data
        node1 = graph['nodes']['node1']
        self.assertEqual(node1['id'], 'node1')
        self.assertEqual(node1['data'], "some string here")
        
        # Check edges
        self.assertEqual(len(graph['edges']), 1)
        edge = graph['edges'][0]
        self.assertEqual(edge['source'], 'node1')
        self.assertEqual(edge['target'], 'node2')
        self.assertEqual(edge['label'], 'connection')
    
    def test_parse_complex_graph(self):
        """Test parsing a more complex graph with multiple nodes and edges."""
        complex_dot = '''
        strict digraph {
            __start__[data="some string"]
            __start__ -> request_input;
            request_input -> extract_n_check[label="OK (Name and email provided)", data="{m: 1, n: 2}"];
            request_input -> request_input[label="NOK (Missing name or email)"];
            request_input -> __end__[label="QUIT"];

            extract_n_check -> request_input[label="NOK (Data missing)"];
            extract_n_check -> ask_confirmation[label="OK (Data extracted)"];
            ask_confirmation -> process_data[label="Y (Confirmed)"];
            ask_confirmation -> request_input[label="N (Not confirmed)"];
            ask_confirmation -> __end__[label="Q (Quit)"];
            process_data -> __end__;
        }
        '''
        parser = DotParser()
        graph = parser.parse(complex_dot)
        
        # Check graph properties
        self.assertTrue(graph['strict'])
        self.assertTrue(graph['directed'])
        
        # Check nodes
        expected_nodes = ['__start__', 'request_input', 'extract_n_check',
                          'ask_confirmation', 'process_data', '__end__']
        for node_id in expected_nodes:
            self.assertIn(node_id, graph['nodes'])
        
        # Check __start__ node data
        start_node = graph['nodes']['__start__']
        self.assertEqual(start_node['data'], "some string")
        
        # Check edges
        self.assertEqual(len(graph['edges']), 10)
        
        # Check specific edge
        edge_found = False
        for edge in graph['edges']:
            if (edge['source'] == 'request_input' and
                edge['target'] == 'extract_n_check' and
                edge['label'] == 'OK (Name and email provided)'):
                edge_found = True
                self.assertEqual(edge['data'], "{m: 1, n: 2}")
                break
        self.assertTrue(edge_found, "Expected edge not found")
    
    def test_node_str_representation(self):
        """Test the string representation of Node objects."""
        parser = DotParser()
        node = {"id": "test_node", "data": "{\"key\": \"value\"}"}
        self.assertEqual(parser.node_str(node), "Node(test_node, data={\"key\": \"value\"})")
    
    def test_edge_str_representation(self):
        """Test the string representation of Edge objects."""
        parser = DotParser()
        edge = {"source": "src", "target": "dst", "label": "test", "data": "{\"weight\": 5}"}
        self.assertEqual(parser.edge_str(edge), "Edge(src -> dst, label=test, data={\"weight\": 5})")
    
    def test_graph_str_representation(self):
        """Test the string representation of Graph objects."""
        parser = DotParser()
        simple_dot = '''
        strict digraph {
            node1[data="something"]
            node1 -> node2[label="connection"];
        }
        '''
        graph = parser.parse(simple_dot)
        expected_str = f"Graph(strict={graph['strict']}, directed={graph['directed']}, nodes={list(graph['nodes'].keys())}, edges={len(graph['edges'])})"
        self.assertEqual(parser.graph_str(graph), expected_str)
    
    def test_javascript_style_object_notation(self):
        """Test parsing JavaScript-style object notation in data attributes."""
        dot_string = '''
        strict digraph {
            Node1 [data="{key: 'value', num: 42, bool: true}"];
        }
        '''
        parser = DotParser()
        graph = parser.parse(dot_string)
        
        self.assertEqual(len(graph['nodes']), 1)
        node = graph['nodes']['Node1']
        self.assertEqual(node['data'], "{key: 'value', num: 42, bool: true}")
        
    def test_node_with_no_attributes(self):
        """Test node definition without attributes."""
        dot_string = '''
        strict digraph {
            Node1;
        }
        '''
        parser = DotParser()
        graph = parser.parse(dot_string)

        self.assertEqual(len(graph['nodes']), 1)
        self.assertIn('Node1', graph['nodes'])
        node = graph['nodes']['Node1']
        self.assertIsNone(node['data'])

    def test_node_with_empty_attributes(self):
        """Test node definition with empty attributes."""
        dot_string = '''
        strict digraph {
            Node1 [];
        }
        '''
        parser = DotParser()
        graph = parser.parse(dot_string)

        self.assertEqual(len(graph['nodes']), 1)
        self.assertIn('Node1', graph['nodes'])
        node = graph['nodes']['Node1']
        self.assertIsNone(node['data'])

if __name__ == '__main__':
    unittest.main()
