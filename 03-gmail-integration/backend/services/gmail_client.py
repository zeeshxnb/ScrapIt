"""
Gmail API Client Wrapper

Wrapper class for Gmail API with rate limiting and error handling
"""
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import time
import logging
from typing import List, Dict, Optional, Any
from functools import wraps
import backoff

from ..config.oauth_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_TOKEN_URI, DEFAULT_SCOPES

logger = logging.getLogger(__name__)

def retry_on_rate_limit(max_tries: int = 3):
    """Decorator for retrying API calls with exponential backoff"""
    def decorator(func):
        @wraps(func)
        @backoff.on_exception(
            backoff.expo,
            HttpError,
            max_tries=max_tries,
            giveup=lambda e: e.resp.status != 429
        )
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

class GmailClient:
    """Gmail API client with rate limiting and error handling"""
    
    # API configuration
    API_SERVICE_NAME = 'gmail'
    API_VERSION = 'v1'
    BATCH_SIZE = 100
    
    def __init__(self, access_token: str, refresh_token: str, user_id: str):
        """
        Initialize Gmail client
        
        Args:
            access_token: OAuth access token
            refresh_token: OAuth refresh token  
            user_id: User identifier for logging
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.service = None
        self.credentials = None
        self._quota_usage = 0
        
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API
        
        Returns:
            True if authentication successful
        """
        try:
            # Create credentials object
            self.credentials = Credentials(
                token=self.access_token,
                refresh_token=self.refresh_token,
                token_uri=GOOGLE_TOKEN_URI,
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                scopes=DEFAULT_SCOPES
            )
            
            # Build Gmail service
            self._build_service()
            
            # Test connection by getting user profile
            profile = self.service.users().getProfile(userId='me').execute()
            
            logger.info(f"Successfully authenticated Gmail for user: {profile.get('emailAddress')}")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False
    
    def refresh_token_if_needed(self) -> bool:
        """
        Refresh access token if expired
        
        Returns:
            True if token refresh successful or not needed
        """
        if not self.credentials:
            logger.error("No credentials to refresh")
            return False
            
        try:
            # Check if token is expired and refresh if needed
            if self.credentials.expired:
                logger.info("Access token expired, refreshing...")
                self.credentials.refresh(Request())
                
                # Rebuild service with new credentials
                self._build_service()
                logger.info("Token refreshed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return False
    
    @retry_on_rate_limit(max_tries=3)
    def list_messages(self, query: str = None, max_results: int = 100, 
                     page_token: str = None) -> Dict[str, Any]:
        """
        List Gmail messages with optional query
        
        Args:
            query: Gmail search query
            max_results: Maximum number of results
            page_token: Token for pagination
            
        Returns:
            Dictionary with messages and nextPageToken
        """
        try:
            # Ensure we have a valid service
            if not self.service:
                self.authenticate()
                
            # Build request parameters
            params = {
                'userId': 'me',
                'maxResults': min(max_results, self.BATCH_SIZE)  # Limit to batch size
            }
            
            if query:
                params['q'] = query
                
            if page_token:
                params['pageToken'] = page_token
                
            # Execute API call
            self._track_quota_usage('list_messages')
            response = self.service.users().messages().list(**params).execute()
            
            # Return results with metadata
            result = {
                'messages': response.get('messages', []),
                'nextPageToken': response.get('nextPageToken'),
                'resultSizeEstimate': response.get('resultSizeEstimate', 0)
            }
            
            logger.debug(f"Listed {len(result['messages'])} messages")
            return result
            
        except HttpError as error:
            self._handle_api_error(error)
            raise
    
    @retry_on_rate_limit(max_tries=3)
    def get_message(self, message_id: str, format: str = 'full') -> Dict[str, Any]:
        """
        Get single Gmail message by ID
        
        Args:
            message_id: Gmail message ID
            format: Message format (full, metadata, minimal)
            
        Returns:
            Gmail message object
        """
        try:
            # Ensure we have a valid service
            if not self.service:
                self.authenticate()
                
            # Execute API call
            self._track_quota_usage('get_message')
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format=format
            ).execute()
            
            # Parse message data into standardized format
            parsed_message = self._parse_message_data(message)
            
            logger.debug(f"Retrieved message {message_id}")
            return parsed_message
            
        except HttpError as error:
            self._handle_api_error(error)
            raise
    
    def get_messages_batch(self, message_ids: List[str], 
                          format: str = 'full') -> List[Dict[str, Any]]:
        """
        Get multiple Gmail messages using batch API
        
        Args:
            message_ids: List of Gmail message IDs
            format: Message format
            
        Returns:
            List of Gmail message objects
        """
        if not message_ids:
            return []
            
        # Ensure we have a valid service
        if not self.service:
            self.authenticate()
            
        results = []
        
        # Process in batches to avoid API limits
        for i in range(0, len(message_ids), self.BATCH_SIZE):
            batch = message_ids[i:i+self.BATCH_SIZE]
            logger.debug(f"Processing batch of {len(batch)} messages")
            
            # Process each message in the batch
            batch_results = []
            for msg_id in batch:
                try:
                    message = self.get_message(msg_id, format)
                    batch_results.append(message)
                except HttpError as e:
                    logger.warning(f"Failed to get message {msg_id}: {str(e)}")
                    continue
                    
            results.extend(batch_results)
            
            # Add a small delay between batches to avoid rate limits
            if i + self.BATCH_SIZE < len(message_ids):
                time.sleep(0.5)
                
        logger.info(f"Retrieved {len(results)} of {len(message_ids)} messages in batch")
        return results
    
    @retry_on_rate_limit(max_tries=3)
    def search_messages(self, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Search Gmail messages with query
        
        Args:
            query: Gmail search query
            max_results: Maximum results to return
            
        Returns:
            List of matching message objects
        """
        # TODO: Implement message search
        # Execute search query
        # Handle pagination for large results
        # Return all matching messages
        pass
    
    @retry_on_rate_limit(max_tries=3)
    def get_labels(self) -> List[Dict[str, Any]]:
        """
        Get Gmail labels for user
        
        Returns:
            List of Gmail label objects
        """
        # TODO: Implement label retrieval
        # Execute API call
        # Return label data
        pass
    
    @retry_on_rate_limit(max_tries=3)
    def modify_message(self, message_id: str, add_labels: List[str] = None, 
                      remove_labels: List[str] = None) -> bool:
        """
        Modify Gmail message labels
        
        Args:
            message_id: Gmail message ID
            add_labels: Labels to add
            remove_labels: Labels to remove
            
        Returns:
            True if modification successful
        """
        # TODO: Implement message modification
        # Build modification request
        # Execute API call
        # Return success status
        pass
    
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get Gmail user profile information
        
        Returns:
            User profile data
        """
        # TODO: Implement profile retrieval
        # Execute API call
        # Return profile data
        pass
    
    def _build_service(self) -> None:
        """Build Gmail API service object"""
        if not self.credentials:
            raise ValueError("Credentials not initialized. Call authenticate() first.")
            
        # Build service with credentials
        self.service = build(
            self.API_SERVICE_NAME,
            self.API_VERSION,
            credentials=self.credentials,
            cache_discovery=False
        )
        logger.debug("Gmail API service built successfully")
    
    def _handle_api_error(self, error: HttpError) -> None:
        """Handle Gmail API errors"""
        status_code = error.resp.status
        error_message = error.content.decode('utf-8') if error.content else "Unknown error"
        
        logger.error(f"Gmail API error: {status_code} - {error_message}")
        
        # Handle specific error codes
        if status_code == 401:
            logger.warning("Authentication error - token may be expired")
            # Try to refresh the token
            self.refresh_token_if_needed()
        elif status_code == 403:
            logger.warning("Permission denied or quota exceeded")
        elif status_code == 404:
            logger.warning("Resource not found")
        elif status_code == 429:
            logger.warning("Rate limit exceeded - backing off")
            # Backoff is handled by the retry decorator
        elif status_code >= 500:
            logger.warning("Gmail API server error")
    
    def _track_quota_usage(self, operation: str) -> None:
        """Track API quota usage for monitoring"""
        self._quota_usage += 1
        if self._quota_usage % 100 == 0:
            logger.info(f"Gmail API quota usage: {self._quota_usage} operations")
        logger.debug(f"Gmail API operation: {operation}")
    
    def _parse_message_data(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail message data into standardized format"""
        result = {
            'id': message.get('id'),
            'thread_id': message.get('threadId'),
            'label_ids': message.get('labelIds', []),
            'snippet': message.get('snippet', ''),
            'internal_date': message.get('internalDate'),
            'headers': {},
            'body': {
                'plain': '',
                'html': ''
            },
            'attachments': []
        }
        
        # Extract headers
        headers = {}
        if 'payload' in message and 'headers' in message['payload']:
            for header in message['payload']['headers']:
                name = header.get('name', '').lower()
                value = header.get('value', '')
                headers[name] = value
                
                # Extract common headers to top level
                if name == 'subject':
                    result['subject'] = value
                elif name == 'from':
                    result['from'] = value
                elif name == 'to':
                    result['to'] = value
                elif name == 'date':
                    result['date'] = value
        
        result['headers'] = headers
        
        # Extract body content
        if 'payload' in message:
            self._extract_body_parts(message['payload'], result)
            
        return result
        
    def _extract_body_parts(self, payload: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Helper method to extract body parts recursively"""
        if 'body' in payload:
            body_data = payload['body']
            mime_type = payload.get('mimeType', '')
            
            # Handle simple body part
            if 'data' in body_data:
                import base64
                data = base64.urlsafe_b64decode(body_data['data']).decode('utf-8', errors='replace')
                
                if 'text/plain' in mime_type:
                    result['body']['plain'] = data
                elif 'text/html' in mime_type:
                    result['body']['html'] = data
            
            # Handle attachment
            if 'attachmentId' in body_data:
                result['attachments'].append({
                    'id': body_data['attachmentId'],
                    'filename': payload.get('filename', ''),
                    'mime_type': mime_type,
                    'size': body_data.get('size', 0)
                })
        
        # Process nested parts recursively
        if 'parts' in payload:
            for part in payload['parts']:
                self._extract_body_parts(part, result)