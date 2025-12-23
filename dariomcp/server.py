"""
DarioMCP Server - Main MCP server implementation.
"""
import asyncio
import os
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

from .table_analyzer import TableAnalyzer
from .postgres_client import PostgresMCPClient


# Initialize the server
app = Server("dario-mcp")

# Global instances
table_analyzer: Optional[TableAnalyzer] = None
postgres_client: Optional[PostgresMCPClient] = None


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="analyze_table",
            description="Analyze a database table to determine its type (fact/dimension), keys, references, record counts, and daily load statistics. Requires connection to Postgres MCP server for metadata retrieval.",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema_name": {
                        "type": "string",
                        "description": "Schema name containing the table"
                    },
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to analyze"
                    },
                    "database_uri": {
                        "type": "string",
                        "description": "PostgreSQL database connection URI (e.g., postgresql://user:password@host:port/dbname). If not provided, uses DATABASE_URI environment variable."
                    },
                    "postgres_mcp_url": {
                        "type": "string",
                        "description": "URL of the Postgres MCP server (default: http://localhost:8000)"
                    }
                },
                "required": ["schema_name", "table_name"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    global table_analyzer, postgres_client
    
    if name == "analyze_table":
        schema_name = arguments.get("schema_name")
        table_name = arguments.get("table_name")
        database_uri = arguments.get("database_uri") or os.getenv("DATABASE_URI")
        postgres_mcp_url = arguments.get("postgres_mcp_url", "http://localhost:8000")
        
        if not database_uri:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Database URI is required. Provide it as an argument or set DATABASE_URI environment variable."
                    }, indent=2)
                )
            ]
        
        if not schema_name or not table_name:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "schema_name and table_name are required"
                    }, indent=2)
                )
            ]
        
        try:
            # Initialize analyzer if needed
            if table_analyzer is None or table_analyzer.db_uri != database_uri:
                table_analyzer = TableAnalyzer(database_uri)
            
            # Initialize Postgres MCP client if needed
            if postgres_client is None:
                postgres_client = PostgresMCPClient(postgres_mcp_url)
            
            # Get table metadata from Postgres MCP
            # Note: In a real implementation, this would use the MCP client to call
            # the Postgres MCP server's get_object_details tool
            # For now, we'll fetch metadata directly from the database
            metadata = await get_table_metadata_direct(database_uri, schema_name, table_name)
            
            # Perform analysis
            analysis_result = table_analyzer.analyze_table(
                schema_name, 
                table_name, 
                metadata
            )
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(analysis_result, indent=2, default=str)
                )
            ]
            
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "error": str(e),
                        "error_type": type(e).__name__
                    }, indent=2)
                )
            ]
    
    else:
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2)
            )
        ]


async def get_table_metadata_direct(
    db_uri: str, 
    schema_name: str, 
    table_name: str
) -> Dict[str, Any]:
    """
    Get table metadata directly from the database.
    In a full implementation, this would use the Postgres MCP client.
    """
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    conn = psycopg2.connect(db_uri)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get columns
            columns_query = """
                SELECT
                    column_name as name,
                    data_type,
                    is_nullable,
                    column_default as default_value,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
            """
            cur.execute(columns_query, (schema_name, table_name))
            columns = [dict(row) for row in cur.fetchall()]
            
            # Get constraints
            constraints_query = """
                SELECT
                    tc.constraint_name as name,
                    tc.constraint_type,
                    kcu.column_name,
                    ccu.table_schema AS referenced_table_schema,
                    ccu.table_name AS referenced_table,
                    ccu.column_name AS referenced_column
                FROM information_schema.table_constraints AS tc
                LEFT JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                LEFT JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.table_schema = %s AND tc.table_name = %s
            """
            cur.execute(constraints_query, (schema_name, table_name))
            constraint_rows = cur.fetchall()
            
            # Group constraints
            constraints = {}
            for row in constraint_rows:
                constraint_name = row['name']
                if constraint_name not in constraints:
                    constraints[constraint_name] = {
                        "name": constraint_name,
                        "constraint_type": row['constraint_type'],
                        "columns": [],
                        "referenced_table": None,
                        "referenced_columns": []
                    }
                
                if row['column_name']:
                    constraints[constraint_name]["columns"].append(row['column_name'])
                
                if row['referenced_table']:
                    constraints[constraint_name]["referenced_table"] = f"{row['referenced_table_schema']}.{row['referenced_table']}"
                    if row['referenced_column']:
                        constraints[constraint_name]["referenced_columns"].append(row['referenced_column'])
            
            # Get indexes
            indexes_query = """
                SELECT
                    i.relname as index_name,
                    a.attname as column_name,
                    ix.indisunique as is_unique,
                    ix.indisprimary as is_primary
                FROM pg_class t
                JOIN pg_index ix ON t.oid = ix.indrelid
                JOIN pg_class i ON i.oid = ix.indexrelid
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
                JOIN pg_namespace n ON n.oid = t.relnamespace
                WHERE n.nspname = %s AND t.relname = %s
                ORDER BY i.relname, a.attname
            """
            cur.execute(indexes_query, (schema_name, table_name))
            index_rows = cur.fetchall()
            
            # Group indexes
            indexes = {}
            for row in index_rows:
                index_name = row['index_name']
                if index_name not in indexes:
                    indexes[index_name] = {
                        "name": index_name,
                        "columns": [],
                        "is_unique": row['is_unique'],
                        "is_primary": row['is_primary']
                    }
                indexes[index_name]["columns"].append(row['column_name'])
            
            return {
                "columns": columns,
                "constraints": list(constraints.values()),
                "indexes": list(indexes.values())
            }
    finally:
        conn.close()


async def main():
    """Main entry point for the server."""
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

