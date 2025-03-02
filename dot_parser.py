import re
import json
from utils import strip_quotes

class DotParser:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def parse(self, dot_string):
        # Remove multi-line and single-line comments.
        dot_string = re.sub(r'/\*.*?\*/', '', dot_string, flags=re.DOTALL)
        dot_string = re.sub(r'//.*', '', dot_string)
        dot_string = dot_string.strip()
        # print(f"Parsing dot_string: '{dot_string}'")

        # Abort if unbalanced quotes.  This is less relevant now,
        # but still good to check for malformed input.
        if dot_string.count('"') % 2 != 0:
            return

        # Handle 'strict digraph {}' wrapper
        graph_match = re.match(r'strict\s+digraph\s*{(.*)}', dot_string, re.DOTALL)
        if graph_match:
            # Extract the content inside the graph declaration
            dot_string = graph_match.group(1).strip()
            # print(f"Extracted graph content: '{dot_string}'")

        # Only parse edge connections.
        while dot_string:
            initial_length = len(dot_string)
            success, consumed, statement_text = self._parse_edge_connection(dot_string)
            # print(f"  Statement: '{statement_text}'")
            # print(f"  Success: {success}, Consumed: {consumed}")
            if success:
                dot_string = dot_string[consumed:].lstrip()
                # print(f"  Remaining dot_string: '{dot_string}'")
                if not statement_text.rstrip().endswith(';'):
                    dot_string = ""
            if not success or len(dot_string) == initial_length:
                # print("  Breaking loop")
                break
            # print(f"  Nodes: {self.nodes}")
            # print(f"  Edges: {self.edges}")
        # print(f"Final Nodes: {self.nodes}")
        # print(f"Final Edges: {self.edges}")


    def _parse_edge_connection(self, text):
        # Edge connection with attributes: e.g. "Start" -> "End" [label = "OK", data = '{"key": "value"}'];
        #  or Start -> End [label = "OK"];
        pattern_with_attributes = (
            r'^(?P<source>"[^"]+"|[^"\s;-]+)\s*->\s*(?P<destination>"[^"]+"|[^"\s;-]+)\s*'
            r'(?:\[\s*(?P<attributes>[^]]*)\s*\])?\s*;?'
        )

        m = re.match(pattern_with_attributes, text)
        if m:
            statement_text = m.group(0)
            source = m.group('source')
            destination = m.group('destination')
            # Remove quotes if present
            if source.startswith('"') and source.endswith('"'):
                source = source[1:-1]
            if destination.startswith('"') and destination.endswith('"'):
                destination = destination[1:-1]

            attributes_text = m.group('attributes')  # Can be None

            self._ensure_node_exists(source)
            self._ensure_node_exists(destination)

            edge = {'source': source, 'destination': destination, 'connector': '->'}
            
            if attributes_text:
                edge['attributes'] = self._parse_attributes(attributes_text)
                
            self.edges.append(edge)
            return (True, m.end(), statement_text)
        return (False, 0, "")

    def _ensure_node_exists(self, name):
        name = name.strip()
        if not any(n.get('name') == name for n in self.nodes):
            self.nodes.append({'name': name, 'label': name})
            
    def _parse_attributes(self, attributes_text):
        """Parse attribute string into a dictionary of attributes."""
        attributes = {}
        # Match attribute name-value pairs: name = "value" or name = 'value'
        attr_pattern = r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\')(?:,\s*|$)'
        
        for match in re.finditer(attr_pattern, attributes_text):
            attr_name = match.group(1)
            # Value is either in group 2 (double quotes) or group 3 (single quotes)
            attr_value = match.group(2) if match.group(2) is not None else match.group(3)
            
            # Try to parse JSON if the value is enclosed in single quotes
            if match.group(3) is not None:
                try:
                    # Attempt to parse as JSON
                    json_value = json.loads(attr_value)
                    attributes[attr_name] = json_value
                    continue
                except json.JSONDecodeError:
                    # If JSON parsing fails, use the string value
                    pass
            
            # Default case: use the string value
            attributes[attr_name] = attr_value
            
        return attributes
