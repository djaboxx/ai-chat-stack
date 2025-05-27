
import React, { useState, useEffect, useCallback, useRef } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';
import { ConfigurationScreen } from './components/ConfigurationScreen';
import { ChatInterface } from './components/ChatInterface';
import { Spinner } from './components/common/Spinner';
import type { ConfigData, ChatMessage, FileNode, ServerToClientMessage, ClientToServerMessage } from './types';
import { WEBSOCKET_URL, MOCK_FILE_TREE_ENABLED, MOCK_FILE_TREE_DATA } from './constants';

const App: React.FC = () => {
  const [isConfigured, setIsConfigured] = useState<boolean>(false);
  const [_configData, setConfigData] = useState<ConfigData | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [fileTree, setFileTree] = useState<FileNode[] | null>(null);
  const [isFileTreeLoading, setIsFileTreeLoading] = useState<boolean>(false);
  const [fileTreeError, setFileTreeError] = useState<string | null>(null);
  const [systemMessage, setSystemMessage] = useState<string | null>(null);

  const mockFileTreeTimeoutRef = useRef<number | null>(null);

  const { sendMessage, lastJsonMessage, readyState } = useWebSocket(WEBSOCKET_URL, {
    shouldReconnect: (_closeEvent) => true,
    reconnectAttempts: 10,
    reconnectInterval: 3000,
  });

  useEffect(() => {
    // Cleanup timeout on component unmount
    return () => {
      if (mockFileTreeTimeoutRef.current !== null) {
        clearTimeout(mockFileTreeTimeoutRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (lastJsonMessage) {
      const message = lastJsonMessage as ServerToClientMessage;

      // Clear mock file tree timeout if a relevant response arrives
      if (message.type === 'FILE_TREE_DATA' || message.type === 'FILE_TREE_ERROR') {
        if (mockFileTreeTimeoutRef.current !== null) {
          clearTimeout(mockFileTreeTimeoutRef.current);
          mockFileTreeTimeoutRef.current = null;
        }
      }

      switch (message.type) {
        case 'CONFIG_SUCCESS':
          setIsConfigured(true);
          setSystemMessage('Configuration successful. You can now chat with the agent.');
          setChatMessages(prev => prev.filter(msg => msg.sender === 'system'));
          break;
        case 'CONFIG_ERROR':
          setSystemMessage(`Configuration Error: ${message.payload.message}`);
          setIsConfigured(false);
          break;
        case 'FILE_TREE_DATA':
          setFileTree(message.payload.tree);
          setIsFileTreeLoading(false);
          setFileTreeError(null);
          break;
        case 'FILE_TREE_ERROR':
          setFileTreeError(message.payload.message);
          setIsFileTreeLoading(false);
          setFileTree(null);
           if (MOCK_FILE_TREE_ENABLED) {
            setSystemMessage(`File tree fetch error: ${message.payload.message}. Displaying mock data.`);
            setFileTree(MOCK_FILE_TREE_DATA);
            setFileTreeError(null); 
          }
          break;
        case 'NEW_CHAT_MESSAGE':
          setChatMessages((prevMessages) => [...prevMessages, message.payload]);
          break;
        case 'AGENT_TYPING':
          console.log('Agent typing status:', message.payload.isTyping);
          break;
        default:
          console.warn('Received unknown WebSocket message:', message);
      }
    }
  }, [lastJsonMessage]);

  const handleConfigure = useCallback((data: ConfigData) => {
    setConfigData(data);
    const wsMessage: ClientToServerMessage = { type: 'SUBMIT_CONFIG', payload: data };
    sendMessage(JSON.stringify(wsMessage));
    setSystemMessage('Submitting configuration...');
  }, [sendMessage]);

  const handleFetchFileTree = useCallback((details: { repo: string; branch: string; githubToken: string }) => {
    setIsFileTreeLoading(true);
    setFileTreeError(null);
    setFileTree(null); 
    const wsMessage: ClientToServerMessage = { type: 'FETCH_FILES', payload: details };
    sendMessage(JSON.stringify(wsMessage));
    setSystemMessage('Fetching file tree...');

    if (mockFileTreeTimeoutRef.current !== null) {
        clearTimeout(mockFileTreeTimeoutRef.current);
    }

    if (MOCK_FILE_TREE_ENABLED) {
        mockFileTreeTimeoutRef.current = window.setTimeout(() => {
            // This timeout executes if no FILE_TREE_DATA or FILE_TREE_ERROR message
            // cleared it within the 2-second window.
            // This implies the fetch "timed out" from the frontend's perspective for mock display.
            setFileTree(MOCK_FILE_TREE_DATA);
            setIsFileTreeLoading(false); // Loading "resolved" with mock data.
            setSystemMessage('Displaying mock file tree data (fallback).');
            mockFileTreeTimeoutRef.current = null; // Timeout has executed.
        }, 2000);
    }
  }, [sendMessage]); // readyState is implicitly handled by useWebSocket's sendMessage

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
    const wsMessage: ClientToServerMessage = { type: 'SEND_CHAT_MESSAGE', payload: { text } };
    sendMessage(JSON.stringify(wsMessage));
  }, [sendMessage, systemMessage]);
  
  const connectionStatusMessage = {
    [ReadyState.CONNECTING]: 'Connecting to agent...',
    [ReadyState.OPEN]: null, 
    [ReadyState.CLOSING]: 'Disconnecting...',
    [ReadyState.CLOSED]: 'Disconnected from agent. Attempting to reconnect...',
    [ReadyState.UNINSTANTIATED]: 'WebSocket not ready.',
  }[readyState];

  // Remove the automatic timeout - system messages will be cleared when user starts chatting
  // or when specific events occur (like configuration reset)

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
            setSystemMessage("Configuration reset. Please re-configure.");
             if (mockFileTreeTimeoutRef.current !== null) { // Clear timeout on reset
              clearTimeout(mockFileTreeTimeoutRef.current);
              mockFileTreeTimeoutRef.current = null;
            }
          }}
        />
      )}
    </div>
  );
};

export default App;
