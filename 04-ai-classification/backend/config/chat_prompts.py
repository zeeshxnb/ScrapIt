"""
Chat Interface Prompts

Prompts for the chat interface and task extraction
"""

# System prompt for the chat interface
CHAT_SYSTEM_PROMPT = """
You are an AI assistant for the ScrapIt email management system. Your role is to help users manage their email inbox by understanding their requests and converting them into specific actionable tasks.

Available task types:
- delete: Remove emails from the inbox
- archive: Move emails to archive
- categorize: Assign emails to categories
- search: Find emails matching criteria
- filter: Filter emails based on various attributes
- organize: Organize emails by sender, date, or category
- summarize: Provide summaries of emails
- analyze: Analyze email patterns and statistics

Always respond in a helpful, concise manner. Extract specific tasks from user requests and format them for the system to execute.
"""

# Task extraction prompt template
TASK_EXTRACTION_PROMPT_TEMPLATE = """
The user has sent the following message about email management:

"{user_message}"

Extract specific, actionable tasks from this message. For each task, provide:
1. A brief description
2. The task type (one of: delete, archive, categorize, search, filter, organize, summarize, analyze)
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

# Example task extraction for different request types
TASK_EXTRACTION_EXAMPLES = {
    "delete": {
        "user_message": "Delete all emails from newsletter@example.com",
        "tasks": [
            {
                "id": "task_1",
                "description": "Delete all emails from newsletter@example.com",
                "type": "delete",
                "parameters": {
                    "query": "from:newsletter@example.com"
                }
            }
        ]
    },
    "search": {
        "user_message": "Find emails about project deadlines from last week",
        "tasks": [
            {
                "id": "task_1",
                "description": "Search for emails about project deadlines from last week",
                "type": "search",
                "parameters": {
                    "query": "project deadline",
                    "date_range": {
                        "start": "1 week ago",
                        "end": "today"
                    }
                }
            }
        ]
    },
    "multiple": {
        "user_message": "Find all promotion emails and move them to archive",
        "tasks": [
            {
                "id": "task_1",
                "description": "Search for promotional emails",
                "type": "search",
                "parameters": {
                    "query": "category:promotions"
                }
            },
            {
                "id": "task_2",
                "description": "Archive found promotional emails",
                "type": "archive",
                "parameters": {
                    "use_previous_results": True
                }
            }
        ]
    }
}

# Task confirmation prompt template
TASK_CONFIRMATION_TEMPLATE = """
I've identified the following tasks from your request:

{task_list}

Would you like me to proceed with these tasks?
"""

# Task execution summary template
TASK_EXECUTION_TEMPLATE = """
I've completed the following tasks:

{completed_tasks}

{failed_tasks_section}

{summary}
"""

# Failed tasks section template
FAILED_TASKS_TEMPLATE = """
The following tasks couldn't be completed:

{failed_tasks}

Reason: {failure_reason}
"""