# DoorDash MCP Server

A Model Context Protocol (MCP) server for DoorDash Drive API integration.

## Overview

This project provides a FastAPI server that implements the Model Context Protocol (MCP) for DoorDash Drive API, allowing Language Models (LLMs) to interact with DoorDash's delivery services.

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the example environment file and update with your DoorDash credentials:

```bash
cp example.env .env
```

## DoorDash API Integration

This project integrates with the DoorDash Drive API. For detailed instructions on setup and usage, see [DOORDASH_API.md](DOORDASH_API.md).

## Running the Server

Start the server with:

```bash
uvicorn app.main:app --reload
```

The server will be available at http://localhost:8000

## MCP Configuration

The MCP configuration is served at `/mcp-config` endpoint and is also available in the `mcp-config.json` file.

For IDE integration, an `mcp.json` file is provided that contains server startup configuration. The `print_mcp_config.py` script helps you manage this configuration:

1. View the current configuration:
```bash
python print_mcp_config.py
```

2. Generate a new configuration with your DoorDash credentials:
```bash
python print_mcp_config.py --generate --developer-id "your-id" --key-id "your-key-id" --signing-secret "your-secret"
```

3. Generate a template configuration:
```bash
python print_mcp_config.py --generate
```

4. See all available options:
```bash
python print_mcp_config.py --help
```

## Example Usage

There are example scripts in the `examples` directory showing how to:

1. Generate a JWT for DoorDash API authentication
2. Create, get, update, and cancel deliveries

## Documentation

API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features

- FastAPI-based server with MCP integration
- DoorDash Drive API integration with JWT authentication
- Tools for creating quotes, deliveries, and more
- Uses the official MCP Python SDK from GitHub
- MCP configuration for IDE and client integration

## Prerequisites

- Python 3.9+
- Conda

## Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/doordash-mcp.git
cd doordash-mcp
```

2. Create and activate the conda environment:

```bash
conda create -n mcp-server python=3.9 -y
conda activate mcp-server
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables by copying the example file:

```bash
cp example.env .env
```

Edit the `.env` file to add your DoorDash API key (if applicable).

## Running the Server

Start the server using Uvicorn:

```bash
uvicorn app.main:app --reload --port 8000
```

The server will start at http://localhost:8000.

## API Documentation

Once the server is running, you can access:

- API documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc
- Health check: http://localhost:8000/health
- MCP configuration: http://localhost:8000/mcp-config

## MCP Tool Reference

The server exposes the following MCP tools:

### create_quote

Create a delivery quote from DoorDash.

```python
create_quote(
    external_delivery_id: str,
    dropoff_address: str, 
    dropoff_phone_number: str, 
    **kwargs
)
```

### accept_quote

Accept a delivery quote from DoorDash.

```python
accept_quote(
    external_delivery_id: str,
    **kwargs
)
```

### create_delivery

Create a delivery with DoorDash.

```python
create_delivery(
    external_delivery_id: str,
    dropoff_address: str, 
    dropoff_phone_number: str, 
    **kwargs
)
```

### get_delivery

Get delivery details from DoorDash.

```python
get_delivery(
    external_delivery_id: str
)
```

### update_delivery

Update delivery details in DoorDash.

```python
update_delivery(
    external_delivery_id: str,
    **kwargs  # Fields to update (e.g., dropoff_instructions)
)
```

### cancel_delivery

Cancel a delivery in DoorDash.

```python
cancel_delivery(
    external_delivery_id: str
)
```

## REST API Endpoints

The server also provides REST API endpoints that mirror the MCP tools functionality:

- `POST /api/create_quote`
- `POST /api/accept_quote`
- `POST /api/create_delivery`
- `GET /api/delivery/{external_delivery_id}`
- `PATCH /api/delivery/{external_delivery_id}`
- `DELETE /api/delivery/{external_delivery_id}`

## IDE and Client Integration

The server provides a JSON configuration file for IDE and client integration. You can access this configuration at:

```
http://localhost:8000/mcp-config
```

This configuration can be used to automatically integrate the MCP tools with your IDE or client application. The configuration includes:

- Server name and version
- Available capabilities
- Tool definitions with parameter schemas
- Endpoint information