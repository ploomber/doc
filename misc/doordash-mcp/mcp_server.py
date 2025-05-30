#!/usr/bin/env python

# Import required modules
from mcp.server.fastmcp import FastMCP
import os
import sys
import traceback
from app.routers.doordash import doordash_service

# Initialize MCP server
mcp = FastMCP("DoorDash MCP Tools")

# Define MCP tools
@mcp.tool()
def create_quote(external_delivery_id: str, dropoff_address: str, dropoff_phone_number: str, **kwargs):
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
        # Handle the case where kwargs is passed as a string
        processed_kwargs = {}
        if 'kwargs' in kwargs and isinstance(kwargs['kwargs'], str):
            try:
                # Try to parse the kwargs string as JSON
                import json
                parsed_kwargs = json.loads(kwargs['kwargs'].replace('\\', ''))
                processed_kwargs = parsed_kwargs
                # Remove the original kwargs parameter
                del kwargs['kwargs']
            except Exception as e:
                print(f"Error parsing kwargs string: {str(e)}")
        
        # Combine the processed kwargs with any other kwargs
        data = {
            "external_delivery_id": external_delivery_id,
            "dropoff_address": dropoff_address,
            "dropoff_phone_number": dropoff_phone_number,
            **kwargs,
            **processed_kwargs
        }
        return doordash_service.create_quote(data)
    except Exception as e:
        traceback.print_exc()
        raise ValueError(str(e))

@mcp.tool()
def accept_quote(external_delivery_id: str, **kwargs):
    """
    Accept a delivery quote from DoorDash.
    
    Args:
        external_delivery_id: Your unique identifier for the delivery
        **kwargs: Additional optional parameters
    
    Returns:
        A delivery object with tracking information
    """
    try:
        # Handle the case where kwargs is passed as a string
        processed_kwargs = {}
        if 'kwargs' in kwargs and isinstance(kwargs['kwargs'], str):
            try:
                # Try to parse the kwargs string as JSON
                import json
                parsed_kwargs = json.loads(kwargs['kwargs'].replace('\\', ''))
                processed_kwargs = parsed_kwargs
                # Remove the original kwargs parameter
                del kwargs['kwargs']
            except Exception as e:
                print(f"Error parsing kwargs string: {str(e)}")
        
        # Combine the processed kwargs with any other kwargs
        data = {
            "external_delivery_id": external_delivery_id,
            **kwargs,
            **processed_kwargs
        }
        return doordash_service.accept_quote(data)
    except Exception as e:
        traceback.print_exc()
        raise ValueError(str(e))

@mcp.tool()
def create_delivery(external_delivery_id: str, dropoff_address: str, dropoff_phone_number: str, pickup_address: str, **kwargs):
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
        # Handle the case where kwargs is passed as a string
        processed_kwargs = {}
        if 'kwargs' in kwargs and isinstance(kwargs['kwargs'], str):
            try:
                # Try to parse the kwargs string as JSON
                import json
                parsed_kwargs = json.loads(kwargs['kwargs'].replace('\\', ''))
                processed_kwargs = parsed_kwargs
                # Remove the original kwargs parameter
                del kwargs['kwargs']
            except Exception as e:
                print(f"Error parsing kwargs string: {str(e)}")
        
        # Combine the processed kwargs with any other kwargs
        data = {
            "external_delivery_id": external_delivery_id,
            "dropoff_address": dropoff_address,
            "dropoff_phone_number": dropoff_phone_number,
            "pickup_address": pickup_address,
            **kwargs,
            **processed_kwargs
        }
        return doordash_service.create_delivery(data)
    except Exception as e:
        traceback.print_exc()
        raise ValueError(str(e))

@mcp.tool()
def get_delivery(external_delivery_id: str):
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
        traceback.print_exc()
        raise ValueError(str(e))

@mcp.tool()
def update_delivery(external_delivery_id: str, **kwargs):
    """
    Update delivery details in DoorDash.
    
    Args:
        external_delivery_id: Your unique identifier for the delivery
        **kwargs: Fields to update (e.g., dropoff_instructions, 
                 dropoff_phone_number, pickup_instructions, etc.)
    
    Returns:
        The updated delivery object
    """
    try:
        # Handle the case where kwargs is passed as a string
        processed_kwargs = {}
        if 'kwargs' in kwargs and isinstance(kwargs['kwargs'], str):
            try:
                # Try to parse the kwargs string as JSON
                import json
                parsed_kwargs = json.loads(kwargs['kwargs'].replace('\\', ''))
                processed_kwargs = parsed_kwargs
                # Remove the original kwargs parameter
                del kwargs['kwargs']
            except Exception as e:
                print(f"Error parsing kwargs string: {str(e)}")
        
        # Combine the processed kwargs with any other kwargs
        data = {
            "external_delivery_id": external_delivery_id,
            **kwargs,
            **processed_kwargs
        }
        return doordash_service.update_delivery(data)
    except Exception as e:
        traceback.print_exc()
        raise ValueError(str(e))

@mcp.tool()
def cancel_delivery(external_delivery_id: str):
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
        traceback.print_exc()
        raise ValueError(str(e))
    
# Business management MCP tools
@mcp.tool()
def create_business(external_business_id: str, name: str, description: str, **kwargs):
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
        # Handle the case where kwargs is passed as a string
        processed_kwargs = {}
        if 'kwargs' in kwargs and isinstance(kwargs['kwargs'], str):
            try:
                # Try to parse the kwargs string as JSON
                import json
                parsed_kwargs = json.loads(kwargs['kwargs'].replace('\\', ''))
                processed_kwargs = parsed_kwargs
                # Remove the original kwargs parameter
                del kwargs['kwargs']
            except Exception as e:
                print(f"Error parsing kwargs string: {str(e)}")
        
        # Combine the processed kwargs with any other kwargs
        data = {
            "external_business_id": external_business_id,
            "description": description,
            "name": name,
            **kwargs,
            **processed_kwargs
        }
        return doordash_service.create_business(data)
    except Exception as e:
        traceback.print_exc()
        raise ValueError(str(e))

@mcp.tool()
def get_business(external_business_id: str):
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
        traceback.print_exc()
        raise ValueError(str(e))

@mcp.tool()
def update_business(external_business_id: str, **kwargs):
    """
    Update business details in DoorDash.
    
    Args:
        external_business_id: Unique identifier for the business
        **kwargs: Fields to update (name, description, external_metadata)
    
    Returns:
        The updated business object
    """
    try:
        # Handle the case where kwargs is passed as a string
        processed_kwargs = {}
        if 'kwargs' in kwargs and isinstance(kwargs['kwargs'], str):
            try:
                # Try to parse the kwargs string as JSON
                import json
                parsed_kwargs = json.loads(kwargs['kwargs'].replace('\\', ''))
                processed_kwargs = parsed_kwargs
                # Remove the original kwargs parameter
                del kwargs['kwargs']
            except Exception as e:
                print(f"Error parsing kwargs string: {str(e)}")
        
        # Combine the processed kwargs with any other kwargs
        data = {
            "external_business_id": external_business_id,
            **kwargs,
            **processed_kwargs
        }
        return doordash_service.update_business(data)
    except Exception as e:
        traceback.print_exc()
        raise ValueError(str(e))

@mcp.tool()
def list_businesses(**kwargs):
    """
    List businesses in DoorDash.
    
    Args:
        **kwargs: Optional filter parameters (activationStatus, continuationToken)
    
    Returns:
        List of businesses
    """
    try:
        # Handle the case where kwargs is passed as a string
        processed_kwargs = {}
        if 'kwargs' in kwargs and isinstance(kwargs['kwargs'], str):
            try:
                # Try to parse the kwargs string as JSON
                import json
                parsed_kwargs = json.loads(kwargs['kwargs'].replace('\\', ''))
                processed_kwargs = parsed_kwargs
                # Remove the original kwargs parameter
                del kwargs['kwargs']
            except Exception as e:
                print(f"Error parsing kwargs string: {str(e)}")
        
        # Combine the processed kwargs with any other kwargs
        data = {**kwargs, **processed_kwargs}
        return doordash_service.list_businesses(data if data else None)
    except Exception as e:
        traceback.print_exc()
        raise ValueError(str(e))

# Store management MCP tools
@mcp.tool()
def create_store(external_business_id: str, external_store_id: str, name: str, address: str, **kwargs):
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
        # Handle the case where kwargs is passed as a string
        processed_kwargs = {}
        if 'kwargs' in kwargs and isinstance(kwargs['kwargs'], str):
            try:
                # Try to parse the kwargs string as JSON
                import json
                parsed_kwargs = json.loads(kwargs['kwargs'].replace('\\', ''))
                processed_kwargs = parsed_kwargs
                # Remove the original kwargs parameter
                del kwargs['kwargs']
            except Exception as e:
                print(f"Error parsing kwargs string: {str(e)}")
        
        # Combine the processed kwargs with any other kwargs
        data = {
            "external_business_id": external_business_id,
            "external_store_id": external_store_id,
            "name": name,
            "address": address,
            **kwargs,
            **processed_kwargs
        }
        return doordash_service.create_store(data)
    except Exception as e:
        traceback.print_exc()
        raise ValueError(str(e))

@mcp.tool()
def get_store(external_business_id: str, external_store_id: str):
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
        traceback.print_exc()
        raise ValueError(str(e))

@mcp.tool()
def update_store(external_business_id: str, external_store_id: str, **kwargs):
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
        # Handle the case where kwargs is passed as a string
        processed_kwargs = {}
        if 'kwargs' in kwargs and isinstance(kwargs['kwargs'], str):
            try:
                # Try to parse the kwargs string as JSON
                import json
                parsed_kwargs = json.loads(kwargs['kwargs'].replace('\\', ''))
                processed_kwargs = parsed_kwargs
                # Remove the original kwargs parameter
                del kwargs['kwargs']
            except Exception as e:
                print(f"Error parsing kwargs string: {str(e)}")
        
        # Combine the processed kwargs with any other kwargs
        data = {
            "external_business_id": external_business_id,
            "external_store_id": external_store_id,
            **kwargs,
            **processed_kwargs
        }
        return doordash_service.update_store(data)
    except Exception as e:
        traceback.print_exc()
        raise ValueError(str(e))

@mcp.tool()
def list_stores(external_business_id: str, **kwargs):
    """
    List stores for a business in DoorDash.
    
    Args:
        external_business_id: Unique identifier for the business
        **kwargs: Optional filter parameters (activationStatus, continuationToken)
    
    Returns:
        List of stores
    """
    try:
        # Handle the case where kwargs is passed as a string
        processed_kwargs = {}
        if 'kwargs' in kwargs and isinstance(kwargs['kwargs'], str):
            try:
                # Try to parse the kwargs string as JSON
                import json
                parsed_kwargs = json.loads(kwargs['kwargs'].replace('\\', ''))
                processed_kwargs = parsed_kwargs
                # Remove the original kwargs parameter
                del kwargs['kwargs']
            except Exception as e:
                print(f"Error parsing kwargs string: {str(e)}")
        
        # Combine the processed kwargs with any other kwargs
        data = {
            "external_business_id": external_business_id,
            **kwargs,
            **processed_kwargs
        }
        return doordash_service.list_stores(data)
    except Exception as e:
        traceback.print_exc()
        raise ValueError(str(e))

# Run the server
if __name__ == "__main__":
    # Start both the FastAPI and MCP servers
    import uvicorn
    from threading import Thread
    import time
    
    # Start FastAPI server in a separate thread
    fastapi_thread = Thread(
        target=uvicorn.run, 
        args=("app.main:app",),
        kwargs={
            "host": "127.0.0.1",
            "port": 8800,
            "log_level": "info"
        },
        daemon=True
    )
    fastapi_thread.start()
    
    # Allow FastAPI server to start
    time.sleep(2)
    
    # Start MCP server with stdio transport (for Cursor)
    try:
        # Use the run method with stdio transport for MCP
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("Server stopped")
    except Exception as e:
        print(f"Error starting MCP server: {e}")
        traceback.print_exc()
        sys.exit(1) 