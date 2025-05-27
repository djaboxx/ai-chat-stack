"""
Database models with MongoDB integration
"""
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import logging
from ..core.mongodb import mongodb

logger = logging.getLogger(__name__)

class MongoDB:
    """MongoDB database interface"""
    
    async def add_connection(self, client_id: str) -> None:
        """Add a new WebSocket connection"""
        try:
            await mongodb.db.connections.update_one(
                {"client_id": client_id},
                {"$set": {"client_id": client_id, "active": True}},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error adding connection: {e}")

    async def remove_connection(self, client_id: str) -> None:
        """Mark a WebSocket connection as inactive"""
        try:
            await mongodb.db.connections.update_one(
                {"client_id": client_id},
                {"$set": {"active": False}}
            )
        except Exception as e:
            logger.error(f"Error removing connection: {e}")

    async def update_connection_config(self, client_id: str, config: Dict[str, Any]) -> None:
        """Update configuration for a connection"""
        try:
            await mongodb.db.connections.update_one(
                {"client_id": client_id},
                {"$set": {"config": config}}
            )
        except Exception as e:
            logger.error(f"Error updating connection config: {e}")
    
    async def get_connection_config(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a connection"""
        try:
            connection = await mongodb.db.connections.find_one({"client_id": client_id})
            if connection and "config" in connection:
                return connection["config"]
        except Exception as e:
            logger.error(f"Error getting connection config: {e}")
        return None

    async def add_message(self, client_id: str, sender: str, text: str) -> Dict[str, Any]:
        """Add a new message"""
        try:
            message = {
                "id": str(uuid.uuid4()),
                "sender": sender,
                "text": text, 
                "timestamp": int(datetime.now().timestamp() * 1000),
                "client_id": client_id
            }
            await mongodb.db.messages.insert_one(message)
            # Remove _id field from message (ObjectId is not JSON serializable)
            return {k: v for k, v in message.items() if k != '_id'}
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            # Fallback to returning message without DB insertion
            return {
                "id": str(uuid.uuid4()),
                "sender": sender,
                "text": text, 
                "timestamp": int(datetime.now().timestamp() * 1000),
                "client_id": client_id
            }
    
    async def get_messages(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a client"""
        try:
            cursor = mongodb.db.messages.find({"client_id": client_id}).sort("timestamp", 1)
            messages = []
            async for message in cursor:
                # Remove _id field (ObjectId is not JSON serializable)
                message.pop("_id", None)
                messages.append(message)
            return messages
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    async def add_repository(self, client_id: str, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add or update a repository for a client"""
        try:
            logger.info(f"Adding repository for client {client_id}: {repo_data.get('name')}")
            repo = {
                "id": repo_data.get("id", str(uuid.uuid4())),
                "name": repo_data["name"],
                "url": repo_data["url"],
                "host": repo_data.get("host", "github.com"),  # Default to github.com
                "owner": repo_data["owner"],
                "repo": repo_data["repo"],
                "branch": repo_data.get("branch", "main"),
                "token": repo_data["token"],
                "client_id": client_id,
                "created_at": int(datetime.now().timestamp() * 1000)
            }
            
            # Use upsert to add or update
            logger.info(f"MongoDB URI: {mongodb.client.address}")
            logger.info(f"MongoDB Database: {mongodb.db.name}")
            logger.info(f"Upserting repository {repo['name']} for client {client_id}")
            result = await mongodb.db.repositories.update_one(
                {"client_id": client_id, "name": repo["name"]},
                {"$set": repo},
                upsert=True
            )
            logger.info(f"Repository upsert result: matched={result.matched_count}, modified={result.modified_count}, upserted={result.upserted_id is not None}")
            
            # Remove token before returning
            repo_response = repo.copy()
            repo_response.pop("token", None)
            repo_response.pop("_id", None)
            return repo_response
            
        except Exception as e:
            logger.error(f"Error adding repository: {e}")
            raise
    
    async def get_repositories(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all repositories for a client"""
        try:
            cursor = mongodb.db.repositories.find({"client_id": client_id})
            repos = []
            async for repo in cursor:
                # Don't include tokens or _id in response
                repo.pop("_id", None)
                repo.pop("token", None)
                repos.append(repo)
            return repos
        except Exception as e:
            logger.error(f"Error getting repositories: {e}")
            return []
    
    async def get_repository(self, client_id: str, repo_id: str) -> Optional[Dict[str, Any]]:
        """Get a repository by ID"""
        try:
            repo = await mongodb.db.repositories.find_one({"client_id": client_id, "id": repo_id})
            if repo:
                # Don't include _id in response
                repo.pop("_id", None)
                return repo
        except Exception as e:
            logger.error(f"Error getting repository: {e}")
        return None
    
    async def delete_repository(self, client_id: str, repo_id: str) -> bool:
        """Delete a repository"""
        try:
            result = await mongodb.db.repositories.delete_one({"client_id": client_id, "id": repo_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting repository: {e}")
            return False

# Create a single database instance
db = MongoDB()
