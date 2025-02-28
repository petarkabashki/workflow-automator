#!/bin/bash

# Allow arguments for individual tests to be passed and used.

eval "$(conda shell.bash hook)"
conda activate py311

# Install pytest if it's not already installed
pip install pytest

# Run all tests
pytest -v

# Commented out previous tests
# pytest test_engine.py
