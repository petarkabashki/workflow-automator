#!/bin/bash

# Allow arguments for individual tests to be passed and used.

eval "$(conda shell.bash hook)"
conda activate py311

# Install pytest if it's not already installed
pip install pytest

# Run the dot parser tests
pytest test_dot_parser.py test_parse_simple_graph_with_nodes_and_edges -v

# Commented out previous tests
# pytest test_engine.py
