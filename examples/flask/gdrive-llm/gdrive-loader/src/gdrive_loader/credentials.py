import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from gdrive_loader.models import User
from sqlalchemy.orm import Session


def get_valid_credentials(user: User, db_session: Session):
    """
    Get valid credentials for the user, refreshing if necessary.

    Parameters
    ----------
    user : User
        User model instance containing token information

    Returns
    -------
    google.oauth2.credentials.Credentials
        Valid credentials object
    """
    token_info = json.loads(user.token_info)

    # Convert expiry string back to datetime
    if token_info["expiry"]:
        token_info["expiry"] = datetime.fromisoformat(token_info["expiry"])

    credentials = Credentials(
        token=token_info["token"],
        refresh_token=token_info["refresh_token"],
        token_uri=token_info["token_uri"],
        client_id=token_info["client_id"],
        client_secret=token_info["client_secret"],
        scopes=token_info["scopes"],
        expiry=token_info["expiry"],
    )

    # Refresh token if expired
    if credentials.expired:
        credentials.refresh(Request())

        # Update stored token info
        token_info.update(
            {"token": credentials.token, "expiry": credentials.expiry.isoformat()}
        )
        user.token_info = json.dumps(token_info)

        db_session.commit()

    return credentials
