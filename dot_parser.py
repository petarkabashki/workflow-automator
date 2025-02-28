import re

class DotParser:
    """Parses a DOT language string into a graph structure."""

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.default_node_attributes = {}
        self.default_edge_attributes = {}

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
                    continue
                else:
                    continue

            if line.startswith('node'):
                self._parse_node_definition(line)
            elif line.startswith('edge'):
                self._parse_edge_definition(line)
            elif '->' in line or '--' in line:
                self._parse_edge_connection(line)
            else:
                self._parse_standalone_node(line)  # Handle nodes w/o "node"

    def _parse_node_definition(self, line):
        """Parses a node definition line (starting with 'node')."""
        # Match default node attributes ONLY
        match = re.match(r'node\s*\{(.*)\}', line)
        if match:
            attributes_str = match.group(1).strip()
            self.default_node_attributes = self._parse_attributes(attributes_str)
            return  # Important: Only set defaults, don't create a node

        # Match node with name and attributes
        match = re.match(r'node\s+"([^"]+)"\s*\{([^}]*)\}', line)
        if match:
            node_name = match.group(1).strip()
            attributes_str = match.group(2).strip()
            attributes = self._parse_attributes(attributes_str)
            label = attributes.get('label', node_name)
            # Apply default attributes *before* adding inline attributes
            node_attributes = self.default_node_attributes.copy()
            node_attributes.update(attributes)
            self.nodes.append({'name': node_name, 'label': label, 'attributes': node_attributes})
            return

        # Match node with just a name (no inline attributes)
        match = re.match(r'node\s+"([^"]+)"\s*;?', line)
        if match:
            node_name = match.group(1).strip()
            node_data = {'name': node_name, 'label': node_name}
            if self.default_node_attributes:
                node_data['attributes'] = self.default_node_attributes.copy()
            self.nodes.append(node_data)
            return

    def _parse_standalone_node(self, line):
        """Parses a node defined without the 'node' keyword."""
        match = re.match(r'"([^"]+)"\s*\{([^}]*)\}', line)
        if match:
            node_name = match.group(1).strip()
            attributes_str = match.group(2).strip()
            attributes = self._parse_attributes(attributes_str)
            label = attributes.get('label', node_name)
            # Apply default attributes *before* adding inline attributes
            node_attributes = self.default_node_attributes.copy()
            node_attributes.update(attributes)
            self.nodes.append({'name': node_name, 'label': label, 'attributes': node_attributes})
            return

        match = re.match(r'"([^"]+)"\s*;?', line)
        if match:
            node_name = match.group(1).strip()
            node_data = {'name': node_name, 'label': node_name}
            if self.default_node_attributes:
                node_data['attributes'] = self.default_node_attributes.copy()
            self.nodes.append(node_data)
            return

    def _parse_edge_definition(self, line):
        """Parses an edge definition line (starting with 'edge')."""
        match = re.match(r'edge\s*\{(.*)\}', line)
        if match:
            attributes_str = match.group(1).strip()
            self.default_edge_attributes = self._parse_attributes(attributes_str)
            return

    def _parse_edge_connection(self, line):
        """Parse an edge connection line."""
        # Handle edge with attributes
        match = re.match(r'"([^"]+)"\s*([-<>]+)\s*"([^"]+)"\s*\{([^}]*)\}', line)
        if match:
            source = match.group(1).strip()
            connector = match.group(2).strip()
            destination = match.group(3).strip()
            attributes_str = match.group(4).strip()
            attributes = self._parse_attributes(attributes_str)
            # Apply default attributes *before* adding inline attributes
            edge_attributes = self.default_edge_attributes.copy()
            edge_attributes.update(attributes)
            self.edges.append({
                'source': source,
                'destination': destination,
                'connector': connector,
                'attributes': edge_attributes
            })
            return

        # Handle edge without attributes
        match = re.match(r'"([^"]+)"\s*([-<>]+)\s*"([^"]+)"\s*;?', line)
        if match:
            source = match.group(1).strip()
            connector = match.group(2).strip()
            destination = match.group(3).strip()
            edge_data = {
                'source': source,
                'destination': destination,
                'connector': connector,
            }
            if self.default_edge_attributes:
                edge_data['attributes'] = self.default_edge_attributes.copy()
            self.edges.append(edge_data)
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
