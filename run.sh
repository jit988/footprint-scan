#!/usr/bin/env bash
cd "$(dirname "$0")"
[ -f venv/bin/activate ] && . venv/bin/activate
exec python3 osint_toolkit.py "$@"
