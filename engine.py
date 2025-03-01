from dot_parser import DotParser
import utils

# Implement the engine as a generator, also expecting the state functions to be generators to be iterated over. Expect each state function to return return on it's iterations a flag indicating whether it's finished. AI! 
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

    def _run_state(self, state_name):
        """Runs the method associated with the given state."""
        self.logger.debug(f"Running state: {state_name}")

        # Check if the state function exists as a method in the StateFunctions instance
        if not hasattr(self.state_functions, state_name):
            self.logger.error(f"No function found for state: {state_name}")
            return None, None  # No function associated with the state

        func = getattr(self.state_functions, state_name)
        try:
            result, next_state = func()
            return result, next_state
        except Exception as e:
            self.logger.error(f"Error in state function {state_name}: {e}")
            return None, None

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

    def evaluate_condition(self, label, condition):
        """
        Evaluates a condition based on its label.
        Conditions are boolean expressions defined as strings.
        """
        self.logger.debug(f"Evaluating condition: {label} ({condition})")

        if not condition:
            return True  # If no condition is defined, consider it True

        try:
            # Basic boolean conditions with restricted environment
            result = eval(condition, {"__builtins__": {}}, {"label": label})
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error evaluating condition '{condition}': {e}")
            return False  # Consider condition as False on error

    def run(self):
        """
        Executes the workflow starting from the current state.
        Handles transitions between states based on state function results.
        """
        if not self.current_state:
            self.logger.error("No current state to run from.")
            return

        while self.current_state and self.current_state != "__end__":
            yield self.current_state  # Yield the current state name
            self.logger.debug(f"Current state: {self.current_state}") # Log after yielding
            
            # Run the current state function
            result, next_state = self._run_state(self.current_state)
            
            # If the state function specified the next state directly, use it
            if next_state:
                self.logger.debug(f"State function returned next state: {next_state}")
                self.current_state = next_state
                continue
            
            # Otherwise, check transitions from the current state
            if self.current_state in self.transitions:
                possible_transitions = self.transitions[self.current_state]
                
                if len(possible_transitions) == 1:
                    # If only one transition, take it
                    next_state, _ = possible_transitions[0]
                    self.logger.debug(f"Taking only available transition to: {next_state}")
                    self.current_state = next_state
                elif len(possible_transitions) > 1:
                    # Multiple transitions - need to evaluate conditions
                    self.logger.debug(f"Multiple transitions available from {self.current_state}")
                    
                    # Check if all transitions have empty conditions
                    if all(not cond for _, cond in possible_transitions):
                        self.logger.error("Multiple transitions require conditions")
                        break
                    
                    # Try to find a transition that matches the result
                    matched = False
                    for dest, condition in possible_transitions:
                        if self.evaluate_condition(result, condition):
                            self.logger.debug(f"Condition matched for transition to {dest}")
                            self.current_state = dest
                            matched = True
                            break
                    
                    if not matched:
                        # No matching transition found
                        self.logger.warning(f"No matching transition found for result: {result}")
                        break
                else:
                    # No transitions defined
                    self.logger.warning(f"No transitions defined from state: {self.current_state}")
                    break
            else:
                # No transitions from current state
                self.logger.warning(f"No transitions defined from state: {self.current_state}")
                break

        if self.current_state == "__end__":
            self.logger.debug("Workflow completed successfully")
        else:
            self.logger.warning("Workflow stopped without reaching end state")

    @staticmethod
    def from_dot_string(dot_string, state_functions):
        """Creates an WFEngine from a DOT string."""
        try:
            parser = DotParser()
            parser.parse(dot_string)
            if not parser.nodes or not parser.edges:
                print("Error: No graph could be created from DOT string. Check for parsing errors.")
                return None

            # Extract node names from parser.nodes
            nodes = [utils.strip_quotes(node['name']).strip() for node in parser.nodes]
            
            # Build transitions dictionary
            transitions = {}
            for edge in parser.edges:
                source = utils.strip_quotes(edge['source']).strip()
                destination = utils.strip_quotes(edge['destination']).strip()
                label = edge.get('attributes', {}).get('label', '')  # Default to empty string if no label
                
                if source not in transitions:
                    transitions[source] = []
                
                # Extract condition from label if present
                condition = ""
                if label and "(" in label and ")" in label:
                    parts = label.split("(", 1)
                    if len(parts) > 1:
                        condition = parts[1].rsplit(")", 1)[0].strip()
                
                transitions[source].append((destination, condition))
            
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

