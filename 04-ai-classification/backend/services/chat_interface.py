"""
Chat Interface Service

Provides a chat interface for users to request tasks and processes these requests
using LLMs to extract actionable tasks.
"""
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from .llm_client import LLMClient, LLMProvider

logger = logging.getLogger(__name__)

@dataclass
class TaskItem:
    """Represents a single task extracted from user chat"""
    id: str
    description: str
    type: str  # e.g., "delete", "archive", "categorize", "search"
    parameters: Dict[str, Any]
    status: str = "pending"  # pending, in_progress, completed, failed

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "description": self.description,
            "type": self.type,
            "parameters": self.parameters,
            "status": self.status
        }

class ChatInterface:
    """Chat interface for processing user requests and extracting tasks"""
    
    # Task types that can be extracted
    TASK_TYPES = [
        "delete", "archive", "categorize", "search", 
        "filter", "organize", "summarize", "analyze"
    ]
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize chat interface
        
        Args:
            llm_client: LLM client for processing chat messages
        """
        self.llm_client = llm_client
        self.conversation_history = []
    
    async def process_user_message(self, user_message: str) -> List[TaskItem]:
        """
        Process user message and extract tasks
        
        Args:
            user_message: User's chat message
            
        Returns:
            List of extracted tasks
        """
        # Add message to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Build prompt for task extraction
        prompt = self._build_task_extraction_prompt(user_message)
        
        # Get response from LLM
        response = await self.llm_client._make_openai_request(
            prompt, 
            system_message="You are an AI assistant that extracts actionable email management tasks from user requests."
        )
        
        # Parse tasks from response
        tasks = self._parse_tasks_from_response(response)
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant", 
            "content": f"I've identified {len(tasks)} tasks from your request."
        })
        
        return tasks
    
    async def get_task_confirmation(self, tasks: List[TaskItem]) -> str:
        """
        Generate confirmation message for extracted tasks
        
        Args:
            tasks: List of extracted tasks
            
        Returns:
            Confirmation message for user
        """
        if not tasks:
            return "I couldn't identify any specific tasks to perform. Could you please clarify what you'd like me to do with your emails?"
        
        task_descriptions = [f"- {task.description}" for task in tasks]
        confirmation = "I'll help you with the following tasks:\n\n" + "\n".join(task_descriptions)
        confirmation += "\n\nWould you like me to proceed with these tasks?"
        
        return confirmation
    
    async def execute_tasks(self, tasks: List[TaskItem]) -> Dict[str, Any]:
        """
        Execute confirmed tasks
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            Results of task execution
        """
        results = {
            "completed": [],
            "failed": [],
            "summary": ""
        }
        
        # TODO: Implement task execution logic
        # This will connect to other services like email_service, etc.
        # For now, just mark tasks as completed
        
        for task in tasks:
            # Update task status
            task.status = "completed"
            results["completed"].append(task.to_dict())
        
        # Generate summary
        results["summary"] = f"Completed {len(results['completed'])} tasks successfully."
        
        return results
    
    def _build_task_extraction_prompt(self, user_message: str) -> str:
        """
        Build prompt for extracting tasks from user message
        
        Args:
            user_message: User's chat message
            
        Returns:
            Prompt for LLM
        """
        prompt = f"""
        The user has sent the following message about email management:
        
        "{user_message}"
        
        Extract specific, actionable tasks from this message. For each task, provide:
        1. A brief description
        2. The task type (one of: {', '.join(self.TASK_TYPES)})
        3. Any relevant parameters (search terms, date ranges, categories, etc.)
        
        Format your response as a JSON array of task objects with the following structure:
        
        ```json
        [
          {{
            "id": "unique_id",
            "description": "Human-readable description of the task",
            "type": "task_type",
            "parameters": {{
              "param1": "value1",
              "param2": "value2"
            }}
          }},
          ...
        ]
        ```
        
        If no clear tasks can be extracted, return an empty array: []
        """
        
        return prompt
    
    def _parse_tasks_from_response(self, response: Dict[str, Any]) -> List[TaskItem]:
        """
        Parse tasks from LLM response
        
        Args:
            response: LLM response
            
        Returns:
            List of TaskItem objects
        """
        try:
            # Extract JSON from response
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                content = response.get("content", "")
            
            # Find JSON array in content
            json_start = content.find("[")
            json_end = content.rfind("]") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                tasks_data = json.loads(json_str)
                
                # Convert to TaskItem objects
                tasks = []
                for i, task_data in enumerate(tasks_data):
                    # Ensure task has required fields
                    if "description" not in task_data:
                        continue
                    
                    # Use provided ID or generate one
                    task_id = task_data.get("id", f"task_{i+1}")
                    
                    # Create TaskItem
                    task = TaskItem(
                        id=task_id,
                        description=task_data.get("description", ""),
                        type=task_data.get("type", "unknown"),
                        parameters=task_data.get("parameters", {}),
                        status="pending"
                    )
                    tasks.append(task)
                
                return tasks
            
            return []
        
        except Exception as e:
            logger.error(f"Error parsing tasks from response: {e}")
            return []