from engine import WFEngine
from state_functions import StateFunctions

def main():
    """
    Main entry point for the workflow automation application.
    """
    # Load the DOT file
    with open("workflow.dot", "r") as f:
        dot_content = f.read()

    # Initialize the state function class
    state_functions = StateFunctions()

    # Initialize the engine using from_dot_string
    engine = WFEngine.from_dot_string(dot_content, state_functions)
    if engine is None:
        print("Failed to create workflow engine")
        return

    # Render the graph visualization
    engine.render_graph()

    # Run the workflow
    engine.start()
    # The workflow execution is handled by the engine internally
    # No need to iterate over the result as it doesn't return anything

if __name__ == "__main__":
    main()
