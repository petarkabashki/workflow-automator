import re

class DotParser:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def parse(self, dot_string):
        # Remove multi-line and single-line comments.
        dot_string = re.sub(r'/\*.*?\*/', '', dot_string, flags=re.DOTALL)
        dot_string = re.sub(r'//.*', '', dot_string)
        dot_string = dot_string.strip()

        # Abort if unbalanced quotes.  This is less relevant now,
        # but still good to check for malformed input.
        if dot_string.count('"') % 2 != 0:
            return

        # Only parse edge connections.
        while dot_string:
            initial_length = len(dot_string)
            success, consumed, statement_text = self._parse_edge_connection(dot_string)
            if success:
                dot_string = dot_string[consumed:].lstrip()
                if not statement_text.rstrip().endswith(';'):
                    dot_string = ""
            if not success or len(dot_string) == initial_length:
                break

    def _parse_edge_connection(self, text):
        # Edge connection with label attribute: e.g. "Start" -> "End" [label = "OK"];
        #  or Start -> End [label = "OK"];
        pattern_with_label = (
            r'^(?P<source>"[^"]+"|[^"\s;-]+)\s*->\s*(?P<destination>"[^"]+"|[^"\s;-]+)\s*'
            r'(?:\[\s*label\s*=\s*"(?P<label>[^"]*)"\s*\])?\s*;?'
        )

        m = re.match(pattern_with_label, text)
        if m:
            statement_text = m.group(0)
            source = m.group('source')
            destination = m.group('destination')
            # Remove quotes if present
            if source.startswith('"') and source.endswith('"'):
                source = source[1:-1]
            if destination.startswith('"') and destination.endswith('"'):
                destination = destination[1:-1]

            label = m.group('label')  # Can be None

            self._ensure_node_exists(source)
            self._ensure_node_exists(destination)

            edge = {'source': source, 'destination': destination, 'connector': '->'}
            if label:
                edge['attributes'] = {'label': label}
            self.edges.append(edge)
            return (True, m.end(), statement_text)
        return (False, 0, "")

    def _ensure_node_exists(self, name):
        if not any(n.get('name') == name for n in self.nodes):
            self.nodes.append({'name': name, 'label': name})
