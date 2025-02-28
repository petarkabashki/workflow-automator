import re

class DotParser:
    """Parses a DOT language string into a graph structure."""

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.default_edge_attributes = {}  # Initialize default_edge_attributes

    def parse(self, dot_string):
        """Parse a DOT language string and create a graph."""
        lines = dot_string.split('\n')
        lines = [line.strip() for line in lines]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip comments
            if line.startswith('//') or line.startswith('/*'):
                if line.startswith('/*') and '*/' not in line:
                    # Handle multi-line comments.  Assume they end eventually.
                    continue  # Skip until we find the end of the multi-line comment
                else:
                    continue # Skip single line comments

            if line.startswith('node'):
                self._parse_node(line)
            elif line.startswith('edge'):
                self._parse_edge(line)
            elif '->' in line or '--' in line:
                self._parse_edge_connection(line)

    def _parse_node(self, line):
        """Parses a node definition line."""
        # Match node with attributes
        node_match = re.match(r'node\s+"([^"]+)"\s*\{(.*)\}', line)
        if node_match:
            node_name = node_match.group(1).strip()
            attributes_str = node_match.group(2).strip()
            attributes = self._parse_attributes(attributes_str)
            label = attributes.get('label', node_name)
            self.nodes.append({'name': node_name, 'label': label, 'attributes': attributes})
            return

        # Match node without attributes, but with a name
        node_match = re.match(r'node\s+"([^"]+)"\s*;?', line)
        if node_match:
            node_name = node_match.group(1).strip()
            self.nodes.append({'name': node_name, 'label': node_name})
            return

        # Match default node attributes
        node_match = re.match(r'node\s*\{(.*)\}', line)
        if node_match:
            attributes_str = node_match.group(1).strip()
            attributes = self._parse_attributes(attributes_str)
            # Apply to subsequently defined nodes
            if attributes: # Only if not empty
              self.default_node_attributes = attributes
            return

    def _parse_edge(self, line):
        """Parses an edge definition line."""
        edge_match = re.match(r'edge\s*\{(.*)\}', line)
        if edge_match:
            attributes_str = edge_match.group(1).strip()
            self.default_edge_attributes = self._parse_attributes(attributes_str)
            return

    def _parse_edge_connection(self, line):
        """Parse an edge connection line."""
        # Handle edge with attributes
        edge_match = re.match(r'"([^"]+)"\s*([-<>]+)\s*"([^"]+)"\s*\{(.*)\}', line)
        if edge_match:
            source = edge_match.group(1).strip()
            connector = edge_match.group(2).strip()
            destination = edge_match.group(3).strip()
            attributes_str = edge_match.group(4).strip()
            attributes = self._parse_attributes(attributes_str)
            attributes = {**self.default_edge_attributes, **attributes}  # Merge with defaults
            self.edges.append({
                'source': source,
                'destination': destination,
                'connector': connector,
                'attributes': attributes
            })
            return

        # Handle edge without attributes
        edge_match = re.match(r'"([^"]+)"\s*([-<>]+)\s*"([^"]+)"\s*;?', line)
        if edge_match:
            source = edge_match.group(1).strip()
            connector = edge_match.group(2).strip()
            destination = edge_match.group(3).strip()
            self.edges.append({
                'source': source,
                'destination': destination,
                'connector': connector,
                'attributes': self.default_edge_attributes.copy()  # Use a copy of defaults
            })
            return

    def _parse_attributes(self, attributes_str):
        """Parses a string of attributes."""
        attributes = {}
        if attributes_str:
            for attr in re.split(r';\s*', attributes_str):
                attr = attr.strip()
                if attr:
                    if '=' in attr:
                        key, value = attr.split('=', 1)
                        attributes[key.strip()] = value.strip().strip('"')
                    else:
                        attributes[attr.strip()] = True
        return attributes

