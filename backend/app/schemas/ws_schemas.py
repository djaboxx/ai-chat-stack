"""
Pydantic schemas for the application
"""
from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


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


# Client -> Server Message Types
class ConfigData(BaseModel):
    """Configuration data from client"""
    githubToken: str
    geminiToken: str
    githubRepo: str
    githubBranch: str
    selectedFiles: List[str]


class FetchFilesPayload(BaseModel):
    """Payload for fetching files from GitHub"""
    repo: str
    branch: str
    githubToken: str


class SendChatMessagePayload(BaseModel):
    """Payload for sending chat messages"""
    text: str


# Client -> Server Message Union Type
class ClientMessage(BaseModel):
    """Base model for client messages"""
    type: str
    payload: Union[ConfigData, FetchFilesPayload, SendChatMessagePayload, Dict[str, Any]]


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
    payload: Dict[str, List[FileNode]]


class FileTreeErrorMessage(BaseModel):
    """File tree error message"""
    type: str = "FILE_TREE_ERROR"
    payload: Dict[str, str]


class NewChatMessage(BaseModel):
    """New chat message"""
    type: str = "NEW_CHAT_MESSAGE"
    payload: ChatMessage


class AgentTypingMessage(BaseModel):
    """Agent typing status message"""
    type: str = "AGENT_TYPING"
    payload: Dict[str, bool]
