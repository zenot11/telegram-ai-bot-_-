#!/usr/bin/env bash
set -e

python3 -m compileall telegram_bot backend_stub
python3 -m json.tool backend_stub/data/universities.json > /tmp/universities_check.json
pytest

echo "Project check completed successfully."
