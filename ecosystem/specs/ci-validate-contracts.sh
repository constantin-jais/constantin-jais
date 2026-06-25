#!/usr/bin/env sh
set -eu

VENV_DIR="${SPEC_CONTRACTS_VENV:-.venv-spec-contracts}"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install -r ecosystem/specs/requirements-ci.txt
"$VENV_DIR/bin/python" ecosystem/specs/validate_spec_schemas.py
