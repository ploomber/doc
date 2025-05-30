from fastapi import APIRouter, HTTPException, Path, Query, Depends
from typing import Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

from app.services.doordash_service import DoordashService
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessList, BusinessResponse, BusinessListResponse
from app.schemas.store import StoreCreate, StoreUpdate, StoreList, StoreResponse, StoreListResponse

router = APIRouter(tags=["doordash"])

# Initialize DoorDash service
doordash_service = DoordashService()

# Initialize MCP server
mcp_server = FastMCP("DoorDash MCP Tools")

# Define MCP tools
@mcp_server.tool()
def create_quote(external_delivery_id: str, dropoff_address: str, dropoff_phone_number: str, **kwargs) -> Dict[str, Any]:
    """
    Create a delivery quote from DoorDash.
    
    Args:
        external_delivery_id: Your unique identifier for the delivery
        dropoff_address: The delivery destination address
        dropoff_phone_number: The recipient's phone number
        **kwargs: Additional optional parameters
    
    Returns:
        A quote object with pricing and estimated times
    """
    try:
        data = {
            "external_delivery_id": external_delivery_id,
            "dropoff_address": dropoff_address,
            "dropoff_phone_number": dropoff_phone_number,
            **kwargs
        }
        return doordash_service.create_quote(data)
    except Exception as e:
        raise ValueError(str(e))

@mcp_server.tool()
def accept_quote(external_delivery_id: str, **kwargs) -> Dict[str, Any]:
    """
    Accept a delivery quote from DoorDash.
    
    Args:
        external_delivery_id: Your unique identifier for the delivery
        **kwargs: Additional optional parameters
    
    Returns:
        A delivery object with tracking information
    """
    try:
        data = {
            "external_delivery_id": external_delivery_id,
            **kwargs
        }
        return doordash_service.accept_quote(data)
    except Exception as e:
        raise ValueError(str(e))

@mcp_server.tool()
def create_delivery(external_delivery_id: str, dropoff_address: str, dropoff_phone_number: str, pickup_address: str, **kwargs) -> Dict[str, Any]:
    """
    Create a delivery with DoorDash.
    
    Args:
        external_delivery_id: Your unique identifier for the delivery
        dropoff_address: The delivery destination address
        dropoff_phone_number: The recipient's phone number
        pickup_address: The pickup location address
        **kwargs: Additional optional parameters
    
    Returns:
        A delivery object with tracking information
    """
    try:
        data = {
            "external_delivery_id": external_delivery_id,
            "dropoff_address": dropoff_address,
            "dropoff_phone_number": dropoff_phone_number,
            "pickup_address": pickup_address,
            "pickup_external_store_id": "joes-pizza-sf-001",
            "pickup_external_business_id": "bryans-business-001",
            **kwargs
        }
        return doordash_service.create_delivery(data)
    except Exception as e:
        raise ValueError(str(e))

@mcp_server.tool()
def get_delivery(external_delivery_id: str) -> Dict[str, Any]:
    """
    Get delivery details from DoorDash.
    
    Args:
        external_delivery_id: Your unique identifier for the delivery
    
    Returns:
        The current status and details of the delivery
    """
    try:
        data = {
            "external_delivery_id": external_delivery_id
        }
        return doordash_service.get_delivery(data)
    except Exception as e:
        raise ValueError(str(e))

@mcp_server.tool()
def update_delivery(external_delivery_id: str, **kwargs) -> Dict[str, Any]:
    """
    Update delivery details in DoorDash.
    
    Args:
        external_delivery_id: Your unique identifier for the delivery
        **kwargs: Fields to update (e.g., dropoff_instructions)
    
    Returns:
        The updated delivery object
    """
    try:
        data = {
            "external_delivery_id": external_delivery_id,
            **kwargs
        }
        return doordash_service.update_delivery(data)
    except Exception as e:
        raise ValueError(str(e))

@mcp_server.tool()
def cancel_delivery(external_delivery_id: str) -> Dict[str, Any]:
    """
    Cancel a delivery in DoorDash.
    
    Args:
        external_delivery_id: Your unique identifier for the delivery
    
    Returns:
        Confirmation of cancellation
    """
    try:
        data = {
            "external_delivery_id": external_delivery_id
        }
        return doordash_service.cancel_delivery(data)
    except Exception as e:
        raise ValueError(str(e))

# Business management MCP tools
@mcp_server.tool()
def create_business(external_business_id: str, name: str, **kwargs) -> Dict[str, Any]:
    """
    Create a business in DoorDash.
    
    Args:
        external_business_id: Unique identifier for the business
        name: The name of the business
        **kwargs: Additional optional parameters (description, external_metadata)
    
    Returns:
        The created business object
    """
    try:
        data = {
            "external_business_id": external_business_id,
            "name": name,
            **kwargs
        }
        return doordash_service.create_business(data)
    except Exception as e:
        raise ValueError(str(e))

@mcp_server.tool()
def get_business(external_business_id: str) -> Dict[str, Any]:
    """
    Get details of a business from DoorDash.
    
    Args:
        external_business_id: Unique identifier for the business
    
    Returns:
        The business details
    """
    try:
        data = {
            "external_business_id": external_business_id
        }
        return doordash_service.get_business(data)
    except Exception as e:
        raise ValueError(str(e))

@mcp_server.tool()
def update_business(external_business_id: str, **kwargs) -> Dict[str, Any]:
    """
    Update business details in DoorDash.
    
    Args:
        external_business_id: Unique identifier for the business
        **kwargs: Fields to update (name, description, external_metadata)
    
    Returns:
        The updated business object
    """
    try:
        data = {
            "external_business_id": external_business_id,
            **kwargs
        }
        return doordash_service.update_business(data)
    except Exception as e:
        raise ValueError(str(e))

@mcp_server.tool()
def list_businesses(**kwargs) -> Dict[str, Any]:
    """
    List businesses in DoorDash.
    
    Args:
        **kwargs: Optional filter parameters (activationStatus, continuationToken)
    
    Returns:
        List of businesses
    """
    try:
        return doordash_service.list_businesses(kwargs if kwargs else None)
    except Exception as e:
        raise ValueError(str(e))

# Store management MCP tools
@mcp_server.tool()
def create_store(external_business_id: str, external_store_id: str, name: str, address: str, **kwargs) -> Dict[str, Any]:
    """
    Create a store in DoorDash.
    
    Args:
        external_business_id: Unique identifier for the business
        external_store_id: Unique identifier for the store
        name: The name of the store
        address: The full address of the store
        **kwargs: Additional optional parameters (phone_number)
    
    Returns:
        The created store object
    """
    try:
        data = {
            "external_business_id": external_business_id,
            "external_store_id": external_store_id,
            "name": name,
            "address": address,
            **kwargs
        }
        return doordash_service.create_store(data)
    except Exception as e:
        raise ValueError(str(e))

@mcp_server.tool()
def get_store(external_business_id: str, external_store_id: str) -> Dict[str, Any]:
    """
    Get details of a store from DoorDash.
    
    Args:
        external_business_id: Unique identifier for the business
        external_store_id: Unique identifier for the store
    
    Returns:
        The store details
    """
    try:
        data = {
            "external_business_id": external_business_id,
            "external_store_id": external_store_id
        }
        return doordash_service.get_store(data)
    except Exception as e:
        raise ValueError(str(e))

@mcp_server.tool()
def update_store(external_business_id: str, external_store_id: str, **kwargs) -> Dict[str, Any]:
    """
    Update store details in DoorDash.
    
    Args:
        external_business_id: Unique identifier for the business
        external_store_id: Unique identifier for the store
        **kwargs: Fields to update (name, address, phone_number)
    
    Returns:
        The updated store object
    """
    try:
        data = {
            "external_business_id": external_business_id,
            "external_store_id": external_store_id,
            **kwargs
        }
        return doordash_service.update_store(data)
    except Exception as e:
        raise ValueError(str(e))

@mcp_server.tool()
def list_stores(external_business_id: str, **kwargs) -> Dict[str, Any]:
    """
    List stores for a business in DoorDash.
    
    Args:
        external_business_id: Unique identifier for the business
        **kwargs: Optional filter parameters (activationStatus, continuationToken)
    
    Returns:
        List of stores
    """
    try:
        data = {
            "external_business_id": external_business_id,
            **kwargs
        }
        return doordash_service.list_stores(data)
    except Exception as e:
        raise ValueError(str(e))

# REST API endpoints that mirror the MCP tools
@router.post("/create_quote")
async def api_create_quote(data: Dict[str, Any]):
    try:
        return doordash_service.create_quote(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/accept_quote")
async def api_accept_quote(data: Dict[str, Any]):
    try:
        return doordash_service.accept_quote(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/create_delivery")
async def api_create_delivery(data: Dict[str, Any]):
    try:
        return doordash_service.create_delivery(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/delivery/{external_delivery_id}")
async def api_get_delivery(external_delivery_id: str):
    try:
        data = {"external_delivery_id": external_delivery_id}
        return doordash_service.get_delivery(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/delivery/{external_delivery_id}")
async def api_update_delivery(external_delivery_id: str, data: Dict[str, Any]):
    try:
        data["external_delivery_id"] = external_delivery_id
        return doordash_service.update_delivery(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/delivery/{external_delivery_id}")
async def api_cancel_delivery(external_delivery_id: str):
    try:
        data = {"external_delivery_id": external_delivery_id}
        return doordash_service.cancel_delivery(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Business and Store REST API endpoints
@router.post("/businesses", response_model=BusinessResponse)
async def api_create_business(business: BusinessCreate):
    try:
        return doordash_service.create_business(business.dict(exclude_none=True))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/businesses/{external_business_id}", response_model=BusinessResponse)
async def api_get_business(external_business_id: str = Path(..., regex=r"^[A-Za-z0-9_-]{3,64}$")):
    try:
        data = {"external_business_id": external_business_id}
        return doordash_service.get_business(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/businesses/{external_business_id}", response_model=BusinessResponse)
async def api_update_business(
    data: BusinessUpdate, 
    external_business_id: str = Path(..., regex=r"^[A-Za-z0-9_-]{3,64}$")
):
    try:
        data_dict = data.dict(exclude_none=True)
        data_dict["external_business_id"] = external_business_id
        return doordash_service.update_business(data_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/businesses", response_model=BusinessListResponse)
async def api_list_businesses(
    activation_status: Optional[str] = Query(None, regex=r"^(active|inactive)$"),
    continuation_token: Optional[str] = Query(None)
):
    try:
        params = {}
        if activation_status:
            params["activationStatus"] = activation_status
        if continuation_token:
            params["continuationToken"] = continuation_token
        return doordash_service.list_businesses(params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/businesses/{external_business_id}/stores", response_model=StoreResponse)
async def api_create_store(
    store: StoreCreate,
    external_business_id: str = Path(..., regex=r"^[A-Za-z0-9_-]{3,64}$")
):
    try:
        store_dict = store.dict(exclude_none=True)
        # Ensure external_business_id in path is used
        store_dict["external_business_id"] = external_business_id
        return doordash_service.create_store(store_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/businesses/{external_business_id}/stores/{external_store_id}", response_model=StoreResponse)
async def api_get_store(
    external_business_id: str = Path(..., regex=r"^[A-Za-z0-9_-]{3,64}$"),
    external_store_id: str = Path(..., regex=r"^[A-Za-z0-9_-]{3,64}$")
):
    try:
        data = {
            "external_business_id": external_business_id,
            "external_store_id": external_store_id
        }
        return doordash_service.get_store(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/businesses/{external_business_id}/stores/{external_store_id}", response_model=StoreResponse)
async def api_update_store(
    data: StoreUpdate,
    external_business_id: str = Path(..., regex=r"^[A-Za-z0-9_-]{3,64}$"),
    external_store_id: str = Path(..., regex=r"^[A-Za-z0-9_-]{3,64}$")
):
    try:
        data_dict = data.dict(exclude_none=True)
        # Ensure IDs in path are used
        data_dict["external_business_id"] = external_business_id
        data_dict["external_store_id"] = external_store_id
        return doordash_service.update_store(data_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/businesses/{external_business_id}/stores", response_model=StoreListResponse)
async def api_list_stores(
    external_business_id: str = Path(..., regex=r"^[A-Za-z0-9_-]{3,64}$"),
    activation_status: Optional[str] = Query(None, regex=r"^(active|inactive)$"),
    continuation_token: Optional[str] = Query(None)
):
    try:
        params = {"external_business_id": external_business_id}
        if activation_status:
            params["activationStatus"] = activation_status
        if continuation_token:
            params["continuationToken"] = continuation_token
        return doordash_service.list_stores(params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 