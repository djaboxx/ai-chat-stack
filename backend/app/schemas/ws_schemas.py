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


class GitHubIssueState(str, Enum):
    """Issue state enumeration"""
    OPEN = "open"
    CLOSED = "closed"
    ALL = "all"


class GitHubIssue(BaseModel):
    """Schema for GitHub issues"""
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: GitHubIssueState
    html_url: str
    created_at: str
    updated_at: str
    labels: List[Dict[str, Any]] = []
    assignees: List[Dict[str, Any]] = []
    repository_id: str  # Link to our repository ID


class GitHubBranch(BaseModel):
    """Schema for GitHub branches"""
    name: str
    commit_sha: str
    protected: bool = False


class GitHubPullRequest(BaseModel):
    """Schema for GitHub pull requests"""
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: str
    html_url: str
    created_at: str
    updated_at: str
    head_branch: str
    base_branch: str
    repository_id: str  # Link to our repository ID


class FileCommit(BaseModel):
    """Schema for file commit operations"""
    path: str
    content: str
    message: Optional[str] = None


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
                  DeleteRepositoryPayload, SelectRepositoryPayload,
                  GetIssuesPayload, GetAssignedIssuesPayload, CreateIssuePayload,
                  GetBranchesPayload, CreateBranchPayload, PushFilePayload, PushFilesPayload,
                  CreatePullRequestPayload, GetPullRequestsPayload, Dict[str, Any]]


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


class GetIssuesPayload(BaseModel):
    """Payload for fetching issues from GitHub"""
    repository_id: str
    state: Optional[str] = "open"


class GetAssignedIssuesPayload(BaseModel):
    """Payload for fetching issues assigned to a user"""
    username: str


class CreateIssuePayload(BaseModel):
    """Payload for creating a GitHub issue"""
    repository_id: str
    title: str
    body: str
    assignees: Optional[List[str]] = None
    labels: Optional[List[str]] = None


class GetBranchesPayload(BaseModel):
    """Payload for fetching branches from GitHub"""
    repository_id: str


class CreateBranchPayload(BaseModel):
    """Payload for creating a GitHub branch"""
    repository_id: str
    branch_name: str
    base_branch: Optional[str] = None


class PushFilePayload(BaseModel):
    """Payload for pushing a file to GitHub"""
    repository_id: str
    file_path: str
    content: str
    commit_message: str
    branch: Optional[str] = None


class PushFilesPayload(BaseModel):
    """Payload for pushing multiple files to GitHub"""
    repository_id: str
    files: List[FileCommit]
    commit_message: str
    branch: Optional[str] = None


class CreatePullRequestPayload(BaseModel):
    """Payload for creating a GitHub pull request"""
    repository_id: str
    title: str
    body: str
    head_branch: str
    base_branch: str


class GetPullRequestsPayload(BaseModel):
    """Payload for fetching pull requests from GitHub"""
    repository_id: str
    state: Optional[str] = "open"


class GithubIssuesListMessage(BaseModel):
    """GitHub issues list message"""
    type: str = "GITHUB_ISSUES_LIST"
    payload: Dict[str, List[Dict[str, Any]]]


class GithubIssueActionSuccessMessage(BaseModel):
    """GitHub issue action success message"""
    type: str = "GITHUB_ISSUE_ACTION_SUCCESS"
    payload: Dict[str, Any]


class GithubBranchesListMessage(BaseModel):
    """GitHub branches list message"""
    type: str = "GITHUB_BRANCHES_LIST"
    payload: Dict[str, List[Dict[str, Any]]]


class GithubBranchActionSuccessMessage(BaseModel):
    """GitHub branch action success message"""
    type: str = "GITHUB_BRANCH_ACTION_SUCCESS"
    payload: Dict[str, Any]


class GithubFileActionSuccessMessage(BaseModel):
    """GitHub file action success message"""
    type: str = "GITHUB_FILE_ACTION_SUCCESS"
    payload: Dict[str, Any]


class GithubPullRequestsListMessage(BaseModel):
    """GitHub pull requests list message"""
    type: str = "GITHUB_PULL_REQUESTS_LIST"
    payload: Dict[str, List[Dict[str, Any]]]


class GithubPullRequestActionSuccessMessage(BaseModel):
    """GitHub pull request action success message"""
    type: str = "GITHUB_PULL_REQUEST_ACTION_SUCCESS"
    payload: Dict[str, Any]


class GithubActionErrorMessage(BaseModel):
    """GitHub action error message"""
    type: str = "GITHUB_ACTION_ERROR"
    payload: Dict[str, str]


class GetFileContentPayload(BaseModel):
    """Payload for fetching file content from GitHub"""
    repository_id: str
    file_path: str
    branch: Optional[str] = None
