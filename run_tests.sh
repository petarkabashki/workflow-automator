#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate py311

# Install pytest if it's not already installed
pip install pytest

# Pass all script arguments to pytest
pytest test_engine.py "$@"
