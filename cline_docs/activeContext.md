## Active Context

**Current Task:** Fixing the `test_edge_label` test in `test_dot_parser.py`.

**Recent Changes:**

*   Rewrote the DOT parser to use regular expressions instead of Lark.
*   Fixed an issue where the simple edge regex was matching edges with attributes.
*   Fixed an issue where duplicate edges were being created.

**Next Steps:**

*   Update the memory bank.