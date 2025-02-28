"""Tests for the DotParser class."""
import pytest
from dot_parser import DotParser

# Fixtures
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

# Basic parsing tests
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

def test_parse_unclosed_quote():
    """Test parsing with an unclosed quote."""
    parser = DotParser()
    parser.parse('node "Start { label = "Start"; }')
    assert len(parser.nodes) == 0
    assert len(parser.edges) == 0

def test_parse_invalid_identifier():
    """Test parsing with invalid characters in an identifier."""
    parser = DotParser()
    parser.parse('node "Start!" { label = "Start"; }')
    assert len(parser.nodes) == 0  # Or handle the error as appropriate
    assert len(parser.edges) == 0

def test_parse_missing_semicolon():
    """Test parsing with a missing semicolon."""
    parser = DotParser()
    parser.parse('node "Start" { label = "Start" } "Start" -> "End"')
    assert len(parser.nodes) == 1 #parsing stops at the missing semicolon
    assert len(parser.edges) == 0

def test_parse_incorrect_keyword():
    """Test parsing with an incorrect keyword."""
    parser = DotParser()
    parser.parse('nodee "Start" { label = "Start"; }')
    assert len(parser.nodes) == 0
    assert len(parser.edges) == 0

def test_parse_duplicate_node():
    """Test parsing with duplicate node declarations."""
    parser = DotParser()
    parser.parse('node "Start" { label = "A"; } node "Start" { label = "B"; }')
     # Only the first declaration should be considered.
    assert len(parser.nodes) == 1
    assert parser.nodes[0]['label'] == 'A'

#
def test_parse_simple_graph_with_nodes_and_edges(simple_dot_string):
    """Test parsing of a simple graph with nodes and edges."""
    parser = DotParser()
    parser.parse(simple_dot_string)

    # Verify nodes
    assert len(parser.nodes) == 3, "Expected 3 nodes"
    labels = [node['label'] for node in parser.nodes]
    assert 'Start' in labels, "Start node should be present"
    assert 'Process1' in labels, "Process1 node should be present"
    assert 'End' in labels, "End node should be present"

    # Verify edges
    assert len(parser.edges) == 2, "Expected 2 edges"
    edge_sources = [edge['source'] for edge in parser.edges]
    edge_destinations = [edge['destination'] for edge in parser.edges]
    assert 'Start' in edge_sources, "Start node should be a source"
    assert 'Process1' in edge_destinations, "Process1 node should be a destination"
    assert 'Process1' in edge_sources, "Process1 node should be a source"
    assert 'End' in edge_destinations, "End node should be a destination"

# Node attribute tests
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

# Edge attribute tests
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

def test_parse_different_edge_connection():
    """Test parsing of different edge connection styles (e.g., --)."""
    parser = DotParser()
    dot_string = '"Start" -- "End"'
    parser.parse(dot_string)
    assert len(parser.edges) == 1
    assert parser.edges[0]['source'] == 'Start'
    assert parser.edges[0]['destination'] == 'End'
    assert parser.edges[0]['connector'] == '--'

def test_parse_combined_node_and_edge_attributes():
    """Test parsing of combined node and edge attributes."""
    parser = DotParser()
    dot_string = '''
    node {
        color = "blue";
    }
    edge {
        style = "dashed";
    }
    "Start" -> "Process" {
        color = "red";
    };
    "Process" -> "End";
    '''
    parser.parse(dot_string)
    assert len(parser.nodes) == 1
    assert len(parser.edges) == 2
    assert parser.nodes[0]['attributes']['color'] == 'blue'
    assert parser.edges[0]['attributes']['style'] == 'dashed'
    assert parser.edges[0]['attributes']['color'] == 'red'  # Specific edge attr
    assert parser.edges[1]['attributes']['style'] == 'dashed' #edge default carried
    assert 'color' not in parser.edges[1]['attributes']

def test_parse_comments():
    """Test parsing of comments."""
    parser = DotParser()
    dot_string = '''
    // This is a single-line comment
    node "Start" {
        label = "Start";  // Another comment
    }
    /*
     * This is a
     * multi-line comment.
     */
    "Start" -> "End";
    '''
    parser.parse(dot_string)
    assert len(parser.nodes) == 1
    assert len(parser.edges) == 1
    assert parser.nodes[0]['label'] == 'Start'
    assert parser.edges[0]['source'] == 'Start'
    assert parser.edges[0]['destination'] == 'End'

def test_node_no_attributes():
    parser = DotParser()
    dot_string = 'node "start";'
    parser.parse(dot_string)
    assert len(parser.nodes) == 1
    assert 'attributes' not in parser.nodes[0]

def test_edge_no_attributes():
    parser = DotParser()
    dot_string = '"start" -> "end";'
    parser.parse(dot_string)
    assert len(parser.edges) == 1
    assert 'attributes' not in parser.edges[0]
