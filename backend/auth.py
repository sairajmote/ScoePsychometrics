"""
Authentication module for Google Identity Services.
Handles verification of Google ID tokens on the server side using the google-auth library.
"""
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# The Google Client ID for the SCOE_Psychometric project.
# This ID must match the one used in the frontend and registered in Google Cloud Console.
GOOGLE_CLIENT_ID = "363945290379-gogiov7n9mkc8pjqcmq0gapalrasesfg.apps.googleusercontent.com"

def verify_google_token(token: str):
    """
    Verifies a Google ID token received from the frontend.
    Returns the user's name and email if the token is valid, or None if verification fails.
    """
    try:
        # Specify the GOOGLE_CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        # userid = idinfo['sub']
        return idinfo
    except ValueError:
        # Invalid token
        return None
