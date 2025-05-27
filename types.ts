
export interface Repository {
  id?: string;
  name: string;
  url: string;
  host: string;
  owner: string;
  repo: string;
  branch: string;
  token: string;
}

export interface RepositoryResponse {
  id: string;
  name: string;
  url: string;
  host: string;
  owner: string;
  repo: string;
  branch: string;
  created_at: number;
}

export interface ConfigData {
  geminiToken: string;
  repositories: Repository[]; // Multiple repositories
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
  | { type: 'FETCH_FILES'; payload: { repository_id: string } }
  | { type: 'SEND_CHAT_MESSAGE'; payload: { text: string } }
  | { type: 'ADD_REPOSITORY'; payload: { repository: Repository } }
  | { type: 'UPDATE_REPOSITORY'; payload: { repository_id: string; repository: Repository } }
  | { type: 'DELETE_REPOSITORY'; payload: { repository_id: string } }
  | { type: 'SELECT_REPOSITORY'; payload: { repository_id: string } };

// Server -> Client
export type ServerToClientMessage =
  | { type: 'CONFIG_SUCCESS' }
  | { type: 'CONFIG_ERROR'; payload: { message: string } }
  | { type: 'FILE_TREE_DATA'; payload: { tree: FileNode[]; repository?: RepositoryResponse } }
  | { type: 'FILE_TREE_ERROR'; payload: { message: string } }
  | { type: 'NEW_CHAT_MESSAGE'; payload: ChatMessage }
  | { type: 'AGENT_TYPING'; payload: { isTyping: boolean } }
  | { type: 'REPOSITORIES_LIST'; payload: { repositories: RepositoryResponse[] } }
  | { type: 'REPOSITORY_ACTION_SUCCESS'; payload: { repository?: RepositoryResponse; repository_id?: string; action: string } }
  | { type: 'REPOSITORY_ACTION_ERROR'; payload: { message: string } };
