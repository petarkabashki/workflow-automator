import pytest
from dot_parser import DotParser

# Test that an empty string produces no nodes or edges.
def test_empty_string():
    parser = DotParser()
    parser.parse("")
    assert len(parser.nodes) == 0
    assert len(parser.edges) == 0

# Test that a completely malformed string produces no nodes or edges.
def test_malformed_string():
    parser = DotParser()
    parser.parse("invalid dot syntax")
    assert len(parser.nodes) == 0
    assert len(parser.edges) == 0

# Test that an unclosed quote stops parsing.
def test_unclosed_quote():
    parser = DotParser()
    parser.parse('"Start -> "End')
    assert len(parser.nodes) == 0
    assert len(parser.edges) == 0

# Test parsing a simple graph with three nodes and two edges (quoted).
def test_simple_graph_with_nodes_and_edges_quoted():
    dot_string = '''
    "Start" -> "Process1";
    "Process1" -> "End";
    '''
    
    parser = DotParser()
    parser.parse(dot_string)
    # raise Exception (parser.nodes)
    assert len(parser.nodes) == 3, "Expected 3 nodes"
    labels = [node.get('name') for node in parser.nodes] #check names, not labels
    assert "Start" in labels
    assert "Process1" in labels
    assert "End" in labels
    assert len(parser.edges) == 2

# Test parsing a simple graph with three nodes and two edges (unquoted).
def test_simple_graph_with_nodes_and_edges_unquoted():
    dot_string = '''
    Start -> Process1;
    Process1 -> End;
    '''
    parser = DotParser()
    parser.parse(dot_string)
    assert len(parser.nodes) == 3, "Expected 3 nodes"
    labels = [node.get('name') for node in parser.nodes]
    assert "Start" in labels
    assert "Process1" in labels
    assert "End" in labels
    assert len(parser.edges) == 2

# Test parsing a simple graph with mixed quoted and unquoted nodes.
def test_simple_graph_with_nodes_and_edges_mixed():
    dot_string = '''
    "Start" -> Process1;
    Process1 -> "End";
    '''
    parser = DotParser()
    parser.parse(dot_string)
    assert len(parser.nodes) == 3, "Expected 3 nodes"
    labels = [node.get('name') for node in parser.nodes]
    assert "Start" in labels
    assert "Process1" in labels
    assert "End" in labels
    assert len(parser.edges) == 2

# Test parsing edge label.
def test_edge_label():
    parser = DotParser()
    dot_string = '"Start" -> "End" [label = "Test Label"];'
    parser = DotParser()
    parser.parse(dot_string)
    assert len(parser.edges) == 1
    attrs = parser.edges[0].get('attributes', {})
    assert attrs.get('label') == "Test Label"

# Test that comments (single-line and multi-line) are ignored.
def test_comments():
    parser = DotParser()
    dot_string = '''
    // This is a single-line comment
    "Start" -> "End"; // inline comment
    /*
      This is a multi-line comment.
    */
    "A" -> "B";
    '''
    parser.parse(dot_string)
    assert len(parser.nodes) == 4
    assert len(parser.edges) == 2

# Test that a missing semicolon causes parsing to stop before later statements.
def test_missing_semicolon():
    parser = DotParser()
    dot_string = '"Start" -> "End" "A" -> "B";'
    parser.parse(dot_string)
    assert len(parser.edges) == 1
    assert parser.edges[0]['source'] == "Start"

# Test edge without label
def test_edge_without_label():
    parser = DotParser()
    dot_string = '"Start" -> "End";'
    parser.parse(dot_string)
    assert len(parser.edges) == 1
    assert 'attributes' not in parser.edges[0]

# Test edge without label and no attributes key
def test_edge_without_label_no_attributes():
    parser = DotParser()
    dot_string = 'process_data -> __end__;'
    parser.parse(dot_string)
    assert len(parser.edges) == 1
    assert parser.edges[0]['source'] == "process_data"
    assert parser.edges[0]['destination'] == "__end__"
    assert 'attributes' not in parser.edges[0] # Verify no attributes key is present

# Test incorrect keyword
def test_incorrect_keyword():
    parser = DotParser()
    dot_string = 'node "Start";'
    parser.parse(dot_string)
    assert len(parser.nodes) == 0
    assert len(parser.edges) == 0

# Test unquoted node names with special characters (but valid).
def test_unquoted_node_names_with_special_chars():
    parser = DotParser()
    dot_string = 'Start_Node -> End.Node;'
    parser.parse(dot_string)
    assert len(parser.nodes) == 2
    assert len(parser.edges) == 1
    assert parser.edges[0]['source'] == "Start_Node"
    assert parser.edges[0]['destination'] == "End.Node"

# Test unquoted node names with leading/trailing spaces (should be trimmed).
def test_unquoted_node_names_with_spaces():
    parser = DotParser()
    dot_string = '   Start   ->   End   ;'
    parser.parse(dot_string)
    assert len(parser.nodes) == 2
    assert len(parser.edges) == 1
    assert parser.edges[0]['source'] == "Start"
    assert parser.edges[0]['destination'] == "End"
