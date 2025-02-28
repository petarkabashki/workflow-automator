import pytest
from engine import WFEngine
from state_functions import StateFunctions
from utils import strip_quotes
import pydot
from unittest.mock import patch
import logging
import io
import os

def setup_test_logger(test_name):
    """Creates a logger that writes to a file in test_logs directory"""
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

def create_test_engine(logger=None):
    dot_string = """
    strict digraph {
        start -> end;
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
    return engine

def test_engine_creation_from_dot_string():
    logger = setup_test_logger('test_engine_creation_from_dot_string')
    dot_string = """
    strict digraph {
        start -> end;
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
    assert engine is not None
    assert isinstance(engine.graph, pydot.Dot)

def test_engine_creation_from_nodes_and_edges():
    nodes = ['start', 'end']
    edges = [('start', 'end')]
    state_functions = StateFunctions()
    setattr(state_functions, 'start', lambda: (None, 'end'))
    engine = WFEngine.from_nodes_and_edges(nodes, edges, state_functions)
    assert engine is not None
    assert isinstance(engine.graph, pydot.Dot)

def test_state_execution():
    logger = setup_test_logger('test_state_execution')
    dot_string = """
    strict digraph {
        start -> end;
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
    workflow = engine.run()
    for state, condition, state_override in workflow:
        assert state == "__start__"
        break

def test_conditional_transition():
    logger = setup_test_logger('test_conditional_transition')
    dot_string = """
    strict digraph {
        start -> a [label="OK"];
        start -> b [label="NOK"];
        a -> end;
        b -> end;
    }
    """
    state_functions = StateFunctions()
    setattr(state_functions, 'start', lambda: ("OK", None))
    logger = logging.getLogger('test_conditional_transition')
    engine = create_test_engine(logger=logger)
    
    # Run the engine as a generator
    workflow = engine.run()
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
           process_data -> __end__;
       }
   """
    state_functions = StateFunctions()
    

    engine = WFEngine.from_dot_string(dot_string, state_functions)
    engine.set_logger(logger)

    # Mock input by controlling the generator
    workflow = engine.run()
    
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

    #assert engine.current_state == "__end__"

def test_engine_creation_from_nodes_and_edges():
    nodes = ['start', 'end']
    edges = [('start', 'end')]
    state_functions = StateFunctions()
    setattr(state_functions, 'start', lambda: (None, 'end'))
    engine = WFEngine.from_nodes_and_edges(nodes, edges, state_functions)
    assert engine is not None
    assert isinstance(engine.graph, pydot.Dot)

def test_state_execution():
    logger = logging.getLogger('test_state_execution')
    engine = create_test_engine(logger=logger)
    if engine is not None:
        workflow = engine.run()
        for state, condition, state_override in workflow:
            assert state == "__start__"
            break

def test_conditional_transition():
    dot_string = """
    strict digraph {
        start -> a [label="OK"];
        start -> b [label="NOK"];
        a -> end;
        b -> end;
    }
    """
    state_functions = StateFunctions()
    setattr(state_functions, 'start', lambda: ("OK", None))
    engine = WFEngine.from_dot_string(dot_string, state_functions)
    
    # Run the engine as a generator
    workflow = engine.run()
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
           process_data -> __end__;
       }
   """
    state_functions = StateFunctions()
    engine = WFEngine.from_dot_string(dot_string, state_functions)

    # Mock input by controlling the generator
    workflow = engine.run()
    
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

    dot_string = """
    strict digraph {
        start -> end;
    }
    """
