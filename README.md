# DOT File Driven State Machine in Python

[![License](about:sanitized)](https://www.google.com/url?sa=E&source=gmail&q=https://opensource.org/licenses/MIT)

## Description

This Python project implements a flexible state machine engine that is driven by DOT graph files. It allows you to define state machines visually using the DOT language and then execute them in Python by associating states with Python functions.

The core idea is to decouple the state machine's structure (defined in the DOT file) from its behavior (implemented in Python functions). This makes it easy to:

  * **Visually design and understand state machine workflows.**
  * **Modify the state machine's structure without changing Python code.**
  * **Reuse the state machine engine for different tasks by simply changing the DOT file and state functions.**

This project is ideal for applications that involve complex workflows, decision-making processes, or sequential operations where the flow needs to be easily configurable and maintainable.

## Features

  * **DOT File Parsing:** Reads state machine definitions from DOT (`.dot`) files using the `graphviz` library.
  * **State Function Execution:** Executes Python functions associated with each state in the DOT graph.
  * **Context Management:** Passes a context dictionary to each state function, allowing for data sharing and stateful operations throughout the state machine execution.
  * **Override Next State:** State functions can optionally override the next state defined in the DOT graph, providing dynamic control over state transitions based on function logic.
  * **Initial State Configuration:** Flexible options to define the initial state:
      * Explicitly set in the Python code.
      * Derived from the graph name in the DOT file (using `state_machine_initial_state` convention).
      * Defaults to the first node in the DOT file if no initial state is otherwise specified.
  * **End State Handling:**  Supports a designated end state (`__end__` by default) to gracefully terminate the state machine.
  * **Error Handling:** Includes robust error handling for common issues like DOT file parsing errors, missing state functions, and unexpected function return types.
  * **Informative Output:** Provides clear console output, logging state transitions, context changes, and any warnings or errors encountered during execution.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

  * **Python 3.x:**  You'll need a working Python 3 environment.

  * **Graphviz Python library:** Install using pip:

    ```bash
    pip install graphviz
    ```

  * **Graphviz Executables:**  **Crucially, you also need to install the Graphviz *system executables*** on your operating system. This is separate from the Python library.

      * **macOS:**  Using Homebrew: `brew install graphviz`
      * **Debian/Ubuntu:** `sudo apt-get install graphviz`
      * **Windows:** Download from the [Graphviz website](https://www.google.com/url?sa=E&source=gmail&q=https://graphviz.org/download/) and ensure the `bin` directory is added to your system's `PATH` environment variable.
      * **Other systems:** Refer to the [Graphviz installation guide](https://www.google.com/url?sa=E&source=gmail&q=https://graphviz.org/download/).

    **Without the Graphviz system executables installed and in your PATH, the DOT file parsing will fail.**

### Usage

1.  **Create a DOT File:** Define your state machine visually using the DOT language and save it as a `.dot` file (e.g., `state_machine_graph.dot`).  Refer to the [Graphviz DOT language documentation](https://www.google.com/url?sa=E&source=gmail&q=https://graphviz.org/doc/info/lang.html) for details on DOT syntax.

    **Example `state_machine_graph.dot`:**

    ```dot
    digraph state_machine {
        graph [name="state_machine_extract_data"] // Example to set initial state, remove for default
        extract_data -> check_all_data_collected;
        check_all_data_collected -> request_input [label="needs_input"];
        check_all_data_collected -> ask_confirmation [label="data_collected"];
        request_input -> extract_data;
        ask_confirmation -> process_data [label="confirm"];
        ask_confirmation -> extract_data [label="reject"];
        process_data -> __end__ [label="process_done"];
    }
    ```

      * **Nodes (States):**  Represent states in your machine (e.g., `extract_data`, `check_all_data_collected`).
      * **Edges (Transitions):**  Define transitions between states (e.g., `extract_data -> check_all_data_collected;`). Labels on edges are optional and not currently used by the state machine engine itself, but can be helpful for documentation.
      * **Graph Name (Optional):** You can set the graph name to influence the initial state using the `graph [name="state_machine_your_initial_state"]` syntax.

2.  **Define State Functions in Python:** Create Python functions for each state in your DOT file. These functions will implement the logic for each state.

    **Example State Functions (from `main.py`):**

    ```python
    def extract_data_func(context):
        print("Executing: extract_data_func")
        context['extracted_data'] = "some data" # Simulate data extraction
        context['question'] = None # Reset question
        return context, None # No override, use DOT file for next state

    def check_all_data_collected_func(context):
        # ... (other state functions) ...
    ```

      * **Function Signature:** Each state function should accept a `context` dictionary as its first argument.
      * **Return Value:**  A state function should return either:
          * **A dictionary:**  This is the updated context. The next state will be determined by the transitions defined in the DOT file from the current state.
          * **A tuple:** `(updated_context, override_next_state)`.
              * `updated_context`: The updated context dictionary.
              * `override_next_state`: A string specifying the name of the state to transition to *next*, overriding the DOT file's transitions. Set to `None` to use DOT file transitions.

3.  **Create the Main Python Script (e.g., `main.py`):**

    ```python
    from state_machine import StateMachine # Assuming you saved the code as state_machine.py

    # 1. Define state functions mapping
    state_functions_map = {
        "extract_data": extract_data_func,
        "check_all_data_collected": check_all_data_collected_func,
        # ... (map all your state functions) ...
        "__end__": lambda context: context # End state function (can be a simple lambda)
    }

    # 2. Path to your DOT file
    dot_file = 'state_machine_graph.dot'

    # 3. Initialize and run the state machine
    initial_context = {} # Start with an empty context, or populate with initial data
    try:
        sm = StateMachine(dot_file, state_functions_map) #, initial_state="extract_data") // Optional initial state
        final_context = sm.run(initial_context)
        print("\nFinal Context:", final_context)
    except Exception as e:
        print(f"State Machine Error: {e}")
    ```

4.  **Run the Script:** Execute your Python script:

    ```bash
    python main.py
    ```

    The script will:

      * Parse the `state_machine_graph.dot` file.
      * Initialize the `StateMachine` with the DOT file and state functions.
      * Run the state machine, starting from the initial state.
      * Execute the Python function associated with each state as it transitions.
      * Print output showing state transitions and the final context dictionary.

## DOT File Format Details

  * **Directed Graphs (`digraph`):** The DOT file must define a directed graph using `digraph`.
  * **State Names:** State names in the DOT file must exactly match the keys in your `state_functions_map` dictionary in Python.
  * **Transitions:** Transitions between states are defined using `->`.
  * **Initial State:**  Can be configured as described in "Usage" step 3 (optional `initial_state` parameter, graph name convention, or defaults to first node).
  * **End State:** While the code uses `__end__` as a default end state, you can also define `__end__` (or your chosen `end_state`) as a node in your DOT file if you want to visually represent it.

## State Function Requirements

  * **Argument:** Each state function must accept a single argument: `context` (a dictionary).
  * **Return Value:** Each state function must return either:
      * A dictionary (updated `context`).
      * A tuple: `(updated_context, override_next_state)`.
  * **Function Logic:** Implement the specific logic for each state within its corresponding Python function. This might involve data processing, API calls, user interaction, or any other operations relevant to your state machine.

## Error Handling

The `StateMachine` class includes error handling for:

  * **Graphviz Executables Not Found:** Checks if Graphviz system executables are in the system's PATH.
  * **DOT File Parsing Errors:** Catches errors during DOT file parsing (syntax errors, invalid graph structure).
  * **Empty State Function Dictionary:** Ensures that state functions are provided.
  * **Undefined Initial State:** Handles cases where the initial state cannot be determined.
  * **Missing State Functions:** Warns if a function is not defined for a state encountered during execution.
  * **Unexpected Function Return Types:** Checks that state functions return the expected dictionary or tuple format.
  * **Errors within State Functions:** Catches exceptions that occur during the execution of state functions and stops the state machine.

## Example

See the `if __name__ == '__main__':` block in the `state_machine.py` (or `main.py` example) for a complete working example, including example state functions and a DOT file configuration.  You can adapt this example to create your own state machines.

## Further Development (Optional)

  * **Edge Labels for Logic:** Enhance the engine to use edge labels in the DOT file to define conditions or logic for transitions (e.g., conditional transitions based on context data).
  * **Visualization Tools:** Create tools to visually monitor the state machine's execution in real-time.
  * **State History/Logging:** Implement more detailed logging of state transitions and context changes for debugging and auditing.
  * **More Complex Context Handling:**  Explore options for more advanced context management, such as context inheritance or hierarchical contexts.

## License

[MIT License](https://www.google.com/url?sa=E&source=gmail&q=LICENSE)

## Author

[Your Name/Organization] - [Your Contact Information (Optional)]

-----

This README provides a comprehensive guide to using the DOT File Driven State Machine project.  Remember to replace the bracketed placeholders (like `[Your Name/Organization]`, license badge link, etc.) with your actual information. Good luck building your state machines\!