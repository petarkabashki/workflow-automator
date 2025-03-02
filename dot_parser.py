import re
from typing import Dict, List, Optional, Any

class DotParser:
    def parse(self, dot_content: str) -> Dict[str, Any]:
        """Parse DOT language content and return a Graph dictionary."""
        nodes: Dict[str, Dict[str, Any]] = {}
        edges: List[Dict[str, Any]] = []
        strict = "strict" in dot_content
        directed = "digraph" in dot_content

        for line in dot_content.splitlines():
            line = line.strip()
            if not line:
                continue

            # Node parsing
            node_match = re.match(r'(\w+)\s*\[(.*?)\]', line)
            if node_match:
                node_id = node_match.group(1)
                attrs_str = node_match.group(2)
                data = None
                if attrs_str:
                    # Simple data attribute extraction - treat as a string
                    # Use a more robust regex that can handle the entire content between quotes
                    data_match = re.search(r'data="(.*?)"', attrs_str)
                    if data_match:
                        data = data_match.group(1)
                nodes[node_id] = {"id": node_id, "data": data}
                continue
            
            # Node parsing without attributes
            node_match = re.match(r'(\w+);', line)
            if node_match:
                node_id = node_match.group(1)
                nodes[node_id] = {"id": node_id, "data": None}
                continue

            # Edge parsing with label and possibly data
            edge_match = re.match(r'(\w+)\s*->\s*(\w+)\s*\[(.*?)\]', line)
            if edge_match:
                source = edge_match.group(1)
                target = edge_match.group(2)
                attrs_str = edge_match.group(3)
                
                # Extract label
                label = None
                label_match = re.search(r'label\s*=\s*"([^"]*)"', attrs_str)
                if label_match:
                    label = label_match.group(1)
                    
                # Extract data
                data = None
                data_match = re.search(r'data="(.*?)"', attrs_str)
                if data_match:
                    data = data_match.group(1)
                    
                edges.append({"source": source, "target": target, "label": label, "data": data})
                if source not in nodes:
                    nodes[source] = {"id": source, "data": None}
                if target not in nodes:
                    nodes[target] = {"id": target, "data": None}
                continue
            
            edge_match = re.match(r'(\w+)\s*->\s*(\w+)', line)
            if edge_match:
                source = edge_match.group(1)
                target = edge_match.group(2)
                edges.append({"source": source, "target": target, "label": None, "data": None})
                if source not in nodes:
                    nodes[source] = {"id": source, "data": None}
                if target not in nodes:
                    nodes[target] = {"id": target, "data": None}
                continue

        return {
            "strict": strict,
            "directed": directed,
            "nodes": nodes,
            "edges": edges
        }

    # Pretty printing functions
    def print_graph(self, graph):
        print(f"Graph: strict={graph['strict']}, directed={graph['directed']}")
        print("\nNodes:")
        for node_id, node in graph['nodes'].items():
            print(f"  Node({node['id']}, data={node['data']})")
        
        print("\nEdges:")
        for edge in graph['edges']:
            print(f"  Edge({edge['source']} -> {edge['target']}, label={edge['label']}, data={edge['data']})")

    # Helper functions to maintain compatibility with tests
    def node_str(self, node):
        """Return string representation of a node dictionary."""
        return f"Node({node['id']}, data={node['data']})"

    def edge_str(self, edge):
        """Return string representation of an edge dictionary."""
        return f"Edge({edge['source']} -> {edge['target']}, label={edge['label']}, data={edge['data']})"

    def graph_str(self, graph):
        """Return string representation of a graph dictionary."""
        return f"Graph(strict={graph['strict']}, directed={graph['directed']}, nodes={list(graph['nodes'].keys())}, edges={len(graph['edges'])})"

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
        parser = DotParser()
        graph = parser.parse(dot_example)
        parser.print_graph(graph)
    except Exception as e:
        print(f"Error parsing DOT: {e}")
