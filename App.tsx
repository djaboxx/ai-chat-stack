import React, { useState, useEffect, useCallback, useRef } from 'react';
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
    const wsMessage: ClientToServerMessage = { 
      type: 'ADD_REPOSITORY', 
      payload: { repository: repo } 
    };
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

  return (
    <div className="flex flex-col h-screen max-h-screen bg-gray-800 text-gray-100">
      {(systemMessage || (connectionStatusMessage && readyState !== ReadyState.OPEN)) && (
        <div className={`p-3 text-center text-sm ${fileTreeError || readyState === ReadyState.CLOSED ? 'bg-red-600' : 'bg-blue-600'} text-white transition-opacity duration-300`}>
          {systemMessage || connectionStatusMessage}
        </div>
      )}
      {!isConfigured ? (
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
        />
      ) : (
        <ChatInterface
          messages={chatMessages}
          onSendMessage={handleSendChatMessage}
          isSendingMessage={readyState !== ReadyState.OPEN}
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
      )}
    </div>
  );
};

export default App;
