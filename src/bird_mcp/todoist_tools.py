"""Todoist integration tools for the Bird MCP server."""

import asyncio
from datetime import datetime
from typing import Any, Optional
from collections import defaultdict

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task


class TodoistTools:
    """Tools for interacting with Todoist API."""

    def __init__(self, api_token: str):
        """Initialize Todoist tools with API token."""
        self.api = TodoistAPI(api_token)

    async def create_task(
        self,
        content: str,
        description: Optional[str] = None,
        project_id: Optional[str] = None,
        due_string: Optional[str] = None,
        priority: int = 1,
        labels: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Create a new task in Todoist.

        Args:
            content: Task title/content
            description: Task description
            project_id: Project ID to add task to
            due_string: Due date in natural language (e.g., "tomorrow", "next Monday")
            priority: Priority level (1-4, where 4 is highest)
            labels: List of label names

        Returns:
            Created task details
        """
        try:
            task = await asyncio.to_thread(
                self.api.add_task,
                content=content,
                description=description,
                project_id=project_id,
                due_string=due_string,
                priority=priority,
                labels=labels or [],
            )
            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "content": task.content,
                    "description": task.description,
                    "project_id": task.project_id,
                    "due": task.due.string if task.due else None,
                    "priority": task.priority,
                    "labels": task.labels,
                    "url": task.url,
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_tasks(
        self,
        project_id: Optional[str] = None,
        label: Optional[str] = None,
        filter_string: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Retrieve tasks from Todoist.

        Args:
            project_id: Filter by project ID
            label: Filter by label name
            filter_string: Todoist filter string (e.g., "today", "overdue")

        Returns:
            List of tasks matching the criteria
        """
        try:
            tasks = await asyncio.to_thread(
                self.api.get_tasks,
                project_id=project_id,
                label=label,
                filter=filter_string,
            )

            task_list = [
                {
                    "id": task.id,
                    "content": task.content,
                    "description": task.description,
                    "project_id": task.project_id,
                    "due": task.due.string if task.due else None,
                    "priority": task.priority,
                    "labels": task.labels,
                    "is_completed": task.is_completed,
                    "url": task.url,
                }
                for task in tasks
            ]

            return {"success": True, "tasks": task_list, "count": len(task_list)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def complete_task(self, task_id: str) -> dict[str, Any]:
        """
        Mark a task as completed.

        Args:
            task_id: ID of the task to complete

        Returns:
            Success status
        """
        try:
            await asyncio.to_thread(self.api.close_task, task_id=task_id)
            return {"success": True, "message": f"Task {task_id} marked as completed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def update_task(
        self,
        task_id: str,
        content: Optional[str] = None,
        description: Optional[str] = None,
        due_string: Optional[str] = None,
        priority: Optional[int] = None,
        labels: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Update an existing task.

        Args:
            task_id: ID of the task to update
            content: New task content
            description: New task description
            due_string: New due date
            priority: New priority level (1-4)
            labels: New labels list

        Returns:
            Updated task details
        """
        try:
            task = await asyncio.to_thread(
                self.api.update_task,
                task_id=task_id,
                content=content,
                description=description,
                due_string=due_string,
                priority=priority,
                labels=labels,
            )
            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "content": task.content,
                    "description": task.description,
                    "due": task.due.string if task.due else None,
                    "priority": task.priority,
                    "labels": task.labels,
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def analyze_stats(self) -> dict[str, Any]:
        """
        Analyze Todoist tasks and provide statistics.

        Returns:
            Statistics about tasks including counts by priority, project, and labels
        """
        try:
            # Get all active tasks
            tasks = await asyncio.to_thread(self.api.get_tasks)
            projects = await asyncio.to_thread(self.api.get_projects)

            # Build project name mapping
            project_map = {project.id: project.name for project in projects}

            # Calculate statistics
            total_tasks = len(tasks)
            priority_counts = defaultdict(int)
            project_counts = defaultdict(int)
            label_counts = defaultdict(int)
            overdue_count = 0
            today_count = 0
            upcoming_count = 0

            today = datetime.now().date()

            for task in tasks:
                # Priority distribution
                priority_counts[task.priority] += 1

                # Project distribution
                project_name = project_map.get(task.project_id, "Unknown")
                project_counts[project_name] += 1

                # Label distribution
                for label in task.labels:
                    label_counts[label] += 1

                # Due date analysis
                if task.due and task.due.date:
                    due_date = datetime.fromisoformat(task.due.date).date()
                    if due_date < today:
                        overdue_count += 1
                    elif due_date == today:
                        today_count += 1
                    else:
                        upcoming_count += 1

            return {
                "success": True,
                "stats": {
                    "total_tasks": total_tasks,
                    "priority_distribution": dict(priority_counts),
                    "project_distribution": dict(project_counts),
                    "label_distribution": dict(label_counts),
                    "due_date_analysis": {
                        "overdue": overdue_count,
                        "today": today_count,
                        "upcoming": upcoming_count,
                        "no_due_date": total_tasks
                        - (overdue_count + today_count + upcoming_count),
                    },
                    "projects": [
                        {"id": p.id, "name": p.name, "color": p.color}
                        for p in projects
                    ],
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_projects(self) -> dict[str, Any]:
        """
        Get all Todoist projects.

        Returns:
            List of all projects
        """
        try:
            projects = await asyncio.to_thread(self.api.get_projects)
            project_list = [
                {
                    "id": project.id,
                    "name": project.name,
                    "color": project.color,
                    "is_favorite": project.is_favorite,
                    "url": project.url,
                }
                for project in projects
            ]
            return {"success": True, "projects": project_list, "count": len(project_list)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def delete_task(self, task_id: str) -> dict[str, Any]:
        """
        Permanently delete a task.

        Args:
            task_id: ID of the task to delete

        Returns:
            Success status
        """
        try:
            await asyncio.to_thread(self.api.delete_task, task_id=task_id)
            return {"success": True, "message": f"Task {task_id} deleted permanently"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_comments(self, task_id: str) -> dict[str, Any]:
        """
        Get all comments for a task.

        Args:
            task_id: ID of the task

        Returns:
            List of comments
        """
        try:
            comments = await asyncio.to_thread(self.api.get_comments, task_id=task_id)
            comment_list = [
                {
                    "id": comment.id,
                    "content": comment.content,
                    "posted_at": comment.posted_at,
                }
                for comment in comments
            ]
            return {"success": True, "comments": comment_list, "count": len(comment_list)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def add_comment(self, task_id: str, content: str) -> dict[str, Any]:
        """
        Add a comment to a task.

        Args:
            task_id: ID of the task
            content: Comment text

        Returns:
            Created comment details
        """
        try:
            comment = await asyncio.to_thread(
                self.api.add_comment,
                task_id=task_id,
                content=content
            )
            return {
                "success": True,
                "comment": {
                    "id": comment.id,
                    "content": comment.content,
                    "posted_at": comment.posted_at,
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_labels(self) -> dict[str, Any]:
        """
        Get all available labels.

        Returns:
            List of labels
        """
        try:
            labels = await asyncio.to_thread(self.api.get_labels)
            label_list = [
                {
                    "id": label.id,
                    "name": label.name,
                    "color": label.color,
                    "order": label.order,
                    "is_favorite": label.is_favorite,
                }
                for label in labels
            ]
            return {"success": True, "labels": label_list, "count": len(label_list)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_sections(self, project_id: Optional[str] = None) -> dict[str, Any]:
        """
        Get sections (optionally filtered by project).

        Args:
            project_id: Project ID to filter sections

        Returns:
            List of sections
        """
        try:
            sections = await asyncio.to_thread(self.api.get_sections, project_id=project_id)
            section_list = [
                {
                    "id": section.id,
                    "name": section.name,
                    "project_id": section.project_id,
                    "order": section.order,
                }
                for section in sections
            ]
            return {"success": True, "sections": section_list, "count": len(section_list)}
        except Exception as e:
            return {"success": False, "error": str(e)}
