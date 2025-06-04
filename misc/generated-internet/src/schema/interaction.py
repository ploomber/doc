from pydantic import BaseModel
from typing import Any
from datetime import datetime

class InteractionData(BaseModel):
    """Data model for user interactions"""
    action_type: str  # "click", "input", "navigation", etc.
    element_id: str | None = None
    element_text: str | None = None
    input_value: str | None = None
    page_url: str
    timestamp: datetime
    additional_data: dict[str, Any] | None = None

class InteractionResponse(BaseModel):
    """Response model for AI-generated content"""
    html_content: str
    success: bool = True
    message: str | None = None 
