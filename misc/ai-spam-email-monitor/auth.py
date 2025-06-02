#!/usr/bin/env python3
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the scopes needed for Gmail API access
# gmail.modify - Allows reading and modifying emails (marking as read, labeling)
# gmail.send - Allows sending emails
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

def authenticate(credentials_path='credentials.json', token_path='token.json'):
    """
    Authenticate with Gmail API using OAuth2
    This function is used if you need to set up authentication from scratch
    """
    creds = None
    
    # Check if token file exists
    if os.path.exists(token_path):
        with open(token_path, 'r') as token:
            creds = Credentials.from_authorized_user_info(json.load(token), SCOPES)
    
    # If credentials don't exist or are invalid, go through auth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_gmail_service(credentials_path='credentials.json', token_path='token.json'):
    """
    Creates and returns an authenticated Gmail API service
    """
    creds = authenticate(credentials_path, token_path)
    service = build('gmail', 'v1', credentials=creds)
    return service

def sign_out(token_path='token.json'):
    """
    Signs out the user by removing the token file
    """
    if os.path.exists(token_path):
        try:
            os.remove(token_path)
            return True, f"Successfully signed out. Token file '{token_path}' has been removed."
        except Exception as e:
            return False, f"Error signing out: {str(e)}"
    else:
        return False, f"Not signed in. Token file '{token_path}' does not exist."

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--signout":
        success, message = sign_out()
        print(message)
    else:
        # Running this file directly will test authentication
        print("Testing Gmail API authentication...")
        service = get_gmail_service()
        print("Authentication successful!") 