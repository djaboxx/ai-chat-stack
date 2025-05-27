
import type { FileNode } from './types';

// Using relative path for WebSocket URL to work with the Nginx proxy in Docker
// For development, connect directly to the backend
export const WEBSOCKET_URL = `ws://localhost:8081/ws`;

// Disable mock data now that we have a real backend
export const MOCK_FILE_TREE_ENABLED = false;

// Empty mock data structure - only used if backend is unavailable and MOCK_FILE_TREE_ENABLED is true
export const MOCK_FILE_TREE_DATA: FileNode[] = [];
