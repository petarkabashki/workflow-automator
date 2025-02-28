#!/bin/bash

# Allow arguments for individual tests to be passed and used. AI!

eval "$(conda shell.bash hook)"
conda activate py311

# Install pytest if it's not already installed
# pip install pytest

# pytest test_engine.py
pytest test_engine.py
