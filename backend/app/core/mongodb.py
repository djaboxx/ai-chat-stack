"""
MongoDB connection manager
"""
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

# Get MongoDB URI from environment variable or use a default
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://admin:password@mongodb:27017")
DB_NAME = os.environ.get("DB_NAME", "ai_chat_app")

# Log the MongoDB connection details
logger.info(f"MongoDB URI: {MONGODB_URI}")
logger.info(f"MongoDB DB Name: {DB_NAME}")

class MongoDBManager:
    """MongoDB connection manager"""
    
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(MONGODB_URI)
            # Verify connection is successful
            await self.client.admin.command('ping')
            self.db = self.client[DB_NAME]
            
            # Create indexes
            await self._create_indexes()
            
            logger.info("Connected to MongoDB")
            return self.db
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def _create_indexes(self):
        """Create necessary indexes for performance"""
        # Connection index
        await self.db.connections.create_index("client_id", unique=True)
        # Messages index
        await self.db.messages.create_index("client_id")
        # Repositories index
        await self.db.repositories.create_index([("client_id", 1), ("name", 1)], unique=True)
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Create a singleton instance
mongodb = MongoDBManager()
