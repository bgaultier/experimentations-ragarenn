"""
title: Redmine API Tool
author: Baptiste Gaultier and RAGaRenn Codestral
version: 1.0.1
description: Control your Redmine project management system via REST API
required_open_webui_version: 0.3.9
"""

import requests
from typing import Callable, Any, Awaitable
from pydantic import BaseModel, Field
import json


class Tools:
    class Valves(BaseModel):
        REDMINE_URL: str = Field(
            default="https://your-redmine-instance.fr",
            description="Your Redmine instance URL (without trailing slash)",
        )
        REDMINE_API_KEY: str = Field(
            default="",
            description="Your Redmine API key (found in My Account > API access key)",
        )

    def __init__(self):
        self.valves = self.Valves()

    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Helper method to make API requests to Redmine"""
        url = f"{self.valves.REDMINE_URL}{endpoint}"
        headers = {
            "X-Redmine-API-Key": self.valves.REDMINE_API_KEY,
            "Content-Type": "application/json",
        }

        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)

            response.raise_for_status()

            if response.status_code == 204:  # No content
                return {
                    "status": "success",
                    "message": "Operation completed successfully",
                }

            return response.json() if response.text else {"status": "success"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "failed"}

    async def list_projects(
        self,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
    ) -> str:
        """
        List all projects in Redmine.

        :return: JSON string with list of projects
        """
        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Fetching projects...", "done": False},
            }
        )

        result = self._make_request("GET", "/projects.json")

        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Projects fetched", "done": True},
            }
        )

        return json.dumps(result, indent=2)

    async def list_issues(
        self,
        project_id: str = 2356,
        status: str = "open",
        limit: int = 25,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
    ) -> str:
        """
        List issues from Redmine.

        :param project_id: Optional project identifier to filter issues
        :param status: Filter by status ('open', 'closed', or '*' for all)
        :param limit: Maximum number of issues to return (default 25)
        :return: JSON string with list of issues
        """
        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Fetching issues...", "done": False},
            }
        )

        endpoint = f"/issues.json?limit={limit}&status_id={status}"
        if project_id:
            endpoint += f"&project_id={project_id}"

        result = self._make_request("GET", endpoint)

        await __event_emitter__(
            {"type": "status", "data": {"description": "Issues fetched", "done": True}}
        )

        return json.dumps(result, indent=2)

    async def get_issue(
        self,
        issue_id: int,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
    ) -> str:
        """
        Get details of a specific issue.

        :param issue_id: The issue ID number
        :return: JSON string with issue details
        """
        await __event_emitter__(
            {
                "type": "status",
                "data": {
                    "description": f"Fetching issue #{issue_id}...",
                    "done": False,
                },
            }
        )

        result = self._make_request("GET", f"/issues/{issue_id}.json")

        await __event_emitter__(
            {"type": "status", "data": {"description": "Issue fetched", "done": True}}
        )

        return json.dumps(result, indent=2)

    async def create_issue(
        self,
        project_id: str,
        subject: str,
        description: str = "",
        priority_id: int = 2,
        tracker_id: int = 1,
        assigned_to_id: int = None,
        due_date: str = None,
        done_ratio: int = None,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
    ) -> str:
        """
        Create a new issue in Redmine.

        :param project_id: Project identifier
        :param subject: Issue subject/title
        :param description: Issue description
        :param priority_id: Priority ID (1=Low, 2=Normal, 3=High, 4=Urgent, 5=Immediate)
        :param tracker_id: Tracker ID (typically 1=Bug, 2=Feature, 3=Support)
        :param assigned_to_id: Optional user ID to assign the issue to
        :param due_date: Due date in YYYY-MM-DD format (e.g., "2025-12-31")
        :param done_ratio: Completion percentage (0-100)
        :return: JSON string with created issue details
        """
        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Creating issue...", "done": False},
            }
        )

        issue_data = {
            "issue": {
                "project_id": project_id,
                "subject": subject,
                "description": description,
                "priority_id": priority_id,
                "tracker_id": tracker_id,
            }
        }

        if assigned_to_id:
            issue_data["issue"]["assigned_to_id"] = assigned_to_id
        if due_date:
            issue_data["issue"]["due_date"] = due_date
        if done_ratio is not None:
            issue_data["issue"]["done_ratio"] = done_ratio

        result = self._make_request("POST", "/issues.json", issue_data)

        await __event_emitter__(
            {"type": "status", "data": {"description": "Issue created", "done": True}}
        )

        return json.dumps(result, indent=2)

    async def update_issue(
        self,
        issue_id: int,
        subject: str = None,
        description: str = None,
        status_id: int = None,
        priority_id: int = None,
        assigned_to_id: int = None,
        due_date: str = None,
        done_ratio: int = None,
        notes: str = None,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
    ) -> str:
        """
        Update an existing issue.

        :param issue_id: The issue ID to update
        :param subject: New subject (optional)
        :param description: New description (optional)
        :param status_id: New status ID (optional)
        :param priority_id: New priority ID (optional)
        :param assigned_to_id: New assignee user ID (optional)
        :param due_date: Due date in YYYY-MM-DD format (e.g., "2025-12-31")
        :param done_ratio: Completion percentage (0-100)
        :param notes: Add a note/comment to the issue (optional)
        :return: JSON string with operation result
        """
        await __event_emitter__(
            {
                "type": "status",
                "data": {
                    "description": f"Updating issue #{issue_id}...",
                    "done": False,
                },
            }
        )

        issue_data = {"issue": {}}

        if subject:
            issue_data["issue"]["subject"] = subject
        if description:
            issue_data["issue"]["description"] = description
        if status_id:
            issue_data["issue"]["status_id"] = status_id
        if priority_id:
            issue_data["issue"]["priority_id"] = priority_id
        if assigned_to_id:
            issue_data["issue"]["assigned_to_id"] = assigned_to_id
        if due_date:
            issue_data["issue"]["due_date"] = due_date
        if done_ratio is not None:
            issue_data["issue"]["done_ratio"] = done_ratio
        if notes:
            issue_data["issue"]["notes"] = notes

        result = self._make_request("PUT", f"/issues/{issue_id}.json", issue_data)

        await __event_emitter__(
            {"type": "status", "data": {"description": "Issue updated", "done": True}}
        )

        return json.dumps(result, indent=2)

    async def delete_issue(
        self,
        issue_id: int,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
    ) -> str:
        """
        Delete an issue from Redmine.

        :param issue_id: The issue ID to delete
        :return: JSON string with operation result
        """
        await __event_emitter__(
            {
                "type": "status",
                "data": {
                    "description": f"Deleting issue #{issue_id}...",
                    "done": False,
                },
            }
        )

        result = self._make_request("DELETE", f"/issues/{issue_id}.json")

        await __event_emitter__(
            {"type": "status", "data": {"description": "Issue deleted", "done": True}}
        )

        return json.dumps(result, indent=2)

    async def list_users(
        self,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
    ) -> str:
        """
        List all users in Redmine.

        :return: JSON string with list of users
        """
        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Fetching users...", "done": False},
            }
        )

        result = self._make_request("GET", "/users.json")

        await __event_emitter__(
            {"type": "status", "data": {"description": "Users fetched", "done": True}}
        )

        return json.dumps(result, indent=2)

    async def get_time_entries(
        self,
        project_id: str = None,
        user_id: int = None,
        from_date: str = None,
        to_date: str = None,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
    ) -> str:
        """
        Get time entries from Redmine.

        :param project_id: Optional project identifier to filter
        :param user_id: Optional user ID to filter
        :param from_date: Start date in YYYY-MM-DD format
        :param to_date: End date in YYYY-MM-DD format
        :return: JSON string with time entries
        """
        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Fetching time entries...", "done": False},
            }
        )

        endpoint = "/time_entries.json?"
        params = []

        if project_id:
            params.append(f"project_id={project_id}")
        if user_id:
            params.append(f"user_id={user_id}")
        if from_date:
            params.append(f"from={from_date}")
        if to_date:
            params.append(f"to={to_date}")

        endpoint += "&".join(params)

        result = self._make_request("GET", endpoint)

        await __event_emitter__(
            {
                "type": "status",
                "data": {"description": "Time entries fetched", "done": True},
            }
        )

        return json.dumps(result, indent=2)

redmine = Tools.__init__()
Tools.update_issue(issue_id=7099, done_ratio=90,)