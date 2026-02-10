#!/bin/bash
# ==============================================================================
# Setup Script - Install dependencies
# ==============================================================================
# Usage: ./setup.sh

set -e

echo "📦 Installing dependencies..."

# Check and install uv if needed
if ! command -v uv &> /dev/null; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Install Python dependencies
echo "Installing Python dependencies..."
uv sync --dev

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend && pnpm install && cd ..

echo "✅ Installation complete."
