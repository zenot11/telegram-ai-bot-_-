#!/usr/bin/env bash
set -e

PYTHON_BIN="python3"
if [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
fi

"$PYTHON_BIN" -m compileall telegram_bot backend_stub
"$PYTHON_BIN" -m json.tool backend_stub/data/universities.json > /tmp/universities_check.json
"$PYTHON_BIN" -m pytest

echo "Project check completed successfully."
