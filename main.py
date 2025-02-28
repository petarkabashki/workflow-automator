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

    # Run the workflow and process all states
    workflow = engine.start()
    for state, condition, state_override in workflow:
        if condition:
            print(f"State: {state}, Condition: {condition}")
        else:
            print(f"State: {state}")

if __name__ == "__main__":
    main()
