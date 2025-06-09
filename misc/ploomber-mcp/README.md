# mcp-ploomber

Setup:

```sh
# requires conda
pip install invoke
invoke setup
conda activate mcp-ploomber
```

If you're not using conda, create a virtual env and do:

```sh
pip install --editable .
```

## Virtual Environment Setup

You'll need to set up a virtual environment to run the MCP server. We provide setup scripts to make this easy:

1. Run the setup script to create and configure the virtual environment:

```sh
# Make the script executable first
chmod +x setup_venv.sh
./setup_venv.sh
```

This script will:
- Create a Python virtual environment
- Install all required dependencies
- Set up the package in development mode

## MCP Configuration

To configure the MCP server, you need to create an `mcp.json` file:

1. Run the generation script to create a personalized configuration:

```sh
# Make the script executable first
chmod +x generate_mcp_json.sh
./generate_mcp_json.sh
```

2. Edit the generated `mcp.json` file to add your Ploomber Cloud API key:

```json
{
    "mcpServers": {
        "ploomber-mcp": {
            "command": "/path/to/your/venv/bin/python",
            "args": [
                "/path/to/your/src/mcp_ploomber/server.py"
            ],
            "env": {
                "_PLOOMBER_CLOUD_ENV": "",
                "PLOOMBER_CLOUD_KEY": "YOUR_API_KEY_HERE"
            },
            "setup": "/path/to/your/setup_venv.sh"
        }
    }
}
```

## Running the Server

Once you've completed the setup, you can start the MCP server manually using:

```sh
cd src/mcp_ploomber
```

```sh
mcp run server.py
```

To debug, you can also run the MCP server in dev mode:

```sh
mcp dev server.py
```

To add the MCP to your LLM client, simply copy/paste your `mcp.json` where the client expects the MCP config file.




