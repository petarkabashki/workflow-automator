import pytest
from engine import WFEngine
from state_functions import StateFunctions
from utils import strip_quotes
import pydot


def create_test_engine():
    dot_string = """
    strict digraph {
        start -> end;
    }
    """
    state_functions = StateFunctions()
    setattr(state_functions, 'start', lambda: (None, 'end'))
    engine = WFEngine.from_dot_string(dot_string, state_functions)
    return engine

def test_engine_creation_from_dot_string():
    engine = create_test_engine()
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
    engine = create_test_engine()
    engine._run_state('start')
    assert engine.current_state == "__start__"  # Initial state

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
    engine.run()
    assert engine.current_state == "__end__"

def test_strip_quotes():
    assert strip_quotes('"hello"') == "hello"
    assert strip_quotes("'world'") == "world"
    assert strip_quotes('test') == 'test'
    assert strip_quotes('') == ''
    assert strip_quotes(None) == None

def test_run_method():
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

     # Mock input to simulate user interaction
     state_functions.request_input = lambda: ("OK", None)
     state_functions.extract_n_check = lambda: ("OK", None)
     state_functions.ask_confirmation = lambda: ("Y", None)
     state_functions.process_data = lambda: (None, None)

     engine.run()
     assert engine.current_state == "__end__"
