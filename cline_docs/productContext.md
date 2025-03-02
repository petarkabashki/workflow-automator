## Product Context

**Why this project exists:**

This project implements a flexible, asynchronous state machine engine driven by DOT graph files. It allows users to define state machines visually using the DOT language and execute them in Python.

**What problems it solves:**

*   Decouples state machine structure (DOT file) from behavior (Python methods).
*   Makes it easy to visually design and understand state machine workflows.
*   Allows modification of the state machine's structure without changing Python code.
*   Enables reuse of the state machine engine for different tasks.
*   Suitable for applications with complex workflows, decision-making processes, or sequential operations.

**How it should work:**

The engine parses a DOT file, defining the states and transitions of the state machine. It then executes the corresponding asynchronous Python methods defined in a state function class, managing state transitions based on conditions and overrides.