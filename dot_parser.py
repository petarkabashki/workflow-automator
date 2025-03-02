from lark import Lark, Transformer, v_args
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Any

@dataclass
class Node:
    id: str
    data: Optional[Dict] = None
    
    def __str__(self):
        return f"Node({self.id}, data={self.data})"

@dataclass
class Edge:
    source: str
    target: str
    label: Optional[str] = None
    data: Optional[Dict] = None
    
    def __str__(self):
        return f"Edge({self.source} -> {self.target}, label={self.label}, data={self.data})"

@dataclass
class Graph:
    strict: bool
    directed: bool
    nodes: Dict[str, Node]
    edges: List[Edge]

class DotParser:
    def __init__(self):
        # Define the grammar for the subset of DOT language
        self.grammar = r"""
        start: graph
        
        graph: strict? graph_type "{" stmt_list "}"
        strict: "strict"
        graph_type: "digraph"
        
        stmt_list: stmt (";" stmt)* ";"?
                 | 
        stmt: node_stmt | edge_stmt
        
        node_stmt: node_id attr_list?
        node_id: ID
        
        edge_stmt: node_id "->" node_id attr_list?
        
        attr_list: "[" attr ("," attr)* "]"
        attr: ID "=" value
        
        value: STRING | ID
        
        ID: /[a-zA-Z_][a-zA-Z0-9_]*/
        STRING: /"(?:[^"\\]|\\.)*"/ | /'(?:[^'\\]|\\.)*'/
        
        %import common.WS
        %ignore WS
        """
        
        self.parser = Lark(self.grammar, parser='lalr', transformer=DotTransformer())
    
    def parse(self, dot_content: str) -> Graph:
        """Parse DOT language content and return a Graph object."""
        if not dot_content.strip():
            raise ValueError("Empty DOT content")
            
        try:
            return self.parser.parse(dot_content)
        except Exception as e:
            raise ValueError(f"Failed to parse DOT content: {e}")

class DotTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.nodes = {}
        self.edges = []
        self.strict = False
        self.directed = False
    
    @v_args(inline=True)
    def strict(self, _):
        self.strict = True
        return True
    
    @v_args(inline=True)
    def graph_type(self, graph_type):
        self.directed = graph_type.value == "digraph"
        return self.directed
    
    def node_id(self, items):
        return str(items[0].value)
    
    def attr(self, items):
        key = str(items[0].value)
        value = self._process_value(items[1])
        return (key, value)
    
    def attr_list(self, items):
        return dict(items)
    
    def node_stmt(self, items):
        node_id = items[0]
        attrs = items[1] if len(items) > 1 else {}
        
        # Process data attribute if present
        data = None
        if 'data' in attrs:
            try:
                data = self._parse_data(attrs['data'])
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON in data attribute: {attrs['data']}")
        
        node = Node(id=node_id, data=data)
        self.nodes[node_id] = node
        return node
    
    def edge_stmt(self, items):
        source = items[0]
        target = items[1]
        attrs = items[2] if len(items) > 2 else {}
        
        # Process attributes
        label = attrs.get('label')
        if label and (label.startswith('"') or label.startswith("'")):
            # Remove quotes if present
            label = label[1:-1]
        
        # Process data attribute if present
        data = None
        if 'data' in attrs:
            try:
                data = self._parse_data(attrs['data'])
            except json.JSONDecodeError:
                # If it's not valid JSON, keep the original string
                data = attrs['data']
        
        edge = Edge(source=source, target=target, label=label, data=data)
        self.edges.append(edge)
        
        # Ensure both nodes exist in the graph
        if source not in self.nodes:
            self.nodes[source] = Node(id=source)
        if target not in self.nodes:
            self.nodes[target] = Node(id=target)
            
        return edge
    
    def stmt(self, items):
        return items[0]
    
    def stmt_list(self, items):
        return items
    
    def graph(self, items):
        # Process strict flag if present
        i = 0
        if items and isinstance(items[0], bool):
            self.strict = items[0]
            i += 1
        
        # Process directed flag
        if i < len(items) and isinstance(items[i], bool):
            self.directed = items[i]
            i += 1
        
        # Skip the opening and closing braces in our grammar
        return Graph(
            strict=self.strict,
            directed=self.directed,
            nodes=self.nodes,
            edges=self.edges
        )
    
    def start(self, items):
        return items[0]
    
    def value(self, items):
        return items[0].value
    
    def _process_value(self, value_token):
        value = value_token.value
        if isinstance(value, str) and (value.startswith('"') or value.startswith("'")):
            # Remove quotes for string values
            return value[1:-1]
        return value
    
    def _parse_data(self, data_str):
        # Handle the case where data is a JSON string
        if isinstance(data_str, str):
            # Remove quotes if they exist
            if (data_str.startswith('"') and data_str.endswith('"')) or \
               (data_str.startswith("'") and data_str.endswith("'")):
                data_str = data_str[1:-1]
                
            # Try to parse as JSON
            try:
                # Sometimes JSON uses single quotes instead of double quotes
                data_str_fixed = data_str.replace("'", '"')
                return json.loads(data_str_fixed)
            except json.JSONDecodeError:
                # If it's not valid JSON but has a format like {m: 1, n: 2}
                # Try to convert it to proper JSON
                if data_str.strip().startswith('{') and data_str.strip().endswith('}'):
                    try:
                        # Convert JavaScript-style object to Python dict
                        # This is a simple implementation that handles basic cases
                        content = data_str.strip()[1:-1]  # Remove { }
                        pairs = [pair.strip() for pair in content.split(',')]
                        result = {}
                        for pair in pairs:
                            if ':' in pair:
                                key, value = [p.strip() for p in pair.split(':', 1)]
                                # Remove quotes from key if present
                                if (key.startswith('"') and key.endswith('"')) or \
                                   (key.startswith("'") and key.endswith("'")):
                                    key = key[1:-1]
                                
                                # Try to convert value to appropriate type
                                try:
                                    if value.isdigit():
                                        value = int(value)
                                    elif value.replace('.', '', 1).isdigit():
                                        value = float(value)
                                    elif value.lower() == 'true':
                                        value = True
                                    elif value.lower() == 'false':
                                        value = False
                                    elif value.lower() == 'null':
                                        value = None
                                except:
                                    pass  # Keep as string if conversion fails
                                
                                result[key] = value
                        return result
                    except:
                        # If parsing fails, return the original string
                        return data_str
                return data_str
        return data_str

# Example usage
def parse_dot(dot_content):
    parser = DotParser()
    graph = parser.parse(dot_content)
    return graph

# Pretty printing functions
def print_graph(graph):
    print(f"Graph: strict={graph.strict}, directed={graph.directed}")
    print("\nNodes:")
    for node_id, node in graph.nodes.items():
        print(f"  {node}")
    
    print("\nEdges:")
    for edge in graph.edges:
        print(f"  {edge}")

# Test with the provided example
if __name__ == "__main__":
    dot_example = '''
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
    
    try:
        graph = parse_dot(dot_example)
        print_graph(graph)
    except Exception as e:
        print(f"Error parsing DOT: {e}")
