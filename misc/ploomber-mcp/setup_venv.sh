#!/bin/bash
# setup_venv.sh - Script to set up virtual environment for Ploomber MCP

# Exit on error
set -e

echo "Setting up virtual environment for Ploomber MCP..."

# Create virtual environment
python -m venv venv
echo "Virtual environment created."

# Determine the correct activation script based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    ACTIVATE="venv/Scripts/activate"
    PIP="venv/Scripts/pip"
    PYTHON="venv/Scripts/python"
else
    # Unix-like (macOS, Linux)
    ACTIVATE="venv/bin/activate"
    PIP="venv/bin/pip"
    PYTHON="venv/bin/python"
fi

# Upgrade pip
echo "Upgrading pip..."
$PIP install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    $PIP install -r requirements.txt
else
    echo "Warning: requirements.txt not found. Creating minimal requirements..."
    echo "mcp" > requirements.txt
    echo "ploomber_cloud" >> requirements.txt
    $PIP install -r requirements.txt
fi

# Install package in development mode
echo "Installing package in development mode..."
$PIP install -e .

# Verify installation
echo "Verifying installation..."
$PYTHON -c "import sys; print(f'Setup complete! Python version: {sys.version}')"

echo ""
echo "Setup complete! To activate the virtual environment, run:"
echo "source $ACTIVATE  # On Unix-like systems (Linux, macOS)"
echo "or"
echo "$ACTIVATE  # On Windows"
echo ""