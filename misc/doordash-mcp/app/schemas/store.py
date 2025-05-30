from pydantic import BaseModel, Field
from typing import Dict, Optional, Any, List

class StoreBase(BaseModel):
    """Base model for store operations"""
    external_business_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]{3,64}$", description="Unique, caller-selected ID of the business")
    external_store_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]{3,64}$", description="Unique, caller-selected ID for the store")

class StoreCreate(BaseModel):
    """Model for creating a store"""
    external_business_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]{3,64}$", description="Unique, caller-selected ID of the business")
    external_store_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]{3,64}$", description="Unique, caller-selected ID for the store")
    name: str = Field(..., description="The name of the store")
    address: str = Field(..., description="The full address of the store")
    phone_number: Optional[str] = Field(None, description="Phone number of the store")

class StoreUpdate(BaseModel):
    """Model for updating a store"""
    external_business_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]{3,64}$", description="Unique, caller-selected ID of the business")
    external_store_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]{3,64}$", description="Unique, caller-selected ID for the store")
    name: Optional[str] = Field(None, description="The name of the store")
    address: Optional[str] = Field(None, description="The full address of the store")
    phone_number: Optional[str] = Field(None, description="Phone number of the store")

class StoreList(BaseModel):
    """Model for listing stores"""
    external_business_id: str = Field(..., pattern=r"^[A-Za-z0-9_-]{3,64}$", description="Unique, caller-selected ID of the business")
    activation_status: Optional[str] = Field(None, description="Filter stores by activation status ('active' or 'inactive')")
    continuation_token: Optional[str] = Field(None, description="Token for pagination")

class StoreResponse(StoreBase):
    """Model for store response"""
    name: str
    address: str
    phone_number: Optional[str] = None
    status: str
    is_test: bool
    created_at: str
    last_updated_at: str

class StoreListResponse(BaseModel):
    """Model for listing stores response"""
    result: List[StoreResponse]
    continuation_token: Optional[str] = None
    result_count: int 