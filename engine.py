import asyncio
import pydot
from io import StringIO

class WFEngine:
    """
    The WFEngine class manages user interaction, engine observability,
    and interaction history.
    """

    def __init__(self, graph, state_functions):
        self.graph = graph
        self.state_functions = state_functions
        self.context = {}  # Shared memory for state functions
        self.current_state = "__start__"
        self.interaction_history = []
        self.lock = asyncio.Lock()  # Asynchronous lock

    async def send_input(self, input_data):
        """
        Provides text/option input to the engine.
        """
        async with self.lock:
            self.context["last_input"] = input_data
            self.interaction_history.append(("user", input_data))
            # Resume execution after input
            self.resume_event.set()

    async def upload_file(self, file_path):
        """
        Provides file uploads to the engine.
        """
        async with self.lock:
            self.context["last_file"] = file_path
            self.interaction_history.append(("user", f"Uploaded file: {file_path}"))
            # Resume execution after file upload
            self.resume_event.set()

    async def _request_input(self, prompt, input_type="text"):
        """Handles user input requests."""
        async with self.lock:
            print(prompt)
            self.interaction_history.append(("system", prompt))
            self.resume_event = asyncio.Event()

        # Pause workflow during input request
        await self.resume_event.wait()
        return self.context.get("last_input")

    async def _run_state(self, state_name):
        """Runs the state function associated with the given state name."""

        # Transition History
        print(f"Transitioning to state: {state_name}")
        self.interaction_history.append(("system", f"Transition to state: {state_name}"))

        state_method = getattr(self.state_functions, state_name, None)

        if state_method:
            if asyncio.iscoroutinefunction(state_method):
                next_state = await state_method(self.context, self)
            else:
                next_state = state_method(self.context, self)  # Still pass self for consistency
        else:
            next_state = None  # No method associated, stay in current state

        return next_state

    async def run(self):
        """Runs the workflow."""
        while self.current_state != "__end__":
            next_state_or_condition = await self._run_state(self.current_state)

            if next_state_or_condition == "override_state":
                # Prompt for the next state
                next_state = await self._request_input("Enter next state:")
                self.current_state = next_state
            elif isinstance(next_state_or_condition, str):
                # Condition string: find matching edge
                found_transition = False
                for edge in self.graph.get_edges():
                    if edge.get_source() == self.current_state:
                        label = edge.get_label()
                        if label and self.evaluate_condition(label, next_state_or_condition):
                            self.current_state = edge.get_destination()
                            found_transition = True
                            break
                if not found_transition:
                    print(f"No matching edge found for condition: {next_state_or_condition}")
                    self.current_state = '__end__'  # Or handle differently
            elif next_state_or_condition is None:
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
            else:
                # Invalid return type
                print(f"Invalid return type from state function: {type(next_state_or_condition)}")
                self.current_state = '__end__'

        print("Workflow finished.")
        print("Interaction History:")
        for interaction in self.interaction_history:
            print(f"- {interaction[0]}: {interaction[1]}")

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
