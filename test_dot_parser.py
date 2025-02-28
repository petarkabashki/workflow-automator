"""Tests for the DotParser class."""
import pytest
from dot_parser import DotParser

@pytest.fixture
def simple_dot_string():
    return """
node "Start" {
        label = "Start";
    }
    "Start" -> "Process1";
    "Process1" -> "End";
    "End" {
        label = "End";
    }
    """

def test_parse_simple_graph(simple_dot_string):
    parser = DotParser()
    parser.parse(simple_dot_string)
    
    # Verify nodes
    assert len(parser.nodes) == 3
    assert any(node.get('label') == 'Start' for node in parser.nodes)
    assert any(node.get('label') == 'End' for node in parser.nodes)
    
    # Verify edges
    assert len(parser.edges) == 2
    assert any(edge['source'] == 'Start' and edge['destination'] == 'Process1' for edge in parser.edges)
    assert any(edge['source'] == 'Process1' and edge['destination'] == 'End' for edge in parser.edges)

def test_parse_node_attributes():
    parser = DotParser()
    dot_string = '''
    node {
        label = "Test Node";
        color = "blue";
    }
    '''
    parser.parse(dot_string)
    
    assert len(parser.nodes) == 1
    node = parser.nodes[0]
    assert node['label'] == 'Test Node'
    assert node['attributes'] == {'label': 'Test Node', 'color': 'blue'}

def test_parse_edge_attributes():
    parser = DotParser()
    dot_string = '''
    edge {
        color = "red";
    }
    "Start" -> "End"
    '''
    parser.parse(dot_string)
    
    assert len(parser.edges) == 1
    edge = parser.edges[0]
    assert edge['source'] == 'Start'
    assert edge['destination'] == 'End'
    assert edge['attributes'] == {'color': 'red'}
