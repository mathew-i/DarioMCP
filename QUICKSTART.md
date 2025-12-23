# Quick Start Guide

## Prerequisites

1. **PostgreSQL Database**: Ensure you have a PostgreSQL database running
2. **Python 3.8+**: Make sure Python is installed
3. **uv**: Fast Python package installer - [Install uv](https://github.com/astral-sh/uv)
4. **Postgres MCP Server** (optional): For full MCP integration

## Setup Steps

### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### 2. Install Dependencies

**Using uv (recommended):**

```bash
# Install the project and dependencies (automatically creates .venv)
uv sync

# Or use the installation script
bash setup/install.sh

# Alternative: Install system-wide (requires --system flag)
# uv pip install -e . --system
```

**Alternative (traditional pip):**

```bash
pip install -r requirements.txt
```

### 3. Configure Database Connection

Set the `DATABASE_URI` environment variable:

```bash
export DATABASE_URI="postgresql://padmin:TopSecret@localhost:5432/testdb"
```

Or create a `.env` file:

```bash
DATABASE_URI=postgresql://padmin:TopSecret@localhost:5432/testdb
```

### 4. Start the MCP Server

**Using uv (recommended):**

```bash
uv run python -m dariomcp.server
```

**Or traditionally:**

```bash
python -m dariomcp.server
```

The server will run using stdio transport and wait for MCP client connections.

### 5. Use with MCP Client

#### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

**Using uv:**

```json
{
  "mcpServers": {
    "dario-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "dariomcp.server"],
      "env": {
        "DATABASE_URI": "postgresql://padmin:TopSecret@localhost:5432/testdb"
      }
    }
  }
}
```

**Or using traditional Python:**

```json
{
  "mcpServers": {
    "dario-mcp": {
      "command": "python",
      "args": ["-m", "dariomcp.server"],
      "env": {
        "DATABASE_URI": "postgresql://padmin:TopSecret@localhost:5432/testdb"
      }
    }
  }
}
```

Restart Claude Desktop to load the server.

## Example Usage

Once connected, you can use the `analyze_table` tool:

```json
{
  "schema_name": "public",
  "table_name": "sales",
  "database_uri": "postgresql://user:password@localhost:5432/dbname"
}
```

## Testing

Run the test script to verify the analyzer works:

**Using uv:**

```bash
export DATABASE_URI="postgresql://padmin:TopSecret@localhost:5432/testdb"
uv run python tests/test_table_analyzer.py
```

**Or traditionally:**

```bash
export DATABASE_URI="postgresql://padmin:TopSecret@localhost:5432/testdb"
python tests/test_table_analyzer.py
```

## Troubleshooting

### Connection Issues

- Verify PostgreSQL is running: `psql -U padmin -d testdb`
- Check database URI format: `postgresql://user:password@host:port/database`
- Ensure database credentials are correct

### MCP Server Issues

- Verify Python path: `which python`
- Verify uv installation: `uv --version`
- Check MCP SDK installation: `uv pip list | grep mcp` (or `pip list | grep mcp`)
- Review server logs for error messages

### Analysis Errors

- Ensure table exists in the specified schema
- Verify you have SELECT permissions on the table
- Check that timestamp columns exist for daily load analysis

