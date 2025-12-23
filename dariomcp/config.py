"""
Configuration for DarioMCP server.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for DarioMCP."""
    
    # Database connection
    DATABASE_URI: Optional[str] = os.getenv("DATABASE_URI")
    
    # Postgres MCP server settings
    POSTGRES_MCP_URL: str = os.getenv("POSTGRES_MCP_URL", "http://localhost:8000")
    USE_POSTGRES_MCP: bool = os.getenv("USE_POSTGRES_MCP", "false").lower() == "true"
    
    # Postgres MCP stdio settings (if using stdio transport)
    POSTGRES_MCP_COMMAND: Optional[str] = os.getenv("POSTGRES_MCP_COMMAND")
    POSTGRES_MCP_ARGS: Optional[str] = os.getenv("POSTGRES_MCP_ARGS", "").split() if os.getenv("POSTGRES_MCP_ARGS") else []

