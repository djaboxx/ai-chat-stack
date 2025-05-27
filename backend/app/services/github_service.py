"""
GitHub integration service
"""
from typing import List, Dict, Any, Optional
import logging
from github import Github, GithubException
from ..schemas.ws_schemas import FileNode, FileNodeType

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for interacting with GitHub API"""
    
    @staticmethod
    async def fetch_file_tree(repo_name: str, branch: str, token: str) -> List[FileNode]:
        """Fetch file tree from GitHub repository"""
        try:
            # Create GitHub instance with token
            g = Github(token)
            
            # Get the repository
            repo = g.get_repo(repo_name)
            
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
            
            return file_nodes
        
        except GithubException as e:
            logger.error(f"GitHub error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error fetching GitHub file tree: {e}")
            raise e
    
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
