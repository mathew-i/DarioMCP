#!/bin/bash

# Installation script for DarioMCP using uv

set -e

echo "🚀 Installing DarioMCP with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing uv..."
    
    # Install uv
    if command -v curl &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    elif command -v pip &> /dev/null; then
        pip install uv
    else
        echo "❌ Please install uv manually: https://github.com/astral-sh/uv"
        exit 1
    fi
    
    echo "✅ uv installed successfully"
fi

# Verify uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is still not available. Please add it to your PATH."
    exit 1
fi

echo "📦 Installing dependencies with uv..."

# Use uv sync (recommended - automatically manages virtual environment)
# This will create .venv if it doesn't exist and install all dependencies
if uv sync; then
    echo "✅ Dependencies installed using uv sync"
else
    echo "⚠️  uv sync failed, trying alternative method..."
    
    # Fallback: Create venv and install manually
    if [ ! -d ".venv" ]; then
        echo "📁 Creating virtual environment..."
        uv venv
    fi
    
    echo "📥 Installing project and dependencies..."
    source .venv/bin/activate
    uv pip install -e .
fi

echo "✅ DarioMCP installed successfully!"
echo ""
echo "Next steps:"
echo "1. Set DATABASE_URI environment variable:"
echo "   export DATABASE_URI='postgresql://user:password@localhost:5432/dbname'"
echo ""
echo "2. Run the server (uv will automatically use .venv):"
echo "   uv run python -m dariomcp.server"
echo ""
echo "Or activate the virtual environment and run directly:"
echo "   source .venv/bin/activate"
echo "   python -m dariomcp.server"

