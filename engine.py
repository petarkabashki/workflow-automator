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
            next_state = await self._run_state(self.current_state)

            if next_state:
                # Method override
                self.current_state = next_state
            else:
                # pydot-specific edge traversal with label checking
                found_transition = False
                for edge in self.graph.get_edges():
                    if edge.get_source() == self.current_state:
                        label = edge.get_label()  # Get the edge label
                        if label:
                            # VERY SIMPLE condition evaluation (replace with your logic)
                            if self.evaluate_condition(label):
                                self.current_state = edge.get_destination()
                                found_transition = True
                                break
                        else:
                            # Transition if there is no label
                            self.current_state = edge.get_destination()
                            found_transition = True
                            break

                if not found_transition:
                    if self.current_state != '__end__':
                        print(f"No outgoing edges from state: {self.current_state}")
                        self.current_state = '__end__'

        print("Workflow finished.")
        print("Interaction History:")
        for interaction in self.interaction_history:
            print(f"- {interaction[0]}: {interaction[1]}")

    def evaluate_condition(self, condition_string):
        """
        Evaluates a condition string.  This is a placeholder; you'll need
        to implement your actual condition evaluation logic here.
        """
        # VERY BASIC EXAMPLE:  Just checks if the condition string is "true" (case-insensitive)
        if condition_string.lower() == "true":
            return True
        elif condition_string.lower() == "false":
            return False
        else:
            print(f"invalid condition {condition_string}")
            return False


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
            graph.add_edge(pydot.Edge(edge[0], edge[1]))
        return WFEngine(graph, state_functions)

    def render_graph(self, filename="workflow", format="png"):
        """Renders the graph to a file."""
        self.graph.write(f"{filename}.{format}", format=format)
