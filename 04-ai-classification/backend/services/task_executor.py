"""
Task Executor Service

Executes tasks extracted from user chat messages
"""
import logging
from typing import Dict, List, Any, Optional
import asyncio

from .chat_interface import TaskItem

logger = logging.getLogger(__name__)

class TaskExecutor:
    """Service for executing tasks extracted from chat"""
    
    def __init__(self, email_service=None, category_service=None):
        """
        Initialize task executor
        
        Args:
            email_service: Service for email operations
            category_service: Service for category operations
        """
        self.email_service = email_service
        self.category_service = category_service
        
    async def execute_tasks(self, tasks: List[TaskItem]) -> Dict[str, Any]:
        """
        Execute a list of tasks
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            Results of execution
        """
        results = {
            "completed": [],
            "failed": [],
            "summary": ""
        }
        
        for task in tasks:
            try:
                # Update task status to in_progress
                task.status = "in_progress"
                
                # Execute task based on type
                if task.type == "delete":
                    await self._execute_delete_task(task)
                elif task.type == "archive":
                    await self._execute_archive_task(task)
                elif task.type == "categorize":
                    await self._execute_categorize_task(task)
                elif task.type == "search":
                    await self._execute_search_task(task)
                elif task.type == "filter":
                    await self._execute_filter_task(task)
                elif task.type == "organize":
                    await self._execute_organize_task(task)
                elif task.type == "summarize":
                    await self._execute_summarize_task(task)
                elif task.type == "analyze":
                    await self._execute_analyze_task(task)
                else:
                    raise ValueError(f"Unknown task type: {task.type}")
                
                # Mark task as completed
                task.status = "completed"
                results["completed"].append(task.to_dict())
                
            except Exception as e:
                logger.error(f"Error executing task {task.id}: {e}")
                task.status = "failed"
                results["failed"].append(task.to_dict())
        
        # Generate summary
        completed_count = len(results["completed"])
        failed_count = len(results["failed"])
        
        if failed_count == 0:
            results["summary"] = f"Successfully completed all {completed_count} tasks."
        else:
            results["summary"] = f"Completed {completed_count} tasks with {failed_count} failures."
        
        return results
    
    async def _execute_delete_task(self, task: TaskItem) -> None:
        """Execute delete task"""
        if not self.email_service:
            raise ValueError("Email service not available")
        
        # Extract parameters
        email_ids = task.parameters.get("email_ids", [])
        query = task.parameters.get("query")
        
        if email_ids:
            # Delete specific emails
            await self.email_service.delete_emails(email_ids)
        elif query:
            # Search and delete emails matching query
            matching_emails = await self.email_service.search_emails(query)
            if matching_emails:
                await self.email_service.delete_emails([email.id for email in matching_emails])
        else:
            raise ValueError("Delete task requires email_ids or query parameter")
    
    async def _execute_archive_task(self, task: TaskItem) -> None:
        """Execute archive task"""
        if not self.email_service:
            raise ValueError("Email service not available")
        
        # Extract parameters
        email_ids = task.parameters.get("email_ids", [])
        query = task.parameters.get("query")
        
        if email_ids:
            # Archive specific emails
            await self.email_service.archive_emails(email_ids)
        elif query:
            # Search and archive emails matching query
            matching_emails = await self.email_service.search_emails(query)
            if matching_emails:
                await self.email_service.archive_emails([email.id for email in matching_emails])
        else:
            raise ValueError("Archive task requires email_ids or query parameter")
    
    async def _execute_categorize_task(self, task: TaskItem) -> None:
        """Execute categorize task"""
        if not self.category_service:
            raise ValueError("Category service not available")
        
        # Extract parameters
        email_ids = task.parameters.get("email_ids", [])
        category = task.parameters.get("category")
        
        if not category:
            raise ValueError("Categorize task requires category parameter")
        
        if email_ids:
            # Categorize specific emails
            await self.category_service.categorize_emails(email_ids, category)
        else:
            raise ValueError("Categorize task requires email_ids parameter")
    
    async def _execute_search_task(self, task: TaskItem) -> List[Dict[str, Any]]:
        """
        Execute search task
        
        Returns:
            List of matching emails
        """
        if not self.email_service:
            raise ValueError("Email service not available")
        
        # Extract parameters
        query = task.parameters.get("query")
        
        if not query:
            raise ValueError("Search task requires query parameter")
        
        # Search emails
        matching_emails = await self.email_service.search_emails(query)
        
        # Add results to task parameters
        task.parameters["results"] = [email.to_dict() for email in matching_emails]
        
        return task.parameters["results"]
    
    async def _execute_filter_task(self, task: TaskItem) -> List[Dict[str, Any]]:
        """
        Execute filter task
        
        Returns:
            List of filtered emails
        """
        if not self.email_service:
            raise ValueError("Email service not available")
        
        # Extract parameters
        filters = task.parameters.get("filters", {})
        
        if not filters:
            raise ValueError("Filter task requires filters parameter")
        
        # Filter emails
        filtered_emails = await self.email_service.filter_emails(filters)
        
        # Add results to task parameters
        task.parameters["results"] = [email.to_dict() for email in filtered_emails]
        
        return task.parameters["results"]
    
    async def _execute_organize_task(self, task: TaskItem) -> None:
        """Execute organize task"""
        if not self.email_service or not self.category_service:
            raise ValueError("Email and category services not available")
        
        # Extract parameters
        organization_type = task.parameters.get("organization_type")
        
        if organization_type == "by_sender":
            await self._organize_by_sender()
        elif organization_type == "by_date":
            await self._organize_by_date()
        elif organization_type == "by_category":
            await self._organize_by_category()
        else:
            raise ValueError(f"Unknown organization type: {organization_type}")
    
    async def _execute_summarize_task(self, task: TaskItem) -> Dict[str, Any]:
        """
        Execute summarize task
        
        Returns:
            Summary information
        """
        if not self.email_service:
            raise ValueError("Email service not available")
        
        # Extract parameters
        email_ids = task.parameters.get("email_ids", [])
        query = task.parameters.get("query")
        
        if email_ids:
            # Summarize specific emails
            summary = await self.email_service.summarize_emails(email_ids)
        elif query:
            # Search and summarize emails matching query
            matching_emails = await self.email_service.search_emails(query)
            if matching_emails:
                summary = await self.email_service.summarize_emails(
                    [email.id for email in matching_emails]
                )
            else:
                summary = {"summary": "No emails found matching the query."}
        else:
            raise ValueError("Summarize task requires email_ids or query parameter")
        
        # Add summary to task parameters
        task.parameters["summary"] = summary
        
        return summary
    
    async def _execute_analyze_task(self, task: TaskItem) -> Dict[str, Any]:
        """
        Execute analyze task
        
        Returns:
            Analysis results
        """
        if not self.email_service:
            raise ValueError("Email service not available")
        
        # Extract parameters
        analysis_type = task.parameters.get("analysis_type")
        
        if not analysis_type:
            raise ValueError("Analyze task requires analysis_type parameter")
        
        # Perform analysis
        if analysis_type == "sender_statistics":
            analysis = await self.email_service.analyze_senders()
        elif analysis_type == "time_patterns":
            analysis = await self.email_service.analyze_time_patterns()
        elif analysis_type == "category_distribution":
            analysis = await self.email_service.analyze_categories()
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        # Add analysis to task parameters
        task.parameters["analysis"] = analysis
        
        return analysis
    
    # Helper methods for organize task
    async def _organize_by_sender(self) -> None:
        """Organize emails by sender"""
        # Implementation depends on email_service capabilities
        pass
    
    async def _organize_by_date(self) -> None:
        """Organize emails by date"""
        # Implementation depends on email_service capabilities
        pass
    
    async def _organize_by_category(self) -> None:
        """Organize emails by category"""
        # Implementation depends on category_service capabilities
        pass