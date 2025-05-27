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
from ..core.mongodb import mongodb
from ..schemas.ws_schemas import (
    ChatMessage, MessageSender, FileNode, Repository, 
    RepositoryResponse
)
from ..services.github_service import GitHubService
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
                    await db.add_repository(client_id, repo_data)
                
                # Get all repositories and send them back
                repos = await db.get_repositories(client_id)
                await self.send_personal_message({
                    "type": "REPOSITORIES_LIST",
                    "payload": {"repositories": repos}
                }, client_id)
                
                # Select the first repository by default
                if repos and len(repos) > 0:
                    first_repo = repos[0]
                    self.selected_repositories[client_id] = first_repo["id"]
                    
                    # Fetch file tree for the first repository
                    repo_details = await db.get_repository(client_id, first_repo["id"])
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
            repository = await db.get_repository(client_id, repository_id)
            
            if not repository:
                await self.send_personal_message({
                    "type": "FILE_TREE_ERROR",
                    "payload": {"message": "Repository not found"}
                }, client_id)
                return
            
            # Update selected repository for this client
            self.selected_repositories[client_id] = repository_id
                
            # Fetch the file tree using repository details
            file_tree = await GitHubService.fetch_file_tree(repository)
            
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
                repository = await db.get_repository(client_id, repository_id)
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
            repository_data = payload.get("repository")
            if not repository_data:
                await self.send_personal_message({
                    "type": "REPOSITORY_ACTION_ERROR",
                    "payload": {"message": "Repository data is required"}
                }, client_id)
                return
                
            # Validate repository before adding
            is_valid = await GitHubService.validate_repository(repository_data)
            if not is_valid:
                await self.send_personal_message({
                    "type": "REPOSITORY_ACTION_ERROR",
                    "payload": {"message": "Invalid repository or unable to access with provided token"}
                }, client_id)
                return
            
            # Add repository to database
            repo = await db.add_repository(client_id, repository_data)
            
            # Send success response
            await self.send_personal_message({
                "type": "REPOSITORY_ACTION_SUCCESS",
                "payload": {"repository": repo, "action": "add"}
            }, client_id)
            
            # Get all repositories and send updated list
            repos = await db.get_repositories(client_id)
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
            repo = await db.add_repository(client_id, repository_data)
            
            # Send success response
            await self.send_personal_message({
                "type": "REPOSITORY_ACTION_SUCCESS",
                "payload": {"repository": repo, "action": "update"}
            }, client_id)
            
            # Get all repositories and send updated list
            repos = await db.get_repositories(client_id)
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
            success = await db.delete_repository(client_id, repository_id)
            
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
            repos = await db.get_repositories(client_id)
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

# Create a global instance of the connection manager
manager = ConnectionManager()
