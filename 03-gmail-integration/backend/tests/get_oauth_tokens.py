"""
OAuth Token Generator

Script to obtain OAuth tokens for Gmail API access.
"""
from google_auth_oauthlib.flow import InstalledAppFlow
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.oauth_config import get_client_config, DEFAULT_SCOPES

def get_oauth_tokens():
    """Get OAuth tokens through the authorization flow"""
    # Get client configuration from config
    client_config = get_client_config()
    
    # Create flow instance
    flow = InstalledAppFlow.from_client_config(
        client_config, DEFAULT_SCOPES
    )
    
    # Force consent screen to get refresh token
    flow.oauth2session.params['prompt'] = 'consent'
    
    # Run the OAuth flow
    for port in [8000, 8080, 8888, 9000]:
        try:
            print(f"Trying port {port}...")
            credentials = flow.run_local_server(port=port)
            break
        except OSError:
            print(f"Port {port} is in use, trying another port...")
            if port == 9000:
                raise Exception("All ports are in use. Please try again later.")
    
    print("\nOAuth Tokens:")
    print(f"Access token: {credentials.token}")
    print(f"Refresh token: {credentials.refresh_token}")
    
    return credentials

if __name__ == "__main__":
    print("Starting OAuth flow to get Gmail API tokens...")
    print("This will open a browser window for you to authorize the application.")
    get_oauth_tokens()