## Tech Context

The project uses the following technologies:

*   **Python 3.7+:** The project requires Python 3.7 or later.
*   **pydot:** Used for parsing DOT files.
*   **nest_asyncio:** Required for handling nested asyncio event loops.
*   **asyncio:** Used for asynchronous programming.
*   **Graphviz:** System executables are required for DOT file parsing.
*   **pytest:** Used for testing.

**Development Setup:**

1.  Install Python 3.7 or later.
2.  Install dependencies: `pip install pydot nest_asyncio pytest`
3.  Install Graphviz system executables:
    *   **macOS:** `brew install graphviz`
    *   **Debian/Ubuntu:** `sudo apt-get install graphviz`
    *   **Windows:** Download from the [Graphviz website](https://graphviz.org/download/) and add the `bin` directory to your system's `PATH`.