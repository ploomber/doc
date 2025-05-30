from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List

class BusinessBase(BaseModel):
    """Base model for business operations"""
    external_business_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]{3,64}$", description="Unique, caller-selected ID of the business")
    
class BusinessCreate(BusinessBase):
    """Model for creating a business"""
    name: str = Field(..., description="The name of the business")
    description: Optional[str] = Field(None, description="A description of the business")
    external_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the business")
    
class BusinessUpdate(BaseModel):
    """Model for updating a business"""
    external_business_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]{3,64}$", description="Unique, caller-selected ID of the business")
    name: Optional[str] = Field(None, description="The name of the business")
    description: Optional[str] = Field(None, description="A description of the business")
    external_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the business")
    
class BusinessList(BaseModel):
    """Model for listing businesses"""
    activation_status: Optional[str] = Field(None, description="Filter businesses by activation status ('active' or 'inactive')")
    continuation_token: Optional[str] = Field(None, description="Token for pagination")
    
class BusinessResponse(BusinessBase):
    """Model for business response"""
    name: str
    description: Optional[str] = None
    activation_status: str
    created_at: str
    last_updated_at: str
    is_test: bool
    external_metadata: Optional[Dict[str, Any]] = None
    
class BusinessListResponse(BaseModel):
    """Model for listing businesses response"""
    result: List[BusinessResponse]
    continuation_token: Optional[str] = None
    result_count: int 