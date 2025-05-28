"""
GitHub integration service
"""
from typing import List, Dict, Any, Optional, Union
import logging
from ..models.github_model import github_model
from ..schemas.ws_schemas import (
    FileNode, FileNodeType, Repository, RepositoryResponse,
    GitHubIssue, GitHubBranch, GitHubPullRequest, FileCommit
)

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for interacting with GitHub API"""
    
    @staticmethod
    async def fetch_file_tree(repository_data: Dict[str, Any]) -> List[FileNode]:
        """
        Fetch file tree from GitHub repository
        
        Args:
            repository_data: Dict containing repository info including host, token, owner, repo, branch
        """
        # Delegate to the GitHub model to fetch the file tree
        return await github_model.fetch_file_tree(repository_data)
    
    @staticmethod
    async def validate_repository(repo_data: Dict[str, Any]) -> bool:
        """Validate that a repository exists and is accessible"""
        return await github_model.validate_repository(repo_data)
    
    @staticmethod
    async def get_issues(client_id: str, repository_id: str, state: str = "open") -> List[Dict[str, Any]]:
        """Get issues from a GitHub repository"""
        return await github_model.get_issues(client_id, repository_id, state)
    
    @staticmethod
    async def get_assigned_issues(client_id: str, username: str) -> List[Dict[str, Any]]:
        """Get issues assigned to a specific user across all repositories"""
        return await github_model.get_assigned_issues(client_id, username)
    
    @staticmethod
    async def create_issue(client_id: str, repository_id: str, title: str, body: str, 
                           assignees: Optional[List[str]] = None, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new issue in a GitHub repository"""
        return await github_model.create_issue(client_id, repository_id, title, body, assignees, labels)
    
    @staticmethod
    async def create_branch(client_id: str, repository_id: str, branch_name: str, 
                            base_branch: Optional[str] = None) -> Dict[str, Any]:
        """Create a new branch in a GitHub repository"""
        return await github_model.create_branch(client_id, repository_id, branch_name, base_branch)
    
    @staticmethod
    async def get_branches(client_id: str, repository_id: str) -> List[Dict[str, Any]]:
        """Get branches for a GitHub repository"""
        return await github_model.get_branches(client_id, repository_id)
    
    @staticmethod
    async def push_file(client_id: str, repository_id: str, file_path: str, content: str,
                        commit_message: str, branch: Optional[str] = None) -> Dict[str, Any]:
        """Push a single file to a GitHub repository"""
        return await github_model.push_file(client_id, repository_id, file_path, content, commit_message, branch)
    
    @staticmethod
    async def push_files(client_id: str, repository_id: str, files: List[Dict[str, str]],
                         commit_message: str, branch: Optional[str] = None) -> Dict[str, Any]:
        """Push multiple files to a GitHub repository in a single commit"""
        return await github_model.push_files(client_id, repository_id, files, commit_message, branch)
    
    @staticmethod
    async def create_pull_request(client_id: str, repository_id: str, title: str, body: str,
                                  head_branch: str, base_branch: str) -> Dict[str, Any]:
        """Create a pull request in a GitHub repository"""
        return await github_model.create_pull_request(client_id, repository_id, title, body, head_branch, base_branch)
    
    @staticmethod
    async def get_pull_requests(client_id: str, repository_id: str, state: str = "open") -> List[Dict[str, Any]]:
        """Get pull requests from a GitHub repository"""
        return await github_model.get_pull_requests(client_id, repository_id, state)
    
    @staticmethod
    async def get_file_content(client_id: str, repository_id: str, file_path: str, 
                               branch: Optional[str] = None) -> Dict[str, Any]:
        """Get the contents of a file from GitHub"""
        return await github_model.get_file_content(client_id, repository_id, file_path, branch)
