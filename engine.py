from typing import Dict, List, Any, Tuple, Generator, Optional, Union, Callable
import logging

# Module-level logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class StateFunctionRegistry:
    """Registry for state functions to allow dynamic registration and retrieval."""

    def __init__(self):
        self._registry = {}

    def register(self, state_name: str, func: Callable) -> None:
        """
        Registers a state function for the given state name.

        Args:
            state_name: The name of the state to register
            func: The function to associate with the state
        """
        self._registry[state_name] = func

    def get_function(self, state_name: str) -> Optional[Callable]:
        """
        Retrieves the state function for the given state name.

        Args:
            state_name: The name of the state to retrieve

        Returns:
            The function associated with the state or None if not found
        """
        return self._registry.get(state_name)


class Engine:
    def __init__(self, registered_functions: Dict[str, Callable]) -> None:
        """
        Engine implemented as a generator function.

        Args:
            registered_functions: A dictionary mapping state names to generator functions.

        Yields:
            Tuples of (instruction, context, current_node_name, current_node) received from the current node.

        Receives:
            Tuples of (instruction, context) to be passed to the current node.
        """

        # Enforce starting from '__start__'
        self.registered_functions = registered_functions
        if "__start__" not in registered_functions:
            raise ValueError("Registered functions must include a '__start__' node.")

        self.current_node_name = "__start__"  # Initialize current_node_name
        self.current_node = self.registered_functions["__start__"]
        self.instruction, self.context = None, None
        self.current_node_instance = self.current_node()  # Instantiate the generator
        received_from_node = next(self.current_node_instance)  # Prime
        self.temp_yield = (
            self.current_node_name,  # Yield the function, not the instance
            received_from_node[0] if received_from_node is not None else None,
            received_from_node[1] if received_from_node is not None else None,
        )

    def run(self) -> Generator:
        yield self.temp_yield  # and yield immediately with node

        while True:
            try:
                if self.instruction == "transition" or self.instruction == "node_transition":
                    next_node_name = self.context
                    if next_node_name == "__end__":
                        yield (None, "transition", "__end__")  # Yield transition to __end__ with None node
                        break  # Stop after yielding the transition to __end__
                    if next_node_name not in self.registered_functions:
                        raise KeyError(f"Invalid transition target: {next_node_name}")
                    self.current_node_name = next_node_name  # Update current_node_name
                    self.current_node = self.registered_functions[next_node_name]
                    self.current_node_instance = self.current_node()  # Instantiate the generator
                    # Yield the NEXT node, along with the transition instruction
                    yield (next_node_name, "transition", next_node_name)
                    # The next input will be sent to this new node, and we receive it here
                    self.instruction, self.context = yield
                else:
                    received_from_node = self.current_node_instance.send((self.instruction, self.context))
                    self.instruction, self.context = received_from_node
                    temp_yield = (self.current_node_name, self.instruction, self.context)
                    print(f"Engine yielding in else: {temp_yield}")
                    yield temp_yield

            except StopIteration:
                break
            except KeyError as e:
                yield ("error", str(e))
                break

    def run_engine(self, registered_functions: Dict[str, Callable]):
        """
        Runs the engine, handling instructions and transitions.

        Args:
            registered_functions: A dictionary mapping state names to generator functions.
        """
        instruction, context = None, None
        engine_instance = Engine(registered_functions)
        engine = engine_instance.run()
        # Prime the engine generator
        try:
            response = next(engine)
            current_node, instruction, context = response  # Unpack current_node, instruction, and context
            print(f"Engine output: {instruction}, {context}")  # For demonstration
        except StopIteration:
            return

        while True:
            try:
                response = engine.send((instruction, context))
                current_node, instruction, context = response  # Unpack current_node, instruction, and context
                print(f"Engine output: {instruction}, {context}")  # For demonstration

                if instruction == "transition" and context == "__end__":
                    print("Reached end state - capturing final output")  # DEBUG print
                    # Capture the __end__ transition output BEFORE breaking
                    # No need to do anything special, the 'output.append((instruction, context))' in run_and_capture already captures it
                    break  # Exit if engine transitions to the end node

            except StopIteration:
                break
