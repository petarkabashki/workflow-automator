

# Technical Specifications: Composable State Machine Engine

**1. Engine Name:** `generator_based_engine`

**2. Language:** Python 3.x

**3. Dependencies:** None (Pure Python Standard Library)

**4. Architecture:**

*   **Iterative, Stack-Based Architecture:** The engine uses a stack (`engine_stack`) to manage the execution context of state machines, enabling non-recursive composition of sub-machines.
*   **Generator-Based State Functions:** State logic is implemented using Python generator functions, allowing for step-by-step execution and yielding of instructions.
*   **Instruction-Driven Execution:** State transitions and runner interactions are controlled by a predefined set of instruction dictionaries `yield`ed by state functions.
*   **Composition through Stack Management:** Sub-machine execution is initiated by pushing a new machine context (state definitions, initial state, generator) onto the `engine_stack`. The engine iteratively processes machines from the stack.
*   **State Transition and Parent Transition Mechanisms:**
    *   `transition` instruction for state changes within the current machine.
    *   `parent_transition` instruction for explicitly triggering transitions in the parent machine, allowing sub-machines to control the parent's workflow.

**5. Instruction Set:**

*   **Control Flow Instructions:**
    *   `transition`: `{ "instruction": "transition", "next_state": "state_name", "payload": { ... } }` -  Initiates a state transition to `state_name` in the current state machine. Payload is optional.
    *   `parent_transition`: `{ "instruction": "parent_transition", "next_state_for_parent": "parent_state_name", "payload": { ... } }` - Signals a transition to `parent_state_name` in the parent state machine. Payload is optional.

*   **Input/Output Instruction:**
    *   `request_input`: `{ "instruction": "request_input", "query": "Input prompt" , "payload": { ... }}` - Requests input from the runner, displaying the `query` prompt. Payload is optional.

*   **Notification Instructions:**
    *   `notify`: `{ "instruction": "notify", "message": "Notification message", "level": "info" ("info"|"warning"|"success"|"progress"), "payload": { ... } }` - Sends a notification to the runner with a message and level. Payload is optional.
    *   `debug`: `{ "instruction": "debug", "message": "Debug message", "level": "debug_level" ("state_enter"|"state_exit"|"action"|"progress"|"action_complete"), "payload": { ... } }` - Sends a debug message to the runner with a message and level. Payload is optional.
    *   `warning`: `{ "instruction": "warning", "message": "Warning message",  "payload": { ... } }` - Sends a warning message to the runner. Payload is optional.
    *   `error`: `{ "instruction": "error", "message": "Error message", "payload": { ... } }` - Sends an error message to the runner. Payload is optional.

*   **Custom Action Instruction:**
    *   `custom`: `{ "instruction": "custom", "name": "action_name", "payload": { ... } }` - Signals the runner to perform a custom action named `action_name`. Payload is optional.

*   **Runner-Specific Instructions (Internal Communication):**
    *   `runner_notify`, `runner_warning`, `runner_error`, `runner_debug`, `runner_request_input`, `runner_custom`, `runner_warning` - Used for internal communication between the engine and runner; processed by the runner.

**6. State Function Requirements:**

*   **Generator Functions:** State functions must be defined as Python generator functions (using `yield`).
*   **Input Data:** State functions receive an `input_data` dictionary, which can contain contextual information.
*   **Instruction Yielding:** State functions `yield` instruction dictionaries to control state transitions, request input, and communicate with the runner.
*   **StopIteration Termination:** State functions signal their completion by raising a `StopIteration` exception (implicitly when the generator function naturally ends).

**7. Sub-Machine Definition Requirements:**

*   **Dictionary-Based:** Sub-machine definitions are dictionaries that follow the same structure as main state machine definitions, mapping state names to state functions or further sub-machine definitions.
*   **`__start__` and `__end__` States:** Sub-machine definitions must include `__start__` and `__end__` states.
*   **Function-Based Definition (Optional):** Sub-machine definitions can be created and returned by functions for better organization and reusability.

**8. Runner Responsibilities:**

*   **Engine Generator Iteration:** The runner is responsible for iterating through the engine's generator (`generator_based_engine`).
*   **Instruction Processing:** The runner processes each instruction `yield`ed by the engine, performing actions based on the instruction type (e.g., printing notifications, requesting user input, executing custom actions).
*   **Input Handling:** For `request_input` instructions, the runner must obtain input (e.g., from user input, external system) and send it back to the engine using the `engine_generator.send(input_value)` method.
*   **Output and Debugging:** The runner handles outputting notifications, warnings, errors, and debug messages to the console or logs, providing visibility into state machine execution.
*   **Custom Action Execution:** For `custom` instructions, the runner is responsible for implementing and executing the specified custom actions.

**9. Limitations:**

*   **Simple Runner Implementation:** The provided `runner` is a basic console-based implementation. For real-world applications, you might need to develop a more sophisticated runner with a user interface, integration with external systems, or different output mechanisms.
*   **No Built-in State Persistence:** The state of the state machine is transient and exists in memory during execution. If state persistence is required (e.g., for long-running workflows or recovery after interruptions), you would need to add state serialization and storage mechanisms to the engine and runner.
*   **Basic Error Handling:** Error handling in the engine is basic (error reporting and halting). More advanced error handling strategies (e.g., retry policies, error propagation to parent machines, compensation mechanisms) would require further development.