# README: Composable State Machine Engine (Python)

**Project Title:** Composable State Machine Engine (Generator-Based, Iterative)

**Short Description:**

This Python library provides a flexible and robust engine for building state machines, emphasizing composability and iterative execution. It allows for defining complex workflows by composing state machines as sub-machines within a main machine, all driven by a non-recursive, generator-based engine.

**Key Features:**

*   **Composition with Sub-Machines:** Define nested workflows by embedding sub-state machines within states of a parent machine.
*   **Iterative, Generator-Based Engine:** The core engine uses an iterative, stack-based approach for execution, avoiding recursion and potential stack overflow issues.
*   **Uniform State Definitions:** State definitions are highly flexible. A state can be associated with either:
    *   A **state function** (a Python generator function) for regular states.
    *   A **sub-machine definition** (a dictionary of state definitions) to invoke a nested state machine.
*   **Clear Instruction Set:** States communicate with the runner and engine via a well-defined set of instructions, including:
    *   `transition`:  Move to a new state within the current machine.
    *   `parent_transition`: Trigger a state transition in the parent state machine.
    *   `request_input`: Request input from the user or external system.
    *   `notify`:  Send notifications to the runner (info, warning, success, progress).
    *   `debug`: Output debug messages with levels for detailed tracing.
    *   `error`: Report an error condition.
    *   `warning`:  Report a warning.
    *   `custom`:  Signal the runner to perform a custom action.
*   **Flexible Runner:** The provided runner handles instruction processing, user input/output, and debugging, but can be extended or replaced for custom integration.
*   **Parent Transition Mechanisms:**  Two mechanisms for sub-machines to trigger transitions in their parent:
    *   `parent_transition` instruction from within any sub-machine state.
    *   `transition` instruction in the `__end__` state of a sub-machine to define the default parent transition upon sub-machine completion.
*   **Function-Based Sub-Machine Definitions:** Sub-machine definitions can be encapsulated within functions, improving code organization and reusability.

**Getting Started:**

**Installation:**

This library is pure Python and has no external dependencies. Simply copy the code (engine, runner, state functions) into your project.

**Basic Usage:**

1.  **Define State Functions:** Create generator functions for each state in your workflow. These functions `yield` instruction dictionaries.
2.  **Define State Machine:** Create a dictionary where keys are state names (including `__start__` and `__end__`) and values are either state functions or sub-machine definitions (or functions that return them).
3.  **Run the Engine:** Instantiate the engine with your state definitions and use the `runner` function to execute the state machine.

**Example:**

```python
# (Assume engine, runner, and state function code are already in your environment)

def example_state_a(input_data=None):
    yield {"instruction": "notify", "message": "Entering State A", "level": "info"}
    yield {"instruction": "transition", "next_state": "example_state_b"}

def example_state_b(input_data=None):
    yield {"instruction": "notify", "message": "Entering State B", "level": "info"}
    yield {"instruction": "transition", "next_state": "__end__"}

example_state_machine = {
    "__start__": example_state_a,
    "example_state_a": example_state_a,
    "example_state_b": example_state_b,
    "__end__": state_end  # Reusing the provided state_end function
}

if __name__ == "__main__":
    engine = generator_based_engine(example_state_machine, debug_mode=True)
    runner(engine, debug_mode=True)