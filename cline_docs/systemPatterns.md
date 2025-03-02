## System Patterns

The system is built around the following key patterns:

*   **State Machine:** The core pattern is a state machine, with states and transitions defined in a DOT file.
*   **Asynchronous Execution:** State functions are executed asynchronously, allowing for non-blocking I/O operations.
*   **Class-Based State Functions:** State functions are organized within a Python class, promoting modularity and maintainability.
*   **Observer Pattern:** The `WFEngine` uses the observer pattern to notify subscribers of events.
*   **DOT Specification Driven:** The state machine is driven by a DOT graph specification.