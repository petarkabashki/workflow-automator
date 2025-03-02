import pytest
from dot_parser import DotParser, tokenize, build_graph

# Test that an empty string produces no nodes or edges.
def test_empty_string():
    parser = DotParser(tokenize(""))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["nodes"]) == 0
    assert len(graph["edges"]) == 0

# Test parsing a simple graph with three nodes and two edges (quoted).
def test_simple_graph_with_nodes_and_edges_quoted():
    dot_string = '''
    "Start" -> "Process1";
    "Process1" -> "End";
    '''
    
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["nodes"]) == 3, "Expected 3 nodes"
    assert "Start" in graph["nodes"]
    assert "Process1" in graph["nodes"]
    assert "End" in graph["nodes"]
    assert len(graph["edges"]) == 2

# Test parsing a simple graph with three nodes and two edges (unquoted).
def test_simple_graph_with_nodes_and_edges_unquoted():
    dot_string = '''
    Start -> Process1;
    Process1 -> End;
    '''
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["nodes"]) == 3, "Expected 3 nodes"
    assert "Start" in graph["nodes"]
    assert "Process1" in graph["nodes"]
    assert "End" in graph["nodes"]
    assert len(graph["edges"]) == 2

# Test parsing a simple graph with mixed quoted and unquoted nodes.
def test_simple_graph_with_nodes_and_edges_mixed():
    dot_string = '''
    "Start" -> Process1;
    Process1 -> "End";
    '''
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["nodes"]) == 3, "Expected 3 nodes"
    assert "Start" in graph["nodes"]
    assert "Process1" in graph["nodes"]
    assert "End" in graph["nodes"]
    assert len(graph["edges"]) == 2

# Test parsing edge label.
def test_edge_label():
    dot_string = '"Start" -> "End" [label = "Test Label"];'
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["edges"]) == 1
    attrs = graph["edges"][0].get('attributes', {})
    assert attrs.get('label') == "Test Label"

# Test that comments (single-line and multi-line) are ignored.
def test_comments():
    dot_string = '''
    // This is a single-line comment
    "Start" -> "End"; // inline comment
    /*
    This is a multi-line comment.
    */
    "A" -> "B";
    '''
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["nodes"]) == 4
    assert len(graph["edges"]) == 2

# Test that a missing semicolon causes parsing to stop before later statements.
def test_missing_semicolon():
    dot_string = '"Start" -> "End" "A" -> "B";'
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]['source'] == "Start"

# Test edge without label
def test_edge_without_label():
    dot_string = '"Start" -> "End";'
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["edges"]) == 1
    assert 'attributes' not in graph["edges"][0] or not graph["edges"][0]['attributes']

# Test edge without label and no attributes key
def test_edge_without_label_no_attributes():
    dot_string = 'process_data -> __end__;'
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]['source'] == "process_data"
    assert graph["edges"][0]['target'] == "__end__"
    assert 'attributes' not in graph["edges"][0] or not graph["edges"][0]['attributes'] # Verify no attributes key is present

# Test unquoted node names with special characters (but valid).
def test_unquoted_node_names_with_special_chars():
    dot_string = 'Start_Node -> End.Node;'
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]['source'] == "Start_Node"
    assert graph["edges"][0]['target'] == "End.Node"

# Test unquoted node names with leading/trailing spaces (should be trimmed).
def test_unquoted_node_names_with_spaces():
    dot_string = '   Start   ->   End   ;'
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]['source'] == "Start"
    assert graph["edges"][0]['target'] == "End"

# Test node definition with attributes
def test_node_definition_with_attributes():
    dot_string = 'Node1 [label="Test Node", data="{\\"key\\": \\"value\\"}"];'
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["nodes"]) == 1
    assert "Node1" in graph["nodes"]
    node_attrs = graph["nodes"]["Node1"]
    assert 'label' in node_attrs
    assert node_attrs['label'] == "Test Node"
    assert isinstance(node_attrs['data'], dict) # assert type is dict
    assert node_attrs['data']['key'] == "value" # assert key and value

# Test node definition without attributes
def test_node_definition_without_attributes():
    dot_string = 'Node1;'
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["nodes"]) == 1
    assert "Node1" in graph["nodes"]

# Test quoted node definition
def test_quoted_node_definition():
    dot_string = '"Node with spaces" [label="Test"];'
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["nodes"]) == 1
    assert "Node with spaces" in graph["nodes"]
    assert graph["nodes"]["Node with spaces"]['label'] == "Test"

# Test mixed node definitions and edge connections
def test_mixed_node_and_edge_definitions():
    dot_string = '''
    Node1 [label="First Node"];
    Node2 [label="Second Node"];
    Node1 -> Node2;
    '''
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1
    assert graph["nodes"]["Node1"]['label'] == "First Node"
    assert graph["nodes"]["Node2"]['label'] == "Second Node"
    assert graph["edges"][0]['source'] == "Node1"
    assert graph["edges"][0]['target'] == "Node2"

# Test edge with JSON attribute
def test_edge_json_attribute():
    dot_string = '"Start" -> "End" [data="{\\"key\\": \\"value\\", \\"number\\": 123}"];'
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["edges"]) == 1
    attrs = graph["edges"][0].get('attributes', {})
    assert "data" in attrs
    assert attrs["data"]["key"] == "value" # assert key and value
    assert attrs["data"]["number"] == 123 # assert key and value

# Test edge with string attribute
def test_edge_string_attribute():
    dot_string = '"Start" -> "End" [config = "string value"];'
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["edges"]) == 1
    attrs = graph["edges"][0].get('attributes', {})
    assert "config" in attrs
    assert isinstance(attrs["config"], str)
    assert attrs["config"] == "string value"

# Test edge with invalid JSON attribute (should fallback to string)
def test_edge_json_attribute_invalid_json_fallback_string():
    dot_string = '"Start" -> "End" [data="{invalid json}"];'
    parser = DotParser(tokenize(dot_string))
    ast = parser.parse()
    graph = build_graph(ast)
    assert len(graph["edges"]) == 1
    attrs = graph["edges"][0].get('attributes', {})
    assert attrs.get('data') == "{invalid json}"
