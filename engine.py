class WFEngine:
    """
    The WFEngine class manages state transitions and state method invocations.
    It supports conditional transitions, state-specific methods,
    and integration with external systems.
    """

    def __init__(self, states=None, transitions=None, current_state=None, state_functions=None):
        # Initialize states and transitions (handling None values)
        self.states = states if states is not None else []
        self.transitions = transitions if transitions is not None else {}
        self.current_state = current_state
        self.state_functions = state_functions if state_functions is not None else {}
        self.logger = None  # Initialize logger to None

    def set_logger(self, logger):
        """Sets the logger for the engine."""
        self.logger = logger

    def _run_state(self, state_name):
        """Runs the method associated with the given state."""
        if self.logger:
            self.logger.debug(f"Running state: {state_name}")

        if state_name not in self.state_functions:
            if self.logger:
                self.logger.error(f"No function found for state: {state_name}")
            return None, None  # No function associated with the state

        func = self.state_functions[state_name]
        try:
            result, next_state = func()
            return result, next_state
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in state function {state_name}: {e}")
            return None, None

    def start(self):
        """Starts the engine from the initial state."""
        if self.logger:
            self.logger.debug("Starting engine")

        if not self.states:
            if self.logger:
                self.logger.warning("No states defined.")
            return

        # Find and set the initial state
        initial_state = self._find_initial_state()
        if initial_state:
            self.current_state = initial_state
            if self.logger:
                self.logger.debug(f"Initial state: {self.current_state}")
            self._run_state(self.current_state)  # Run the initial state
        else:
            if self.logger:
                self.logger.error("No valid initial state found.")

    def _find_initial_state(self):
        """Determines the initial state of the workflow."""
        # Check if '__start__' is defined
        if "__start__" in self.states:
            return "__start__"

        # Look for states with no incoming transitions
        incoming_states = set()
        for destinations in self.transitions.values():
            incoming_states.update(destinations)
        initial_states = [state for state in self.states if state not in incoming_states]

        if not initial_states:
            return None  # No initial state found
        elif len(initial_states) > 1:
            if self.logger:
                self.logger.warning("Multiple potential initial states found. Using the first one.")
            return initial_states[0]  # Return the first potential initial state
        else:
            return initial_states[0]  # Single initial state

    def evaluate_condition(self, label, condition):
        """
        Evaluates a condition based on its label.
        Conditions are boolean expressions defined as strings.
        """
        if self.logger:
            self.logger.debug(f"Evaluating condition: {label} ({condition})")

        if not condition:
            return True  # If no condition is defined, consider it True

        try:
            # Basic boolean conditions
            result = eval(condition, {"label": label})
            return result
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error evaluating condition '{condition}': {e}")
            return False  # Consider condition as False on error

    @staticmethod
    def from_dot_string(dot_string, state_functions):
        """Creates an WFEngine from a DOT string."""
        parser = DotParser()
        parser.parse(dot_string)
        if not parser.nodes or not parser.edges:
            raise ValueError("No graph could be created from DOT string. Check for parsing errors.")

        nodes = [node['name'].strip() for node in parser.nodes]
        edges = []
        for edge in parser.edges:
            source = edge['source'].strip()
            destination = edge['destination'].strip()
            label = edge.get('attributes', {}).get('label', '')  # Default to empty string if no label
            edges.append((source, destination, label))

        return WFEngine.from_nodes_and_edges(nodes, edges, state_functions)

    @staticmethod
    def from_nodes_and_edges(nodes, edges, state_functions):
        """Creates an WFEngine from lists of nodes and edges."""
        # For now, raise a NotImplementedError.  This method is not yet used.
        raise NotImplementedError("Use from_dot_string instead")
        states = nodes
        transitions = {}
        for source, destination, label in edges:
            if source not in transitions:
                transitions[source] = []
            transitions[source].append((destination, label))

        return WFEngine(states, transitions, None, state_functions)

    def render_graph(self, output_file="workflow", format_type="png"):
        """
        Renders the workflow graph to a file using Graphviz.

        :param output_file: The name of the output file (without extension).
        :param format_type: The desired output format (e.g., "png", "pdf", "svg").
        """
        try:
            from graphviz import Digraph

            dot = Digraph(comment='Workflow')

            # Add nodes
            for state in self.states:
                dot.node(state)

            # Add edges with labels
            for source, destinations in self.transitions.items():
                for destination, label in destinations:
                    dot.edge(source, destination, label=label)

            # Render to file
            dot.render(output_file, format=format_type, cleanup=True)
            print(f"Workflow graph rendered to {output_file}.{format_type}")

        except ImportError:
            print("Graphviz is not installed. Please install it to render the graph.")
        except Exception as e:
            print(f"An error occurred while rendering the graph: {e}")

