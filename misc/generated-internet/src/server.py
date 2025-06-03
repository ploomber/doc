from contextlib import asynccontextmanager
from logging import Logger
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.services.logging.logging import setup_logging
from src.services.cors.middleware import setup_cors_middleware
from src.schema.interaction import InteractionData
from src.services.ai_generator import AIContentGenerator
from .settings import Settings, get_settings
from .utils import error_html

# Setup templates
templates = Jinja2Templates(directory="src/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application. Handles startup and shutdown events.
    """
    settings: Settings = app.state.settings
    logger: Logger = app.state.logger
    
    # --- STARTUP ---
    app.state.ai_generator = AIContentGenerator(
        provider=settings.MODEL_PROVIDER,
        api_key=settings.MODEL_API_KEY,
        model=settings.MODEL_NAME
    )
    
    # Initialize the database / redis here
    logger.info("Application startup complete")
    
    yield
    
    # --- SHUTDOWN ---
    # Close connection here
    logger.info("Application shutdown complete")


def create_server(settings: Settings) -> FastAPI:
    app = FastAPI(
        title="Interactive Web App",
        description="A web app that tracks user interactions and sends them to the API",
        version="0.1.0",
        lifespan=lifespan
    )

    logger = setup_logging(settings)
    logger.info(f"Profile: {settings.PROFILE}") 

    app.state.logger = logger
    app.state.settings = settings
    
    # Include routes
    
    @app.get("/health")
    async def health_check(settings: Settings = Depends(get_settings)):
        return {"message": "ok", "profile": settings.PROFILE, "version": settings.VERSION}

    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        """Serve the main interactive HTML page"""
        return templates.TemplateResponse("index.html", {"request": request})

    @app.post("/api/interact")
    async def handle_interaction(interaction: InteractionData, settings: Settings = Depends(get_settings)):
        """Handle user interactions and return AI-generated complete HTML page"""
        logger: Logger = app.state.logger
        ai_generator: AIContentGenerator = app.state.ai_generator

        logger.info(f"Interaction received: \n{interaction}")
        
        try:
            interaction_dict = {
                "action_type": interaction.action_type,
                "element_id": interaction.element_id,
                "element_text": interaction.element_text,
                "input_value": interaction.input_value,
                "page_url": interaction.page_url,
                "timestamp": interaction.timestamp,
                "additional_data": interaction.additional_data
            }
            
            complete_html = await ai_generator.generate_content(interaction_dict, logger)
            
            # Return the complete HTML page directly
            return HTMLResponse(
                content=complete_html,
                status_code=200,
                headers={"Content-Type": "text/html; charset=utf-8"}
            )
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return HTMLResponse(
                content=error_html,
                status_code=500,
                headers={"Content-Type": "text/html; charset=utf-8"}
            )

    # Setup authentication middleware
    setup_cors_middleware(app, settings)

    return app
