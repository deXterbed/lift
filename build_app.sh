#!/bin/bash
# Build Lift.app for distribution. Requires: uv sync --extra dev
set -e
cd "$(dirname "$0")"

# Python 3.12: py2app tries to copy zlib.__file__ which doesn't exist. Apply fix.
.venv/bin/python patch_py2app_zlib.py

# py2app 0.28+ errors if setuptools merges install_requires from pyproject.toml.
# Run py2app without pyproject.toml so only setup.py is used.
if [ -f pyproject.toml ]; then
  mv pyproject.toml pyproject.toml.bak
  trap 'mv pyproject.toml.bak pyproject.toml' EXIT
fi

.venv/bin/python setup.py py2app "$@"
