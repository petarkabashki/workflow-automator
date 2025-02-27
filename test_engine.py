import asyncio
import pytest
import graphviz
from workflow_automator.engine import EngineExecutor


# Mock StateFunctions class for testing
class MockStateFunctions:

    def __init__(self):
        self.called_states = []

    async def state1(self, context, executor):
        self.called_states.append("state1")
        return "state2"  # Override transition

    async def state2(self, context, executor):
        self.called_states.append("state2")
        return None

    async def state3(self, context, executor):
        self.called_states.append("state3")
        return None  # No outgoing edge

    async def request_input(self, context, executor):
        self.called_states.append("request_input")
        context['input_received'] = await executor._request_input("Enter something:", input_type="text")
        return "extract_data"

    async def extract_data(self, context, executor):
        self.called_states.append("extract_data")
        return None


@pytest.fixture
def simple_dot_graph():
    dot_graph = """
    strict digraph {
        __start__ -> state1;
        state1 -> state2;
        state2 -> __end__;
    }
    """
    return graphviz.Source(dot_graph)

@pytest.fixture
def no_edge_dot_graph():
    dot_graph = """
    strict digraph {
        __start__ -> state3;
        state3;
    }
    """
    return graphviz.Source(dot_graph)

@pytest.fixture
def input_dot_graph():
    dot_graph = """
    strict digraph {
        __start__ -> request_input;
        request_input -> extract_data;
        extract_data -> __end__;
    }
    """
    return graphviz.Source(dot_graph)

@pytest.fixture
def mock_state_functions():
    return MockStateFunctions()


@pytest.fixture
async def executor(simple_dot_graph, mock_state_functions):
    return EngineExecutor(simple_dot_graph, mock_state_functions)

@pytest.fixture
async def no_edge_executor(no_edge_dot_graph, mock_state_functions):
    return EngineExecutor(no_edge_dot_graph, mock_state_functions)

@pytest.fixture
async def input_executor(input_dot_graph, mock_state_functions):
    return EngineExecutor(input_dot_graph, mock_state_functions)


@pytest.mark.asyncio
async def test_run_simple_workflow(executor, mock_state_functions):
    await executor.run()
    assert mock_state_functions.called_states == ["state1", "state2"]
    assert executor.current_state == "__end__"


@pytest.mark.asyncio
async def test_run_workflow_no_outgoing_edges(no_edge_executor, mock_state_functions):
    await no_edge_executor.run()
    assert mock_state_functions.called_states == ["state3"]
    assert no_edge_executor.current_state == "__end__"

@pytest.mark.asyncio
async def test_send_input(executor):
    await executor.send_input("test input")
    assert ("user", "test input") in executor.interaction_history
    assert executor.context.get("input_received") == None # Check that send_input doesn't modify a specific context key
    assert executor.context.get("last_input") == "test input" # Check that the last input is stored


@pytest.mark.asyncio
async def test_upload_file(executor):
    await executor.upload_file("test.txt")
    assert ("user", "Uploaded file: test.txt") in executor.interaction_history
    assert executor.context.get("file_received") == None # Check that upload_file doesn't modify a specific context key
    assert executor.context.get("last_file") == "test.txt"

@pytest.mark.asyncio
async def test_request_input(executor):
    async def mock_input():
        await asyncio.sleep(0.1)  # Simulate some delay
        await executor.send_input("mocked input")

    asyncio.create_task(mock_input())  # Run mock_input concurrently
    result = await executor._request_input("Test prompt", input_type="text")
    assert result == "mocked input"
    assert ("system", "Test prompt") in executor.interaction_history

@pytest.mark.asyncio
async def test_interaction_history(input_executor, mock_state_functions):

    async def mock_input():
        await asyncio.sleep(0.1)
        await input_executor.send_input("test_data")

    asyncio.create_task(mock_input())
    await input_executor.run()

    assert ('system', 'Transition to state: request_input') in input_executor.interaction_history
    assert ('system', 'Enter something:') in input_executor.interaction_history
    assert ('user', 'test_data') in input_executor.interaction_history
    assert ('system', 'Transition to state: extract_data') in input_executor.interaction_history
    assert ('system', 'Transition to state: __end__') in input_executor.interaction_history
    assert mock_state_functions.called_states == ['request_input', 'extract_data']
    assert input_executor.context['input_received'] == 'test_data'

@pytest.mark.asyncio
async def test_initial_state_transition(executor, mock_state_functions):
    await executor.run()
    assert ('system', 'Transition to state: state1') in executor.interaction_history

