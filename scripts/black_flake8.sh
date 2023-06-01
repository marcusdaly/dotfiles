#!/bin/bash
python -m black "${@:1}"
python -m flake8 "${@:1}"