#!/usr/bin/env bash

# Exit in case of error
set -e
set -x

pip install pip pip-tools
pip-compile --resolver=backtracking --strip-extras requirements/requirements.in
pip-compile --resolver=backtracking --strip-extras requirements/requirements-dev.in
