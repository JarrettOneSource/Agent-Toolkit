#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")/.."

python_bin=.venv/bin/python
"$python_bin" scripts/sync_package.py --check
.venv/bin/ruff check plugins/local-tools scripts tests
.venv/bin/ruff format --check plugins/local-tools scripts tests
sh -n plugins/agent-toolkit/scripts/session-start.sh
bash -n utilities/tmux-keep-waiting/tmux-keep-waiting

export PYTHONPATH="$PWD/plugins/local-tools/src${PYTHONPATH:+:$PYTHONPATH}"
"$python_bin" -m coverage erase
"$python_bin" -m coverage run -m unittest discover -s tests
"$python_bin" -m coverage run -m unittest discover -s plugins/local-tools/tests
"$python_bin" -m coverage run scripts/quality.py
"$python_bin" -m coverage combine
"$python_bin" -m coverage report --skip-empty
"$python_bin" -m coverage json -o coverage.json
.venv/bin/vulture plugins/local-tools/src scripts --min-confidence 100
