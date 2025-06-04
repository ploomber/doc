from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.settings import Settings

def setup_cors_middleware(app: FastAPI, settings: Settings):
    """
    Configure CORS middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        settings: Application settings (optional)
    """
    # Default origins if settings are not provided
    # Note: Adding "null" to handle iframe requests from data URLs or sandboxed contexts
    allowed_origins = [
        "*",
        "null"  # This is crucial for iframe requests
    ]
    
    # If settings are provided, use configured origins
    if settings and hasattr(settings, 'ALLOWED_ORIGINS'):
        # Always add "null" for iframe support, even when using custom origins
        allowed_origins = settings.ALLOWED_ORIGINS + ["null"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,
    )
