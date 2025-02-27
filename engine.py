import asyncio
import graphviz

class EngineExecutor:
    """
    The EngineExecutor class manages user interaction, engine observability,
    and interaction history.
    """

    def __init__(self, graph: graphviz.Source, state_functions):
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
                # DOT transition
                found_transition = False
                for statement in self.graph.body:
                    if statement.startswith(f'\t{self.current_state} ->'):
                        parts = statement.split("->")
                        self.current_state = parts[1].strip()
                        found_transition = True
                        break  # Only take the first transition

                if not found_transition:
                    # No outgoing edges, stay in current state
                    if self.current_state != '__end__':
                        print(f"No outgoing edges from state: {self.current_state}")
                        # Could raise an exception or handle differently
                        self.current_state = '__end__' # Stop the execution

        print("Workflow finished.")
        print("Interaction History:")
        for interaction in self.interaction_history:
            print(f"- {interaction[0]}: {interaction[1]}")
