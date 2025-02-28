#%% 
from engine import WFEngine
from state_functions import StateFunctions
from engine_observer import EngineObserver

def main():
    """
    Main entry point for the workflow automation application.
    """

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
    engine.run()

    # Save the log
    observer.save_log()

if __name__ == "__main__":
    main()

# %%
