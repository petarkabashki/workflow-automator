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
        # New attributes for instruction handling
        self.instruction_queue = []  # Queue for external instructions
        self.state_gen = None  # Current state function generator

    def set_logger(self, logger):
        """Sets the logger for the engine."""
        self.logger = logger

    def _run_state(self, state_name, arg=None):
        """Runs the method associated with the given state."""
        self.logger.debug(f"Running state: {state_name}")
        
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
        Generator that processes state functions and handles instructions.
        Yields and receives (instruction, context) tuples.
        """
        self.logger.debug("Starting engine run")

        # Initial state change notification
        yield ("state_change", self.current_state)
        
        # Check if we're starting at the end state
        if self.current_state == "__end__":
            self.logger.debug("Workflow completed - reached end state")
            return
        
        while self.current_state:
            # Process any queued external instructions first
            if self.instruction_queue:
                instruction, context = self.instruction_queue.pop(0)
                self.logger.debug(f"Processing queued instruction: {instruction}")
                yield (instruction, context)
                continue

            # Initialize state generator if needed
            if not self.state_gen:
                self.state_gen = self._get_state_generator(self.current_state)
                if not self.state_gen:
                    self.logger.error(f"Failed to get generator for state: {self.current_state}")
                    break

            try:
                # Get instruction/context from external or state function
                instruction, context = yield
                
                # Send instruction/context to state generator
                response = self.state_gen.send((instruction, context))
                
                # Handle state change instruction
                if isinstance(response, tuple) and response[0] == 'state_change':
                    new_state = response[1]
                    self.logger.info(f"Processing state change to: {new_state}")
                    
                    if new_state in self.states:
                        self.current_state = new_state
                        # Notify about state change
                        yield ("state_change", self.current_state)
                        
                        # Check if we've reached the end state
                        if self.current_state == "__end__":
                            self.logger.info("Workflow completed successfully")
                            break
                            
                        # Reset state generator for new state
                        self.state_gen = None
                    else:
                        self.logger.error(f"Invalid state transition requested: {new_state}")
                else:
                    # Pass through any other response
                    yield response
                    
            except StopIteration:
                self.logger.info(f"State function for {self.current_state} completed")
                self.state_gen = None
                
                # Auto-transition if there's only one possible next state
                if self.current_state in self.transitions:
                    destinations = self.transitions[self.current_state]
                    if len(destinations) == 1:
                        next_state, condition = destinations[0]
                        if not condition:  # Only auto-transition if no condition
                            self.current_state = next_state
                            yield ("state_change", self.current_state)
                            continue
                            
                # If no auto-transition, wait for explicit instruction
                self.logger.info(f"Waiting for next instruction in state: {self.current_state}")
                
            except Exception as e:
                self.logger.error(f"Error in state generator: {e}")
                self.state_gen = None
                
        self.logger.info("Workflow engine run completed")

    def _get_state_generator(self, state_name):
        """
        Creates and initializes a generator for the specified state function.
        """
        self.logger.debug(f"Getting generator for state: {state_name}")
        
        if not hasattr(self.state_functions, state_name):
            self.logger.error(f"No function found for state: {state_name}")
            return None
            
        state_func = getattr(self.state_functions, state_name)
        
        # Check if the function is a generator function
        try:
            gen = state_func()
            # Prime the generator
            next(gen)
            return gen
        except Exception as e:
            self.logger.error(f"Error initializing generator for state {state_name}: {e}")
            return None

    def send_instruction(self, instruction, context=None):
        """
        Queues an instruction to be processed by the engine.
        """
        self.logger.debug(f"Queuing instruction: {instruction}, context: {context}")
        self.instruction_queue.append((instruction, context))

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
            return Engine(nodes, transitions, None, state_functions)
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
