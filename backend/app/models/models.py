"""
Database models (in-memory for this example)
"""
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime


class InMemoryConnection:
    """In-memory connection store"""
    def __init__(self):
        self.client_id: str = str(uuid.uuid4())
        self.config: Dict[str, Any] = {}
        self.active: bool = True
        

class InMemoryDatabase:
    """Simple in-memory database for development purposes"""
    def __init__(self):
        self.connections: Dict[str, InMemoryConnection] = {}
        self.messages: List[Dict[str, Any]] = []

    def add_connection(self, client_id: str) -> None:
        """Add a new WebSocket connection"""
        if client_id not in self.connections:
            self.connections[client_id] = InMemoryConnection()

    def remove_connection(self, client_id: str) -> None:
        """Remove a WebSocket connection"""
        if client_id in self.connections:
            del self.connections[client_id]

    def update_connection_config(self, client_id: str, config: Dict[str, Any]) -> None:
        """Update configuration for a connection"""
        if client_id in self.connections:
            self.connections[client_id].config = config
    
    def get_connection_config(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a connection"""
        if client_id in self.connections:
            return self.connections[client_id].config
        return None

    def add_message(self, client_id: str, sender: str, text: str) -> Dict[str, Any]:
        """Add a new message"""
        message = {
            "id": str(uuid.uuid4()),
            "sender": sender,
            "text": text, 
            "timestamp": int(datetime.now().timestamp() * 1000),
            "client_id": client_id
        }
        self.messages.append(message)
        return message


# Create a single in-memory database instance
db = InMemoryDatabase()
