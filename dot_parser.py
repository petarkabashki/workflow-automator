class DotParser:
    """Parses a DOT language string into a graph structure."""
    
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.current_node = None
        self.current_edge = None
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
                self.in_node = True
                self.in_edge = False
            elif line.startswith('edge'):
                self._parse_edge(line)
                self.in_node = False
                self.in_edge = True
            elif '->' in line:
                self._parse_edge_connection(line)
                self.in_edge = False
            elif line.startswith('"'):
                self._parse_label(line)
            elif line.startswith('{'):
                if self.in_node:
                    self.current_node = {'attributes': {}}
                elif self.in_edge:
                    self.current_edge = {'attributes': {}}
            elif line.startswith('}'):
                if self.in_node:
                    self.nodes.append(self.current_node)
                    self.current_node = None
                    self.in_node = False
                elif self.in_edge and self.current_edge:
                    self.edges.append(self.current_edge)
                    self.current_edge = None
                    self.in_edge = False
    
    def _parse_node(self, line):
        """Parse a node line."""
        parts = line.split(' ', 1)
        if len(parts) > 1:
            node_name = parts[1].strip('"')
            self.current_node = {'name': node_name, 'label': node_name, 'attributes': {}}
        else:
            self.current_node = {'name': '', 'label': '', 'attributes': {}}
    
    def _parse_edge(self, line):
        """Parse an edge line."""
        parts = line.split(' ', 1)
        if len(parts) > 1:
            edge_name = parts[1].strip('"')
            self.current_edge = {'name': edge_name, 'attributes': {}}
        else:
            self.current_edge = {'name': '', 'attributes': {}}
    
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
        """Parse a label line."""
        label = line.strip().strip('"')
        if self.in_node and self.current_node:
            self.current_node['label'] = label
        elif self.in_edge and self.current_edge:
            self.current_edge['label'] = label
    
    def _parse_attributes(self, attrs_str):
        """Parse key=value pairs from a string."""
        attributes = {}
        if not attrs_str:
            return attributes
            
        attrs = attrs_str.split(',')
        for attr in attrs:
            attr = attr.strip()
            if '=' in attr:
                key, value = attr.split('=', 1)
                attributes[key.strip()] = value.strip().strip('"')
                
        return attributes
