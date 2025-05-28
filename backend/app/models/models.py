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

# Create a single database instance
db = MongoDB()
