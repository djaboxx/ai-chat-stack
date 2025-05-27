import React, { useState, useEffect, useCallback } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { ConfigurationScreen } from './components/ConfigurationScreen';
import { ChatInterface } from './components/ChatInterface';
import { Spinner } from './components/common/Spinner';
import type { 
  ConfigData, ChatMessage, FileNode, ServerToClientMessage, 
  ClientToServerMessage, Repository, RepositoryResponse 
} from './types';
import { WEBSOCKET_URL } from './constants';

const App: React.FC = () => {
  const [isConfigured, setIsConfigured] = useState<boolean>(false);
  const [configData, setConfigData] = useState<ConfigData | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [fileTree, setFileTree] = useState<FileNode[] | null>(null);
  const [isFileTreeLoading, setIsFileTreeLoading] = useState<boolean>(false);
  const [fileTreeError, setFileTreeError] = useState<string | null>(null);
  const [systemMessage, setSystemMessage] = useState<string | null>(null);
  const [repositories, setRepositories] = useState<RepositoryResponse[]>([]);
  const [selectedRepositoryId, setSelectedRepositoryId] = useState<string | null>(null);
  const [selectedRepository, setSelectedRepository] = useState<RepositoryResponse | null>(null);
  const [activeSection, setActiveSection] = useState<string>('gemini');

  const { sendMessage, lastJsonMessage, readyState } = useWebSocket(WEBSOCKET_URL, {
    shouldReconnect: (_closeEvent) => true,
    reconnectAttempts: 10,
    reconnectInterval: 3000,
  });

  useEffect(() => {
    if (lastJsonMessage) {
      const message = lastJsonMessage as ServerToClientMessage;
      
      switch (message.type) {
        case 'CONFIG_SUCCESS':
          setIsConfigured(true);
          setSystemMessage('Configuration successful. You can now chat with the agent.');
          break;
          
        case 'CONFIG_ERROR':
          setSystemMessage(`Configuration Error: ${message.payload.message}`);
          setIsConfigured(false);
          break;
          
        case 'FILE_TREE_DATA':
          setFileTree(message.payload.tree);
          setIsFileTreeLoading(false);
          setFileTreeError(null);
          
          // Update selected repository information
          if (message.payload.repository) {
            setSelectedRepository(message.payload.repository);
          }
          break;
          
        case 'FILE_TREE_ERROR':
          setFileTreeError(message.payload.message);
          setIsFileTreeLoading(false);
          setFileTree(null);
          break;
          
        case 'NEW_CHAT_MESSAGE':
          setChatMessages((prevMessages) => [...prevMessages, message.payload]);
          break;
          
        case 'AGENT_TYPING':
          console.log('Agent typing status:', message.payload.isTyping);
          break;
          
        case 'REPOSITORIES_LIST':
          setRepositories(message.payload.repositories);
          if (message.payload.repositories.length > 0 && !selectedRepositoryId) {
            setSelectedRepositoryId(message.payload.repositories[0].id);
          }
          break;
          
        case 'REPOSITORY_ACTION_SUCCESS':
          if (message.payload.action === 'select' && message.payload.repository_id) {
            setSelectedRepositoryId(message.payload.repository_id);
          } else if (message.payload.repository) {
            // For add/update repository actions
            setSystemMessage(`Repository ${message.payload.action === 'add' ? 'added' : 'updated'} successfully`);
          } else if (message.payload.action === 'delete') {
            setSystemMessage('Repository deleted successfully');
          }
          break;
          
        case 'REPOSITORY_ACTION_ERROR':
          setSystemMessage(`Repository action error: ${message.payload.message}`);
          break;
          
        default:
          console.warn('Received unknown WebSocket message:', message);
      }
    }
  }, [lastJsonMessage]);

  // Clear system message when user starts chatting
  const handleSendChatMessage = useCallback((text: string) => {
    // Clear system message when user starts chatting
    if (systemMessage) {
      setSystemMessage(null);
    }
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text,
      timestamp: Date.now(),
    };
    setChatMessages((prevMessages) => [...prevMessages, userMessage]);
    const wsMessage: ClientToServerMessage = { 
      type: 'SEND_CHAT_MESSAGE', 
      payload: { text } 
    };
    sendMessage(JSON.stringify(wsMessage));
  }, [sendMessage, systemMessage]);
  
  const handleConfigure = useCallback((data: ConfigData) => {
    setConfigData(data);
    const wsMessage: ClientToServerMessage = { 
      type: 'SUBMIT_CONFIG', 
      payload: data 
    };
    sendMessage(JSON.stringify(wsMessage));
    setSystemMessage('Submitting configuration...');
  }, [sendMessage]);

  const handleFetchFileTree = useCallback((details: { repository_id: string }) => {
    setIsFileTreeLoading(true);
    setFileTreeError(null);
    setFileTree(null); 
    const wsMessage: ClientToServerMessage = { 
      type: 'FETCH_FILES', 
      payload: details 
    };
    sendMessage(JSON.stringify(wsMessage));
    setSystemMessage('Fetching file tree...');
  }, [sendMessage]);

  // Repository management handlers
  const handleAddRepository = useCallback((repo: Repository) => {
    console.log("handleAddRepository called with:", { ...repo, token: "REDACTED" });
    const wsMessage: ClientToServerMessage = { 
      type: 'ADD_REPOSITORY', 
      payload: { repository: repo } 
    };
    console.log("Sending WebSocket message:", JSON.stringify({ 
      type: wsMessage.type, 
      payload: { repository: { ...wsMessage.payload.repository, token: "REDACTED" } } 
    }));
    sendMessage(JSON.stringify(wsMessage));
    setSystemMessage('Adding repository...');
  }, [sendMessage]);

  const handleUpdateRepository = useCallback((id: string, repo: Repository) => {
    const wsMessage: ClientToServerMessage = { 
      type: 'UPDATE_REPOSITORY', 
      payload: { repository_id: id, repository: repo } 
    };
    sendMessage(JSON.stringify(wsMessage));
    setSystemMessage('Updating repository...');
  }, [sendMessage]);

  const handleDeleteRepository = useCallback((id: string) => {
    const wsMessage: ClientToServerMessage = { 
      type: 'DELETE_REPOSITORY', 
      payload: { repository_id: id } 
    };
    sendMessage(JSON.stringify(wsMessage));
    setSystemMessage('Deleting repository...');
  }, [sendMessage]);

  const handleSelectRepository = useCallback((id: string) => {
    const wsMessage: ClientToServerMessage = { 
      type: 'SELECT_REPOSITORY', 
      payload: { repository_id: id } 
    };
    sendMessage(JSON.stringify(wsMessage));
    setSystemMessage('Selecting repository...');
    setSelectedRepositoryId(id);
  }, [sendMessage]);
  
  const connectionStatusMessage = {
    [ReadyState.CONNECTING]: 'Connecting to agent...',
    [ReadyState.OPEN]: null, 
    [ReadyState.CLOSING]: 'Disconnecting...',
    [ReadyState.CLOSED]: 'Disconnected from agent. Attempting to reconnect...',
    [ReadyState.UNINSTANTIATED]: 'WebSocket not ready.',
  }[readyState];

  if (readyState === ReadyState.CONNECTING && !isConfigured) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
        <Spinner />
        <p className="mt-4 text-xl">{connectionStatusMessage}</p>
      </div>
    );
  }

  // Only allow chat if Gemini key is set
  const canChat = !!configData?.geminiToken;

  return (
    <div className="flex h-screen bg-gray-800 text-gray-100">
      {/* Left: Configuration panel */}
      <div className="w-full max-w-xs border-r border-gray-700 bg-gray-900 flex flex-col">
        {/* Simple navigation header */}
        <div className="bg-gray-950 p-4 border-b border-gray-700">
          <h2 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500 mb-4">
            AI Chat Stack
          </h2>
          
          <div className="mb-4">
            <h3 className="text-xs uppercase tracking-wider text-gray-500 mb-2 font-semibold">
              Configuration
            </h3>
            <ul className="space-y-1">
              {[
                { id: 'gemini', title: 'Gemini API Key', icon: '🔑' },
                { id: 'repositories', title: 'Repositories', icon: '📁' },
                { id: 'filetree', title: 'File Tree', icon: '🌲' }
              ].map((item) => (
                <li key={item.id}>
                  <button
                    onClick={() => setActiveSection(item.id)}
                    className={`flex items-center w-full px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      activeSection === item.id
                        ? 'bg-gray-800 text-purple-400 font-semibold'
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                    }`}
                  >
                    <span role="img" aria-label={item.title} className="mr-2">
                      {item.icon}
                    </span>
                    {item.title}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto">
          <ConfigurationScreen
            onConfigure={handleConfigure}
            fetchFileTree={handleFetchFileTree}
            addRepository={handleAddRepository}
            updateRepository={handleUpdateRepository}
            deleteRepository={handleDeleteRepository}
            selectRepository={handleSelectRepository}
            repositories={repositories}
            selectedRepositoryId={selectedRepositoryId}
            fileTreeData={fileTree}
            isFileTreeLoading={isFileTreeLoading}
            fileTreeError={fileTreeError}
            isConnecting={readyState === ReadyState.CONNECTING || readyState === ReadyState.CLOSED}
            activeSection={activeSection}
          />
        </div>
      </div>
      {/* Right: Chat panel */}
      <div className="flex-1 flex flex-col relative">
        <ChatInterface
          messages={chatMessages}
          onSendMessage={handleSendChatMessage}
          isSendingMessage={readyState !== ReadyState.OPEN || !canChat}
          onResetConfiguration={() => {
            setIsConfigured(false);
            setConfigData(null);
            setChatMessages([]);
            setFileTree(null);
            setSelectedRepository(null);
            setSelectedRepositoryId(null);
            setSystemMessage("Configuration reset. Please re-configure.");
          }}
          repositoryName={selectedRepository?.name}
        />
        {!canChat && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-60 z-10 pointer-events-none">
            <div className="bg-red-600 text-white px-6 py-4 rounded shadow-lg text-lg pointer-events-auto">
              Please enter your Gemini API Key to enable chat.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
