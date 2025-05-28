"""
WebSocket connection manager
"""
import json
import logging
import uuid
from typing import Dict, List, Any, Optional
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from ..models.models import db
from ..models.github_model import github_model
from ..core.mongodb import mongodb
from ..schemas.ws_schemas import (
    ChatMessage, MessageSender, FileNode, Repository, 
    RepositoryRe            # Retrieve repository from database
            repository = await github_model.get_repository(client_id, repository_id)
            
            if not repository:
                await self.send_personal_message({
                    "type": "REPOSITORY_ACTION_ERROR",
                    "payload": {"message": "Repository not found"}
                }, client_id)
                returnfrom ..services.github_service import GitHubService
from ..services.ai_service import AIAgentService

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.ai_service = AIAgentService()
        # Track selected repository for each client
        self.selected_repositories: Dict[str, str] = {}
    
    async def connect(self, websocket: WebSocket) -> str:
        """Connect a new WebSocket client"""
        await websocket.accept()
        client_id = str(uuid.uuid4())
        self.active_connections[client_id] = websocket
        await db.add_connection(client_id)
        logger.info(f"Client connected: {client_id}")
        return client_id
    
    def disconnect(self, client_id: str) -> None:
        """Disconnect a WebSocket client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.selected_repositories:
            del self.selected_repositories[client_id]
        asyncio.create_task(db.remove_connection(client_id))
        logger.info(f"Client disconnected: {client_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str) -> None:
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def handle_submit_config(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle configuration submission"""
        try:
            # Store configuration in the database
            await db.update_connection_config(client_id, payload)
            
            # Configure AI service with the provided Gemini API key
            self.ai_service.configure(payload.get("geminiToken", ""))
            
            # Process any repositories in the configuration
            repositories = payload.get("repositories", [])
            if repositories:
                for repo_data in repositories:
                    await github_model.add_repository(client_id, repo_data)
                
                # Get all repositories and send them back
                repos = await github_model.get_repositories(client_id)
                await self.send_personal_message({
                    "type": "REPOSITORIES_LIST",
                    "payload": {"repositories": repos}
                }, client_id)
                
                # Select the first repository by default
                if repos and len(repos) > 0:
                    first_repo = repos[0]
                    self.selected_repositories[client_id] = first_repo["id"]
                    
                    # Fetch file tree for the first repository
                    repo_details = await github_model.get_repository(client_id, first_repo["id"])
                    if repo_details:
                        await self.handle_fetch_files(client_id, {"repository_id": first_repo["id"]})
            
            # Send success response
            await self.send_personal_message({"type": "CONFIG_SUCCESS"}, client_id)
            
        except Exception as e:
            logger.error(f"Error in handle_submit_config: {e}")
            await self.send_personal_message({
                "type": "CONFIG_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_fetch_files(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle file tree fetching"""
        try:
            # Set typing indicator
            await self.send_personal_message({
                "type": "AGENT_TYPING",
                "payload": {"isTyping": True}
            }, client_id)
            
            # Get repository ID from payload
            repository_id = payload.get("repository_id")
            
            if not repository_id:
                await self.send_personal_message({
                    "type": "FILE_TREE_ERROR",
                    "payload": {"message": "Repository ID is required"}
                }, client_id)
                return
            
            # Retrieve repository details from database
            repository = await github_model.get_repository(client_id, repository_id)
            
            if not repository:
                await self.send_personal_message({
                    "type": "FILE_TREE_ERROR",
                    "payload": {"message": "Repository not found"}
                }, client_id)
                return
            
            # Update selected repository for this client
            self.selected_repositories[client_id] = repository_id
                
            # Fetch the file tree using repository details
            file_tree = await github_model.fetch_file_tree(repository)
            
            # Send the file tree to the client along with repository info
            await self.send_personal_message({
                "type": "FILE_TREE_DATA",
                "payload": {
                    "tree": [node.model_dump() for node in file_tree],
                    "repository": {
                        "id": repository["id"],
                        "name": repository["name"],
                        "url": repository["url"],
                        "host": repository["host"],
                        "owner": repository["owner"],
                        "repo": repository["repo"],
                        "branch": repository["branch"]
                    }
                }
            }, client_id)
            
            # Turn off typing indicator
            await self.send_personal_message({
                "type": "AGENT_TYPING",
                "payload": {"isTyping": False}
            }, client_id)
            
        except Exception as e:
            logger.error(f"Error in handle_fetch_files: {e}")
            await self.send_personal_message({
                "type": "FILE_TREE_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_chat_message(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle incoming chat messages"""
        try:
            text = payload.get("text", "")
            if not text:
                return
                
            # Save user message (don't send back to client - frontend already displays it)
            user_msg = await db.add_message(
                client_id=client_id,
                sender=MessageSender.USER,
                text=text
            )
            
            # Set typing indicator on
            await self.send_personal_message({
                "type": "AGENT_TYPING",
                "payload": {"isTyping": True}
            }, client_id)
            
            # Get user context
            config = await db.get_connection_config(client_id) or {}
            
            # Add selected repository information to the context if available
            repository_id = self.selected_repositories.get(client_id)
            if repository_id:
                repository = await github_model.get_repository(client_id, repository_id)
                if repository:
                    config["selected_repository"] = repository
            
            # Process the message with AI service
            response = await self.ai_service.process_message(text, config)
            
            # Save agent response
            agent_msg = await db.add_message(
                client_id=client_id,
                sender=MessageSender.AGENT,
                text=response
            )
            
            # Turn off typing indicator
            await self.send_personal_message({
                "type": "AGENT_TYPING",
                "payload": {"isTyping": False}
            }, client_id)
            
            # Send agent response
            await self.send_personal_message({
                "type": "NEW_CHAT_MESSAGE",
                "payload": agent_msg
            }, client_id)
            
        except Exception as e:
            logger.error(f"Error in handle_chat_message: {e}")
            # Send error message
            error_msg = await db.add_message(
                client_id=client_id,
                sender=MessageSender.SYSTEM,
                text=f"Error processing message: {str(e)}"
            )
            await self.send_personal_message({
                "type": "NEW_CHAT_MESSAGE",
                "payload": error_msg
            }, client_id)
            
            # Turn off typing indicator
            await self.send_personal_message({
                "type": "AGENT_TYPING",
                "payload": {"isTyping": False}
            }, client_id)
    
    async def handle_add_repository(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle adding a new repository"""
        try:
            logger.info(f"Received ADD_REPOSITORY request for client {client_id} with payload: {payload}")
            repository_data = payload.get("repository")
            if not repository_data:
                logger.error("Repository data is missing from payload")
                await self.send_personal_message({
                    "type": "REPOSITORY_ACTION_ERROR",
                    "payload": {"message": "Repository data is required"}
                }, client_id)
                return
                
            # Validate repository before adding
            logger.info(f"Validating repository: {repository_data.get('name')} ({repository_data.get('url')})")
            is_valid = await GitHubService.validate_repository(repository_data)
            if not is_valid:
                logger.error(f"Repository validation failed: {repository_data.get('name')} ({repository_data.get('url')})")
                await self.send_personal_message({
                    "type": "REPOSITORY_ACTION_ERROR",
                    "payload": {"message": "Invalid repository or unable to access with provided token"}
                }, client_id)
                return
            
            # Add repository to database
            repo = await github_model.add_repository(client_id, repository_data)
            logger.info(f"Repository added successfully: {repo.get('name')} ({repo.get('url')})")
            logger.debug(f"Repository data: {repo}")
            # Send success response
            await self.send_personal_message({
                "type": "REPOSITORY_ACTION_SUCCESS",
                "payload": {"repository": repo, "action": "add"}
            }, client_id)
            
            # Get all repositories and send updated list
            repos = await github_model.get_repositories(client_id)
            await self.send_personal_message({
                "type": "REPOSITORIES_LIST",
                "payload": {"repositories": repos}
            }, client_id)
            
            # If this is the first repository, select it and fetch its files
            if not self.selected_repositories.get(client_id):
                self.selected_repositories[client_id] = repo["id"]
                await self.handle_fetch_files(client_id, {"repository_id": repo["id"]})
            
        except Exception as e:
            logger.error(f"Error in handle_add_repository: {e}")
            await self.send_personal_message({
                "type": "REPOSITORY_ACTION_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_update_repository(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle updating an existing repository"""
        try:
            repository_id = payload.get("repository_id")
            repository_data = payload.get("repository")
            
            if not repository_id or not repository_data:
                await self.send_personal_message({
                    "type": "REPOSITORY_ACTION_ERROR",
                    "payload": {"message": "Repository ID and data are required"}
                }, client_id)
                return
                
            # Validate repository before updating
            is_valid = await GitHubService.validate_repository(repository_data)
            if not is_valid:
                await self.send_personal_message({
                    "type": "REPOSITORY_ACTION_ERROR",
                    "payload": {"message": "Invalid repository or unable to access with provided token"}
                }, client_id)
                return
            
            # Add ID to repository data
            repository_data["id"] = repository_id
            
            # Update repository in database
            repo = await github_model.add_repository(client_id, repository_data)
            
            # Send success response
            await self.send_personal_message({
                "type": "REPOSITORY_ACTION_SUCCESS",
                "payload": {"repository": repo, "action": "update"}
            }, client_id)
            
            # Get all repositories and send updated list
            repos = await github_model.get_repositories(client_id)
            await self.send_personal_message({
                "type": "REPOSITORIES_LIST",
                "payload": {"repositories": repos}
            }, client_id)
            
            # If this was the selected repository, refresh file tree
            if self.selected_repositories.get(client_id) == repository_id:
                await self.handle_fetch_files(client_id, {"repository_id": repository_id})
            
        except Exception as e:
            logger.error(f"Error in handle_update_repository: {e}")
            await self.send_personal_message({
                "type": "REPOSITORY_ACTION_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_delete_repository(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle deleting a repository"""
        try:
            repository_id = payload.get("repository_id")
            
            if not repository_id:
                await self.send_personal_message({
                    "type": "REPOSITORY_ACTION_ERROR",
                    "payload": {"message": "Repository ID is required"}
                }, client_id)
                return
            
            # Delete repository from database
            success = await github_model.delete_repository(client_id, repository_id)
            
            if not success:
                await self.send_personal_message({
                    "type": "REPOSITORY_ACTION_ERROR",
                    "payload": {"message": "Failed to delete repository"}
                }, client_id)
                return
            
            # Send success response
            await self.send_personal_message({
                "type": "REPOSITORY_ACTION_SUCCESS",
                "payload": {"repository_id": repository_id, "action": "delete"}
            }, client_id)
            
            # Get all repositories and send updated list
            repos = await github_model.get_repositories(client_id)
            await self.send_personal_message({
                "type": "REPOSITORIES_LIST",
                "payload": {"repositories": repos}
            }, client_id)
            
            # If this was the selected repository, select another one if available
            if self.selected_repositories.get(client_id) == repository_id:
                if repos:
                    # Select the first repository
                    self.selected_repositories[client_id] = repos[0]["id"]
                    await self.handle_fetch_files(client_id, {"repository_id": repos[0]["id"]})
                else:
                    # No repositories left, clear selection
                    self.selected_repositories.pop(client_id, None)
                    # Send empty file tree
                    await self.send_personal_message({
                        "type": "FILE_TREE_DATA",
                        "payload": {"tree": [], "repository": None}
                    }, client_id)
            
        except Exception as e:
            logger.error(f"Error in handle_delete_repository: {e}")
            await self.send_personal_message({
                "type": "REPOSITORY_ACTION_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_select_repository(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle selecting a repository to view"""
        try:
            repository_id = payload.get("repository_id")
            
            if not repository_id:
                await self.send_personal_message({
                    "type": "REPOSITORY_ACTION_ERROR",
                    "payload": {"message": "Repository ID is required"}
                }, client_id)
                return
            
            # Check if repository exists
            repository = await db.get_repository(client_id, repository_id)
            
            if not repository:
                await self.send_personal_message({
                    "type": "REPOSITORY_ACTION_ERROR",
                    "payload": {"message": "Repository not found"}
                }, client_id)
                return
            
            # Update selected repository
            self.selected_repositories[client_id] = repository_id
            
            # Send success response
            await self.send_personal_message({
                "type": "REPOSITORY_ACTION_SUCCESS",
                "payload": {"repository_id": repository_id, "action": "select"}
            }, client_id)
            
            # Fetch file tree for the selected repository
            await self.handle_fetch_files(client_id, {"repository_id": repository_id})
            
        except Exception as e:
            logger.error(f"Error in handle_select_repository: {e}")
            await self.send_personal_message({
                "type": "REPOSITORY_ACTION_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_get_issues(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle getting issues from a repository"""
        try:
            repository_id = payload.get("repository_id")
            state = payload.get("state", "open")
            
            if not repository_id:
                await self.send_personal_message({
                    "type": "GITHUB_ACTION_ERROR",
                    "payload": {"message": "Repository ID is required"}
                }, client_id)
                return
            
            # Fetch issues
            issues = await GitHubService.get_issues(client_id, repository_id, state)
            
            # Send response
            await self.send_personal_message({
                "type": "GITHUB_ISSUES_LIST",
                "payload": {"issues": issues, "repository_id": repository_id}
            }, client_id)
        
        except Exception as e:
            logger.error(f"Error in handle_get_issues: {e}")
            await self.send_personal_message({
                "type": "GITHUB_ACTION_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_get_assigned_issues(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle getting issues assigned to a user"""
        try:
            username = payload.get("username")
            
            if not username:
                await self.send_personal_message({
                    "type": "GITHUB_ACTION_ERROR",
                    "payload": {"message": "Username is required"}
                }, client_id)
                return
            
            # Fetch assigned issues
            issues = await GitHubService.get_assigned_issues(client_id, username)
            
            # Send response
            await self.send_personal_message({
                "type": "GITHUB_ISSUES_LIST",
                "payload": {"issues": issues, "assignee": username}
            }, client_id)
        
        except Exception as e:
            logger.error(f"Error in handle_get_assigned_issues: {e}")
            await self.send_personal_message({
                "type": "GITHUB_ACTION_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_create_issue(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle creating an issue in a repository"""
        try:
            repository_id = payload.get("repository_id")
            title = payload.get("title")
            body = payload.get("body")
            assignees = payload.get("assignees")
            labels = payload.get("labels")
            
            if not repository_id or not title:
                await self.send_personal_message({
                    "type": "GITHUB_ACTION_ERROR",
                    "payload": {"message": "Repository ID and title are required"}
                }, client_id)
                return
            
            # Create issue
            issue = await GitHubService.create_issue(
                client_id, repository_id, title, body or "", assignees, labels
            )
            
            # Send response
            await self.send_personal_message({
                "type": "GITHUB_ISSUE_ACTION_SUCCESS",
                "payload": {
                    "issue": issue,
                    "repository_id": repository_id,
                    "action": "create"
                }
            }, client_id)
        
        except Exception as e:
            logger.error(f"Error in handle_create_issue: {e}")
            await self.send_personal_message({
                "type": "GITHUB_ACTION_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_get_branches(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle getting branches from a repository"""
        try:
            repository_id = payload.get("repository_id")
            
            if not repository_id:
                await self.send_personal_message({
                    "type": "GITHUB_ACTION_ERROR",
                    "payload": {"message": "Repository ID is required"}
                }, client_id)
                return
            
            # Fetch branches
            branches = await GitHubService.get_branches(client_id, repository_id)
            
            # Send response
            await self.send_personal_message({
                "type": "GITHUB_BRANCHES_LIST",
                "payload": {"branches": branches, "repository_id": repository_id}
            }, client_id)
        
        except Exception as e:
            logger.error(f"Error in handle_get_branches: {e}")
            await self.send_personal_message({
                "type": "GITHUB_ACTION_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_create_branch(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle creating a branch in a repository"""
        try:
            repository_id = payload.get("repository_id")
            branch_name = payload.get("branch_name")
            base_branch = payload.get("base_branch")
            
            if not repository_id or not branch_name:
                await self.send_personal_message({
                    "type": "GITHUB_ACTION_ERROR",
                    "payload": {"message": "Repository ID and branch name are required"}
                }, client_id)
                return
            
            # Create branch
            branch = await GitHubService.create_branch(
                client_id, repository_id, branch_name, base_branch
            )
            
            # Send response
            await self.send_personal_message({
                "type": "GITHUB_BRANCH_ACTION_SUCCESS",
                "payload": {
                    "branch": branch,
                    "repository_id": repository_id,
                    "action": "create"
                }
            }, client_id)
            
            # Update branches list
            branches = await GitHubService.get_branches(client_id, repository_id)
            await self.send_personal_message({
                "type": "GITHUB_BRANCHES_LIST",
                "payload": {"branches": branches, "repository_id": repository_id}
            }, client_id)
        
        except Exception as e:
            logger.error(f"Error in handle_create_branch: {e}")
            await self.send_personal_message({
                "type": "GITHUB_ACTION_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_push_file(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle pushing a file to a repository"""
        try:
            repository_id = payload.get("repository_id")
            file_path = payload.get("file_path")
            content = payload.get("content")
            commit_message = payload.get("commit_message")
            branch = payload.get("branch")
            
            if not repository_id or not file_path or not content or not commit_message:
                await self.send_personal_message({
                    "type": "GITHUB_ACTION_ERROR",
                    "payload": {"message": "Repository ID, file path, content, and commit message are required"}
                }, client_id)
                return
            
            # Push file
            result = await GitHubService.push_file(
                client_id, repository_id, file_path, content, commit_message, branch
            )
            
            # Send response
            await self.send_personal_message({
                "type": "GITHUB_FILE_ACTION_SUCCESS",
                "payload": {
                    "result": result,
                    "repository_id": repository_id,
                    "action": "push"
                }
            }, client_id)
        
        except Exception as e:
            logger.error(f"Error in handle_push_file: {e}")
            await self.send_personal_message({
                "type": "GITHUB_ACTION_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_push_files(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle pushing multiple files to a repository"""
        try:
            repository_id = payload.get("repository_id")
            files = payload.get("files")
            commit_message = payload.get("commit_message")
            branch = payload.get("branch")
            
            if not repository_id or not files or not commit_message:
                await self.send_personal_message({
                    "type": "GITHUB_ACTION_ERROR",
                    "payload": {"message": "Repository ID, files, and commit message are required"}
                }, client_id)
                return
            
            # Prepare files for the API
            file_list = []
            for file in files:
                file_list.append({
                    "path": file["path"],
                    "content": file["content"]
                })
            
            # Push files
            result = await GitHubService.push_files(
                client_id, repository_id, file_list, commit_message, branch
            )
            
            # Send response
            await self.send_personal_message({
                "type": "GITHUB_FILE_ACTION_SUCCESS",
                "payload": {
                    "result": result,
                    "repository_id": repository_id,
                    "action": "push_multiple"
                }
            }, client_id)
        
        except Exception as e:
            logger.error(f"Error in handle_push_files: {e}")
            await self.send_personal_message({
                "type": "GITHUB_ACTION_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_create_pull_request(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle creating a pull request in a repository"""
        try:
            repository_id = payload.get("repository_id")
            title = payload.get("title")
            body = payload.get("body")
            head_branch = payload.get("head_branch")
            base_branch = payload.get("base_branch")
            
            if not repository_id or not title or not head_branch or not base_branch:
                await self.send_personal_message({
                    "type": "GITHUB_ACTION_ERROR",
                    "payload": {"message": "Repository ID, title, head branch, and base branch are required"}
                }, client_id)
                return
            
            # Create pull request
            pull_request = await GitHubService.create_pull_request(
                client_id, repository_id, title, body or "", head_branch, base_branch
            )
            
            # Send response
            await self.send_personal_message({
                "type": "GITHUB_PULL_REQUEST_ACTION_SUCCESS",
                "payload": {
                    "pull_request": pull_request,
                    "repository_id": repository_id,
                    "action": "create"
                }
            }, client_id)
        
        except Exception as e:
            logger.error(f"Error in handle_create_pull_request: {e}")
            await self.send_personal_message({
                "type": "GITHUB_ACTION_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
    async def handle_get_pull_requests(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle getting pull requests from a repository"""
        try:
            repository_id = payload.get("repository_id")
            state = payload.get("state", "open")
            
            if not repository_id:
                await self.send_personal_message({
                    "type": "GITHUB_ACTION_ERROR",
                    "payload": {"message": "Repository ID is required"}
                }, client_id)
                return
            
            # Fetch pull requests
            pull_requests = await GitHubService.get_pull_requests(client_id, repository_id, state)
            
            # Send response
            await self.send_personal_message({
                "type": "GITHUB_PULL_REQUESTS_LIST",
                "payload": {"pull_requests": pull_requests, "repository_id": repository_id}
            }, client_id)
        
        except Exception as e:
            logger.error(f"Error in handle_get_pull_requests: {e}")
            await self.send_personal_message({
                "type": "GITHUB_ACTION_ERROR",
                "payload": {"message": str(e)}
            }, client_id)
    
# Create a global instance of the connection manager
manager = ConnectionManager()
