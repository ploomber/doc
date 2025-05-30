from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os

from app.routers import doordash

# Create FastAPI application
app = FastAPI(title="Model Context Protocol Server", version="0.1.0")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(doordash.router, prefix="/api")

# Get MCP server instance from router
mcp_server = doordash.mcp_server

@app.get("/")
async def root():
    return {"message": "Welcome to Model Context Protocol Server"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/mcp-config")
async def get_mcp_config():
    """Return the MCP configuration for clients and IDEs"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp-config.json")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return JSONResponse(content=config)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Could not load MCP configuration: {str(e)}"}
        ) 