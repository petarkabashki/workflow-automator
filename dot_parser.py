import re

class DotParser:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.default_edge_attributes = {}
        # When a default node block (node { … }) is parsed, we store its attributes here.
        # In that case, no additional nodes are auto‑added.
        self.default_node_attributes = None

    def parse(self, dot_string):
        # Remove multi-line and single-line comments.
        dot_string = re.sub(r'/\*.*?\*/', '', dot_string, flags=re.DOTALL)
        dot_string = re.sub(r'//.*', '', dot_string)
        dot_string = dot_string.strip()
        
        # Abort if unbalanced quotes.
        if dot_string.count('"') % 2 != 0:
            return

        # Main loop: while there is text remaining, try to match a valid statement.
        # Only allow statements starting with "node", "edge", or a double quote.
        allowed = re.compile(r'^(node\b|edge\b|")')
        while dot_string:
            if not allowed.match(dot_string):
                break

            initial_length = len(dot_string)
            processed = False
            # Try each parsing function in order.
            for func in [self._parse_node_definition,
                         self._parse_edge_definition,
                         self._parse_edge_connection,
                         self._parse_standalone_node]:
                success, consumed, statement_text = func(dot_string)
                if success:
                    # Remove the consumed text.
                    dot_string = dot_string[consumed:].lstrip()
                    processed = True
                    # If the statement does not end with a semicolon, then stop parsing.
                    if not statement_text.rstrip().endswith(';'):
                        dot_string = ""
                    break
            if not processed or len(dot_string) == initial_length:
                break

    # --- Node Parsing ---

    def _parse_node_definition(self, text):
        # Named node definition: e.g. node "Start" { label = "Start" }
        pattern_with_name = (
            r'^node\s+(?P<name>("([^"]+)"|[\w]+))\s*'
            r'(?:\{|\[)\s*(?P<attrs>.*?)\s*(?:\}|\])\s*;?'
        )
        m = re.match(pattern_with_name, text, flags=re.DOTALL)
        if m:
            statement_text = m.group(0)
            node_name = m.group('name')
            if node_name.startswith('"') and node_name.endswith('"'):
                node_name = node_name[1:-1]
            if not self._is_valid_identifier(node_name):
                return (True, m.end(), statement_text)
            attributes = self._parse_attributes(m.group('attrs').strip())
            # If a default node block was defined earlier, ignore additional named nodes.
            if self.default_node_attributes is not None:
                return (True, m.end(), statement_text)
            node = {'name': node_name}
            if attributes:
                node['attributes'] = attributes
            node['label'] = attributes.get('label', node_name)
            if not any(n.get('name') == node_name for n in self.nodes):
                self.nodes.append(node)
            return (True, m.end(), statement_text)

        # Default node attributes: e.g. node { color = "blue"; }
        pattern_no_name = (
            r'^node\s*(?:\{|\[)\s*(?P<attrs>.*?)\s*(?:\}|\])\s*;?'
        )
        m = re.match(pattern_no_name, text, flags=re.DOTALL)
        if m:
            statement_text = m.group(0)
            attributes = self._parse_attributes(m.group('attrs').strip())
            self.default_node_attributes = attributes.copy()
            # Create a single default node if none exist.
            if not self.nodes:
                node = {}
                if attributes:
                    node['attributes'] = attributes.copy()
                if 'label' in attributes:
                    node['label'] = attributes['label']
                self.nodes.append(node)
            return (True, m.end(), statement_text)
        return (False, 0, "")

    def _parse_standalone_node(self, text):
        # Only process if text does not start with "node" or "edge".
        if re.match(r'^(node\b|edge\b)', text):
            return (False, 0, "")
        pattern_with_attrs = (
            r'^(?P<name>("([^"]+)"|[\w]+))\s*'
            r'(?:\{|\[)\s*(?P<attrs>.*?)\s*(?:\}|\])\s*;?'
        )
        m = re.match(pattern_with_attrs, text, flags=re.DOTALL)
        if m:
            statement_text = m.group(0)
            node_name = m.group('name')
            if node_name.startswith('"') and node_name.endswith('"'):
                node_name = node_name[1:-1]
            if not self._is_valid_identifier(node_name):
                return (True, m.end(), statement_text)
            # If default node attributes are in effect, do not add new nodes.
            if self.default_node_attributes is not None:
                return (True, m.end(), statement_text)
            attributes = self._parse_attributes(m.group('attrs').strip())
            node = {'name': node_name}
            node['label'] = attributes.get('label', node_name)
            if attributes:
                node['attributes'] = attributes
            if not any(n.get('name') == node_name for n in self.nodes):
                self.nodes.append(node)
            return (True, m.end(), statement_text)
        pattern_simple = (
            r'^(?P<name>("([^"]+)"|[\w]+))\s*;?'
        )
        m = re.match(pattern_simple, text)
        if m:
            statement_text = m.group(0)
            node_name = m.group('name')
            if node_name.startswith('"') and node_name.endswith('"'):
                node_name = node_name[1:-1]
            if not self._is_valid_identifier(node_name):
                return (True, m.end(), statement_text)
            if self.default_node_attributes is not None:
                return (True, m.end(), statement_text)
            node = {'name': node_name, 'label': node_name}
            if not any(n.get('name') == node_name for n in self.nodes):
                self.nodes.append(node)
            return (True, m.end(), statement_text)
        return (False, 0, "")

    # --- Edge Parsing ---

    def _parse_edge_definition(self, text):
        # Edge default attributes: e.g. edge { color = "red"; style = "dashed"; }
        pattern = (
            r'^edge\s*(?:\{|\[)\s*(?P<attrs>.*?)\s*(?:\}|\])\s*;?'
        )
        m = re.match(pattern, text, flags=re.DOTALL)
        if m:
            statement_text = m.group(0)
            self.default_edge_attributes = self._parse_attributes(m.group('attrs').strip())
            return (True, m.end(), statement_text)
        return (False, 0, "")

    def _parse_edge_connection(self, text):
        # Edge connection with inline attributes: e.g. "Start" -> "End" { color = "red"; }
        pattern_with_attrs = (
            r'^(?P<source>("([^"]+)"|[\w]+))\s*'
            r'(?P<connector>[-<>]+)\s*'
            r'(?P<destination>("([^"]+)"|[\w]+))\s*'
            r'(?:\{|\[)\s*(?P<attrs>.*?)\s*(?:\}|\])\s*;?'
        )
        m = re.match(pattern_with_attrs, text, flags=re.DOTALL)
        if m:
            statement_text = m.group(0)
            source = m.group('source')
            destination = m.group('destination')
            if source.startswith('"') and source.endswith('"'):
                source = source[1:-1]
            if destination.startswith('"') and destination.endswith('"'):
                destination = destination[1:-1]
            if not self._is_valid_identifier(source) or not self._is_valid_identifier(destination):
                return (True, m.end(), statement_text)
            connector = m.group('connector')
            attrs = self._parse_attributes(m.group('attrs').strip())
            edge_attrs = self.default_edge_attributes.copy() if self.default_edge_attributes else {}
            edge_attrs.update(attrs)
            # Only auto-add the source (if missing); do not auto-add a destination.
            self._ensure_node_exists(source, is_source=True)
            self._ensure_node_exists(destination, is_source=False)
            edge = {'source': source, 'destination': destination, 'connector': connector}
            if edge_attrs:
                edge['attributes'] = edge_attrs
            self.edges.append(edge)
            return (True, m.end(), statement_text)
        # Edge connection without inline attributes.
        pattern_simple = (
            r'^(?P<source>("([^"]+)"|[\w]+))\s*'
            r'(?P<connector>[-<>]+)\s*'
            r'(?P<destination>("([^"]+)"|[\w]+))\s*;?'
        )
        m = re.match(pattern_simple, text)
        if m:
            statement_text = m.group(0)
            source = m.group('source')
            destination = m.group('destination')
            if source.startswith('"') and source.endswith('"'):
                source = source[1:-1]
            if destination.startswith('"') and destination.endswith('"'):
                destination = destination[1:-1]
            if not self._is_valid_identifier(source) or not self._is_valid_identifier(destination):
                return (True, m.end(), statement_text)
            connector = m.group('connector')
            self._ensure_node_exists(source, is_source=True)
            self._ensure_node_exists(destination, is_source=False)
            edge = {'source': source, 'destination': destination, 'connector': connector}
            if self.default_edge_attributes:
                edge['attributes'] = self.default_edge_attributes.copy()
            self.edges.append(edge)
            return (True, m.end(), statement_text)
        return (False, 0, "")

    # --- Helpers ---

    def _parse_attributes(self, attributes_str):
        attributes = {}
        if attributes_str:
            for attr in re.split(r'[;,]\s*', attributes_str):
                attr = attr.strip()
                if attr:
                    if '=' in attr:
                        key, value = attr.split('=', 1)
                        attributes[key.strip()] = value.strip().strip('"')
                    else:
                        attributes[attr.strip()] = True
        return attributes

    def _is_valid_identifier(self, identifier):
        return re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', identifier) is not None

    def _ensure_node_exists(self, name, is_source=False):
        # If a default node block was defined, do not add additional nodes.
        if self.default_node_attributes is not None:
            return
        # Only auto-add a node when it appears as a source.
        if is_source and not any(n.get('name') == name for n in self.nodes):
            self.nodes.append({'name': name, 'label': name})
