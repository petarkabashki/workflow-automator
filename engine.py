import logging
import sys
from io import StringIO
from utils import strip_quotes
from dot_parser import DotParser

class WFEngine:
    """
    The WFEngine class manages state transitions and state method invocations.
    """

    def __init__(self, graph, state_functions):
        self.graph = graph
        self.state_functions = state_functions
        self.current_state = "__start__"

        # Configure logging, accept logger instance or create a default one
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # Set the desired log level

        # Create a handler (e.g., file handler)
        fh = logging.FileHandler('engine_log.txt')
        fh.setLevel(logging.DEBUG)

        # Create a formatter and set it on the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(fh)

    def set_logger(self, logger):
        """Sets a new logger for the engine."""
        self.logger = logger

    def _run_state(self, state_name):
        """Runs the state function associated with the given state name."""
        self.logger.debug(f"Running state: {state_name}")

        state_method = getattr(self.state_functions, state_name, None)

        if state_method:
            try:
                next_state_info = state_method()

                if isinstance(next_state_info, tuple):
                    condition, state_override = next_state_info
                    return condition, state_override
                else:
                    return None, None

            except Exception as e:
                self.logger.exception(f"Exception in state {state_name}")
                raise  # Re-raise the exception to halt execution

        else:
            self.logger.warning(f"No state method found for {state_name}")
            return None, None
    def start(self):
        """Runs the workflow as a generator."""
        self.logger.info("Workflow started.")
        
        # Verify start state exists in graph
        if "__start__" not in [node.get('name') for node in self.graph.get('nodes')]:
            self.logger.error("__start__ state not found in graph")
            raise ValueError("__start__ state not found in graph")
            
        while True:
            self.logger.debug(f"Current state: {self.current_state}")
            
            # First yield the current state before processing
            condition, state_override = self._run_state(self.current_state)
            yield self.current_state, condition, state_override
            
            if self.current_state == "__end__":
                self.logger.info("Workflow finished.")
                break
            
            if self.current_state not in [node.get('name') for node in self.graph.get('nodes')]:
                self.logger.error("Current state %s not found in graph", self.current_state)
                self.current_state = '__end__'
                continue
                

            if state_override:
                self.logger.debug(f"State override: {state_override}")
                self.current_state = state_override
                continue

            if condition is not None:
                found_transition = False
                for edge in self.graph.get('edges'):
                    edge_source = edge.get('source')
                    if edge_source == self.current_state:
                        label = edge.get('attributes', {}).get('label') if edge.get('attributes') else None
                        short_label = label.split(" ")[0] if label else None # Extract the short code
                        if short_label and self.evaluate_condition(short_label, condition):
                            self.logger.debug("Transitioning to %s based on condition %s", edge.get('destination'), condition)
                            self.current_state = edge.get('destination')
                            found_transition = True
                            break
                if not found_transition:
                    self.logger.warning(f"No transition found for condition {condition}")
                    self.current_state = '__end__'
            else:
                # Count possible transitions from current state
                possible_edges = [edge for edge in self.graph.get('edges') if edge.get('source') == self.current_state]
    
                if len(possible_edges) > 1:
                    self.logger.error(f"Multiple transitions found from state {self.current_state} but no condition provided")
                    self.current_state = '__end__'
                elif len(possible_edges) == 1:
                    edge = possible_edges[0]
                    label = edge.get('attributes', {}).get('label') if edge.get('attributes') else None
                    self.logger.debug("Transitioning to %s with condition: %s", edge.get('destination'), condition)
                    self.current_state = edge.get('destination')
                else:
                    self.logger.warning("No transition found without condition, ending workflow.")
                    self.current_state = '__end__'


    def evaluate_condition(self, label, condition):
        """
        Evaluates if the given label matches the condition.
        Returns True if the label exactly matches the condition string.
        """
        if label is None or condition is None:
            self.logger.debug("Label or condition is None")
            return False
        if not label or not condition:
            self.logger.debug("Empty label or condition")
            return False
        result = str(label).strip() == str(condition).strip()
        self.logger.debug("Condition evaluation: %s == %s -> %s", label, condition, result)
        return result

    @staticmethod
    def from_dot_string(dot_string, state_functions):
        """Creates an WFEngine from a DOT string."""
        parser = DotParser()
        parser.parse(dot_string)
        if not parser.nodes or not parser.edges:
            raise ValueError("No graph could be created from DOT string. Check for parsing errors.")

        # Create a simplified graph representation for the engine.  The
        #   engine doesn't need a full pydot graph object.
        graph = {
            'nodes': parser.nodes,
            'edges': parser.edges
        }
        return WFEngine(graph, state_functions)

    @staticmethod
    def from_nodes_and_edges(nodes, edges, state_functions):
        """Creates an WFEngine from lists of nodes and edges."""
        raise NotImplementedError("Use from_dot_string instead")


    def render_graph(self, output_file="workflow", format_type="png"):
        """
        Renders the graph to a file.

        Args:
            output_file (str): Base name for the output file (without extension)
            format_type (str): Output format (e.g., 'png', 'pdf', 'svg')
        """
        # self.graph.write(f"{output_file}.{format_type}", format=format_type)
        # Not implemented, we are not using pydot
        raise NotImplementedError("render_graph is not implemented")

