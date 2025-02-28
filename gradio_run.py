#%%
from engine import WFEngine
from engine_observer import EngineObserver
import gradio as gr

import asyncio

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
        self.context["name"] = input()
        print("Please enter your email:")
        self.context["email"] = input()
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
        confirmation = input()
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

# Run the workflow
# await engine.run()

def respond_to_user_message(message, history):
    yield message


demo = gr.ChatInterface(
    respond_to_user_message,
    type="messages"
)

demo.launch()

# %%
