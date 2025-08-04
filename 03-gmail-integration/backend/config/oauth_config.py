"""
OAuth Configuration

Configuration for Google OAuth authentication.
"""
import os

# OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get(
    "GOOGLE_CLIENT_ID", 
    "656777491355-7mlqhc5eeaureoi6sbp37hjhn467kv15.apps.googleusercontent.com"
)
GOOGLE_CLIENT_SECRET = os.environ.get(
    "GOOGLE_CLIENT_SECRET", 
    "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"
)
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_AUTH_PROVIDER_CERT_URL = "https://www.googleapis.com/oauth2/v1/certs"

# Redirect URIs for OAuth flow
REDIRECT_URIS = [
    "http://localhost:8000/",
    "http://localhost:8080/",
    "http://localhost:8888/",
    "http://localhost:9000/"
]

# Scopes
GMAIL_READ_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
GMAIL_MODIFY_SCOPE = "https://www.googleapis.com/auth/gmail.modify"

# Default scopes
DEFAULT_SCOPES = [GMAIL_READ_SCOPE, GMAIL_MODIFY_SCOPE]

# Client configuration for OAuth flow
def get_client_config():
    """Get OAuth client configuration"""
    return {
        "installed": {
            "client_id": GOOGLE_CLIENT_ID,
            "project_id": "vertical-planet-467620-k9",
            "auth_uri": GOOGLE_AUTH_URI,
            "token_uri": GOOGLE_TOKEN_URI,
            "auth_provider_x509_cert_url": GOOGLE_AUTH_PROVIDER_CERT_URL,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uris": REDIRECT_URIS
        }
    }