#%%
from engine import WFEngine
from engine_observer import EngineObserver
import gradio as gr
import asyncio
import contextlib
import io

class StateFunctions:
    """
    This class houses asynchronous state function logic.
    """

    def __init__(self):
        self.context = {}  # Initialize context here
        self.interaction_history = []  # Initialize history here

    async def request_input(self):
        """Requests user input for name and email."""
        print("Please enter your name:")
        name = await self.get_input()
        print("Please enter your email:")
        email = await self.get_input()
        self.context["name"] = name
        self.context["email"] = email

        # Check for any input, if empty, loop back
        if not self.context["name"] or not self.context["email"] or not self.context["name"].strip() or not self.context["email"].strip():
            print("Name and email are required.")
            self.interaction_history.append(("user", f"Input: Name={self.context.get('name', '')}, Email={self.context.get('email', '')}"))
            return "NOK", None  # Loop back to request_input

        self.interaction_history.append(("user", f"Input: Name={self.context['name']}, Email={self.context['email']}"))
        return "OK", None

    async def extract_n_check(self):
        """Extracts and checks the collected data."""
        print(f"Extracting and Checking {self.context}")
        self.interaction_history.append(("system", f"Extracting and checking: {self.context}"))
        if "name" in self.context and "email" in self.context:
            return "OK", None
        else:
            return "NOK", None # This case should not happen based on the workflow, but is added for completeness

    async def ask_confirmation(self):
        """Asks for confirmation from the user."""
        print("Do you confirm the data is correct? (yes/no/quit)")
        confirmation = await self.get_input()
        self.interaction_history.append(("user", f"Confirmation input: {confirmation}"))
        if confirmation.lower() in ["yes", "y"]:
            return "Y", None
        elif confirmation.lower() in [ "no", "n"] :
            return "N", None
        elif confirmation.lower() in ["quit", "q"]:
            return "Q", None
        else:
            print("Invalid input. Please enter 'yes', 'no', or 'quit'.")
            return "invalid_confirmation", "ask_confirmation" # Loop using override


    async def process_data(self):
        """Processes the collected data (prints it in this example)."""
        print("Processing ")
        print(f"  Name: {self.context['name']}")
        print(f"  Email: {self.context['email']}")
        self.interaction_history.append(("system", "Data processed."))
        return None, None  # No label defined in workflow.dot, goes to __end__

    async def __start__(self):
        """Start state"""
        self.interaction_history.append(("system", "Workflow started."))
        return None, None

    async def get_input(self):
        """Placeholder for getting input.  This will be filled in by Gradio."""
        raise NotImplementedError("get_input must be overridden")

# Load the DOT file
with open("workflow.dot", "r") as f:
    dot_content = f.read()

# Initialize the state function class
state_functions = StateFunctions()

# Initialize the engine executor using from_dot_string
engine = WFEngine.from_dot_string(dot_content, state_functions)

# Create and subscribe the observer
observer = EngineObserver()
engine.subscribe(observer)

# Render the graph
engine.render_graph()

async def respond_to_user_message(message, history):
    """Handles user input and engine progression."""

    # 1. Set the input function for the state functions.
    async def get_user_input():
        nonlocal message
        return message

    state_functions.get_input = get_user_input
    transition_label = "" # store label

    # 2. Capture stdout to display in the chatbot.
    with io.StringIO() as buf, contextlib.redirect_stdout(buf):
        # 3. Run the current state.
        if engine.current_state != "__end__":
            condition, override = await engine._run_state(engine.current_state)
            if override:
                engine.current_state = override
            elif condition:
                for edge in engine.graph.get_edges():
                    if edge.get_source() == engine.current_state:
                        label = engine.strip_quotes(edge.get_label())
                        short_label = label.split(" ")[0]  # Extract the short code
                        if short_label and engine.evaluate_condition(short_label, condition):
                            engine.current_state = edge.get_destination()
                            transition_label = label # store for display
                            break
            else: # transition with no condition
                for edge in engine.graph.get_edges():
                    if edge.get_source() == engine.current_state:
                        label = engine.strip_quotes(edge.get_label())
                        transition_label = label # store for display
                        engine.current_state = edge.get_destination()
                        break

        # 4. Get the captured output.
        captured_output = buf.getvalue()

    # 5. Update history and return.
    history.append((message, captured_output + f"\n\n*Next Transition: {transition_label}*")) # show transition

    # 6. If engine finished, reset for next interaction
    if engine.current_state == "__end__":
        history.append((None, "Workflow finished. Starting over."))
        engine.current_state = "__start__"
        state_functions.context = {} # clear context
        state_functions.interaction_history = []

    return "", history

demo = gr.ChatInterface(
    respond_to_user_message,
    chatbot=gr.Chatbot(type="messages"),
    type="text"
)

demo.launch()

# %%
