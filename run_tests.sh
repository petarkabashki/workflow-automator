#!/bin/bash

eval "$(conda shell.bash hook)"
conda activate py311

pytest test_engine.py
