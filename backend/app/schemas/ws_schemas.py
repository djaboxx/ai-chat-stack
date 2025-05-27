"""
Pydantic schemas for the application
"""
from enum import Enum
import uuid
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class MessageSender(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Schema for chat messages"""
    id: str
    sender: MessageSender
    text: str
    timestamp: int


class FileNodeType(str, Enum):
    FILE = "file"
    DIRECTORY = "directory"


class FileNode(BaseModel):
    """Schema for file tree nodes"""
    id: str
    name: str
    type: FileNodeType
    path: str
    children: Optional[List['FileNode']] = None


class Repository(BaseModel):
    """Schema for a GitHub repository"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    url: str
    host: str = "github.com"  # Default to github.com, can be a GH Enterprise domain
    owner: str
    repo: str
    branch: str = "main"
    token: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "My React App",
                "url": "https://github.com/user/repo",
                "host": "github.com",
                "owner": "user",
                "repo": "repo",
                "branch": "main",
                "token": "ghp_xxxxxxxxxxxx"
            }
        }


class RepositoryResponse(BaseModel):
    """Schema for repository response (no token)"""
    id: str
    name: str
    url: str
    host: str
    owner: str
    repo: str
    branch: str
    created_at: int


# Client -> Server Message Types
class ConfigData(BaseModel):
    """Configuration data from client"""
    geminiToken: str
    repositories: List[Repository] = []


class FetchFilesPayload(BaseModel):
    """Payload for fetching files from GitHub"""
    repository_id: str


class SendChatMessagePayload(BaseModel):
    """Payload for sending chat messages"""
    text: str


class AddRepositoryPayload(BaseModel):
    """Payload for adding a repository"""
    repository: Repository


class UpdateRepositoryPayload(BaseModel):
    """Payload for updating repository details"""
    repository_id: str
    repository: Repository


class DeleteRepositoryPayload(BaseModel):
    """Payload for deleting a repository"""
    repository_id: str


class SelectRepositoryPayload(BaseModel):
    """Payload for selecting a repository"""
    repository_id: str


# Client -> Server Message Union Type
class ClientMessage(BaseModel):
    """Base model for client messages"""
    type: str
    payload: Union[ConfigData, FetchFilesPayload, SendChatMessagePayload, 
                  AddRepositoryPayload, UpdateRepositoryPayload, 
                  DeleteRepositoryPayload, SelectRepositoryPayload, Dict[str, Any]]


# Server -> Client Message Types
class ConfigSuccessMessage(BaseModel):
    """Success message for configuration"""
    type: str = "CONFIG_SUCCESS"


class ConfigErrorMessage(BaseModel):
    """Error message for configuration"""
    type: str = "CONFIG_ERROR"
    payload: Dict[str, str]


class FileTreeDataMessage(BaseModel):
    """File tree data message"""
    type: str = "FILE_TREE_DATA"
    payload: Dict[str, Any]


class FileTreeErrorMessage(BaseModel):
    """File tree error message"""
    type: str = "FILE_TREE_ERROR"
    payload: Dict[str, str]


class RepositoriesListMessage(BaseModel):
    """Repositories list message"""
    type: str = "REPOSITORIES_LIST"
    payload: Dict[str, List[RepositoryResponse]]


class RepositoryActionSuccessMessage(BaseModel):
    """Repository action success message"""
    type: str = "REPOSITORY_ACTION_SUCCESS"
    payload: Dict[str, Any]


class RepositoryActionErrorMessage(BaseModel):
    """Repository action error message"""
    type: str = "REPOSITORY_ACTION_ERROR"
    payload: Dict[str, str]


class NewChatMessage(BaseModel):
    """New chat message"""
    type: str = "NEW_CHAT_MESSAGE"
    payload: ChatMessage


class AgentTypingMessage(BaseModel):
    """Agent typing status message"""
    type: str = "AGENT_TYPING"
    payload: Dict[str, bool]
