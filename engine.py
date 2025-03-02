from dot_parser import DotParser
import utils
import logging
from typing import Dict, List, Any, Tuple, Generator, Optional, Union, Callable

def set_up_logger() -> logging.Logger:
    """Sets up and returns a logger for the engine."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

# Workflow engine implementation as a generator
class Engine:
    """
    The WFEngine class manages state transitions and state method invocations.
    It supports conditional transitions, state-specific methods,
    and integration with external systems.
    """

    def __init__(self, states: List[str] = None, transitions: Dict[str, List[Tuple[str, str]]] = None, 
                 current_state: str = None, state_functions: Any = None, max_queue_size: int = 100):
        """
        Initialize the workflow engine.
        
        Args:
            states: List of state names
            transitions: Dictionary mapping source states to lists of (destination, condition) tuples
            current_state: The initial state of the workflow
            state_functions: Object containing state functions as methods
            max_queue_size: Maximum size of the instruction queue
        """
        # Initialize states and transitions (handling None values)
        self.states = states if states is not None else []
        self.transitions = transitions if transitions is not None else {}
        self.current_state = current_state
        self.state_functions = state_functions if state_functions is not None else {}
        self.max_queue_size = max_queue_size
        
        # Initialize logger
        self.logger = set_up_logger()
        
        # New attributes for instruction handling
        self.instruction_queue = []  # Queue for external instructions
        self.state_gen = None  # Current state function generator

    def set_logger(self, logger: logging.Logger) -> None:
        """
        Sets the logger for the engine.
        
        Args:
            logger: The logger instance to use
        """
        self.logger = logger

    def _run_state(self, state_name: str, arg: Any = None) -> Any:
        """
        Runs the method associated with the given state.
        
        Args:
            state_name: The name of the state to run
            arg: Optional argument to pass to the state function
            
        Returns:
            The result of the state function or None if an error occurs
        """
        self.logger.debug(f"Running state: {state_name}")
        
        # Check if the state function exists as a method in the StateFunctions instance
        if not hasattr(self.state_functions, state_name):
            self.logger.error(f"No function found for state: {state_name}")
            return None  # No function associated with the state

        try:
            func = getattr(self.state_functions, state_name)
            result = func(arg)
            return result
        except Exception as e:
            self.logger.error(f"Error in state function {state_name}: {e}")
            return None

    def start(self) -> Optional[Generator]:
        """
        Starts the engine from the initial state and returns a generator.
        
        Returns:
            A generator that processes the workflow or None if no states are defined
        """
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

    def _find_initial_state(self) -> Optional[str]:
        """
        Determines the initial state of the workflow.
        
        Returns:
            The name of the initial state or None if no initial state is found
        """
        # Check if '__start__' is defined
        if "__start__" in self.states:
            return "__start__"

        # Look for states with no incoming transitions
        incoming_states = set()
        for destinations in self.transitions.values():
            incoming_states.update(dest for dest, _ in destinations)
        initial_states = [state for state in self.states if state not in incoming_states]

        if not initial_states:
            return None  # No initial state found
        elif len(initial_states) > 1:
            self.logger.warning("Multiple potential initial states found. Using the first one.")
            return initial_states[0]  # Return the first potential initial state
        else:
            return initial_states[0]  # Single initial state

    def _handle_state_change(self, new_state: str) -> Tuple[str, str]:
        """
        Handles state change to the new state and validates the transition.
        Includes error handling and fallback options.
        
        Args:
            new_state: The new state to transition to
            
        Returns:
            A tuple containing the state_change instruction and the current state
        """
        if new_state not in self.states:
            self.logger.error(f"Invalid state transition to: {new_state}")
            # Stay in current state if transition is invalid
            return ("state_change", self.current_state)
            
        self.current_state = new_state
        self.logger.info(f"State changed to: {self.current_state}")
        return ("state_change", self.current_state)

    def _process_instruction(self, instruction: str, context: Any, state_gen: Generator) -> Tuple[str, Any]:
        """
        Processes an instruction with the current state generator.
        
        Args:
            instruction: The instruction to process
            context: The context for the instruction
            state_gen: The current state generator
            
        Returns:
            The response from the state generator or a state change notification
        """
        try:
            response = state_gen.send((instruction, context))
            
            # Handle state change instruction
            if isinstance(response, tuple) and response[0] == 'state_change':
                new_state = response[1]
                self.logger.info(f"Processing state change to: {new_state}")
                
                if new_state in self.states:
                    self.current_state = new_state
                    # Reset state generator for new state
                    self.state_gen = None
                    return ("state_change", self.current_state)
                else:
                    self.logger.error(f"Invalid state transition requested: {new_state}")
                    return ("error", f"Invalid state: {new_state}")
            else:
                # Pass through any other response
                return response
                
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
                        return ("state_change", self.current_state)
            
            return ("state_complete", self.current_state)
            
        except Exception as e:
            self.logger.error(f"Error in state generator: {e}")
            self.state_gen = None
            return ("error", str(e))

    def run(self) -> Generator[Tuple[str, Any], Tuple[str, Any], None]:
        """
        Generator that processes state functions and handles instructions.
        Yields and receives (instruction, context) tuples.
        
        Yields:
            Tuple[str, Any]: A tuple containing an instruction and context.
            
        Receives:
            Tuple[str, Any]: A tuple containing an instruction and context to process.
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
                    yield ("error", f"Failed to initialize state: {self.current_state}")
                    break

            try:
                # Get instruction/context from external or state function
                instruction, context = yield
                
                # Process the instruction
                response = self._process_instruction(instruction, context, self.state_gen)
                
                # Check if we've reached the end state after processing
                if response[0] == "state_change" and response[1] == "__end__":
                    self.logger.info("Workflow completed successfully")
                    yield response
                    break
                
                # Yield the response
                yield response
                    
            except Exception as e:
                self.logger.error(f"Unexpected error in run loop: {e}")
                yield ("error", str(e))
                
        self.logger.info("Workflow engine run completed")

    def _get_state_generator(self, state_name: str) -> Optional[Generator]:
        """
        Creates and initializes a generator for the specified state function.
        
        Args:
            state_name: The name of the state to get a generator for
            
        Returns:
            An initialized generator for the state function or None if an error occurs
        """
        self.logger.debug(f"Getting generator for state: {state_name}")
        
        if not state_name:
            self.logger.error("State name is required to get the generator.")
            return None
            
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
        except TypeError as e:
            self.logger.error(f"State function {state_name} is not a generator: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error initializing generator for state {state_name}: {e}")
            return None

    def send_instruction(self, instruction: str, context: Any = None) -> bool:
        """
        Queues an instruction to be processed by the engine.
        Includes a mechanism to manage queue size.
        
        Args:
            instruction: The instruction to queue
            context: Optional context for the instruction
            
        Returns:
            True if the instruction was queued, False if the queue is full
        """
        self.logger.debug(f"Queuing instruction: {instruction}, context: {context}")
        
        # Implement a maximum queue size
        if len(self.instruction_queue) >= self.max_queue_size:
            self.logger.warning(f"Instruction queue is full (max size: {self.max_queue_size}). Discarding instruction.")
            return False
            
        self.instruction_queue.append((instruction, context))
        return True

    @staticmethod
    def from_dot_string(dot_string: str, state_functions: Any) -> Optional['Engine']:
        """
        Creates an WFEngine from a DOT string.
        
        Args:
            dot_string: The DOT string representing the workflow graph
            state_functions: Object containing state functions as methods
            
        Returns:
            An initialized Engine instance or None if an error occurs
        """
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
    def from_nodes_and_edges(nodes: List[str], edges: List[Dict[str, str]], state_functions: Any) -> 'Engine':
        """
        Creates an WFEngine from lists of nodes and edges.
        
        Args:
            nodes: List of node names
            edges: List of edge dictionaries with source, target, and optional label
            state_functions: Object containing state functions as methods
            
        Returns:
            An initialized Engine instance
        """
        # For now, raise a NotImplementedError.  This method is not yet used.
        raise NotImplementedError("Use from_dot_string instead")

    def render_graph(self, output_file: str = "workflow", format_type: str = "png") -> None:
        """
        Renders the workflow graph to a file using Graphviz.

        Args:
            output_file: The name of the output file (without extension).
            format_type: The desired output format (e.g., "png", "pdf", "svg").
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
