import re

class DotParser:
    """Parses a DOT language string into a graph structure."""
    
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.in_node = False
        self.in_edge = False
        
    def parse(self, dot_string):
        """Parse a DOT language string and create a graph."""
        lines = dot_string.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('node'):
                self._parse_node(line)
            elif line.startswith('edge'):
                self._parse_edge(line)
            elif '->' in line:
                self._parse_edge_connection(line)
    
    def _parse_node(self, line):
        """Parses a node definition line."""
        node_match = re.match(r'\s*(node\s*)?"([^"]+)"\s*\{(.*)\}', line)
        if node_match:
            node_name = node_match.group(2)
            attributes_str = node_match.group(3).strip()
            attributes = {}
            if attributes_str:
                # Split attributes by semicolon and parse each
                for attr in attributes_str.split(';'):
                    attr = attr.strip()
                    if attr:
                        if '=' in attr:
                            key, value = attr.split('=', 1)
                            attributes[key.strip()] = value.strip().strip('"')
                        else:
                            attributes[attr.strip()] = True  # Handle boolean attributes

            self.nodes.append({'name': node_name, 'label': attributes.get('label', node_name), 'attributes': attributes})
        else:
            node_match = re.match(r'\s*(node\s*)?"([^"]+)"\s*;', line)
            if node_match:
                node_name = node_match.group(2)
                self.nodes.append({'name': node_name, 'label': node_name, 'attributes': {}})
    
    def _parse_edge(self, line):
        """Parses an edge definition line."""
        # First, check for default edge attributes
        edge_match = re.match(r'\s*edge\s*\{(.*)\}', line)
        if edge_match:
            attributes_str = edge_match.group(1).strip()
            default_attributes = {}
            if attributes_str:
                # Split attributes by semicolon and parse each
                for attr in attributes_str.split(';'):
                    attr = attr.strip()
                    if attr:
                        if '=' in attr:
                            key, value = attr.split('=', 1)
                            default_attributes[key.strip()] = value.strip().strip('"')
                        else:
                            default_attributes[attr.strip()] = True  # Handle boolean attributes
            # Store default attributes for later use
            self.default_edge_attributes = default_attributes
            return  # Skip adding this as a separate edge

        # Then, check for an edge definition with source and destination nodes
        edge_match = re.match(r'\s*"([^"]+)"\s*->\s*"([^"]+)"\s*;', line)
        if edge_match:
            source_node = edge_match.group(1)
            dest_node = edge_match.group(2)
            edge = {'source': source_node, 'destination': dest_node, 'attributes': {}}
            if hasattr(self, 'default_edge_attributes'):
                edge['attributes'].update(self.default_edge_attributes)
            self.edges.append(edge)
    
    def _parse_edge_connection(self, line):
        """Parse an edge connection line."""
        if '->' in line:
            source, dest = line.split('->', 1)
            source = source.strip().strip('"')
            dest = dest.strip().strip('"')
            
            edge = {
                'source': source,
                'destination': dest,
                'attributes': {}
            }
            self.edges.append(edge)
    
    def _parse_label(self, line):
        """Parses a label attribute."""
        label_match = re.match(r'\s*label\s*=\s*"([^"]+)"\s*;', line)
        if label_match:
            return label_match.group(1)
        return None
