import asyncio
import networkx as nx
from networkx.drawing.nx_pydot import parse_dot
from io import StringIO

class EngineExecutor:
    """
    The EngineExecutor class manages user interaction, engine observability,
    and interaction history.
    """

    def __init__(self, graph: nx.DiGraph, state_functions):
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
                # NetworkX-specific edge traversal
                found_transition = False
                for u, v in self.graph.edges():  # Iterate through edges
                    if u == self.current_state:
                        self.current_state = v
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

    @staticmethod
    def from_dot_string(dot_string, state_functions):
        """Creates an EngineExecutor from a DOT string."""
        graph = parse_dot(dot_string)
        # Convert to DiGraph
        di_graph = nx.DiGraph()
        for node in graph.get_nodes():
            di_graph.add_node(node.get_name())
        for edge in graph.get_edges():
            di_graph.add_edge(edge.get_source(), edge.get_destination())

        return EngineExecutor(di_graph, state_functions)

    @staticmethod
    def from_nodes_and_edges(nodes, edges, state_functions):
        """Creates an EngineExecutor from lists of nodes and edges."""
        graph = nx.DiGraph()
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        return EngineExecutor(graph, state_functions)
