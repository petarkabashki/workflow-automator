import logging
import pydot
import sys
from io import StringIO
from utils import strip_quotes

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
        
        while True:
            self.logger.debug(f"Current state: {self.current_state}")
            
            # Always yield current state before processing
            yield self.current_state, None, None
            
            if self.current_state == "__end__":
                self.logger.info("Workflow finished.")
                break

            self.logger.debug(f"Current state: {self.current_state}")
            
            if self.current_state not in [strip_quotes(node.get_name()) for node in self.graph.get_nodes()]:
                self.logger.error("Current state %s not found in graph", self.current_state)
                self.current_state = '__end__'
                continue
                
            condition, state_override = self._run_state(self.current_state)

            yield self.current_state, condition, state_override

            if state_override:
                self.logger.debug(f"State override: {state_override}")
                self.current_state = state_override
                continue

            if condition is not None:
                found_transition = False
                for edge in self.graph.get_edges():
                    edge_source = strip_quotes(edge.get_source())
                    if edge_source == self.current_state:
                        label = strip_quotes(edge.get_label())
                        short_label = label.split(" ")[0]  # Extract the short code
                        if short_label and self.evaluate_condition(short_label, condition):
                            self.logger.debug("Transitioning to %s based on condition %s", edge.get_destination(), condition)
                            self.current_state = strip_quotes(edge.get_destination())
                            found_transition = True
                            break
                if not found_transition:
                    self.logger.warning(f"No transition found for condition {condition}")
                    self.current_state = '__end__'
            else:
                # Count possible transitions from current state
                possible_edges = [edge for edge in self.graph.get_edges() if strip_quotes(edge.get_source()) == self.current_state]
    
                if len(possible_edges) > 1:
                    self.logger.error(f"Multiple transitions found from state {self.current_state} but no condition provided")
                    self.current_state = '__end__'
                elif len(possible_edges) == 1:
                    edge = possible_edges[0]
                    label = strip_quotes(edge.get_label()) # get the label
                    self.logger.debug("Transitioning to %s with condition: %s", edge.get_destination(), condition)
                    self.current_state = strip_quotes(edge.get_destination())
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
        try:
            (graph,) = pydot.graph_from_dot_data(dot_string)
            return WFEngine(graph, state_functions)
        except Exception as e:
            print(f"Error parsing DOT string: {e}")
            return None

    @staticmethod
    def from_nodes_and_edges(nodes, edges, state_functions):
        """Creates an WFEngine from lists of nodes and edges."""
        graph = pydot.Dot(graph_type='digraph')
        for node in nodes:
            graph.add_node(pydot.Node(node))
        for edge in edges:
            if isinstance(edge, tuple):  # Regular edge
                graph.add_edge(pydot.Edge(edge[0], edge[1]))
            else:  # Edge with attributes (e.g., label)
                graph.add_edge(pydot.Edge(edge['src'], edge['dst'], label=edge['label']))
        return WFEngine(graph, state_functions)

    def render_graph(self, output_file="workflow", format_type="png"):
        """
        Renders the graph to a file.
        
        Args:
            output_file (str): Base name for the output file (without extension)
            format_type (str): Output format (e.g., 'png', 'pdf', 'svg')
        """
        self.graph.write(f"{output_file}.{format_type}", format=format_type)
