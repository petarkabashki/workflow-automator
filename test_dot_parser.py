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

def test_parse_multiple_edge_attributes():
    """Test parsing of multiple edge attributes."""
    parser = DotParser()
    dot_string = '''
    edge {
        color = "red";
        style = "dashed";
    }
    "Start" -> "End"
    '''
    parser.parse(dot_string)
    
    assert len(parser.edges) == 1
    edge = parser.edges[0]
    assert edge['source'] == 'Start'
    assert edge['destination'] == 'End'
    assert edge['attributes'] == {
        'color': 'red',
        'style': 'dashed'
    }

def test_parse_node_without_label():
    """Test parsing of a node without a label."""
    parser = DotParser()
    dot_string = '''
    node {
        color = "blue";
    }
    '''
    parser.parse(dot_string)
    
    assert len(parser.nodes) == 1
    node = parser.nodes[0]
    assert 'label' not in node
    assert node['attributes'] == {'color': 'blue'}

def test_parse_edge_without_label():
    """Test parsing of an edge without a label."""
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
    assert 'label' not in edge
    assert edge['attributes'] == {'color': 'red'}

def test_parse_simple_graph_with_nodes_and_edges(simple_dot_string):
    """Test parsing of a simple graph with nodes and edges."""
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
    """Test parsing of node attributes."""
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
    """Test parsing of edge attributes."""
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

def test_parse_empty_string():
    """Test parsing of an empty string."""
    parser = DotParser()
    parser.parse("")
    assert len(parser.nodes) == 0
    assert len(parser.edges) == 0

def test_parse_malformed_string():
    """Test parsing of a malformed string."""
    parser = DotParser()
    parser.parse("invalid dot syntax")
    assert len(parser.nodes) == 0
    assert len(parser.edges) == 0

def test_parse_multiple_node_attributes():
    """Test parsing of multiple node attributes."""
    parser = DotParser()
    dot_string = '''
    node {
        label = "Test";
        shape = "ellipse";
        color = "green";
    }
    '''
    parser.parse(dot_string)
    
    assert len(parser.nodes) == 1
    node = parser.nodes[0]
    assert node['attributes'] == {
        'label': 'Test',
        'shape': 'ellipse',
        'color': 'green'
    }
