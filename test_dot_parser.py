import unittest
from dot_parser import DotParser, Node, Edge, Graph, parse_dot

class TestDotParser(unittest.TestCase):
    def setUp(self):
        self.parser = DotParser()
        
        # Simple test graph
        self.simple_dot = '''
        strict digraph {
            node1[data="{\"key\": \"value\"}"]
            node1 -> node2[label="connection", data="{\"weight\": 5}"];
        }
        '''
        
        # More complex test graph (from the example)
        self.complex_dot = '''
        strict digraph {
            __start__[data="{m: 1, n: 2}"]
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
    
    def test_empty_string(self):
        """Test that an empty string produces an error."""
        # Empty string is not valid DOT syntax
        with self.assertRaises(ValueError):
            self.parser.parse("")
    
    def test_simple_graph_with_nodes_and_edges(self):
        """Test parsing a simple graph with nodes and edges."""
        dot_string = '''
        strict digraph {
            Start -> Process1;
            Process1 -> End;
        }
        '''
        graph = self.parser.parse(dot_string)
        
        self.assertEqual(len(graph.nodes), 3)
        self.assertIn('Start', graph.nodes)
        self.assertIn('Process1', graph.nodes)
        self.assertIn('End', graph.nodes)
        self.assertEqual(len(graph.edges), 2)
    
    def test_edge_label(self):
        """Test parsing edge label."""
        dot_string = '''
        strict digraph {
            Start -> End [label = "Test Label"];
        }
        '''
        graph = self.parser.parse(dot_string)
        
        self.assertEqual(len(graph.edges), 1)
        edge = graph.edges[0]
        self.assertEqual(edge.label, "Test Label")
    
    def test_edge_without_label(self):
        """Test edge without label."""
        dot_string = '''
        strict digraph {
            Start -> End;
        }
        '''
        graph = self.parser.parse(dot_string)
        
        self.assertEqual(len(graph.edges), 1)
        edge = graph.edges[0]
        self.assertIsNone(edge.label)
    
    def test_node_with_attributes(self):
        """Test node definition with attributes."""
        dot_string = '''
        strict digraph {
            Node1 [label="Test Node", data="{\"key\": \"value\"}"];
        }
        '''
        graph = self.parser.parse(dot_string)
        
        self.assertEqual(len(graph.nodes), 1)
        self.assertIn('Node1', graph.nodes)
        node = graph.nodes['Node1']
        self.assertEqual(node.data, {"key": "value"})
    
    def test_edge_with_json_data(self):
        """Test edge with JSON data attribute."""
        dot_string = '''
        strict digraph {
            Start -> End [data="{\"key\": \"value\", \"number\": 123}"];
        }
        '''
        graph = self.parser.parse(dot_string)
        
        self.assertEqual(len(graph.edges), 1)
        edge = graph.edges[0]
        self.assertEqual(edge.data, {"key": "value", "number": 123})
    
    def test_invalid_json_data(self):
        """Test handling of invalid JSON in data attributes."""
        dot_string = '''
        strict digraph {
            node1[data="{invalid json}"]
        }
        '''
        with self.assertRaises(ValueError):
            self.parser.parse(dot_string)
    
    def test_parse_simple_graph(self):
        """Test parsing a simple graph with a single node and edge."""
        graph = self.parser.parse(self.simple_dot)
        
        # Check graph properties
        self.assertTrue(graph.strict)
        self.assertTrue(graph.directed)
        
        # Check nodes
        self.assertEqual(len(graph.nodes), 2)  # node1 and node2 (implicitly created)
        self.assertIn('node1', graph.nodes)
        self.assertIn('node2', graph.nodes)
        
        # Check node1 data
        node1 = graph.nodes['node1']
        self.assertEqual(node1.id, 'node1')
        self.assertEqual(node1.data, {"key": "value"})
        
        # Check edges
        self.assertEqual(len(graph.edges), 1)
        edge = graph.edges[0]
        self.assertEqual(edge.source, 'node1')
        self.assertEqual(edge.target, 'node2')
        self.assertEqual(edge.label, 'connection')
        self.assertEqual(edge.data, {"weight": 5})
    
    def test_parse_complex_graph(self):
        """Test parsing a more complex graph with multiple nodes and edges."""
        graph = self.parser.parse(self.complex_dot)
        
        # Check graph properties
        self.assertTrue(graph.strict)
        self.assertTrue(graph.directed)
        
        # Check nodes
        expected_nodes = ['__start__', 'request_input', 'extract_n_check', 
                          'ask_confirmation', 'process_data', '__end__']
        for node_id in expected_nodes:
            self.assertIn(node_id, graph.nodes)
        
        # Check __start__ node data
        start_node = graph.nodes['__start__']
        self.assertEqual(start_node.data, {"m": 1, "n": 2})
        
        # Check edges
        self.assertEqual(len(graph.edges), 9)  # Correct number of edges
        
        # Check specific edge
        edge_found = False
        for edge in graph.edges:
            if (edge.source == 'request_input' and 
                edge.target == 'extract_n_check' and 
                edge.label == 'OK (Name and email provided)'):
                edge_found = True
                self.assertEqual(edge.data, {"m": 1, "n": 2})  # Now expecting a parsed dict
                break
        self.assertTrue(edge_found, "Expected edge not found")
    
    def test_parse_dot_function(self):
        """Test the parse_dot convenience function."""
        graph = parse_dot(self.simple_dot)
        self.assertTrue(isinstance(graph, Graph))
        self.assertEqual(len(graph.nodes), 2)
        self.assertEqual(len(graph.edges), 1)
    
    def test_node_str_representation(self):
        """Test the string representation of Node objects."""
        # This test doesn't need the parser
        node = Node(id="test_node", data={"key": "value"})
        self.assertEqual(str(node), "Node(test_node, data={'key': 'value'})")
    
    def test_edge_str_representation(self):
        """Test the string representation of Edge objects."""
        # This test doesn't need the parser
        edge = Edge(source="src", target="dst", label="test", data={"weight": 5})
        self.assertEqual(str(edge), "Edge(src -> dst, label=test, data={'weight': 5})")
    
    def test_graph_str_representation(self):
        """Test the string representation of Graph objects."""
        graph = self.parser.parse(self.simple_dot)
        expected_str = f"Graph(strict=True, directed=True, nodes={list(graph.nodes.keys())}, edges={len(graph.edges)})"
        self.assertEqual(str(graph), expected_str)
    
    def test_javascript_style_object_notation(self):
        """Test parsing JavaScript-style object notation in data attributes."""
        dot_string = '''
        strict digraph {
            Node1 [data="{key: 'value', num: 42, bool: true}"];
        }
        '''
        graph = self.parser.parse(dot_string)
        
        self.assertEqual(len(graph.nodes), 1)
        node = graph.nodes['Node1']
        self.assertEqual(node.data, {"key": "value", "num": 42, "bool": True})

if __name__ == '__main__':
    unittest.main()
