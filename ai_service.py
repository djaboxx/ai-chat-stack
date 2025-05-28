"""
AI agent service that handles chat interactions.
"""
import asyncio
import logging
from typing import Dict, Any, List
from pydantic_ai import Agent, RunContext
from .github_service import GitHubService

logger = logging.getLogger(__name__)


class AIAgentService:
    """Service for interacting with AI models"""
    
    def __init__(self):
        self.api_key: str = ""
        self.agent: Agent | None = None
        
    def configure(self, api_key: str):
        """Configure the AI agent with an API key"""
        self.api_key = api_key
        self.agent = Agent(
            model_name="google-gla:gemini-1.5-flash",
            system_prompt=(
                "You are a code analysis and generation agent. "
                "You can analyze code, create new code, and modify existing code. "
                "You have access to various tools for interacting with GitHub repositories, "
                "including fetching file trees, getting issues, creating pull requests, and more. "
                "Plan your actions carefully to achieve the user's goals."
            ),
        )

        # Add GitHubService functions as tools
        self.agent.add_tool(
            GitHubService.get_issues,
            name="get_issues",
            description="Get issues from a GitHub repository"
        )
        self.agent.add_tool(
            GitHubService.create_issue,
            name="create_issue",
            description="Create a new issue in a GitHub repository"
        )
        self.agent.add_tool(
            GitHubService.create_branch,
            name="create_branch",
            description="Create a new branch in a GitHub repository"
        )
        self.agent.add_tool(
            GitHubService.push_file,
            name="push_file",
            description="Push a single file to a GitHub repository"
        )
        self.agent.add_tool(
            GitHubService.push_files,
            name="push_files",
            description="Push multiple files to a GitHub repository in a single commit"
        )
        self.agent.add_tool(
            GitHubService.create_pull_request,
            name="create_pull_request",
            description="Create a pull request in a GitHub repository"
        )
        self.agent.add_tool(
            GitHubService.get_pull_requests,
            name="get_pull_requests",
            description="Get pull requests from a GitHub repository"
        )
        self.agent.add_tool(
            GitHubService.get_file_content,
            name="get_file_content",
            description="Get the contents of a file from GitHub"
        )

        logger.info("AI agent configured with GitHub tools")
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> str:
        """Process a user message and generate a response"""
        if not self.agent:
            return "Agent not configured. Please set the Gemini API key."

        # Run the agent
        result = await self.agent.run_async(message, context)
        return result.output
