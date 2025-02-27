#!/bin/bash

# Install pytest, networkx and pygraphviz
pip install pytest networkx pygraphviz

# Run the tests using pytest
pytest test_engine.py
