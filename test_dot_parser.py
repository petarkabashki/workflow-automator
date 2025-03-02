import pytest
from dot_parser import DotParser

# Test that an empty string produces no nodes or edges.
def test_empty_string():
    parser = DotParser()
    parser.parse("")
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

# Test node definition with attributes
# @pytest.mark.skip(reason="Test might be failing, needs investigation")
def test_node_definition_with_attributes():
    parser = DotParser()
    dot_string = 'Node1 [label="Test Node", data="{\\"key\\": \\"value\\"}"];'
    parser.parse(dot_string)
    assert len(parser.nodes) == 1
    assert parser.nodes[0]['name'] == "Node1"
    assert 'attributes' in parser.nodes[0]
    assert parser.nodes[0]['attributes']['label'] == "Test Node"
    assert parser.nodes[0]['attributes']['data'] == {"key": "value"}

# Test node definition without attributes
# @pytest.mark.skip(reason="Test might be failing, needs investigation")
def test_node_definition_without_attributes():
    parser = DotParser()
    dot_string = 'Node1;'
    parser.parse(dot_string)
    assert len(parser.nodes) == 1
    assert parser.nodes[0]['name'] == "Node1"

# Test quoted node definition
# @pytest.mark.skip(reason="Test might be failing, needs investigation")
def test_quoted_node_definition():
    parser = DotParser()
    dot_string = '"Node with spaces" [label="Test"];'
    parser.parse(dot_string)
    assert len(parser.nodes) == 1
    assert parser.nodes[0]['name'] == "Node with spaces"
    assert parser.nodes[0]['attributes']['label'] == "Test"

# Test mixed node definitions and edge connections
# @pytest.mark.skip(reason="Test might be failing, needs investigation")
def test_mixed_node_and_edge_definitions():
    parser = DotParser()
    dot_string = '''
    Node1 [label="First Node"];
    Node2 [label="Second Node"];
    Node1 -> Node2;
    '''
    parser.parse(dot_string)
    assert len(parser.nodes) == 2
    assert len(parser.edges) == 1
    assert parser.nodes[0]['attributes']['label'] == "First Node"
    assert parser.nodes[1]['attributes']['label'] == "Second Node"
    assert parser.edges[0]['source'] == "Node1"
    assert parser.edges[0]['destination'] == "Node2"

# Test edge with JSON attribute
# @pytest.mark.skip(reason="Test might be failing, needs investigation")
def test_edge_json_attribute():
    parser = DotParser()
    dot_string = '"Start" -> "End" [data="{\\"key\\": \\"value\\", \\"number\\": 123}"];'
    parser.parse(dot_string)
    assert len(parser.edges) == 1
    attrs = parser.edges[0].get('attributes', {})
    assert "data" in attrs
    assert isinstance(attrs["data"], dict)
    assert attrs["data"] == {"key": "value", "number": 123} # assert against the parsed dict

# Test edge with string attribute
# @pytest.mark.skip(reason="Test might be failing, needs investigation")
def test_edge_string_attribute():
    parser = DotParser()
    dot_string = '"Start" -> "End" [config = "string value"];'
    parser.parse(dot_string)
    assert len(parser.edges) == 1
    attrs = parser.edges[0].get('attributes', {})
    assert "config" in attrs
    assert isinstance(attrs["config"], str)
    assert attrs["config"] == "string value"

# Test edge with invalid JSON attribute (should fallback to string)
# @pytest.mark.skip(reason="Test might be failing, needs investigation")
def test_edge_json_attribute_invalid_json_fallback_string():
    parser = DotParser()
    dot_string = '"Start" -> "End" [data="{invalid json}"];'
    parser.parse(dot_string)
    assert len(parser.edges) == 1
    attrs = parser.edges[0].get('attributes', {})
    assert attrs.get('data') == "{invalid json}"
