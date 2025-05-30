#!/usr/bin/env python
"""
Utility script to print or generate the MCP configuration file (mcp.json).
"""

import json
import os
import sys
import argparse
from pathlib import Path

def print_mcp_config():
    """Print the mcp.json file to the console with proper formatting."""
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    mcp_json_path = script_dir / "mcp.json"
    
    if not mcp_json_path.exists():
        print(f"Error: mcp.json file not found at {mcp_json_path}")
        sys.exit(1)
    
    try:
        with open(mcp_json_path, 'r') as f:
            config = json.load(f)
        
        # Print with nice formatting
        print(json.dumps(config, indent=2))
        
        print("\nMCP Configuration file location:")
        print(f"{mcp_json_path}")
        
    except json.JSONDecodeError:
        print(f"Error: mcp.json file contains invalid JSON")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading mcp.json file: {str(e)}")
        sys.exit(1)

def generate_mcp_config(developer_id=None, key_id=None, signing_secret=None, port=8000):
    """
    Generate a customized mcp.json file with the provided credentials.
    """
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    mcp_json_path = script_dir / "mcp.json"
    
    # Default configuration
    config = {
        "mcpServers": {
            "doordash": {
                "command": "python",
                "args": [
                    "-m", "uvicorn",
                    "app.main:app",
                    "--host", "127.0.0.1",
                    "--port", str(port)
                ],
                "env": {
                    "DOORDASH_API_URL": "https://openapi.doordash.com/drive/v2",
                    "DOORDASH_DEVELOPER_ID": developer_id or "your_developer_id",
                    "DOORDASH_KEY_ID": key_id or "your_key_id",
                    "DOORDASH_SIGNING_SECRET": signing_secret or "your_signing_secret",
                    "LOG_LEVEL": "INFO"
                },
                "cwd": str(script_dir),
                "configUrl": f"http://localhost:{port}/mcp-config"
            }
        }
    }
    
    # If all credentials are provided, add a message showing they've been set
    if developer_id and key_id and signing_secret:
        print("Generating mcp.json with your DoorDash credentials...")
    else:
        print("Generating default mcp.json template...")
        
    # Write the configuration to mcp.json
    with open(mcp_json_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"MCP configuration file generated at: {mcp_json_path}")
    
    # Print the generated configuration
    print("\nGenerated configuration:")
    print(json.dumps(config, indent=2))

def main():
    parser = argparse.ArgumentParser(description='Manage MCP configuration')
    parser.add_argument('--print', action='store_true', help='Print the current mcp.json configuration')
    parser.add_argument('--generate', action='store_true', help='Generate a new mcp.json configuration')
    parser.add_argument('--developer-id', help='DoorDash Developer ID')
    parser.add_argument('--key-id', help='DoorDash Key ID')
    parser.add_argument('--signing-secret', help='DoorDash Signing Secret')
    parser.add_argument('--port', type=int, default=8000, help='Server port (default: 8000)')
    
    args = parser.parse_args()
    
    if args.generate:
        generate_mcp_config(
            developer_id=args.developer_id,
            key_id=args.key_id,
            signing_secret=args.signing_secret,
            port=args.port
        )
    elif args.print or len(sys.argv) == 1:  # Default action if no arguments provided
        print_mcp_config()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 