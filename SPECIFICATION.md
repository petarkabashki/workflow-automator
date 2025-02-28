## Technical Description: Asynchronous DOT Specification Driven State Machine Execution Engine with Class-Based State Functions

This Python application implements an **asynchronous** state machine **execution engine** driven by **DOT specifications** and **class-based state functions**. The engine executes workflows defined in a DOT file, using a provided Python class to handle the logic for each state.

**Key Technical Components:**

*   **DOT Specification Parser:** Parses DOT specifications (text or `.dot` files) using `pydot` into an in-memory graph representing the workflow structure (states and transitions).  The `WFEngine` class handles this parsing.

*   **State Function Class:** A Python class (`StateFunctions` in the provided example) houses asynchronous state function logic in methods (using `async/await`). Method names *must* match DOT state names. These methods are responsible for:
    *   Performing actions associated with the state.
    *   Interacting with the user (e.g., requesting input).
    *   Optionally returning a tuple: `(condition, next_state_override)`.
        *   `condition`: A string representing a condition to determine the next state transition (based on edge labels in the DOT graph).
        *   `next_state_override`:  A string representing a state name to force a transition to, bypassing the DOT graph's transitions. If `None`, the DOT graph determines the next state.

*   **Context Dictionary:**  The `StateFunctions` class contains a `context` dictionary, which serves as shared memory. State function methods can access and modify this dictionary to share data between states.

*   **Interaction History:** The `StateFunctions` class maintains an `interaction_history` list.  This list stores a chronological record of:
    *   System messages (e.g., state transitions).
    *   User interactions (input provided).

*   **State Transition Mechanism:**
    *   **DOT Graph Driven:** Transitions generally follow edges in the DOT graph.
    *   **Condition-Based Transitions:**  If a state function returns a `condition` string, the engine finds an outgoing edge from the current state with a matching label.
    *   **Function Override (Method Override):** If a state function returns a `next_state_override` string, the engine transitions to the specified state, ignoring the DOT graph's edges.
    *   **No Matching Edge:** If no matching edge is found for a given condition, or if no condition is returned and there are no unlabeled outgoing edges, the engine transitions to the `__end__` state.

*   **`WFEngine` Class:** This class is the core of the engine.  It is responsible for:
    *   Initializing the engine with a DOT graph and a `StateFunctions` instance.
    *   Managing the current state.
    *   Running the workflow loop (using `asyncio`).
    *   Calling the appropriate state function methods.
    *   Handling state transitions based on the DOT graph and return values from state functions.
    *   Rendering the graph (for visualization).

**Example Usage (using `workflow.dot` and `state_functions.py`):**

**`workflow.dot`:**

