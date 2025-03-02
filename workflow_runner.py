from typing import Dict, List, Any, Tuple, Generator, Optional, Union, Callable
from dot_parser import DotParser
import utils
import logging
from engine import Engine


class WorkflowRunner:
    def __init__(self):
        pass

    def __start__(self):
        yield (f"__start___init", f"Data from __start__")
        instruction, context = yield ("ready", f"Waiting in __start__")
        print(f"__start__ received: {instruction}, {context}")
        if context == "transition_from_node":
            yield ("node_transition", "next_node")  # Example of node-initiated transition
        yield ("node-enter", "__start__")
        yield ("transition", "request_input")

    def request_input(self):
        # Yield the request_input instruction with the query
        yield ("request_input", "Please provide your name and email")
        # Get the user input
        user_input = yield ("get_input", None)
        # Create context dict with user input
        context = {"user_input": user_input}
        
        print(f"request_input received input: {user_input}")
        if user_input.lower() == "quit":
            yield ("node-enter", "request_input")
            yield ("transition", "__end__")
        else:
            yield ("node-enter", "request_input")
            yield ("transition", "extract_n_check", context)

    def extract_n_check(self):
        yield (f"extract_n_check_init", f"Data from extract_n_check")
        instruction, context = yield ("ready", f"Waiting in extract_n_check")
        print(f"extract_n_check received: {instruction}, {context}")
        if context == "transition_from_node":
            yield ("node_transition", "next_node")  # Example of node-initiated transition
        yield ("node-enter", "extract_n_check")
        yield ("transition", "ask_confirmation")

    def ask_confirmation(self):
        yield (f"ask_confirmation_init", f"Data from ask_confirmation")
        instruction, context = yield ("ready", f"Waiting in ask_confirmation")
        print(f"ask_confirmation received: {instruction}, {context}")
        if context == "transition_from_node":
            yield ("node_transition", "next_node")  # Example of node-initiated transition
        yield ("node-enter", "ask_confirmation")
        yield ("transition", "process_data")

    def process_data(self):
        yield (f"process_data_init", f"Data from process_data")
        instruction, context = yield ("ready", f"Waiting in process_data")
        print(f"process_data received: {instruction}, {context}")
        if context == "transition_from_node":
            yield ("node_transition", "next_node")  # Example of node-initiated transition
        yield ("node-enter", "process_data")
        yield ("transition", "__end__")

    def dummy_transition(self):
        yield (f"dummy_transition_init", f"Data from dummy_transition")
        instruction, context = yield ("ready", f"Waiting in dummy_transition")
        print(f"dummy_transition received: {instruction}, {context}")
        if context == "transition_from_node":
            yield ("node_transition", "next_node")  # Example of node-initiated transition
        yield ("node-enter", "dummy_transition")
        yield ("transition", "__end__")

    def __end__(self):
        yield (f"__end___init", f"Data from __end__")
        instruction, context = yield ("ready", f"Waiting in __end__")
        print(f"__end__ received: {instruction}, {context}")
        if context == "transition_from_node":
            yield ("node_transition", "next_node")  # Example of node-initiated transition
        yield ("node-enter", "__end__")
        yield ("transition", "__end__")

    def parse_dot_string(self, dot_string: str) -> Tuple[Dict[str, Callable], str]:
        """
        Parses a DOT string and returns registered functions and the start node.

        Args:
            dot_string: The DOT string representing the workflow.

        Returns:
            A tuple containing:
              - A dictionary of registered functions (node name -> generator function).
              - The start node name ("__start__").
        """
        parser = DotParser()
        graph = parser.parse(dot_string)

        if not graph or not graph['nodes'] or not graph['edges']:
            raise ValueError("Invalid DOT string or empty graph.")

        nodes = [utils.strip_quotes(node['id']).strip() for node in graph['nodes'].values()]
        transitions = {}
        for edge in graph['edges']:
            source = utils.strip_quotes(edge['source']).strip()
            destination = utils.strip_quotes(edge['target']).strip()
            label = edge.get('label')  # Get the label, which might be None
            if label:
                label = label.strip()
            else:
                label = ''  # Set to empty string if label is None

            if source not in transitions:
                transitions[source] = []
            transitions[source].append((destination, label))

        # Create registered functions
        node_names = self.create_node_functions(nodes)

        return node_names, "__start__"

    def create_node_functions(self, nodes: List[str]) -> List[str]:
        """
        Creates dummy node functions for the given nodes.

        Args:
            nodes: List of node names.

        Returns:
            A dictionary of registered functions (node name -> generator function).
        """
        node_names = []
        for node in nodes:
            node_names.append(node)
        return node_names

    def create_registered_functions(self, nodes: List[str]) -> Dict[str, Callable]:
        registered_functions = {}
        for node in nodes:
            registered_functions[node] = getattr(self, node)
        return registered_functions

    def run_workflow_from_dot(self, dot_string: str):
        """
        Runs the workflow engine using a DOT string to define the workflow.

        Args:
            dot_string: The DOT string representing the workflow.
        """
        node_names, start_node = self.parse_dot_string(dot_string)
        registered_functions = self.create_registered_functions(node_names)
        engine_instance = Engine()(registered_functions)  # Create engine instance
        Engine().run_engine(engine_instance)  # Run the engine
