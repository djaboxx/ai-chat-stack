#!/usr/bin/env python3
"""
File manager for gcode tool - handles file uploading to Gemini API
and maintains session state across multiple requests.
"""

import os
import json
import time
import uuid
import mimetypes
from typing import List, Dict, Any, Optional, Tuple
import logging

from google import genai
from google.genai.types import FileData

from code_models import FileReference, SessionStore

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class FileManager:
    """
    Manages file uploads to Gemini API and tracks file references
    across sessions.
    """
    def __init__(self, api_key: str, session_dir: str = None):
        """
        Initialize the file manager with Gemini API credentials.
        
        Args:
            api_key: Gemini API key
            session_dir: Directory to store session files (defaults to ~/.gcode/sessions)
        """
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)
        
        # Set up session directory
        if session_dir is None:
            home_dir = os.path.expanduser("~")
            self.session_dir = os.path.join(home_dir, ".gcode", "sessions")
        else:
            self.session_dir = session_dir
            
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Current session
        self.current_session = None
        
    def create_session(self, project_name: str = None) -> SessionStore:
        """
        Create a new session for file tracking.
        
        Args:
            project_name: Optional project name to include in session metadata
            
        Returns:
            The newly created SessionStore object
        """
        session_id = str(uuid.uuid4())
        metadata = {}
        
        if project_name:
            metadata["project_name"] = project_name
            
        session = SessionStore(
            session_id=session_id,
            metadata=metadata
        )
        
        # Save the session file
        self._save_session(session)
        self.current_session = session
        
        return session
    
    def load_session(self, session_id: str) -> Optional[SessionStore]:
        """
        Load an existing session by ID.
        
        Args:
            session_id: ID of the session to load
            
        Returns:
            SessionStore object if found, None otherwise
        """
        session_path = os.path.join(self.session_dir, f"{session_id}.json")
        if not os.path.exists(session_path):
            logger.warning(f"Session {session_id} not found")
            return None
            
        try:
            session = SessionStore.from_json(session_path)
            session.last_accessed = time.time()
            self.current_session = session
            self._save_session(session)
            return session
        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available sessions.
        
        Returns:
            List of session summaries
        """
        sessions = []
        
        for filename in os.listdir(self.session_dir):
            if filename.endswith('.json'):
                try:
                    session_path = os.path.join(self.session_dir, filename)
                    session = SessionStore.from_json(session_path)
                    sessions.append({
                        "session_id": session.session_id,
                        "created_at": session.created_at,
                        "last_accessed": session.last_accessed,
                        "file_count": len(session.files),
                        "project_name": session.metadata.get("project_name", "Unnamed")
                    })
                except Exception as e:
                    logger.error(f"Error loading session from {filename}: {e}")
        
        # Sort by last accessed time (most recent first)
        return sorted(sessions, key=lambda s: s["last_accessed"], reverse=True)
    
    def upload_file(self, file_path: str) -> FileReference:
        """
        Upload a file to Gemini API and add it to the current session.
        
        Args:
            file_path: Local path to the file
            
        Returns:
            FileReference with file_id populated
            
        Raises:
            ValueError: If no current session or file not found
            RuntimeError: If upload fails
        """
        if not self.current_session:
            raise ValueError("No active session. Create or load a session first.")
        
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
            
        # Determine mime type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            # Default to text/plain for code files
            mime_type = "text/plain"
            
        file_ref = FileReference(
            file_path=file_path,
            mime_type=mime_type
        )
            
        try:
            # Upload to Gemini API
            logger.info(f"Uploading {file_path} to Gemini API...")
            uploaded_file = self.client.files.upload(file=file_path)
            
            # Update the file reference
            file_ref.file_id = uploaded_file.name
            
            # Add to session
            self.current_session.files.append(file_ref)
            self.current_session.last_accessed = time.time()
            self._save_session(self.current_session)
            
            logger.info(f"Successfully uploaded {file_path} with ID {file_ref.file_id}")
            return file_ref
        
        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {e}")
            raise RuntimeError(f"Failed to upload file: {e}")
    
    def upload_directory(self, dir_path: str, extensions: List[str] = None) -> List[FileReference]:
        """
        Upload all files in a directory to Gemini API.
        
        Args:
            dir_path: Local path to the directory
            extensions: Optional list of file extensions to include (e.g., [".py", ".js"])
            
        Returns:
            List of FileReference objects for uploaded files
            
        Raises:
            ValueError: If directory not found
        """
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            raise ValueError(f"Directory not found: {dir_path}")
            
        uploaded_files = []
        
        for root, _, files in os.walk(dir_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                
                # Skip hidden files
                if filename.startswith('.'):
                    continue
                    
                # Check extension if specified
                if extensions:
                    ext = os.path.splitext(filename)[1]
                    if ext.lower() not in extensions and ext not in extensions:
                        continue
                
                try:
                    file_ref = self.upload_file(file_path)
                    uploaded_files.append(file_ref)
                except Exception as e:
                    logger.warning(f"Failed to upload {file_path}: {e}")
        
        return uploaded_files
    
    def remove_file(self, file_path: str) -> bool:
        """
        Remove a file from the current session.
        
        Args:
            file_path: Path of the file to remove
            
        Returns:
            True if file was removed, False otherwise
        """
        if not self.current_session:
            logger.warning("No active session.")
            return False
            
        # Find the file in the session
        for i, file_ref in enumerate(self.current_session.files):
            if file_ref.file_path == file_path:
                del self.current_session.files[i]
                self.current_session.last_accessed = time.time()
                self._save_session(self.current_session)
                logger.info(f"Removed file {file_path} from session")
                return True
                
        logger.warning(f"File {file_path} not found in current session")
        return False
    
    def clear_session(self) -> None:
        """Clear all files from current session."""
        if not self.current_session:
            logger.warning("No active session.")
            return
            
        self.current_session.files = []
        self.current_session.last_accessed = time.time()
        self._save_session(self.current_session)
        logger.info("Cleared all files from current session")
    
    def _save_session(self, session: SessionStore) -> None:
        """
        Save a session to disk.
        
        Args:
            session: The SessionStore to save
        """
        session_path = os.path.join(self.session_dir, f"{session.session_id}.json")
        try:
            session.to_json(session_path)
        except Exception as e:
            logger.error(f"Error saving session {session.session_id}: {e}")
    
    def get_file_references(self) -> List[Tuple[FileData, str]]:
        """
        Get file references for all files in current session in a format
        suitable for passing to Gemini API.
        
        Returns:
            List of (FileData, display_name) tuples
            
        Raises:
            ValueError: If no current session
        """
        if not self.current_session:
            raise ValueError("No active session. Create or load a session first.")
            
        references = []
        
        for file_ref in self.current_session.files:
            if file_ref.file_id:
                file_data = FileData(name=file_ref.file_id)
                display_name = file_ref.get_display_name()
                references.append((file_data, display_name))
        
        return references
