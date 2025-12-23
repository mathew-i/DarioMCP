#!/bin/bash
# Wrapper script to run DarioMCP server using the virtual environment

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Use uv run if available, otherwise use venv Python
if command -v uv &> /dev/null; then
    cd "$SCRIPT_DIR"
    exec uv run python -m dariomcp.server "$@"
else
    # Fallback to venv Python
    VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
    if [ -f "$VENV_PYTHON" ]; then
        cd "$SCRIPT_DIR"
        exec "$VENV_PYTHON" -m dariomcp.server "$@"
    else
        echo "Error: Virtual environment not found. Please run 'uv sync' first." >&2
        exit 1
    fi
fi

