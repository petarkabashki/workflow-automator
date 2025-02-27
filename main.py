import asyncio
from engine import WFEngine  # Use the new class name
from state_functions import StateFunctions

async def main():
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

    # Render the graph
    engine.render_graph()

    # Run the workflow
    await engine.run()

if __name__ == "__main__":
    asyncio.run(main())
