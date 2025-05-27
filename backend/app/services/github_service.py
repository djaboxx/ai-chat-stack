"""
GitHub integration service
"""
from typing import List, Dict, Any, Optional
import logging
from github import Github, GithubException
from ..schemas.ws_schemas import FileNode, FileNodeType, Repository, RepositoryResponse

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
        try:
            # Extract repository data
            host = repository_data.get("host", "github.com")
            token = repository_data.get("token")
            owner = repository_data.get("owner")
            repo_name = repository_data.get("repo")
            branch = repository_data.get("branch", "main")
            
            if not all([token, owner, repo_name]):
                raise ValueError("Token, owner, and repo name are required")
            
            # Build full repo name
            full_repo_name = f"{owner}/{repo_name}"
            
            # Create GitHub instance with token and optional enterprise URL
            if host == "github.com":
                g = Github(token)
            else:
                # For GitHub Enterprise
                api_url = f"https://{host}/api/v3"
                g = Github(base_url=api_url, login_or_token=token)
            
            # Get the repository
            repo = g.get_repo(full_repo_name)
            
            # Get the top-level contents for the specified branch
            contents = repo.get_contents("", ref=branch)
            
            # Convert contents to FileNode objects
            file_nodes: List[FileNode] = []
            
            for content in contents:
                if content.type == "dir":
                    # It's a directory, recursively get its contents
                    file_nodes.append(
                        FileNode(
                            id=content.path,
                            name=content.name,
                            type=FileNodeType.DIRECTORY,
                            path=content.path,
                            children=GitHubService._get_directory_contents(repo, content.path, branch)
                        )
                    )
                else:
                    # It's a file
                    file_nodes.append(
                        FileNode(
                            id=content.path,
                            name=content.name,
                            type=FileNodeType.FILE,
                            path=content.path
                        )
                    )
            
            # Return file nodes with repository info
            return file_nodes
        
        except GithubException as e:
            logger.error(f"GitHub error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error fetching GitHub file tree: {e}")
            raise e
    
    @staticmethod
    async def validate_repository(repo_data: Dict[str, Any]) -> bool:
        """Validate that a repository exists and is accessible"""
        try:
            host = repo_data.get("host", "github.com")
            token = repo_data.get("token")
            owner = repo_data.get("owner")
            repo_name = repo_data.get("repo")
            
            if not all([token, owner, repo_name]):
                return False
            
            # Build full repo name
            full_repo_name = f"{owner}/{repo_name}"
            
            # Create GitHub instance with token and optional enterprise URL
            if host == "github.com":
                g = Github(token)
            else:
                # For GitHub Enterprise
                api_url = f"https://{host}/api/v3"
                g = Github(base_url=api_url, login_or_token=token)
            
            # Try to get the repository
            repo = g.get_repo(full_repo_name)
            # If we get here without an exception, repository exists
            return True
            
        except Exception as e:
            logger.error(f"Error validating repository: {e}")
            return False
    
    @staticmethod
    def _get_directory_contents(repo: Any, path: str, branch: str) -> List[FileNode]:
        """Recursively get directory contents"""
        contents = repo.get_contents(path, ref=branch)
        file_nodes: List[FileNode] = []
        
        for content in contents:
            if content.type == "dir":
                file_nodes.append(
                    FileNode(
                        id=content.path,
                        name=content.name,
                        type=FileNodeType.DIRECTORY,
                        path=content.path,
                        children=GitHubService._get_directory_contents(repo, content.path, branch)
                    )
                )
            else:
                file_nodes.append(
                    FileNode(
                        id=content.path,
                        name=content.name,
                        type=FileNodeType.FILE,
                        path=content.path
                    )
                )
        
        return file_nodes
