#!/bin/bash
# generate_mcp_json.sh - Creates a personalized mcp.json file

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine python executable path based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    PYTHON_PATH="${PROJECT_DIR}/venv/Scripts/python"
else
    # Unix-like (macOS, Linux)
    PYTHON_PATH="${PROJECT_DIR}/venv/bin/python"
fi

# Path to the server script
SERVER_SCRIPT="${PROJECT_DIR}/src/mcp_ploomber/server.py"

# Create the mcp.json file
cat > "${PROJECT_DIR}/mcp.json" << EOF
{
    "mcpServers": {
        "ploomber-mcp": {
            "command": "${PYTHON_PATH}",
            "args": [
                "${SERVER_SCRIPT}"
            ],
            "env": {
                "_PLOOMBER_CLOUD_ENV": "",
                "PLOOMBER_CLOUD_KEY": ""
            },
            "setup": "${PROJECT_DIR}/setup_venv.sh"
        }
    }
}
EOF

echo "Generated mcp.json with your local paths at: ${PROJECT_DIR}/mcp.json"
echo "Please edit the file to add your PLOOMBER_CLOUD_KEY and other environment variables as needed."