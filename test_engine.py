import pytest
from engine import WFEngine
from state_functions import StateFunctions
import logging

def clean_test_logs():
    with open(f'engine_log.txt', 'w') as f:
        f.write('')

class LogCaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_records = []
        
    def emit(self, record):
        self.log_records.append(self.format(record))
        
    def get_logs(self):
        return '\n'.join(self.log_records)
        
    def clear(self):
        self.log_records = []

def setup_test_logger(test_name):
    clean_test_logs()  # Ensure logs are clean before each test
    logger = logging.getLogger(test_name)
    logger.setLevel(logging.DEBUG)
    
    # File handler for backward compatibility
    fh = logging.FileHandler('engine_log.txt')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    
    # Memory capture handler
    ch = LogCaptureHandler()
    ch.setFormatter(formatter)
    
    logger.handlers = []  # Clear any existing handlers
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger, ch

def create_test_engine(logger=None, dot_string=None):
    """Creates a test engine instance, optionally with a custom dot string."""
    if logger is None:
        logger, _ = setup_test_logger('test_engine')
    if dot_string is None:
        dot_string = """
        strict digraph {
            __start__ -> __end__;
        }
        """
    state_functions = StateFunctions()
    engine = WFEngine.from_dot_string(dot_string, state_functions)
    engine.set_logger(logger)
    return engine

# --- Tests ---

def test_multiple_transitions_without_condition_logs():
    """
    Test that appropriate error messages are logged when multiple transitions
    exist but no condition is provided.
    """
    logger, log_capture = setup_test_logger('test_multiple_transitions_without_condition_logs')
    dot_string = """
    strict digraph {
        __start__ -> a;
        __start__ -> b;
        a -> __end__;
        b -> __end__;
    }
    """
    state_functions = StateFunctions()
    setattr(state_functions, '__start__', lambda: (None, None))
    setattr(state_functions, 'a', lambda: (None, None))
    setattr(state_functions, 'b', lambda: (None, None))

    engine = WFEngine.from_dot_string(dot_string, state_functions)  # Initialize
    engine.set_logger(logger)
    state_sequence = [state[1] for state in engine.start() if state[0] == "state_change"]
    assert state_sequence == ['__start__'] # Engine should stop at __start__

    log_content = log_capture.get_logs() # Optionally keep log check for specific message
    assert "Multiple transitions available" in log_content # Verify log message

def test_conditional_transition_logs():
    """
    Test that appropriate debug messages are logged during conditional transitions.
    """
    logger, log_capture = setup_test_logger('test_conditional_transition_logs')
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
    setattr(state_functions, 'a', lambda: (None, "__end__"))
    setattr(state_functions, 'b', lambda: (None, None))

    engine = WFEngine.from_dot_string(dot_string, state_functions)
    engine.set_logger(logger)
    state_sequence = [state[1] for state in engine.start() if state[0] == "state_change"]
    assert state_sequence == ['__start__', 'a', '__end__'] # Expected path

    log_content = log_capture.get_logs() # Optionally keep log checks
    assert "Condition matched for transition to a" in log_content # Verify condition log
    assert "Running state: __start__" in log_content # Verify state execution log
    assert "Running state: a" in log_content # Verify state execution log
    assert "State function for __start__ returned" in log_content # Verify state function result log
    assert "State function did not return next state, checking transitions" in log_content # Verify transition check log
    assert "Workflow completed successfully" in log_content # Verify workflow completion log

def test_multiple_transitions_without_condition():
    """
    Test that the engine properly handles the case where a state has multiple possible
    transitions but no condition is provided by the state function.
    """
    logger, log_capture = setup_test_logger('test_multiple_transitions_without_condition')
    dot_string = """
    strict digraph {
        __start__ -> a;
        __start__ -> b;
        a -> __end__;
        b -> __end__;
    }
    """
    state_functions = StateFunctions()
    # State function returns no condition but has multiple possible transitions
    setattr(state_functions, '__start__', lambda: (None, None))
    setattr(state_functions, 'a', lambda: (None, "__end__"))
    setattr(state_functions, 'b', lambda: (None, "__end__"))

    engine = WFEngine.from_dot_string(dot_string, state_functions)
    engine.set_logger(logger)
    state_sequence = [state[1] for state in engine.start() if state[0] == "state_change"]
    assert state_sequence == ['__start__'] # Engine should stop at __start__

    log_content = log_capture.get_logs() # Optionally keep log check
    assert "Multiple transitions available" in log_content # Verify log message

def test_engine_creation_from_dot_string():
    logger, _ = setup_test_logger('test_engine_creation_from_dot_string')
    engine = create_test_engine(logger=logger)
    assert engine is not None
    assert "__start__" in engine.states
    assert "__end__" in engine.states

def test_engine_creation_from_nodes_and_edges():
    nodes = ['start', 'end']
    edges = [('start', 'end')]
    state_functions = StateFunctions()
    setattr(state_functions, '__start__', lambda: (None, '__end__'))
    with pytest.raises(NotImplementedError):
        engine = WFEngine.from_nodes_and_edges(nodes, edges, state_functions)

def test_state_execution():
    logger, _ = setup_test_logger('test_state_execution')
    dot_string = """
    strict digraph {
        __start__ -> __end__;
    }
    """
    print(f"DOT STRING: {dot_string}")
    state_functions = StateFunctions()
    setattr(state_functions, '__start__', lambda: (None, '__end__'))
    engine = WFEngine.from_dot_string(dot_string, state_functions)
    engine.set_logger(logger)
    result, next_state = engine._run_state('__start__')
    assert result is None
    assert next_state == '__end__'

def test_conditional_transition():
    logger, log_capture = setup_test_logger('test_conditional_transition')
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
    setattr(state_functions, 'a', lambda: (None, "__end__"))
    setattr(state_functions, 'b', lambda: (None, "__end__"))
    engine = WFEngine.from_dot_string(dot_string, state_functions)
    engine.set_logger(logger)
    state_sequence = [state[1] for state in engine.start() if state[0] == "state_change"]
    assert state_sequence == ['__start__', 'a', '__end__'] # Expected path

    log_content = log_capture.get_logs() # Optionally keep log checks
    assert "Condition matched for transition to a" in log_content # Verify condition log

def test_run_method(monkeypatch):
    logger, log_capture = setup_test_logger('test_run_method')
    dot_string = """
       strict digraph {
           __start__ -> request_input;
           request_input -> extract_n_check;
           extract_n_check -> ask_confirmation;
           ask_confirmation -> process_data;
           process_data -> __end__;
       }
    """
    state_functions = StateFunctions()

    # Mock input and state functions to simulate user interaction
    def mock_input(prompt=None):
        return "John Doe, john.doe@example.com"

    def mock_request_input():
        user_input = mock_input()
        if "john.doe" in user_input:  # Simplified condition
            return "OK", "extract_n_check"
        else:
            return "NOK", "request_input"

    def mock_extract_n_check():
        return "OK", "ask_confirmation"

    def mock_ask_confirmation():
        return "Y", "process_data"

    def mock_process_data():
        return "OK", "__end__"
    
    setattr(state_functions, '__start__', lambda: (None, "request_input"))
    setattr(state_functions, 'request_input', mock_request_input)
    setattr(state_functions, 'extract_n_check', mock_extract_n_check)
    setattr(state_functions, 'ask_confirmation', mock_ask_confirmation)
    setattr(state_functions, 'process_data', mock_process_data)

    engine = WFEngine.from_dot_string(dot_string, state_functions)
    engine.set_logger(logger)
    
    state_sequence = []
    yielded_sequence = [] # Capture all yielded values
    workflow_generator = engine.start()
    current_state = next(workflow_generator)
    
    while current_state[1] != "__end__":
        yielded_sequence.append(current_state) # Capture yielded value (tuple)
        if current_state[0] == "state_change": # Extract state name for state_sequence
            state_sequence.append(current_state[1]) # Append just the state name
        try:
            current_state = next(workflow_generator) # Advance to next yield
        except StopIteration:
            break # Exit loop if generator finishes
    
    state_sequence.append("__end__") # Append __end__ as loop breaks before adding it
    yielded_sequence.append(("state_change", "__end__")) # Capture final __end__ state_change
    
    assert state_sequence == ['__start__', 'request_input', 'extract_n_check', 'ask_confirmation', 'process_data', '__end__'] # Full expected path
    
    log_content = log_capture.get_logs() # Optionally keep log check
    assert "Workflow completed successfully" in log_content # Verify workflow completion log
