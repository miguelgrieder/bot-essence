#!/usr/bin/env bash

# Exit in case of error
set -e
set -x

pip install --upgrade pip pip-tools
pip-compile --upgrade --resolver=backtracking --strip-extras requirements/requirements.in
pip-compile --upgrade --resolver=backtracking --strip-extras requirements/requirements-dev.in
