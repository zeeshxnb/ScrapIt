"""
Simple Gmail API Test

Test script to verify Gmail API connectivity.
"""
import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.oauth_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_TOKEN_URI, GMAIL_READ_SCOPE, get_client_config

def test_gmail_connection():
    """Test connection to Gmail API"""
    print("Gmail API Connection Test")
    print("========================\n")
    
    # Get credentials from user input
    print("Please enter your OAuth credentials:")
    access_token = input("Access Token: ")
    refresh_token = input("Refresh Token: ")
    
    # Create credentials object
    credentials = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=GOOGLE_TOKEN_URI,
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=[GMAIL_READ_SCOPE]
    )
    
    try:
        # Build the Gmail API service
        print("\nConnecting to Gmail API...")
        service = build('gmail', 'v1', credentials=credentials)
        
        # Test connection by getting user profile
        print("Fetching user profile...")
        profile = service.users().getProfile(userId='me').execute()
        print(f"Connected to Gmail API")
        print(f"Email address: {profile['emailAddress']}")
        print(f"Messages total: {profile['messagesTotal']}")
        
        # List a few emails
        print("\nFetching recent emails...")
        results = service.users().messages().list(userId='me', maxResults=3).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("No messages found.")
        else:
            print(f"Found {len(messages)} messages:")
            for i, message in enumerate(messages, 1):
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                headers = msg['payload']['headers']
                subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
                sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown')
                print(f"\nEmail {i}:")
                print(f"  From: {sender}")
                print(f"  Subject: {subject}")
                print(f"  Snippet: {msg['snippet'][:50]}...")
        
        print("\nGmail API connection test successful!")
        return True
        
    except HttpError as error:
        print(f"\nGmail API error: {error}")
        return False
    except Exception as e:
        print(f"\nError: {str(e)}")
        return False

def get_oauth_tokens():
    """Get OAuth tokens"""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        # Use read-only scope for this test
        SCOPES = [GMAIL_READ_SCOPE]
        
        # Get client configuration from config
        client_config = get_client_config()
        
        print("Starting OAuth flow...")
        print("This will open a browser window for you to authorize the application.")
        
        # Create flow instance
        flow = InstalledAppFlow.from_client_config(
            client_config, SCOPES
        )
        
        # Force consent screen to get refresh token
        flow.oauth2session.params['prompt'] = 'consent'
        
        # Run the OAuth flow
        for port in [8000, 8080, 8888, 9000]:
            try:
                credentials = flow.run_local_server(port=port)
                break
            except OSError:
                print(f"Port {port} is in use, trying another port...")
                if port == 9000:
                    raise Exception("All ports are in use. Please close some applications and try again.")
        
        print("\nOAuth Tokens:")
        print(f"Access token: {credentials.token}")
        print(f"Refresh token: {credentials.refresh_token}")
        
        return credentials.token, credentials.refresh_token
        
    except Exception as e:
        print(f"Error during OAuth flow: {str(e)}")
        return None, None

if __name__ == "__main__":
    print("Gmail API Test Script")
    print("====================\n")
    
    choice = input("Do you need to get OAuth tokens first? (y/n): ").lower()
    
    access_token = None
    refresh_token = None
    
    if choice.startswith('y'):
        access_token, refresh_token = get_oauth_tokens()
        if access_token and refresh_token:
            print("Tokens obtained successfully. Proceeding with test...")
            
            # Create credentials object
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri=GOOGLE_TOKEN_URI,
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                scopes=[GMAIL_READ_SCOPE]
            )
            
            try:
                # Build the Gmail API service
                print("\nConnecting to Gmail API...")
                service = build('gmail', 'v1', credentials=credentials)
                
                # Test connection by getting user profile
                print("Fetching user profile...")
                profile = service.users().getProfile(userId='me').execute()
                print(f"Connected to Gmail API")
                print(f"Email address: {profile['emailAddress']}")
                print(f"Messages total: {profile['messagesTotal']}")
                
                # List a few emails
                print("\nFetching recent emails...")
                results = service.users().messages().list(userId='me', maxResults=3).execute()
                messages = results.get('messages', [])
                
                if not messages:
                    print("No messages found.")
                else:
                    print(f"Found {len(messages)} messages:")
                    for i, message in enumerate(messages, 1):
                        msg = service.users().messages().get(userId='me', id=message['id']).execute()
                    
                        headers = msg['payload']['headers']
                        subject = next((header['value'] for header in headers if header['name'].lower() == 'subject'), 'No Subject')
                        sender = next((header['value'] for header in headers if header['name'].lower() == 'from'), 'Unknown')
                        print(f"\nEmail {i}:")
                        print(f"  From: {sender}")
                        print(f"  Subject: {subject}")
                        print(f"  Snippet: {msg['snippet'][:50]}...")
                
                print("\nGmail API connection test successful!")
                
            except Exception as e:
                print(f"\nError: {str(e)}")
        else:
            print("Failed to obtain OAuth tokens. Exiting.")
    else:
        # Run the test directly with user input
        test_gmail_connection()