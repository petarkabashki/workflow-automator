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
        current_state = next(workflow_generator) # Start the engine
        while current_state != "__end__":
            if isinstance(current_state, tuple):
                signal_type = current_state[0]
                signal_data = current_state[1] # could be state name, prompt, etc.

                if signal_type == "state_change":
                    state_name = signal_data
                    print(f"Entering state: {state_name}")

                elif signal_type == "input_required":
                    prompt = signal_data
                    user_response = input(prompt) # Get input from *actual* user
                    try:
                        current_state = workflow_generator.send(user_response) # Send input back to engine
                        continue # Skip next() as send() already advances
                    except StopIteration:
                        break # Exit if engine finishes after input
                else:
                    print(f"Unknown signal type: {signal_type},  {signal_data}") # Handle unknown signals
                    break # Exit on unknown signal
            else:
                print(f"Unexpected yield format: {current_state}") # Should yield tuples now
                break # Exit on unexpected format

            try:
                current_state = next(workflow_generator) # Advance to next yield
            except StopIteration:
                break # Exit loop if engine finishes normally

        if current_state == "__end__":
            print("Workflow finished successfully.")
        else:
            print("Workflow finished unexpectedly.") # Or handle other termination conditions

    else:
        print("Failed to start workflow")

if __name__ == "__main__":
    main()
