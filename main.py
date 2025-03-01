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

    # Start the workflow and iterate through states
    workflow_generator = engine.start()
    if workflow_generator:
        for state in workflow_generator:
            print(f"Entering state: {state}")
            # Here you can add any state-specific processing in main.py if needed
    else:
        print("Failed to start workflow")

if __name__ == "__main__":
    main()
