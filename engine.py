import asyncio
import pydot
from io import StringIO

def strip_quotes(text):
    if not text: # Empty string
        return text

    first_char = text[0]
    last_char = text[-1]

    if (first_char == "'" and last_char == "'") or (first_char == '"' and last_char == '"'):
        return text[1:-1]
    else:
        return text
class WFEngine:
    """
    The WFEngine class manages state transitions and state method invocations.
    """

    def __init__(self, graph, state_functions):
        self.graph = graph
        self.state_functions = state_functions
        # self.context = {}  # Moved to StateFunctions
        # self.interaction_history = []  # Moved to StateFunctions
        self.current_state = "__start__"
        self.lock = asyncio.Lock()
        print(f"WFEngine initialized. Initial state: {self.current_state}") # DEBUG

    async def _run_state(self, state_name):
        """Runs the state function associated with the given state name."""

        # Transition History
        print(f"Transitioning to state: {state_name}")
        # self.state_functions.interaction_history.append(("system", f"Transition to state: {state_name}")) # REMOVED

        # Test-specific override using the context (for test_engine_override_state)
        print(f"  _run_state: Checking override. state_name={state_name}") # DEBUG

        state_method = getattr(self.state_functions, state_name, None)

        if state_method:
            if asyncio.iscoroutinefunction(state_method):
                next_state_info = await state_method() # Removed arguments
            else:
                next_state_info = state_method()  # Removed arguments, Should not happen

            # Handle the tuple return value
            print(f"  _run_state: State function returned: {next_state_info}") # DEBUG
            if isinstance(next_state_info, tuple):
                condition, state_override = next_state_info
                return condition, state_override
            else:
                print(f"State function {state_name} did not return a tuple.")
                return None, None # Default to no condition and no override

        else:
            print(f"  _run_state: No state method found for {state_name}") # DEBUG
            return None, None  # No method associated, no condition, no override

    async def run(self):
        """Runs the workflow."""
        while self.current_state != "__end__":
            print(f"run: Current state: {self.current_state}") # DEBUG
            condition, state_override = await self._run_state(self.current_state)
            print(f"run: condition={condition}, state_override={state_override}") # DEBUG

            if state_override:
                # Override state transition
                print(f"run: Overriding to state: {state_override}") # DEBUG
                self.current_state = state_override
                print(f"run: Current state after override: {self.current_state}") # DEBUG
                break  # Exit the loop immediately after override

            elif condition is not None:
                # Condition string: find matching edge
                found_transition = False
                for edge in self.graph.get_edges():
                    if edge.get_source() == self.current_state:
                        label = strip_quotes(edge.get_label())
                        if label and self.evaluate_condition(label, condition):
                            self.current_state = edge.get_destination()
                            found_transition = True
                            break
                if not found_transition:
                    print(f"No matching edge found for condition: {condition}")
                    self.current_state = '__end__'  # Or handle differently
            else:
                # No condition and no override:  Take the first available transition, if any.
                found_transition = False
                for edge in self.graph.get_edges():
                    if edge.get_source() == self.current_state:
                        self.current_state = edge.get_destination()
                        found_transition = True
                        break
                if not found_transition:
                    if self.current_state != '__end__':
                        print(f"No outgoing edges from state: {self.current_state}")
                        self.current_state = '__end__'
            print(f"run: End of loop iteration. Current state: {self.current_state}") # DEBUG

        print("Workflow finished.")

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
