from dot_parser import DotParser
import utils

# Workflow engine implementation as a generator
class Engine:
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
        # Initialize a basic logger
        import logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def set_logger(self, logger):
        """Sets the logger for the engine."""
        self.logger = logger

    def _run_state(self, state_name, arg=None):
        """Runs the method associated with the given state."""
        self.logger.debug(f"Running state: {state_name}")
        print(f"DEBUG: _run_state - self.state_functions: {self.state_functions}")
        print(f"DEBUG: _run_state - state_name: {state_name}")

        # Check if the state function exists as a method in the StateFunctions instance
        if not hasattr(self.state_functions, state_name):
            self.logger.error(f"No function found for state: {state_name}")
            return None  # No function associated with the state

        func = getattr(self.state_functions, state_name)
        try:
            result = func(arg)
            return result
        except Exception as e:
            self.logger.error(f"Error in state function {state_name}: {e}")
            return None

    def start(self):
        """Starts the engine from the initial state and returns a generator."""
        self.logger.debug("Starting engine")

        if not self.states:
            self.logger.warning("No states defined.")
            return None

        # Find and set the initial state
        initial_state = self._find_initial_state()
        if initial_state:
            self.current_state = initial_state
            self.logger.debug(f"Initial state: {self.current_state}")
            return self.run()  # Return the generator
        else:
            self.logger.error("No valid initial state found.")
            return None

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
            self.logger.warning("Multiple potential initial states found. Using the first one.")
            return initial_states[0]  # Return the first potential initial state
        else:
            return initial_states[0]  # Single initial state

    def evaluate_condition(self, result, condition):
        """
        Evaluates a condition based on the result from the state function.
        Compares the result with the condition in the transition.
        """
        self.logger.debug(f"Evaluating condition: result='{result}' against condition='{condition}'")
        self.logger.debug(f"evaluate_condition: result type={type(result)}, condition type={type(condition)}")

        if not condition:
            return True  # If no condition is defined, consider it True
        
        # Handle the case where result is a tuple
        if isinstance(result, tuple):
            result = result[0]

        # For simple conditions, just check if the result matches the condition
        if "==" in condition:
            # Parse condition like "label == 'OK'"
            parts = condition.split("==", 1)
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip()
                
                # Remove quotes if present
                right = utils.strip_quotes(right)
                
                # If left side is "label", compare with result
                if left == "label":
                    return str(result) == str(right)
        
        # For direct comparison (no "=="), just check if result matches condition
        return result == condition

    def run(self):
        """
        Executes the workflow starting from the current state.
        Handles transitions between states based on state function results.
        """
        if not self.current_state:
            self.logger.error("No current state to run from.")
            return

        while self.current_state:
            # Always yield the state change
            yield ("state_change", self.current_state)
            self.logger.debug(f"Current state: {self.current_state}")

            # If we've reached the end state, break after yielding it
            if self.current_state == "__end__":
                self.logger.debug("Workflow completed successfully")
                break

            # Run the current state, passing any received value
            arg = None
            while True:
                result = self._run_state(self.current_state, arg)
                self.logger.debug(f"State function for {self.current_state} returned: result='{result}'")
                arg = yield result  # Yield the result and receive a potential argument

                # Check for state_change tuple
                if isinstance(result, tuple) and len(result) == 2 and result[0] == 'state_change':
                    self.logger.debug(f"State change requested: {result[1]}")
                    self.current_state = result[1]
                    break  # Exit inner loop to transition to the new state

        if self.current_state != "__end__":
            self.logger.warning("Workflow stopped without reaching end state")

    @staticmethod
    def from_dot_string(dot_string, state_functions):
        """Creates an WFEngine from a DOT string."""
        try:
            parser = DotParser()
            graph = parser.parse(dot_string)
            if not graph or not graph['nodes'] or not graph['edges']:
                print("Error: No graph could be created from DOT string. Check for parsing errors.")
                return None

            # Extract node names from parser.nodes
            nodes = [utils.strip_quotes(node['id']).strip() for node in graph['nodes'].values()]

            # Build transitions dictionary
            transitions = {}
            for edge in graph['edges']:
                source = utils.strip_quotes(edge['source']).strip()
                destination = utils.strip_quotes(edge['target']).strip()
                label = edge.get('label', '')  # Default to empty string if no label
                print(f"DEBUG: Edge - source: {source}, destination: {destination}, label: {label}")

                if source not in transitions:
                    transitions[source] = []

                # Extract condition from label if present
                condition = ""
                if label:
                    # Remove parentheses if they exist
                    if "(" in label and ")" in label:
                        label = label.split("(", 1)[1].rsplit(")", 1)[0].strip()
                    condition = utils.strip_quotes(label.strip())

                transitions[source].append((destination, condition))

            print(f"DEBUG: from_dot_string - nodes: {nodes}")
            print(f"DEBUG: from_dot_string - transitions: {transitions}")
            print(f"DEBUG: from_dot_string - state_functions: {state_functions}")
            return WFEngine(nodes, transitions, None, state_functions)
        except Exception as e:
            print(f"Error creating workflow engine: {e}")
            return None

    @staticmethod
    def from_nodes_and_edges(nodes, edges, state_functions):
        """Creates an WFEngine from lists of nodes and edges."""
        # For now, raise a NotImplementedError.  This method is not yet used.
        raise NotImplementedError("Use from_dot_string instead")

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
