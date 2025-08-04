"""
OAuth Configuration

Configuration for Google OAuth authentication.
"""
import os
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

def load_dotenv():
    """Load environment variables from .env file"""
    try:
        # Look for .env file in project root or current directory
        env_paths = [
            Path(__file__).parent.parent.parent.parent / '.env',  # Project root
            Path(__file__).parent.parent / '.env',  # Backend root
            Path(__file__).parent / '.env',  # Config directory
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                logger.info(f"Loading environment variables from {env_path}")
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                return True
        return False
    except Exception as e:
        logger.warning(f"Error loading .env file: {e}")
        return False

# Try to load environment variables from .env file
load_dotenv()

# OAuth configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "YOUR_CLIENT_ID_HERE")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "YOUR_CLIENT_SECRET_HERE")
GOOGLE_PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID", "your-project-id-here")

# Log warning for placeholder credentials
if (GOOGLE_CLIENT_ID == "YOUR_CLIENT_ID_HERE" or 
    GOOGLE_CLIENT_SECRET == "YOUR_CLIENT_SECRET_HERE" or
    GOOGLE_PROJECT_ID == "your-project-id-here"):
    logger.warning("Using placeholder OAuth credentials. Authentication will fail.")
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
    # Validate credentials before returning
    validate_credentials()
    
    return {
        "installed": {
            "client_id": GOOGLE_CLIENT_ID,
            "project_id": GOOGLE_PROJECT_ID,
            "auth_uri": GOOGLE_AUTH_URI,
            "token_uri": GOOGLE_TOKEN_URI,
            "auth_provider_x509_cert_url": GOOGLE_AUTH_PROVIDER_CERT_URL,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uris": REDIRECT_URIS
        }
    }

def validate_credentials():
    """Validate OAuth credentials"""
    if (GOOGLE_CLIENT_ID == "YOUR_CLIENT_ID_HERE" or 
        GOOGLE_CLIENT_SECRET == "YOUR_CLIENT_SECRET_HERE" or
        GOOGLE_PROJECT_ID == "your-project-id-here"):
        print("\n" + "="*80)
        print("⚠️  WARNING: Using placeholder OAuth credentials ⚠️")
        print("This will not work for authentication.")
        print("\nPlease set the following environment variables:")
        print("- GOOGLE_CLIENT_ID")
        print("- GOOGLE_CLIENT_SECRET")
        print("- GOOGLE_PROJECT_ID")
        print("\nYou can set these by:")
        print("1. Creating a .env file in the project root")
        print("2. Adding the variables with your actual Google OAuth credentials")
        print("\nExample .env file:")
        print("-----------------")
        print("GOOGLE_CLIENT_ID=your_client_id_here")
        print("GOOGLE_CLIENT_SECRET=your_client_secret_here")
        print("GOOGLE_PROJECT_ID=your-project-id-here")
        print("-----------------")
        print("="*80 + "\n")
        
        # Ask user if they want to continue
        try:
            response = input("Do you want to continue anyway? (y/n): ").lower()
            if response != 'y':
                print("Exiting...")
                sys.exit(1)
        except:
            # In non-interactive environments, just log the warning
            pass