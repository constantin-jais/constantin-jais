#!/usr/bin/env sh
set -eu

command -v uv >/dev/null 2>&1 || {
  echo "uv required: https://docs.astral.sh/uv/" >&2
  exit 1
}
uv run --script ecosystem/specs/validate_spec_schemas.py
