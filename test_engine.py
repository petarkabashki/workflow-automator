import sys
import pytest
import asyncio
import graphviz
from engine import EngineExecutor
from state_functions import StateFunctions
from unittest.mock import AsyncMock
import psutil
import os

# Get the parent process name
def get_parent_process_name():
    try:
        current_process = psutil.Process(os.getpid())
        parent_process = current_process.parent()
        return parent_process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None

# Check if the script is being run directly with 'python test_engine.py'
# and NOT being called by run_tests.sh or run_test.sh
if __name__ == "__main__":
    parent_name = get_parent_process_name()
    if parent_name not in ("bash", "sh", "pytest", "run_tests.sh", "run_test.sh"):
        print("\nERROR: Do not run this file directly with 'python test_engine.py'.")
        print("       This will bypass pytest and cause errors.")
        print(f"       Instead, run the `run_tests.sh` or `run_test.sh` script:")
        print("       1. Make sure the script is executable: `chmod +x run_tests.sh` (or run_test.sh)")
        print(f"       2. Run the script: `./run_tests.sh` (or ./run_test.sh)")
        print("       This will install pytest and run the tests correctly.\n")
        sys.exit(1)  # Exit with an error code


@pytest.mark.asyncio
async def test_engine_executor_initialization():
    # Create a simple mock graph
    dot = graphviz.Digraph()
    dot.node('__start__')
    dot.node('request_input')
    dot.node('__end__')
    dot.edge('__start__', 'request_input')
    dot.edge('request_input', '__end__')

    # Use the REAL StateFunctions now
    state_functions = StateFunctions()
    engine = EngineExecutor(dot, state_functions)
    assert engine is not None

@pytest.mark.asyncio
async def test_engine_executor_run():
    # Create a simple mock graph
    dot = graphviz.Digraph()
    dot.node('__start__')
    dot.node('request_input')
    dot.node('extract_data')
    dot.node('check_all_data_collected')
    dot.node('ask_confirmation')
    dot.node('process_data')
    dot.node('__end__')

    dot.edge('__start__', 'request_input')
    dot.edge('request_input', 'extract_data')
    dot.edge('extract_data', 'check_all_data_collected')
    dot.edge('check_all_data_collected', 'ask_confirmation')
    dot.edge('ask_confirmation', 'process_data')
    dot.edge('process_data', '__end__')


    # Use the REAL StateFunctions
    state_functions = StateFunctions()
    engine = EngineExecutor(dot, state_functions)

    # Mock _request_input to provide controlled input
    engine._request_input = AsyncMock(side_effect=["Test Name", "test@example.com", "yes"])

    await engine.run()
    assert engine.current_state == "__end__"
    assert "name" in engine.context
    assert "email" in engine.context
    assert engine.context["name"] == "Test Name"
    assert engine.context["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_engine_executor_run_no_confirmation():
    # Create a simple mock graph
    dot = graphviz.Digraph()
    dot.node('__start__')
    dot.node('request_input')
    dot.node('extract_data')
    dot.node('check_all_data_collected')
    dot.node('ask_confirmation')
    dot.node('process_data')
    dot.node('__end__')

    dot.edge('__start__', 'request_input')
    dot.edge('request_input', 'extract_data')
    dot.edge('extract_data', 'check_all_data_collected')
    dot.edge('check_all_data_collected', 'ask_confirmation')
    dot.edge('ask_confirmation', 'process_data')
    dot.edge('process_data', '__end__')
    dot.edge('ask_confirmation', '__end__') # Add edge for 'no' case


    # Use the REAL StateFunctions
    state_functions = StateFunctions()
    engine = EngineExecutor(dot, state_functions)

    # Mock _request_input to provide controlled input, including "no"
    engine._request_input = AsyncMock(side_effect=["Test Name", "test@example.com", "no"])

    await engine.run()
    assert engine.current_state == "__end__"  # Should still end, but via different path

@pytest.mark.asyncio
async def test_engine_executor_run_invalid_confirmation():
    # Create a simple mock graph
    dot = graphviz.Digraph()
    dot.node('__start__')
    dot.node('request_input')
    dot.node('extract_data')
    dot.node('check_all_data_collected')
    dot.node('ask_confirmation')
    dot.node('process_data')
    dot.node('__end__')

    dot.edge('__start__', 'request_input')
    dot.edge('request_input', 'extract_data')
    dot.edge('extract_data', 'check_all_data_collected')
    dot.edge('check_all_data_collected', 'ask_confirmation')
    dot.edge('ask_confirmation', 'process_data')
    dot.edge('process_data', '__end__')
    dot.edge('ask_confirmation', '__end__') # Add edge for 'no' case


    # Use the REAL StateFunctions
    state_functions = StateFunctions()
    engine = EngineExecutor(dot, state_functions)

    # Mock _request_input to provide controlled input, including invalid input
    engine._request_input = AsyncMock(side_effect=["Test Name", "test@example.com", "invalid", "yes"])

    await engine.run()
    assert engine.current_state == "__end__"
    assert "name" in engine.context
    assert "email" in engine.context
    assert engine.context["name"] == "Test Name"
    assert engine.context["email"] == "test@example.com"
