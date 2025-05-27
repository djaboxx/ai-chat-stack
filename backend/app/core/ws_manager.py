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
from ..schemas.ws_schemas import ChatMessage, MessageSender, FileNode
from ..services.github_service import GitHubService
from ..services.ai_service import AIAgentService

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.ai_service = AIAgentService()
    
    async def connect(self, websocket: WebSocket) -> str:
        """Connect a new WebSocket client"""
        await websocket.accept()
        client_id = str(uuid.uuid4())
        self.active_connections[client_id] = websocket
        db.add_connection(client_id)
        logger.info(f"Client connected: {client_id}")
        return client_id
    
    def disconnect(self, client_id: str) -> None:
        """Disconnect a WebSocket client"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        db.remove_connection(client_id)
        logger.info(f"Client disconnected: {client_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str) -> None:
        """Send a message to a specific client"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def handle_submit_config(self, client_id: str, payload: Dict[str, Any]) -> None:
        """Handle configuration submission"""
        try:
            # Store configuration in the database
            db.update_connection_config(client_id, payload)
            
            # Configure AI service with the provided API key
            self.ai_service.configure(payload.get("geminiToken", ""))
            
            # Send success response
            await self.send_personal_message({"type": "CONFIG_SUCCESS"}, client_id)
            
            # Send a welcome message
            system_msg = db.add_message(
                client_id=client_id,
                sender=MessageSender.SYSTEM,
                text="Configuration successful. You can now chat with the agent."
            )
            await self.send_personal_message({
                "type": "NEW_CHAT_MESSAGE",
                "payload": system_msg
            }, client_id)
            
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
            
            # Fetch file tree from GitHub
            repo = payload.get("repo", "")
            branch = payload.get("branch", "main")
            token = payload.get("githubToken", "")
            
            # Check if required parameters are provided
            if not repo or not token:
                await self.send_personal_message({
                    "type": "FILE_TREE_ERROR",
                    "payload": {"message": "Repository and GitHub token are required"}
                }, client_id)
                return
                
            # Fetch the file tree
            file_tree = await GitHubService.fetch_file_tree(repo, branch, token)
            
            # Send the file tree to the client
            await self.send_personal_message({
                "type": "FILE_TREE_DATA",
                "payload": {"tree": [node.model_dump() for node in file_tree]}
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
            user_msg = db.add_message(
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
            config = db.get_connection_config(client_id) or {}
            
            # Process the message with AI service
            response = await self.ai_service.process_message(text, config)
            
            # Save agent response
            agent_msg = db.add_message(
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
            error_msg = db.add_message(
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


# Create a single connection manager instance
manager = ConnectionManager()
