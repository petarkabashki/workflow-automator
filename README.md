# Asynchronous DOT File Driven State Machine in Python

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Description

This Python project implements a flexible, **asynchronous** state machine engine driven by DOT graph files. It allows you to define state machines visually using the DOT language and then execute them in Python by associating states with **asynchronous** Python methods within a class.

The core idea is to decouple the state machine's structure (defined in the DOT file) from its behavior (implemented in Python methods). This makes it easy to:

*   **Visually design and understand state machine workflows.**
*   **Modify the state machine's structure without changing Python code.**
*   **Reuse the state machine engine for different tasks by simply changing the DOT file and state function class.**

This project is ideal for applications that involve complex workflows, decision-making processes, or sequential operations where the flow needs to be easily configurable and maintainable.  The asynchronous nature of the engine makes it suitable for I/O-bound operations within state functions.

## Features

*   **DOT File Parsing:** Reads state machine definitions from DOT (`.dot`) files using the `pydot` library.
*   **Asynchronous State Function Execution:** Executes **asynchronous** Python methods associated with each state in the DOT graph.
*   **Class-Based State Functions:** Organizes state functions within a Python class for better structure and maintainability.
*   **Context Management:**  A `context` dictionary within the state function class allows for data sharing and stateful operations throughout the state machine execution.
*   **Interaction History:**  An `interaction_history` list within the state function class records system messages and user interactions.
*   **Condition-Based Transitions:** Supports transitions based on conditions returned by state functions, matched against edge labels in the DOT graph.
*   **State Override:** State functions can override the next state defined in the DOT graph, providing dynamic control over state transitions.
*   **Observer Pattern:** The `WFEngine` uses the observer pattern to emit detailed notifications about state changes, function calls, conditions, overrides, transitions, and errors.  An observer (`EngineObserver`) is provided to log these events to the console and a file.
*   **End State Handling:** Supports a designated end state (`__end__` by default) to gracefully terminate the state machine.
*   **Error Handling:** Includes robust error handling.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.7+:** You'll need a working Python 3.7 or later environment (due to `asyncio` features).
*   **Dependencies:** Install using pip:

    ```bash
    pip install pydot nest_asyncio
    ```
*   **Graphviz Executables:**  **Crucially, you also need to install the Graphviz *system executables*** on your operating system. This is separate from the Python library.

    *   **macOS:** Using Homebrew: `brew install graphviz`
    *   **Debian/Ubuntu:** `sudo apt-get install graphviz`
    *   **Windows:** Download from the [Graphviz website](https://graphviz.org/download/) and ensure the `bin` directory is added to your system's `PATH` environment variable.
    *   **Other systems:** Refer to the [Graphviz installation guide](https://graphviz.org/download/).

    **Without the Graphviz system executables installed and in your PATH, the DOT file parsing will fail.**

### Usage

1.  **Create a DOT File:** Define your state machine visually using the DOT language and save it as a `.dot` file (e.g., `workflow.dot`). Refer to the [Graphviz DOT language documentation](https://graphviz.org/doc/info/lang.html) for details on DOT syntax.

    **Example `workflow.dot`:**

    ```dot
    strict digraph {
        __start__ -> request_input;
        request_input -> extract_n_check[label="OK"];
        request_input -> request_input[label="NOK"];
        extract_n_check -> request_input[label="NOK"];
        extract_n_check -> ask_confirmation[label="OK"];
        ask_confirmation -> process_data[label="Y"];
        ask_confirmation -> request_input[label="N"];
        ask_confirmation -> __end__[label="Q"];
        process_data -> __end__;
    }
    ```

    *   **Nodes (States):** Represent states in your machine (e.g., `request_input`, `extract_n_check`).
    *   **Edges (Transitions):** Define transitions between states (e.g., `request_input -> extract_n_check`).  Labels on edges represent conditions.
    *   **`__start__` and `__end__`:**  Use these special state names to indicate the starting and ending states.

2.  **Define State Functions in a Class:** Create a Python class (`StateFunctions` is the recommended name) and define asynchronous methods for each state in your DOT file.

    **Example State Functions (from `state_functions.py`):**

    ```python
    import asyncio

    class StateFunctions:
        def __init__(self):
            self.context = {}  # Initialize context
            self.interaction_history = []

        async def request_input(self):
            # ... (implementation) ...
            return "OK", None  # (condition, override_next_state)

        async def extract_n_check(self):
            # ...
            return "OK", None

        # ... (other state functions) ...

        async def __start__(self):
            self.interaction_history.append(("system", "Workflow started."))
            return None, None
    ```

    *   **`__init__`:** Initialize the `context` and `interaction_history`.
    *   **Method Signature:** Each state function should be `async` and have a name matching a state in your DOT file.  They don't *need* to accept any arguments, as they can access `self.context` and `self.interaction_history` directly.
    *   **Return Value:** A state function should return a tuple: `(condition, override_next_state)`.
        *   `condition`: A string matching an edge label in the DOT file, or `None`.
        *   `override_next_state`: A string specifying the next state (overriding DOT file transitions), or `None`.

3.  **Create the Main Python Script (e.g., `main.py`):**

    ```python
    import asyncio
    from engine import WFEngine
    from state_functions import StateFunctions
    from engine_observer import EngineObserver
    import nest_asyncio

    nest_asyncio.apply()  # Required for nested event loops

    async def main():
        with open("workflow.dot", "r") as f:
            dot_content = f.read()

        state_functions = StateFunctions()
        engine = WFEngine.from_dot_string(dot_content, state_functions)

        observer = EngineObserver()
        engine.subscribe(observer)

        engine.render_graph()
        await engine.run()
        observer.save_log()

    if __name__ == "__main__":
        asyncio.run(main())
    ```

4.  **Run the Script:** Execute your Python script:

    ```bash
    python main.py
    ```

    The script will:

    *   Parse the `workflow.dot` file.
    *   Initialize the `WFEngine` and `StateFunctions`.
    *   Create and subscribe an `EngineObserver`.
    *   Run the state machine, starting from the `__start__` state.
    *   Execute the asynchronous Python method associated with each state.
    *   Log events to the console and `engine_log.txt`.

## DOT File Format Details

*   **Directed Graphs (`digraph`):**  Use `digraph` or `strict digraph`.
*   **State Names:** State names in the DOT file *must* exactly match the method names in your `StateFunctions` class.
*   **Transitions:** Transitions are defined using `->`.
*   **Edge Labels:** Edge labels are used as conditions.  A state function's returned `condition` is compared to these labels.
*   **`__start__` and `__end__`:** Required for starting and ending states.

## Observer Pattern

The `WFEngine` emits events to subscribed observers.  The `EngineObserver` class (in `engine_observer.py`) provides console and file logging:

*   **`notify(event_type, data)`:**  This method is called by the engine for each event.
*   **Event Types:**
    *   `state_change`:  Indicates a change in the current state.
    *   `state_function_call`:  Before a state function is called.
    *   `condition_received`: After a state function returns.
    *   `state_override`: When a state override occurs.
    *   `transition`:  When a transition is taken (based on condition or default).
    *   `transition_error`: If a transition fails.
    *   `error`: For errors within state functions or the engine.
    *   `workflow_finished`: When the workflow completes.

## Example

The provided code (`engine.py`, `state_functions.py`, `engine_observer.py`, `main.py`, and `workflow.dot`) forms a complete, runnable example.

## License

[MIT License](https://opensource.org/licenses/MIT)

