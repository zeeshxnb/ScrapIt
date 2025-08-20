"""
Test script for the enhanced AI task executor
This script tests various email task requests and verifies the AI's ability to parse them
"""
import os
import sys
import json
from typing import Dict, Any, List
import argparse

# Add parent directory to path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import get_db
from models import User, Email, Task
from task_executor import process_ai_task

# Test cases - natural language requests and expected outcomes
TEST_CASES = [
    {
        "description": "Simple delete spam emails task",
        "request": "Delete all my spam emails",
        "expected_action": "DELETE",
        "expected_emails": "spam emails"
    },
    {
        "description": "Archive emails task",
        "request": "Archive all read emails",
        "expected_action": "ARCHIVE",
        "expected_emails": "read emails"
    },
    {
        "description": "Label emails task",
        "request": "Label all emails from Amazon as shopping",
        "expected_action": "LABEL",
        "expected_emails": "from Amazon"
    },
    {
        "description": "Mark as read task",
        "request": "Mark all newsletter emails as read",
        "expected_action": "MARK_READ",
        "expected_emails": "newsletter emails"
    },
    {
        "description": "Star important emails",
        "request": "Star all emails from my boss",
        "expected_action": "STAR",
        "expected_emails": "from boss"
    },
    {
        "description": "Complex multi-step task",
        "request": "Find all unread newsletters, mark them as read, then archive them",
        "expected_action": "MULTI_STEP",  # Should have multiple steps
        "expected_emails": "unread newsletters"
    },
    {
        "description": "Archive old emails",
        "request": "Archive all emails older than 3 months",
        "expected_action": "ARCHIVE",
        "expected_emails": "older than 3 months"
    }
]

def run_test(test_case: Dict[str, str], user: User, db: Session) -> Dict[str, Any]:
    """Run a single test case and return the results"""
    print(f"Running test: {test_case['description']}")
    print(f"Request: '{test_case['request']}'")
    
    try:
        result = process_ai_task(test_case['request'], user, db)
        print(f"Task created: {result.get('task_created', False)}")
        print(f"Message: {result.get('message', 'No message')}")
        
        # If task was created, get more details
        if result.get('task_created') and result.get('task_id'):
            task_id = result.get('task_id')
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if task:
                print(f"Task description: {task.description}")
                print(f"Task steps: {len(task.steps)}")
                
                # Check the steps
                steps_analysis = []
                for i, step in enumerate(task.steps):
                    step_result = {
                        "action": step.get("action"),
                        "params": step.get("params"),
                    }
                    steps_analysis.append(step_result)
                    print(f"  Step {i+1}: {step.get('action')} - {len(step.get('params', {}).get('message_ids', []))} emails")
                
                result["steps_analysis"] = steps_analysis
                
                # Validate test
                if test_case['expected_action'] == "MULTI_STEP":
                    result["test_passed"] = len(task.steps) > 1
                    print(f"Test passed: {result['test_passed']} (Expected multiple steps, got {len(task.steps)})")
                else:
                    # Check if any step has the expected action
                    has_expected_action = any(
                        step.get("action") == test_case['expected_action'] 
                        for step in task.steps
                    )
                    result["test_passed"] = has_expected_action
                    print(f"Test passed: {result['test_passed']} (Expected action: {test_case['expected_action']})")
                
                return result
        
        return {
            "test_passed": False,
            "error": "No task created"
        }
    except Exception as e:
        print(f"Error running test: {str(e)}")
        return {
            "test_passed": False,
            "error": str(e)
        }

def run_all_tests(user_id: str):
    """Run all test cases"""
    results = []
    
    # Get database session
    db = next(get_db())
    
    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        print(f"User with ID {user_id} not found")
        return
    
    # Run tests
    for test_case in TEST_CASES:
        result = run_test(test_case, user, db)
        results.append({
            "test_case": test_case,
            "result": result
        })
        print("\n" + "-"*50 + "\n")
    
    # Print summary
    passed = sum(1 for r in results if r.get("result", {}).get("test_passed", False))
    print(f"Tests passed: {passed}/{len(TEST_CASES)}")
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the AI task executor")
    parser.add_argument("user_id", help="User ID to run tests with")
    args = parser.parse_args()
    
    run_all_tests(args.user_id)
