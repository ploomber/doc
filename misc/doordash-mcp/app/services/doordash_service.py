import os
import json
import requests
import jwt
import math
import time
from typing import Dict, Any, Optional
from datetime import datetime

class DoordashService:
    """
    Service class to interact with DoorDash APIs.
    This implementation uses the actual DoorDash Drive API.
    """
    
    def __init__(self):
        self.base_url = os.getenv("DOORDASH_API_URL", "https://openapi.doordash.com/drive/v2")
        self.developer_base_url = os.getenv("DOORDASH_DEVELOPER_API_URL", "https://openapi.doordash.com/developer/v1")
        
        # Try to load credentials from separate environment variables
        developer_id = os.getenv("DOORDASH_DEVELOPER_ID")
        key_id = os.getenv("DOORDASH_KEY_ID")
        signing_secret = os.getenv("DOORDASH_SIGNING_SECRET")
        
        # If separate env vars are provided, use them
        if developer_id and key_id and signing_secret:
            self.access_key = {
                "developer_id": developer_id,
                "key_id": key_id,
                "signing_secret": signing_secret
            }
            print("Using DoorDash credentials from individual environment variables")
        else:
            # Fall back to the combined JSON access key
            self.access_key_str = os.getenv("DOORDASH_ACCESS_KEY", "{}")
            try:
                self.access_key = json.loads(self.access_key_str)
                print("Using DoorDash credentials from DOORDASH_ACCESS_KEY")
            except json.JSONDecodeError:
                self.access_key = {}
                print("Warning: Invalid DOORDASH_ACCESS_KEY format")
    
    def _generate_jwt(self) -> str:
        """
        Generate a JSON Web Token (JWT) for API authentication.
        """
        if not all(key in self.access_key for key in ["developer_id", "key_id", "signing_secret"]):
            raise ValueError("Missing required access key fields")
        
        # Create the JWT payload
        data = {
            "aud": "doordash",
            "iss": self.access_key["developer_id"],
            "kid": self.access_key["key_id"],
            "exp": math.floor(time.time() + 300),  # 5 minutes expiration
            "iat": math.floor(time.time()),
        }
        
        # Create the JWT with the required headers
        headers = {"algorithm": "HS256", "header": {"dd-ver": "DD-JWT-V1"}}
        
        # Sign the JWT
        token = jwt.encode(
            data,
            jwt.utils.base64url_decode(self.access_key["signing_secret"]),
            algorithm="HS256",
            headers={"dd-ver": "DD-JWT-V1"}
        )
        
        return token
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, use_developer_api: bool = False) -> Dict[str, Any]:
        """
        Make an HTTP request to the DoorDash API.
        """
        # Generate a JWT for authentication
        try:
            token = self._generate_jwt()
        except ValueError as e:
            print(f"Error generating JWT: {str(e)}")
            return {"error": "Authentication error", "details": str(e)}
        
        # Set up headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Construct URL - use developer API for business/store operations
        base = self.developer_base_url if use_developer_api else self.base_url
        url = f"{base}/{endpoint}"
        
        # Make the request
        try:
            if method.lower() == "get":
                response = requests.get(url, headers=headers)
            elif method.lower() == "post":
                response = requests.post(url, headers=headers, json=data)
            elif method.lower() == "put":
                response = requests.put(url, headers=headers, json=data)
            elif method.lower() == "patch":
                response = requests.patch(url, headers=headers, data=data)
            elif method.lower() == "delete":
                response = requests.delete(url, headers=headers)
            else:
                return {"error": "Unsupported HTTP method"}
            
            # Handle response
            if response.status_code >= 200 and response.status_code < 300:
                return response.json()
            else:
                print(f"API error: {response.status_code} - {response.text}")
                return {
                    "error": f"API error: {response.status_code}",
                    "details": response.text
                }
                
        except requests.RequestException as e:
            print(f"Request error: {str(e)}")
            return {"error": "Request failed", "details": str(e)}
    
    def create_quote(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a delivery quote from DoorDash.
        """
        # Validate required parameters
        required_fields = ["external_delivery_id", "dropoff_address", "dropoff_phone_number"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Make the request
        return self._make_request("POST", "quotes", data)
    
    def accept_quote(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accept a delivery quote from DoorDash.
        """
        # Validate required parameters
        if "external_delivery_id" not in data:
            raise ValueError("Missing required field: external_delivery_id")
            
        # The API expects the quote_id in the URL. This should be provided by the client.
        if "quote_id" not in data:
            raise ValueError("Missing required field: quote_id")
            
        quote_id = data["quote_id"]
        # Remove quote_id from the payload since it's part of the URL
        payload = {k: v for k, v in data.items() if k != "quote_id"}
        
        # Make the request
        return self._make_request("POST", f"quotes/{quote_id}/accept", payload)
    
    def create_delivery(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a delivery with DoorDash.
        """
        # Validate required parameters
        required_fields = ["external_delivery_id", "dropoff_address", "dropoff_phone_number"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Make the request
        return self._make_request("POST", "deliveries", data)
    
    def get_delivery(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get delivery details from DoorDash.
        """
        # Validate required parameters
        if "external_delivery_id" not in data:
            raise ValueError("Missing required field: external_delivery_id")
        
        external_id = data["external_delivery_id"]
        
        # Make the request
        return self._make_request("GET", f"deliveries/{external_id}", None)
    
    def update_delivery(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update delivery details in DoorDash.
        """
        # Validate required parameters
        if "external_delivery_id" not in data:
            raise ValueError("Missing required field: external_delivery_id")
        
        external_id = data["external_delivery_id"]
        
        # Make the request
        update_data = {k: v for k, v in data.items() if k != "external_delivery_id"}
        return self._make_request("PATCH", f"deliveries/{external_id}", update_data)
    
    def cancel_delivery(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cancel a delivery in DoorDash.
        """
        # Validate required parameters
        if "external_delivery_id" not in data:
            raise ValueError("Missing required field: external_delivery_id")
        
        external_id = data["external_delivery_id"]
        
        # Make the request
        return self._make_request("PUT", f"deliveries/{external_id}/cancel", None)
        
    # Business and Store Management Methods
    
    def create_business(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a business in DoorDash.
        """
        # Validate required parameters
        required_fields = ["external_business_id", "name"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Make the request
        return self._make_request("POST", "businesses", data, use_developer_api=True)
    
    def get_business(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get details of a business from DoorDash.
        """
        # Validate required parameters
        if "external_business_id" not in data:
            raise ValueError("Missing required field: external_business_id")
        
        external_business_id = data["external_business_id"]
        
        # Make the request
        return self._make_request("GET", f"businesses/{external_business_id}", None, use_developer_api=True)
    
    def update_business(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update business details in DoorDash.
        """
        # Validate required parameters
        if "external_business_id" not in data:
            raise ValueError("Missing required field: external_business_id")
        
        external_business_id = data["external_business_id"]
        
        # Remove external_business_id from the payload since it's part of the URL
        update_data = {k: v for k, v in data.items() if k != "external_business_id"}
        
        # Make the request
        return self._make_request("PATCH", f"businesses/{external_business_id}", update_data, use_developer_api=True)
    
    def list_businesses(self, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        List businesses in DoorDash.
        """
        # Make the request
        return self._make_request("GET", "businesses", data, use_developer_api=True)
    
    def create_store(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a store in DoorDash.
        """
        # Validate required parameters
        required_fields = ["external_business_id", "external_store_id", "name", "address"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        external_business_id = data["external_business_id"]
        
        # Remove external_business_id from the payload since it's part of the URL
        store_data = {k: v for k, v in data.items() if k != "external_business_id"}
        
        # Make the request
        return self._make_request("POST", f"businesses/{external_business_id}/stores", store_data, use_developer_api=True)
    
    def get_store(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get details of a store from DoorDash.
        """
        # Validate required parameters
        required_fields = ["external_business_id", "external_store_id"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        external_business_id = data["external_business_id"]
        external_store_id = data["external_store_id"]
        
        # Make the request
        return self._make_request("GET", f"businesses/{external_business_id}/stores/{external_store_id}", None, use_developer_api=True)
    
    def update_store(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update store details in DoorDash.
        """
        # Validate required parameters
        required_fields = ["external_business_id", "external_store_id"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        external_business_id = data["external_business_id"]
        external_store_id = data["external_store_id"]
        
        # Remove IDs from the payload since they're part of the URL
        update_data = {k: v for k, v in data.items() if k not in ["external_business_id", "external_store_id"]}
        
        # Make the request
        return self._make_request("PATCH", f"businesses/{external_business_id}/stores/{external_store_id}", update_data, use_developer_api=True)
    
    def list_stores(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        List stores for a business in DoorDash.
        """
        # Validate required parameters
        if "external_business_id" not in data:
            raise ValueError("Missing required field: external_business_id")
        
        external_business_id = data["external_business_id"]
        
        # Extract query parameters
        query_params = {k: v for k, v in data.items() if k in ["activationStatus", "continuationToken"]}
        
        # Make the request
        return self._make_request("GET", f"businesses/{external_business_id}/stores", query_params, use_developer_api=True) 