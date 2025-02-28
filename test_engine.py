"""
Test suite for the workflow engine.
Logging is managed as follows:
1. Before any tests run, the test_logs directory is cleaned (deleted and recreated)
2. Each test gets its own log file in test_logs/<test_name>.log
3. Log files capture DEBUG level and above messages
4. Log format includes timestamp, logger name, level and message
5. Logs can be inspected after test runs to debug test behavior
"""

import pytest
from engine import WFEngine
from state_functions import StateFunctions
from utils import strip_quotes
import pydot
from unittest.mock import patch
import logging
import io
import os
import shutil
import re

# Update the tests to take into account that the state functions can yield multiple times. AI!

def get_log_contents(test_name):
    """
    Reads and returns the contents of a test's log file.
    
    Args:
        test_name: Name of the test whose log to read
        
    Returns:
        list: Lines from the log file with timestamps stripped
    """
    with open(f'test_logs/{test_name}.log', 'r') as f:
        # Strip timestamps from log lines for easier comparison
        return [re.sub(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - ', '', line.strip())
                for line in f.readlines()]

def clean_test_logs():
    """
    Cleans the test_logs directory before running tests.
    This ensures each test run starts with a fresh log directory.
    """
    if os.path.exists('test_logs'):
        shutil.rmtree('test_logs')
    os.makedirs('test_logs', exist_ok=True)

def setup_test_logger(test_name):
    """
    Creates a logger that writes to a file in test_logs directory.
    Each test gets its own log file for easier debugging.
    
    Args:
        test_name: Name of the test, used as the log file name
        
    Returns:
        logger: Configured logging.Logger instance
    """
    os.makedirs('test_logs', exist_ok=True)
    logger = logging.getLogger(test_name)
    logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers to avoid duplicate logging
    logger.handlers = []
    
    # Create file handler
    handler = logging.FileHandler(f'test_logs/{test_name}.log')
    handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    return logger

def test_multiple_transitions_without_condition_logs():
    """
    Test that appropriate error messages are logged when multiple transitions
    exist but no condition is provided.
    """
    logger = setup_test_logger('test_multiple_transitions_without_condition_logs')
    dot_string = """
    strict digraph {
        __start__ -> a [label="OK"];
        __start__ -> b [label="NOK"];
        a -> __end__;
        b -> __end__;
    }
    """
    state_functions = StateFunctions()
    setattr(state_functions, '__start__', lambda: (None, None))
    setattr(state_functions, 'a', lambda: (None, None))
    setattr(state_functions, 'b', lambda: (None, None))
    
    engine = WFEngine.from_dot_string(dot_string, state_functions)
    engine.set_logger(logger)
    
    # Run the workflow
    workflow = engine.start()
    states = []
    for state, condition, state_override in workflow:
        states.append(state)
        
    # Collect all states and verify sequence
    assert states == ['__start__', '__end__']
    
    logs = get_log_contents('test_multiple_transitions_without_condition_logs')
    expected_logs = [
        'test_multiple_transitions_without_condition_logs - INFO - Workflow started.',
        'test_multiple_transitions_without_condition_logs - DEBUG - Current state: __start__',
        'test_multiple_transitions_without_condition_logs - DEBUG - Running state: __start__',
        'test_multiple_transitions_without_condition_logs - ERROR - Multiple transitions found from state __start__ but no condition provided',
        'test_multiple_transitions_without_condition_logs - INFO - Workflow finished.'
    ]
    
    # Verify logs appear in exact order
    assert logs == expected_logs

def test_conditional_transition_logs():
    """
    Test that appropriate debug messages are logged during conditional transitions.
    """
    logger = setup_test_logger('test_conditional_transition_logs')
    dot_string = """
    strict digraph {
        __start__ -> a [label="OK"];
        __start__ -> b [label="NOK"];
        a -> __end__;
        b -> __end__;
    }
    """
    state_functions = StateFunctions()
    setattr(state_functions, '__start__', lambda: ("OK", None))
    setattr(state_functions, 'a', lambda: (None, None))
    setattr(state_functions, 'b', lambda: (None, None))
    
    engine = WFEngine.from_dot_string(dot_string, state_functions)
    engine.set_logger(logger)
    
    # Run the workflow
    workflow = engine.start()
    states = []
    for state, condition, state_override in workflow:
        states.append(state)
        
    # Collect all states and verify sequence
    assert states == ['__start__', 'a', '__end__']
    
    logs = get_log_contents('test_conditional_transition_logs')
    expected_logs = [
        'test_conditional_transition_logs - INFO - Workflow started.',
        'test_conditional_transition_logs - DEBUG - Current state: __start__',
        'test_conditional_transition_logs - DEBUG - Running state: __start__',
        'test_conditional_transition_logs - DEBUG - Transitioning to a based on condition OK',
        'test_conditional_transition_logs - DEBUG - Current state: a',
        'test_conditional_transition_logs - DEBUG - Running state: a',
        'test_conditional_transition_logs - DEBUG - Transitioning to __end__',
        'test_conditional_transition_logs - INFO - Workflow finished.'
    ]
    
    # Verify logs appear in exact order
    assert logs == expected_logs

def test_multiple_transitions_without_condition():
    """
    Test that the engine properly handles the case where a state has multiple possible
    transitions but no condition is provided by the state function.
    """
    logger = setup_test_logger('test_multiple_transitions_without_condition')
    dot_string = """
    strict digraph {
        __start__ -> a [label="OK"];
        __start__ -> b [label="NOK"];
        a -> __end__;
        b -> __end__;
    }
    """
    state_functions = StateFunctions()
    # State function returns no condition but has multiple possible transitions
    setattr(state_functions, '__start__', lambda: (None, None))
    setattr(state_functions, 'a', lambda: (None, None))
    setattr(state_functions, 'b', lambda: (None, None))
    
    engine = WFEngine.from_dot_string(dot_string, state_functions)
    engine.set_logger(logger)
    
    # Run the engine and check that it ends due to the error
    workflow = engine.start()
    states = []
    for state, condition, state_override in workflow:
        states.append(state)
    
    # Collect all states and verify sequence
    assert states == ['__start__', '__end__']
    
    assert engine.current_state == '__end__'

def create_test_engine(logger=None, dot_string=None):
    """Creates a test engine with optional custom dot string"""
    if dot_string is None:
        dot_string = """
        strict digraph {
            __start__ -> __end__;
        }
        """
    
    print(f"DOT STRING: {dot_string}")
    state_functions = StateFunctions()
    setattr(state_functions, '__start__', lambda: (None, '__end__'))
    engine = WFEngine.from_dot_string(dot_string, state_functions)
    if logger:
        engine.set_logger(logger)
    if engine is None:
        raise Exception("WFEngine.from_dot_string returned None")

    print(f"GRAPH: {engine.graph}")
    return engine

# Clean logs before any tests run
clean_test_logs()

def test_engine_creation_from_dot_string():
    logger = setup_test_logger('test_engine_creation_from_dot_string')
    engine = create_test_engine(logger=logger)
    assert engine is not None
    assert isinstance(engine.graph, pydot.Dot)

def test_engine_creation_from_nodes_and_edges():
    nodes = ['start', 'end']
    edges = [('start', 'end')]
    state_functions = StateFunctions()
    setattr(state_functions, '__start__', lambda: (None, '__end__'))
    engine = WFEngine.from_nodes_and_edges(nodes, edges, state_functions)
    assert engine is not None
    assert isinstance(engine.graph, pydot.Dot)

def test_state_execution():
    logger = setup_test_logger('test_state_execution')
    dot_string = """
    strict digraph {
        __start__ -> __end__;
    }
    """
    print(f"DOT STRING: {dot_string}")
    state_functions = StateFunctions()
    setattr(state_functions, 'start', lambda: (None, 'end'))
    engine = WFEngine.from_dot_string(dot_string, state_functions)
    if logger:
        engine.set_logger(logger)
    if engine is None:
        raise Exception("WFEngine.from_dot_string returned None")

    print(f"GRAPH: {engine.graph}")
    workflow = engine.start()
    for state, condition, state_override in workflow:
        assert state == "__start__"
        break

def test_conditional_transition():
    logger = setup_test_logger('test_conditional_transition')
    dot_string = """
    strict digraph {
        __start__ -> a [label="OK"];
        __start__ -> b [label="NOK"];
        a -> __end__;
        b -> __end__;
    }
    """
    state_functions = StateFunctions()
    setattr(state_functions, '__start__', lambda: ("OK", None))
    setattr(state_functions, 'a', lambda: (None, None))
    setattr(state_functions, 'b', lambda: (None, None))
    engine = WFEngine.from_dot_string(dot_string, state_functions)
    engine.set_logger(logger)
    
    # Run the engine as a generator
    workflow = engine.start()
    for state, condition, state_override in workflow:
        if state == "__end__":
            break
    assert engine.current_state == "__end__"

def test_strip_quotes():
    assert strip_quotes('"hello"') == "hello"
    assert strip_quotes("'world'") == "world"
    assert strip_quotes('test') == 'test'
    assert strip_quotes('') == ''
    assert strip_quotes(None) == None

def test_run_method(monkeypatch):
    logger = setup_test_logger('test_run_method')
    dot_string = """
       strict digraph {
           __start__ -> request_input;
           request_input -> extract_n_check[label="OK (Name and email provided)"];
           request_input -> request_input[label="NOK (Missing name or email)"];
           extract_n_check -> request_input[label="NOK (Data missing)"];
           extract_n_check -> ask_confirmation[label="OK (Data extracted)"];
           ask_confirmation -> process_data[label="Y (Confirmed)"];
           ask_confirmation -> request_input[label="N (Not confirmed)"];
           ask_confirmation -> __end__[label="Q (Quit)"];
           process_data -> __end__ [label="OK"];
       }
   """
    state_functions = StateFunctions()
    

    engine = WFEngine.from_dot_string(dot_string, state_functions)
    engine.set_logger(logger)

    # Mock input by controlling the generator
    workflow = engine.start()
    
    # Define mock responses
    responses = ["test_name", "test_email", "Y"]
    response_index = 0

    def mock_input():
        nonlocal response_index
        response = responses[response_index]
        response_index += 1
        return response

    # monkeypatch.setattr('state_functions.StateFunctions.request_input', lambda self: ("OK", None))
    monkeypatch.setattr('builtins.input', lambda *args: mock_input())

    states = ["__start__", "request_input", "extract_n_check", "ask_confirmation", "process_data"]
    
    i = 0
    for state, condition, state_override in workflow:
        if state == "__end__":
            break
        assert state == states[i]
        i += 1

    assert engine.current_state == "__end__"

