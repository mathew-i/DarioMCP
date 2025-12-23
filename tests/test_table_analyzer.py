"""
Test script for table analyzer functionality.
"""
import sys
import os
import asyncio
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dariomcp.table_analyzer import TableAnalyzer


def test_analyzer():
    """Test the table analyzer with a sample table."""
    # Get database URI from environment or use default
    db_uri = os.getenv("DATABASE_URI", "postgresql://padmin:TopSecret@localhost:5432/testdb")
    
    # Sample metadata (would normally come from Postgres MCP)
    sample_metadata = {
        "columns": [
            {
                "name": "id",
                "data_type": "integer",
                "is_nullable": "NO",
                "default_value": None
            },
            {
                "name": "created_at",
                "data_type": "timestamp without time zone",
                "is_nullable": "NO",
                "default_value": "CURRENT_TIMESTAMP"
            },
            {
                "name": "amount",
                "data_type": "numeric",
                "is_nullable": "YES",
                "default_value": None
            }
        ],
        "constraints": [
            {
                "name": "pk_test",
                "constraint_type": "PRIMARY KEY",
                "columns": ["id"]
            }
        ],
        "indexes": [
            {
                "name": "pk_test",
                "columns": ["id"],
                "is_unique": True,
                "is_primary": True
            }
        ]
    }
    
    try:
        analyzer = TableAnalyzer(db_uri)
        result = analyzer.analyze_table("public", "test_table", sample_metadata)
        print(json.dumps(result, indent=2, default=str))
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. PostgreSQL is running")
        print("2. Database URI is correct")
        print("3. The test table exists (or modify the test)")


if __name__ == "__main__":
    test_analyzer()

