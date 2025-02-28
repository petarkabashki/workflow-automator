class DotParser:
    """Parses a DOT language string into a graph structure."""
    
    def __init__(self):
        self.nodes = []
        self.edges = []
        
    def parse(self, dot_string):
        """Parse a DOT language string and create a graph."""
        lines = dot_string.split('\n')
        current_node = None
        current_edge = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('node '):
                # Parse node attributes
                attrs = line[5:].strip()
                if attrs.startswith('{'):
                    attrs = attrs[1:].strip()
                current_node = {'attributes': self._parse_attributes(attrs)}
                self.nodes.append(current_node)
                
            elif line.startswith('edge '):
                # Parse edge attributes
                attrs = line[5:].strip()
                if attrs.startswith('{'):
                    attrs = attrs[1:].strip()
                current_edge = {'attributes': self._parse_attributes(attrs)}
                
            elif '->' in line:
                # Parse edge connection
                source, dest = line.split('->')
                source = source.strip()
                dest = dest.strip()
                
                if current_edge:
                    current_edge['source'] = source
                    current_edge['destination'] = dest
                    self.edges.append(current_edge)
                    current_edge = None
                    
            elif line.startswith('"'):
                # Handle node or edge label
                label = line.strip().strip('"')
                if current_node:
                    current_node['label'] = label
                elif current_edge:
                    current_edge['label'] = label
                    
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
