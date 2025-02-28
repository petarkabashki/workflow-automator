import sys

# VERY STRICT CHECK: If this file is run directly using the 'python' command
# (and not 'pytest'), prevent execution.  We check the FIRST argument
# in sys.argv.  If it ends with 'test_engine.py', we know it was run directly.
if __name__ == "__main__":
    if sys.argv[0].endswith("test_engine.py"):
        print("\nERROR: Do not run this file directly with 'python test_engine.py'.")
        print("       This will bypass pytest and cause errors.")
        print("       Instead, run the `run_tests.sh` or `run_test.sh` script:")
        print("       1. Make sure the script is executable: `chmod +x run_tests.sh` (or run_test.sh)")
        print("       2. Run the script: `./run_tests.sh` (or ./run_test.sh)")
        print("       This will install pytest and run the tests correctly.\n")
        sys.exit(1)  # Exit with an error code

import pytest
import asyncio
import pydot
from engine import WFEngine
# from state_functions import StateFunctions  # No longer needed
from unittest.mock import AsyncMock  # AsyncMock is no longer needed
import os

# --- Custom Mock State Functions ---
class MockStateFunctions:
    def __init__(self):
        self.context = {}  # Initialize context here
        self.interaction_history = [] # Initialize history here

    def request_input(self):
        # Simulate user input by directly setting context values
        self.context["name"] = "Test Name"
        self.context["email"] = "test@example.com"
        return "data_collected", None

    def extract_data(self):
        print(f"Extracting  {self.context}")
        return "data_extracted", None

    def check_all_data_collected(self):
        if "name" in self.context and "email" in self.context:
            return "all_data_collected", None
        else:
            return None, "override_state"

    def ask_confirmation(self):
        # Simulate different confirmation responses based on context
        confirmation = self.context.get("confirmation_response", "yes")  # Default to "yes"
        if confirmation.lower() == "yes":
            return "confirmed", None
        elif confirmation.lower() == "no":
            return "not_confirmed", None
        else:
            return "invalid_confirmation", None


    def process_data(self):
        print("Processing ")
        print(f"  Name: {self.context['name']}")
        print(f"  Email: {self.context['email']}")
        return "data_processed", None

    def __start__(self):
        return None, None  # No condition, no override

    def state1(self):
        # if self.context.get("override_state_from_state1"):
        return (None, "override_state_target")
        # return None, None # Default

# --- End Custom Mock State Functions ---


def test_engine_executor_initialization():
    # Create a simple pydot graph using from_nodes_and_edges
    nodes = ['__start__', 'request_input', '__end__']
    edges = [('__start__', 'request_input'), ('request_input', '__end__')]
    state_functions = MockStateFunctions()  # Use mock state functions
    engine = WFEngine.from_nodes_and_edges(nodes, edges, state_functions)
    assert engine is not None

def test_engine_executor_run():
    # Create graph with labels for conditions
    nodes = ['__start__', 'request_input', 'extract_data', 'check_all_data_collected',
             'ask_confirmation', 'process_data', '__end__']
    edges = [
        {'src': '__start__', 'dst': 'request_input', 'label': 'start_input'},
        {'src': 'request_input', 'dst': 'extract_data', 'label': 'data_collected'},
        {'src': 'extract_data', 'dst': 'check_all_data_collected', 'label': 'data_extracted'},
        {'src': 'check_all_data_collected', 'dst': 'ask_confirmation', 'label': 'all_data_collected'},
        {'src': 'ask_confirmation', 'dst': 'process_data', 'label': 'confirmed'},
        {'src': 'process_data', 'dst': '__end__', 'label': 'data_processed'}
    ]
    state_functions = MockStateFunctions()  # Use mock state functions
    engine = WFEngine.from_nodes_and_edges(nodes, edges, state_functions)

    # No longer mocking _request_input; interactions happen within state functions
    engine.run()
    assert engine.current_state == "__end__"
    assert "name" in engine.state_functions.context
    assert "email" in engine.state_functions.context
    assert engine.state_functions.context["name"] == "Test Name"
    assert engine.state_functions.context["email"] == "test@example.com"

def test_engine_executor_run_no_confirmation():
    # Create graph from DOT string with labels
    dot_string = """
    digraph {
        __start__ -> request_input [label="start_input"];
        request_input -> extract_data [label="data_collected"];
        extract_data -> check_all_data_collected [label="data_extracted"];
        check_all_data_collected -> ask_confirmation [label="all_data_collected"];
        ask_confirmation -> process_data [label="confirmed"];
        ask_confirmation -> __end__ [label="not_confirmed"];
        process_data -> __end__;
    }
    """
    state_functions = MockStateFunctions()  # Use mock state functions
    engine = WFEngine.from_dot_string(dot_string, state_functions)

    # Set context to simulate "no" response
    engine.state_functions.context["confirmation_response"] = "no"
    engine.run()
    assert engine.current_state == "__end__"  # Should still end, but via different path

def test_engine_executor_run_invalid_confirmation():
    # Create graph from DOT string with labels
    dot_string = """
    digraph {
        __start__ -> request_input [label="start_input"];
        request_input -> extract_data [label="data_collected"];
        extract_data -> check_all_data_collected [label="data_extracted"];
        check_all_data_collected -> ask_confirmation [label="all_data_collected"];
        ask_confirmation -> process_data [label="confirmed"];
        ask_confirmation -> __end__ [label="not_confirmed"];
        process_data -> __end__;
    }
    """
    state_functions = MockStateFunctions()  # Use mock state functions
    engine = WFEngine.from_dot_string(dot_string, state_functions)

    # Set context to simulate "invalid" response, then engine will loop back to ask_confirmation
    engine.state_functions.context["confirmation_response"] = "invalid"
    engine.run()
    assert engine.current_state == '__end__'

def test_engine_executor_render_graph(tmp_path):
    """Tests the render_graph method."""
    # Create a simple graph
    nodes = ['__start__', 'state1', '__end__']
    edges = [('__start__', 'state1'), ('state1', '__end__')]
    state_functions = MockStateFunctions()  # Use mock state functions
    engine = WFEngine.from_nodes_and_edges(nodes, edges, state_functions)

    # Render the graph to a temporary file
    output_file = tmp_path / "test_graph.png"
    engine.render_graph(filename=str(output_file.parent / output_file.stem), format="png")

    # Check if the file exists
    assert output_file.exists()
    # Check file size to ensure it's not empty (basic check for rendering)
    assert output_file.stat().st_size > 0

    # Test with a different format
    output_file_pdf = tmp_path / "test_graph.pdf"
    engine.render_graph(filename=str(output_file_pdf.parent / output_file_pdf.stem), format="pdf")
    assert output_file_pdf.exists()
    assert output_file_pdf.stat().st_size > 0

def test_engine_override_state():
    """Tests the 'override_state' functionality."""
    # Create a simple graph
    nodes = ['__start__', 'state1', 'override_state_target', '__end__']
    edges = [
        {'src': '__start__', 'dst': 'state1', 'label': 'to_state1'},
        {'src': 'state1', 'dst': '__end__', 'label': 'to_end'},
    ]
    state_functions = MockStateFunctions() # Use mock state functions
    engine = WFEngine.from_nodes_and_edges(nodes, edges, state_functions)

    # Set a flag in the context to trigger the override in _run_state
    engine.state_functions.context["override_state_from_state1"] = True

    # No longer mocking _request_input
    engine.run()
    assert engine.current_state == "override_state_target"
