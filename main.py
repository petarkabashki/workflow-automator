import asyncio
import graphviz
from .engine import EngineExecutor
from .state_functions import StateFunctions

async def main():
    """
    Main entry point for the workflow automation application.
    """

    # Load the DOT file
    with open("workflow.dot", "r") as f:
        dot_content = f.read()

    # Parse the DOT file
    graph = graphviz.Source(dot_content)

    # Initialize the state function class
    state_functions = StateFunctions()

    # Initialize the engine executor
    executor = EngineExecutor(graph, state_functions)

    # Run the workflow
    await executor.run()

if __name__ == "__main__":
    asyncio.run(main())
