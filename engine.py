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
    It also acts as an observable, notifying subscribers of significant events.
    """

    def __init__(self, graph, state_functions):
        self.graph = graph
        self.state_functions = state_functions
        self.current_state = "__start__"
        self.lock = asyncio.Lock()
        self.observers = []  # List to store observers

    def subscribe(self, observer):
        """Subscribes an observer to receive notifications."""
        self.observers.append(observer)

    def unsubscribe(self, observer):
        """Unsubscribes an observer."""
        self.observers.remove(observer)

    def _notify_observers(self, event_type, data):
        """Notifies all subscribed observers."""
        for observer in self.observers:
            observer.notify(event_type, data)

    async def _run_state(self, state_name):
        """Runs the state function associated with the given state name."""

        self._notify_observers("state_function_call", {"state": state_name})

        state_method = getattr(self.state_functions, state_name, None)

        if state_method:
            try:
                if asyncio.iscoroutinefunction(state_method):
                    next_state_info = await state_method()
                else:
                    next_state_info = state_method()  # Should not happen

                self._notify_observers("condition_received", {"state": state_name, "condition": next_state_info})

                if isinstance(next_state_info, tuple):
                    condition, state_override = next_state_info
                    return condition, state_override
                else:
                    return None, None

            except Exception as e:
                self._notify_observers("error", {"state": state_name, "error": str(e)})
                raise  # Re-raise the exception to halt execution

        else:
            self._notify_observers("error", {"state": state_name, "error": "No state method found"})
            return None, None

    async def run(self):
        """Runs the workflow."""
        while self.current_state != "__end__":
            self._notify_observers("state_change", {"from": self.current_state, "to": None})  # Indicate upcoming change
            condition, state_override = await self._run_state(self.current_state)

            if state_override:
                self._notify_observers("state_override", {"from": self.current_state, "to": state_override})
                self.current_state = state_override
                self._notify_observers("state_change", {"from": None, "to": self.current_state}) # Indicate completed change
                break  # Exit after override

            elif condition is not None:
                found_transition = False
                for edge in self.graph.get_edges():
                    if edge.get_source() == self.current_state:
                        label = strip_quotes(edge.get_label())
                        short_label = label.split(" ")[0]  # Extract the short code
                        if short_label and self.evaluate_condition(short_label, condition):
                            self._notify_observers("transition", {"from": self.current_state, "to": edge.get_destination(), "condition": condition, "label": label}) # Include full label
                            self.current_state = edge.get_destination()
                            found_transition = True
                            break
                if not found_transition:
                    self._notify_observers("transition_error", {"from": self.current_state, "condition": condition, "error": "No matching edge found"})
                    self.current_state = '__end__'
            else:
                found_transition = False
                for edge in self.graph.get_edges():
                    if edge.get_source() == self.current_state:
                        label = strip_quotes(edge.get_label()) # get the label
                        self._notify_observers("transition", {"from": self.current_state, "to": edge.get_destination(), "condition": None, "label":label}) # pass label
                        self.current_state = edge.get_destination()
                        found_transition = True
                        break
                if not found_transition:
                    if self.current_state != '__end__':
                        self._notify_observers("transition_error", {"from": self.current_state, "error": "No outgoing edges"})
                        self.current_state = '__end__'
            self._notify_observers("state_change", {"from": None, "to": self.current_state}) # completed state change

        self._notify_observers("workflow_finished", {})


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
