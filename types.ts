
export interface ConfigData {
  githubToken: string;
  geminiToken: string; 
  githubRepo: string;
  githubBranch: string;
  selectedFiles: string[]; // Array of full paths to selected files/folders
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'agent' | 'system';
  text: string;
  timestamp: number;
}

export interface FileNode {
  id: string; // Typically the full path
  name: string;
  type: 'file' | 'directory';
  path: string;
  children?: FileNode[];
}

// WebSocket message types
// Client -> Server
export type ClientToServerMessage =
  | { type: 'SUBMIT_CONFIG'; payload: ConfigData }
  | { type: 'FETCH_FILES'; payload: { repo: string; branch: string; githubToken: string } }
  | { type: 'SEND_CHAT_MESSAGE'; payload: { text: string } };

// Server -> Client
export type ServerToClientMessage =
  | { type: 'CONFIG_SUCCESS' }
  | { type: 'CONFIG_ERROR'; payload: { message: string } }
  | { type: 'FILE_TREE_DATA'; payload: { tree: FileNode[] } }
  | { type: 'FILE_TREE_ERROR'; payload: { message: string } }
  | { type: 'NEW_CHAT_MESSAGE'; payload: ChatMessage }
  | { type: 'AGENT_TYPING'; payload: { isTyping: boolean } };
