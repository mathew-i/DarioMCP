"""
Setup script for DarioMCP.
"""
from setuptools import setup, find_packages

setup(
    name="dario-mcp",
    version="0.1.0",
    description="MCP server for analyzing PostgreSQL tables",
    author="DarioMCP Team",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
        "psycopg2-binary>=2.9.9",
        "python-dotenv>=1.0.0",
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "dario-mcp=dariomcp.server:main",
        ],
    },
    python_requires=">=3.8",
)

