# Cursor IDE Setup Guide

This guide explains how to configure DarioMCP server in Cursor IDE.

## Prerequisites

1. Install dependencies using `uv sync`:
   ```bash
   uv sync
   ```

2. Ensure `uv` is in your PATH (or use one of the alternative methods below)

## Configuration Options

### Option 1: Using `uv run` (Recommended)

If `uv` is available in your PATH, use this configuration in Cursor IDE's MCP settings:

```json
{
  "mcpServers": {
    "dario-mcp": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "dariomcp.server"
      ],
      "env": {
        "DATABASE_URI": "postgresql://padmin:TopSecret@localhost:5432/testdb"
      }
    }
  }
}
```

### Option 2: Using Wrapper Script (Recommended if uv not in PATH)

If `uv` is not in PATH, use the wrapper script:

```json
{
  "mcpServers": {
    "dario-mcp": {
      "command": "/Users/mateusziwaszkiewicz/repos/myprojects/DarioMCP/DarioMCP/run_server.sh",
      "args": [],
      "env": {
        "DATABASE_URI": "postgresql://padmin:TopSecret@localhost:5432/testdb"
      }
    }
  }
}
```

**Note**: The wrapper script automatically uses `uv run` if available, or falls back to the venv Python.

### Option 3: Using Virtual Environment Python Directly

Use the Python interpreter from the `.venv` directory:

```json
{
  "mcpServers": {
    "dario-mcp": {
      "command": "/Users/mateusziwaszkiewicz/repos/myprojects/DarioMCP/DarioMCP/.venv/bin/python",
      "args": ["-m", "dariomcp.server"],
      "env": {
        "DATABASE_URI": "postgresql://padmin:TopSecret@localhost:5432/testdb"
      }
    }
  }
}
```

## Finding Your Project Path

To find the absolute path to your project:

```bash
cd /Users/mateusziwaszkiewicz/repos/myprojects/DarioMCP/DarioMCP
pwd
```

Use the output of `pwd` as the base path in the configurations above.

## Troubleshooting

### Error: "No module named 'dariomcp'"

This means the virtual environment is not being used. Try:

1. **Verify virtual environment exists**:
   ```bash
   ls -la .venv/bin/python
   ```

2. **Reinstall the package**:
   ```bash
   uv sync
   ```

3. **Use Option 2 or Option 3** above with absolute paths

### Error: "uv: command not found"

- Install `uv` or add it to your PATH
- Or use Option 2 (wrapper script) or Option 3 (venv Python directly)

### Error: "Permission denied"

Make sure the wrapper script is executable:
```bash
chmod +x run_server.sh
```

## Testing the Configuration

Before configuring in Cursor IDE, test the server manually:

```bash
# Using uv
uv run python -m dariomcp.server

# Or using venv Python directly
.venv/bin/python -m dariomcp.server
```

The server should start without errors (it will wait for MCP client connections via stdio).

