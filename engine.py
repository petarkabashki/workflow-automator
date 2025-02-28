import logging
import pydot
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

        # Configure logging
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

    def run(self):
        """Runs the workflow as a generator."""
        self.logger.info("Workflow started.")
        while True:
            self.logger.debug(f"Current state: {self.current_state}")
            condition, state_override = self._run_state(self.current_state)

            yield self.current_state, condition, state_override

            if self.current_state == "__end__":
                self.logger.info("Workflow finished.")
                break

            if state_override:
                self.logger.debug(f"State override: {state_override}")
                self.current_state = state_override
                continue

            if condition is not None:
                found_transition = False
                for edge in self.graph.get_edges():
                    if edge.get_source() == self.current_state:
                        label = strip_quotes(edge.get_label())
                        short_label = label.split(" ")[0]  # Extract the short code
                        if short_label and self.evaluate_condition(short_label, condition):
                            self.logger.debug(f"Transitioning to {edge.get_destination()} based on condition {condition}")
                            self.current_state = edge.get_destination()
                            found_transition = True
                            break
                if not found_transition:
                    self.logger.warning(f"No transition found for condition {condition}")
                    self.current_state = '__end__'
            else:
                found_transition = False
                for edge in self.graph.get_edges():
                    if edge.get_source() == self.current_state:
                        label = strip_quotes(edge.get_label()) # get the label
                        self.logger.debug(f"Transitioning to {edge.get_destination()} without condition")
                        self.current_state = edge.get_destination()
                        found_transition = True
                        break
                if not found_transition:
                    if self.current_state != '__end__':
                        self.logger.warning("No transition found without condition, ending workflow.")
                        self.current_state = '__end__'


    def evaluate_condition(self, label, condition):
        """
        Evaluates if the given label matches the condition.
        """
        return label == condition

    @staticmethod
    def from_dot_string(dot_string, state_functions):
        """Creates an WFEngine from a DOT string."""
        (graph,) = pydot.graph_from_dot_data(dot_string)
        return WFEngine(graph, state_functions)

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

    def render_graph(self, filename="workflow", format="png"):
        """Renders the graph to a file."""
        self.graph.write(f"{filename}.{format}", format=format)
