"""
GitHub repository models with MongoDB integration
"""
from typing import List, Dict, Any, Optional, Union
import uuid
import base64
from datetime import datetime
import logging
from github import Github, GithubException, InputGitTreeElement
from ..core.mongodb import mongodb
from ..schemas.ws_schemas import Repository, RepositoryResponse, FileNode, FileNodeType, GitHubIssue

logger = logging.getLogger(__name__)


class GitHubModel:
    """GitHub repository model with MongoDB integration"""
    
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
    
    async def validate_repository(self, repo_data: Dict[str, Any]) -> bool:
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
    
    async def fetch_file_tree(self, repository_data: Dict[str, Any]) -> List[FileNode]:
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
                            children=self._get_directory_contents(repo, content.path, branch)
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
    
    def _get_directory_contents(self, repo: Any, path: str, branch: str) -> List[FileNode]:
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
                        children=self._get_directory_contents(repo, content.path, branch)
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
    
    async def get_issues(self, client_id: str, repo_id: str, state: str = "open") -> List[Dict[str, Any]]:
        """Get issues from a GitHub repository"""
        try:
            # Get repository details to access GitHub
            repo_data = await self.get_repository(client_id, repo_id)
            if not repo_data or "token" not in repo_data:
                # Refetch with token if missing
                repo_data = await mongodb.db.repositories.find_one({"client_id": client_id, "id": repo_id})
                if not repo_data:
                    logger.error(f"Repository not found for client {client_id}, repo_id {repo_id}")
                    return []
            
            # Setup GitHub client
            g = self._get_github_client(repo_data)
            
            # Get repository
            full_repo_name = f"{repo_data['owner']}/{repo_data['repo']}"
            repo = g.get_repo(full_repo_name)
            
            # Get issues
            github_issues = repo.get_issues(state=state)
            
            # Convert to our schema format
            issues = []
            for issue in github_issues:
                issues.append({
                    "id": issue.id,
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body,
                    "state": issue.state,
                    "html_url": issue.html_url,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat(),
                    "labels": [{"name": label.name, "color": label.color} for label in issue.labels],
                    "assignees": [{"login": assignee.login, "avatar_url": assignee.avatar_url} for assignee in issue.assignees],
                    "repository_id": repo_id
                })
                
                # Store in MongoDB for syncing
                await self._sync_issue(client_id, repo_id, issues[-1])
                
            return issues
            
        except Exception as e:
            logger.error(f"Error getting issues: {e}")
            return []
    
    async def get_assigned_issues(self, client_id: str, username: str) -> List[Dict[str, Any]]:
        """Get issues assigned to a specific user across all repositories"""
        try:
            # Get all repositories for the client
            repos = await self.get_repositories(client_id)
            all_issues = []
            
            for repo in repos:
                repo_data = await mongodb.db.repositories.find_one({"client_id": client_id, "id": repo["id"]})
                if not repo_data:
                    continue
                
                # Setup GitHub client
                g = self._get_github_client(repo_data)
                
                # Get repository
                full_repo_name = f"{repo_data['owner']}/{repo_data['repo']}"
                github_repo = g.get_repo(full_repo_name)
                
                # Get issues assigned to the user
                issues = github_repo.get_issues(assignee=username)
                
                for issue in issues:
                    issue_data = {
                        "id": issue.id,
                        "number": issue.number,
                        "title": issue.title,
                        "body": issue.body,
                        "state": issue.state,
                        "html_url": issue.html_url,
                        "created_at": issue.created_at.isoformat(),
                        "updated_at": issue.updated_at.isoformat(),
                        "labels": [{"name": label.name, "color": label.color} for label in issue.labels],
                        "assignees": [{"login": assignee.login, "avatar_url": assignee.avatar_url} for assignee in issue.assignees],
                        "repository_id": repo["id"],
                        "repository_name": repo["name"]
                    }
                    
                    all_issues.append(issue_data)
                    # Store in MongoDB for syncing
                    await self._sync_issue(client_id, repo["id"], issue_data)
            
            return all_issues
            
        except Exception as e:
            logger.error(f"Error getting assigned issues: {e}")
            return []
    
    async def create_issue(self, client_id: str, repo_id: str, title: str, body: str, 
                           assignees: Optional[List[str]] = None, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new issue in a GitHub repository"""
        try:
            # Get repository details
            repo_data = await mongodb.db.repositories.find_one({"client_id": client_id, "id": repo_id})
            if not repo_data:
                logger.error(f"Repository not found for client {client_id}, repo_id {repo_id}")
                raise ValueError("Repository not found")
            
            # Setup GitHub client
            g = self._get_github_client(repo_data)
            
            # Get repository
            full_repo_name = f"{repo_data['owner']}/{repo_data['repo']}"
            repo = g.get_repo(full_repo_name)
            
            # Create issue
            issue = repo.create_issue(
                title=title,
                body=body,
                assignees=assignees or [],
                labels=labels or []
            )
            
            # Format response
            issue_data = {
                "id": issue.id,
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "html_url": issue.html_url,
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "labels": [{"name": label.name, "color": label.color} for label in issue.labels],
                "assignees": [{"login": assignee.login, "avatar_url": assignee.avatar_url} for assignee in issue.assignees],
                "repository_id": repo_id
            }
            
            # Store in MongoDB for syncing
            await self._sync_issue(client_id, repo_id, issue_data)
            
            return issue_data
            
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            raise
    
    async def _sync_issue(self, client_id: str, repo_id: str, issue_data: Dict[str, Any]) -> None:
        """Sync issue with MongoDB"""
        try:
            # Add client_id for querying
            issue_data["client_id"] = client_id
            
            # Upsert issue in MongoDB
            await mongodb.db.issues.update_one(
                {"client_id": client_id, "repository_id": repo_id, "number": issue_data["number"]},
                {"$set": issue_data},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error syncing issue: {e}")
    
    async def create_branch(self, client_id: str, repo_id: str, branch_name: str, base_branch: Optional[str] = None) -> Dict[str, Any]:
        """Create a new branch in a repository"""
        try:
            # Get repository details
            repo_data = await mongodb.db.repositories.find_one({"client_id": client_id, "id": repo_id})
            if not repo_data:
                logger.error(f"Repository not found for client {client_id}, repo_id {repo_id}")
                raise ValueError("Repository not found")
            
            # Setup GitHub client
            g = self._get_github_client(repo_data)
            
            # Get repository
            full_repo_name = f"{repo_data['owner']}/{repo_data['repo']}"
            repo = g.get_repo(full_repo_name)
            
            # Determine base branch
            if not base_branch:
                base_branch = repo_data.get("branch", "main")
            
            # Get the latest commit on the base branch
            base_branch_ref = repo.get_branch(base_branch)
            base_sha = base_branch_ref.commit.sha
            
            # Create new branch reference
            ref = f"refs/heads/{branch_name}"
            repo.create_git_ref(ref=ref, sha=base_sha)
            
            # Return branch info
            branch_data = {
                "name": branch_name,
                "commit_sha": base_sha,
                "protected": False,
                "base_branch": base_branch
            }
            
            return branch_data
        
        except Exception as e:
            logger.error(f"Error creating branch: {e}")
            raise
    
    async def get_branches(self, client_id: str, repo_id: str) -> List[Dict[str, Any]]:
        """Get branches for a repository"""
        try:
            # Get repository details
            repo_data = await mongodb.db.repositories.find_one({"client_id": client_id, "id": repo_id})
            if not repo_data:
                logger.error(f"Repository not found for client {client_id}, repo_id {repo_id}")
                return []
            
            # Setup GitHub client
            g = self._get_github_client(repo_data)
            
            # Get repository
            full_repo_name = f"{repo_data['owner']}/{repo_data['repo']}"
            repo = g.get_repo(full_repo_name)
            
            # Get branches
            branches = []
            for branch in repo.get_branches():
                branches.append({
                    "name": branch.name,
                    "commit_sha": branch.commit.sha,
                    "protected": branch.protected
                })
            
            return branches
        
        except Exception as e:
            logger.error(f"Error getting branches: {e}")
            return []
    
    async def push_file(self, client_id: str, repo_id: str, file_path: str, content: str, 
                        commit_message: str, branch: Optional[str] = None) -> Dict[str, Any]:
        """Push a file to a GitHub repository"""
        try:
            # Get repository details
            repo_data = await mongodb.db.repositories.find_one({"client_id": client_id, "id": repo_id})
            if not repo_data:
                logger.error(f"Repository not found for client {client_id}, repo_id {repo_id}")
                raise ValueError("Repository not found")
            
            # Setup GitHub client
            g = self._get_github_client(repo_data)
            
            # Get repository
            full_repo_name = f"{repo_data['owner']}/{repo_data['repo']}"
            repo = g.get_repo(full_repo_name)
            
            # Determine branch
            if not branch:
                branch = repo_data.get("branch", "main")
            
            # Check if file exists to update or create
            file_sha = None
            try:
                contents = repo.get_contents(file_path, ref=branch)
                if isinstance(contents, list):
                    # This is a directory, not a file
                    raise ValueError(f"Path '{file_path}' is a directory, not a file")
                file_sha = contents.sha
            except GithubException as e:
                if e.status != 404:  # Not a "not found" error
                    raise
                # File doesn't exist, will be created
            
            # Create or update file
            result = repo.create_file(
                path=file_path,
                message=commit_message,
                content=content,
                branch=branch,
                sha=file_sha  # None for new file, sha for update
            )
            
            return {
                "commit": {
                    "sha": result["commit"].sha,
                    "message": result["commit"].message,
                    "html_url": result["commit"].html_url
                },
                "file": {
                    "path": file_path,
                    "sha": result["content"].sha,
                    "url": result["content"].html_url
                }
            }
        
        except Exception as e:
            logger.error(f"Error pushing file: {e}")
            raise
    
    async def push_files(self, client_id: str, repo_id: str, files: List[Dict[str, str]], 
                         commit_message: str, branch: Optional[str] = None) -> Dict[str, Any]:
        """Push multiple files to a GitHub repository in a single commit"""
        try:
            # Get repository details
            repo_data = await mongodb.db.repositories.find_one({"client_id": client_id, "id": repo_id})
            if not repo_data:
                logger.error(f"Repository not found for client {client_id}, repo_id {repo_id}")
                raise ValueError("Repository not found")
            
            # Setup GitHub client
            g = self._get_github_client(repo_data)
            
            # Get repository
            full_repo_name = f"{repo_data['owner']}/{repo_data['repo']}"
            repo = g.get_repo(full_repo_name)
            
            # Determine branch
            if not branch:
                branch = repo_data.get("branch", "main")
            
            # Get the latest commit
            branch_ref = repo.get_branch(branch)
            latest_commit = branch_ref.commit
            base_tree = latest_commit.commit.tree
            
            # Create blobs for each file
            element_list = []
            for file_info in files:
                path = file_info["path"]
                content = file_info["content"]
                
                # Create blob (file content)
                blob = repo.create_git_blob(content=content, encoding="utf-8")
                
                # Create tree element
                element = InputGitTreeElement(
                    path=path,
                    mode="100644",  # Regular file mode
                    type="blob",
                    sha=blob.sha
                )
                element_list.append(element)
            
            # Create tree
            tree = repo.create_git_tree(element_list, base_tree)
            
            # Create commit
            parent = repo.get_git_commit(latest_commit.sha)
            commit = repo.create_git_commit(
                message=commit_message,
                parents=[parent],
                tree=tree
            )
            
            # Update branch reference
            ref = repo.get_git_ref(f"heads/{branch}")
            ref.edit(sha=commit.sha)
            
            return {
                "commit": {
                    "sha": commit.sha,
                    "message": commit.message,
                    "url": f"https://{repo_data['host']}/{repo_data['owner']}/{repo_data['repo']}/commit/{commit.sha}"
                },
                "branch": branch,
                "files": [file["path"] for file in files]
            }
        
        except Exception as e:
            logger.error(f"Error pushing files: {e}")
            raise
    
    async def create_pull_request(self, client_id: str, repo_id: str, title: str, body: str, 
                                  head_branch: str, base_branch: str) -> Dict[str, Any]:
        """Create a pull request"""
        try:
            # Get repository details
            repo_data = await mongodb.db.repositories.find_one({"client_id": client_id, "id": repo_id})
            if not repo_data:
                logger.error(f"Repository not found for client {client_id}, repo_id {repo_id}")
                raise ValueError("Repository not found")
            
            # Setup GitHub client
            g = self._get_github_client(repo_data)
            
            # Get repository
            full_repo_name = f"{repo_data['owner']}/{repo_data['repo']}"
            repo = g.get_repo(full_repo_name)
            
            # Create pull request
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            # Format response
            pr_data = {
                "id": pr.id,
                "number": pr.number,
                "title": pr.title,
                "body": pr.body,
                "state": pr.state,
                "html_url": pr.html_url,
                "created_at": pr.created_at.isoformat(),
                "updated_at": pr.updated_at.isoformat(),
                "head_branch": head_branch,
                "base_branch": base_branch,
                "repository_id": repo_id
            }
            
            # Store in MongoDB for reference
            await mongodb.db.pull_requests.update_one(
                {"client_id": client_id, "repository_id": repo_id, "number": pr.number},
                {"$set": dict(pr_data, client_id=client_id)},
                upsert=True
            )
            
            return pr_data
        
        except Exception as e:
            logger.error(f"Error creating pull request: {e}")
            raise
    
    async def get_pull_requests(self, client_id: str, repo_id: str, state: str = "open") -> List[Dict[str, Any]]:
        """Get pull requests from a GitHub repository"""
        try:
            # Get repository details
            repo_data = await mongodb.db.repositories.find_one({"client_id": client_id, "id": repo_id})
            if not repo_data:
                logger.error(f"Repository not found for client {client_id}, repo_id {repo_id}")
                return []
            
            # Setup GitHub client
            g = self._get_github_client(repo_data)
            
            # Get repository
            full_repo_name = f"{repo_data['owner']}/{repo_data['repo']}"
            repo = g.get_repo(full_repo_name)
            
            # Get pull requests
            pull_requests = []
            for pr in repo.get_pulls(state=state):
                pr_data = {
                    "id": pr.id,
                    "number": pr.number,
                    "title": pr.title,
                    "body": pr.body,
                    "state": pr.state,
                    "html_url": pr.html_url,
                    "created_at": pr.created_at.isoformat(),
                    "updated_at": pr.updated_at.isoformat(),
                    "head_branch": pr.head.ref,
                    "base_branch": pr.base.ref,
                    "repository_id": repo_id
                }
                pull_requests.append(pr_data)
                
                # Store in MongoDB for reference
                await mongodb.db.pull_requests.update_one(
                    {"client_id": client_id, "repository_id": repo_id, "number": pr.number},
                    {"$set": dict(pr_data, client_id=client_id)},
                    upsert=True
                )
            
            return pull_requests
        
        except Exception as e:
            logger.error(f"Error getting pull requests: {e}")
            return []
    
    async def get_file_content(self, client_id: str, repo_id: str, file_path: str, branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Get contents of a file from GitHub
        
        Args:
            client_id: Client ID
            repo_id: Repository ID
            file_path: Path to the file
            branch: Branch name (defaults to repository default branch)
        
        Returns:
            Dict with content, path, name, size, type, encoding, sha
        """
        try:
            # Get repository details
            repo_data = await mongodb.db.repositories.find_one({"client_id": client_id, "id": repo_id})
            if not repo_data:
                logger.error(f"Repository not found for client {client_id}, repo_id {repo_id}")
                raise ValueError("Repository not found")
            
            # Setup GitHub client
            g = self._get_github_client(repo_data)
            
            # Get repository
            full_repo_name = f"{repo_data['owner']}/{repo_data['repo']}"
            repo = g.get_repo(full_repo_name)
            
            # Determine branch
            if not branch:
                branch = repo_data.get("branch", "main")
                
            # Get file contents
            content = repo.get_contents(file_path, ref=branch)
            
            # Handle case where get_contents returns a list (directory)
            if isinstance(content, list):
                raise ValueError(f"Path '{file_path}' is a directory, not a file")
                
            # Decode content if it's base64-encoded
            decoded_content = None
            if content.encoding == "base64":
                decoded_content = base64.b64decode(content.content).decode('utf-8')
            else:
                decoded_content = content.content
                
            return {
                "content": decoded_content,
                "path": content.path,
                "name": content.name,
                "size": content.size,
                "type": content.type,
                "encoding": content.encoding,
                "sha": content.sha,
                "download_url": content.download_url,
                "html_url": content.html_url
            }
        
        except GithubException as e:
            logger.error(f"GitHub error getting file content: {e}")
            if e.status == 404:
                raise ValueError(f"File {file_path} not found in repository")
            raise
        except Exception as e:
            logger.error(f"Error getting file content: {e}")
            raise
    
    def _get_github_client(self, repo_data: Dict[str, Any]) -> Github:
        """Helper method to get a GitHub client"""
        host = repo_data.get("host", "github.com")
        token = repo_data.get("token")
        
        if host == "github.com":
            return Github(token)
        else:
            # For GitHub Enterprise
            api_url = f"https://{host}/api/v3"
            return Github(base_url=api_url, login_or_token=token)


# Create a singleton instance
github_model = GitHubModel()
