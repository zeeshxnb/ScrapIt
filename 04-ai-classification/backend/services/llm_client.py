"""
LLM API Client

Wrapper for OpenAI API for email classification
"""
import openai
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
    """LLM client for email classification using OpenAI"""
    
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
        }
    }
    
    def __init__(self, provider: str, api_key: str, model: str):
        """
        Initialize LLM client
        
        Args:
            provider: LLM provider ("openai")
            api_key: API key for the provider
            model: Model name to use
        """
        self.provider = LLMProvider(provider)
        self.api_key = api_key
        self.model = model
        self.usage_stats = {"requests": 0, "tokens": 0, "cost": 0.0}
        
        # Initialize client
        openai.api_key = api_key
        self.client = openai
    
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
        # Build classification prompt
        prompt = self._build_classification_prompt(subject, content, sender)
        # Make API call
        response = await self._make_openai_request(prompt)
        # Parse response
        return self._parse_classification_response(response)
    
    async def classify_emails_batch(self, emails: List[Dict[str, str]]) -> List[ClassificationResult]:
        """
        Classify multiple emails in batch
        
        Args:
            emails: List of email dictionaries with subject, content, sender
            
        Returns:
            List of classification results
        """
        # Process emails concurrently
        tasks = [self.classify_email(email['subject'], email['content'], email['sender']) for email in emails]
        # Handle rate limits
        return await asyncio.gather(*tasks)
    
    async def detect_spam(self, email_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Detect spam using specialized prompt
        
        Args:
            email_data: Email data dictionary
            
        Returns:
            Spam detection result with confidence and reasoning
        """
        # Use spam-specific prompt
        prompt = self._build_spam_detection_prompt(email_data)
        # Analyze sender patterns
        response = await self._make_openai_request(prompt)
        # Return spam probability and reasoning
        return json.loads(response)

    def generate_explanation(self, classification: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation for classification
        
        Args:
            classification: Classification result dictionary
            
        Returns:
            Human-readable explanation
        """
        # Format classification reasoning
        explanation = f"This email was classified as '{classification['category']}' with confidence {classification['confidence']:.2f}. Reason: {classification['reasoning']}"
        # Add confidence interpretation
        return explanation
    
    def estimate_cost(self, text_length: int) -> float:
        """
        Estimate API cost for text processing
        
        Args:
            text_length: Length of text to process
            
        Returns:
            Estimated cost in USD
        """
        # Calculate token count
        tokens = text_length // 4  # Rough estimate: 1 token ≈ 4 chars
        model_info = self.MODELS[self.provider][self.model]
        # Apply model pricing
        cost = (tokens / 1000) * model_info["cost_per_1k"]
        # Return estimated cost
        return cost
    
    def _build_classification_prompt(self, subject: str, content: str, sender: str) -> str:
        """Build prompt for email classification"""
        # Include few-shot examples
        prompt = (
            f"Classify the following email into one of these categories: {', '.join(self.CATEGORIES)}.\n"
            f"Return a JSON with keys: category, confidence (0-1), reasoning, subcategory (optional), suggested_actions (list).\n"
            f"Subject: {subject}\nSender: {sender}\nContent: {content}"
        )
        return prompt
    
    def _build_spam_detection_prompt(self, email_data: Dict[str, str]) -> str:
        """Build prompt for spam detection"""
        # Include spam indicators
        prompt = (
            "Is this email spam? Return JSON with keys: is_spam (true/false), confidence (0-1), reasoning.\n"
            f"Subject: {email_data.get('subject', '')}\nSender: {email_data.get('sender', '')}\nContent: {email_data.get('content', '')}"
        )
        return prompt
    
    async def _make_openai_request(self, prompt: str, system_message: str = None) -> str:
        """Make request to OpenAI API"""
        # Build messages array
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        try:
            response = await self.client.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=0,
                max_tokens=self.MODELS[self.provider][self.model]["max_tokens"] // 2
            )
            content = response["choices"][0]["message"]["content"]
            tokens_used = response["usage"]["total_tokens"]
            cost = self.estimate_cost(tokens_used * 4)  # rough char count
            self._track_usage(tokens_used, cost)
            return content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _parse_classification_response(self, response: str) -> ClassificationResult:
        """Parse LLM response into ClassificationResult"""
        try:
            data = json.loads(response)
            category = self._validate_category(data.get("category", ""))
            confidence = float(data.get("confidence", 0.0))
            reasoning = data.get("reasoning", "")
            subcategory = data.get("subcategory")
            suggested_actions = data.get("suggested_actions", [])
            return ClassificationResult(
                category=category,
                confidence=confidence,
                reasoning=reasoning,
                subcategory=subcategory,
                suggested_actions=suggested_actions
            )
        except Exception as e:
            logger.error(f"Failed to parse classification response: {e}")
            return ClassificationResult(category="Unknown", confidence=0.0, reasoning="Parsing error")
    
    def _validate_category(self, category: str) -> str:
        """Validate and normalize category"""
        for cat in self.CATEGORIES:
            if cat.lower() == category.lower():
                return cat
        return "Other"
    
    def _track_usage(self, tokens_used: int, cost: float) -> None:
        """Track API usage statistics"""
        self.usage_stats["requests"] += 1
        self.usage_stats["tokens"] += tokens_used
        self.usage_stats["cost"] += cost
        
        logger.info(f"LLM usage - Tokens: {tokens_used}, Cost: ${cost:.4f}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return self.usage_stats.copy()