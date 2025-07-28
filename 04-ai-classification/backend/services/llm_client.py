"""
LLM API Client

Wrapper for OpenAI and Claude APIs for email classification
"""
import openai
import anthropic
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    CLAUDE = "claude"

@dataclass
class ClassificationResult:
    """Email classification result"""
    category: str
    confidence: float
    reasoning: str
    subcategory: Optional[str] = None
    suggested_actions: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "category": self.category,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "subcategory": self.subcategory,
            "suggested_actions": self.suggested_actions or []
        }

class LLMClient:
    """LLM client for email classification using OpenAI or Claude"""
    
    # Available categories
    CATEGORIES = [
        "Important", "Promotional", "Social", 
        "Newsletter", "Spam", "Personal"
    ]
    
    # Model configurations
    MODELS = {
        LLMProvider.OPENAI: {
            "gpt-4": {"max_tokens": 8192, "cost_per_1k": 0.03},
            "gpt-3.5-turbo": {"max_tokens": 4096, "cost_per_1k": 0.002}
        },
        LLMProvider.CLAUDE: {
            "claude-3-sonnet": {"max_tokens": 200000, "cost_per_1k": 0.015},
            "claude-3-haiku": {"max_tokens": 200000, "cost_per_1k": 0.0025}
        }
    }
    
    def __init__(self, provider: str, api_key: str, model: str):
        """
        Initialize LLM client
        
        Args:
            provider: LLM provider ("openai" or "claude")
            api_key: API key for the provider
            model: Model name to use
        """
        self.provider = LLMProvider(provider)
        self.api_key = api_key
        self.model = model
        self.usage_stats = {"requests": 0, "tokens": 0, "cost": 0.0}
        
        # Initialize client
        if self.provider == LLMProvider.OPENAI:
            openai.api_key = api_key
            self.client = openai
        elif self.provider == LLMProvider.CLAUDE:
            self.client = anthropic.Anthropic(api_key=api_key)
    
    async def classify_email(self, subject: str, content: str, sender: str) -> ClassificationResult:
        """
        Classify single email using LLM
        
        Args:
            subject: Email subject line
            content: Email content/body
            sender: Sender email address
            
        Returns:
            Classification result
        """
        # TODO: Implement email classification
        # Build classification prompt
        # Make API call
        # Parse response
        # Return ClassificationResult
        pass
    
    async def classify_emails_batch(self, emails: List[Dict[str, str]]) -> List[ClassificationResult]:
        """
        Classify multiple emails in batch
        
        Args:
            emails: List of email dictionaries with subject, content, sender
            
        Returns:
            List of classification results
        """
        # TODO: Implement batch classification
        # Process emails concurrently
        # Handle rate limits
        # Return results in same order
        pass
    
    async def detect_spam(self, email_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Detect spam using specialized prompt
        
        Args:
            email_data: Email data dictionary
            
        Returns:
            Spam detection result with confidence and reasoning
        """
        # TODO: Implement spam detection
        # Use spam-specific prompt
        # Analyze sender patterns
        # Return spam probability and reasoning
        pass
    
    def generate_explanation(self, classification: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation for classification
        
        Args:
            classification: Classification result dictionary
            
        Returns:
            Human-readable explanation
        """
        # TODO: Implement explanation generation
        # Format classification reasoning
        # Add confidence interpretation
        # Return user-friendly explanation
        pass
    
    def estimate_cost(self, text_length: int) -> float:
        """
        Estimate API cost for text processing
        
        Args:
            text_length: Length of text to process
            
        Returns:
            Estimated cost in USD
        """
        # TODO: Implement cost estimation
        # Calculate token count
        # Apply model pricing
        # Return estimated cost
        pass
    
    def _build_classification_prompt(self, subject: str, content: str, sender: str) -> str:
        """Build prompt for email classification"""
        # TODO: Implement prompt building
        # Include few-shot examples
        # Add context about categories
        # Request structured JSON response
        pass
    
    def _build_spam_detection_prompt(self, email_data: Dict[str, str]) -> str:
        """Build prompt for spam detection"""
        # TODO: Implement spam prompt
        # Include spam indicators
        # Request probability score
        # Add reasoning requirement
        pass
    
    async def _make_openai_request(self, prompt: str, system_message: str = None) -> Dict[str, Any]:
        """Make request to OpenAI API"""
        # TODO: Implement OpenAI API call
        # Build messages array
        # Set temperature=0 for consistency
        # Handle errors and retries
        pass
    
    async def _make_claude_request(self, prompt: str, system_message: str = None) -> Dict[str, Any]:
        """Make request to Claude API"""
        # TODO: Implement Claude API call
        # Build request parameters
        # Handle errors and retries
        # Parse response
        pass
    
    def _parse_classification_response(self, response: str) -> ClassificationResult:
        """Parse LLM response into ClassificationResult"""
        # TODO: Implement response parsing
        # Parse JSON response
        # Validate required fields
        # Handle malformed responses
        # Return ClassificationResult
        pass
    
    def _validate_category(self, category: str) -> str:
        """Validate and normalize category"""
        # TODO: Implement category validation
        # Check against allowed categories
        # Handle case variations
        # Return normalized category
        pass
    
    def _track_usage(self, tokens_used: int, cost: float) -> None:
        """Track API usage statistics"""
        self.usage_stats["requests"] += 1
        self.usage_stats["tokens"] += tokens_used
        self.usage_stats["cost"] += cost
        
        logger.info(f"LLM usage - Tokens: {tokens_used}, Cost: ${cost:.4f}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return self.usage_stats.copy()