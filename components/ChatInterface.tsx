
import React, { useState, useRef, useEffect } from 'react';
import type { ChatMessage } from '../types';
import { Button } from './common/Button';
import { PaperAirplaneIcon } from './icons/PaperAirplaneIcon';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  onSendMessage: (text: string) => void;
  isSendingMessage: boolean;
  onResetConfiguration: () => void;
  repositoryName?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isSendingMessage,
  onResetConfiguration,
  repositoryName,
}) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputText.trim() && !isSendingMessage) {
      onSendMessage(inputText.trim());
      setInputText('');
    }
  };

  const getBubbleStyles = (sender: ChatMessage['sender']) => {
    if (sender === 'user') {
      return 'bg-blue-600 text-white self-end rounded-l-xl rounded-tr-xl';
    } else if (sender === 'agent') {
      return 'bg-gray-600 text-gray-100 self-start rounded-r-xl rounded-tl-xl';
    }
    return 'bg-yellow-500 text-yellow-900 self-center text-sm italic'; // System messages
  };

  return (
    <div className="flex flex-col h-full max-h-screen bg-gray-800">
      <header className="bg-gray-700 p-4 shadow-md flex justify-between items-center">
        <div>
          <h1 className="text-xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">
            AI Agent Chat
          </h1>
          {repositoryName && (
            <p className="text-sm text-gray-400 mt-1">Repository: {repositoryName}</p>
          )}
        </div>
        <Button onClick={onResetConfiguration} variant="danger_ghost" size="sm">
          Reset Configuration
        </Button>
      </header>

      <div className="flex-grow p-4 space-y-4 overflow-y-auto bg-gray-800">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`max-w-xs md:max-w-md lg:max-w-lg xl:max-w-2xl p-3 shadow ${getBubbleStyles(msg.sender)}`}>
              {msg.sender === 'agent' || msg.sender === 'system' ? (
                <div className="markdown-content text-sm">
                  {/* @ts-ignore */}
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeHighlight]}
                    components={{
                      // @ts-ignore
                      p: ({...props}) => <p className="my-2" {...props} />,
                      // @ts-ignore
                      h1: ({...props}) => <h1 className="text-lg font-bold my-3" {...props} />,
                      // @ts-ignore
                      h2: ({...props}) => <h2 className="text-base font-bold my-2" {...props} />,
                      // @ts-ignore
                      h3: ({...props}) => <h3 className="text-sm font-bold my-2" {...props} />,
                      // @ts-ignore
                      ul: ({...props}) => <ul className="list-disc pl-5 my-3" {...props} />,
                      // @ts-ignore
                      ol: ({...props}) => <ol className="list-decimal pl-5 my-3" {...props} />,
                      // @ts-ignore
                      li: ({...props}) => <li className="my-1" {...props} />,
                      // @ts-ignore
                      a: ({...props}) => <a className="text-blue-300 hover:underline" target="_blank" rel="noopener noreferrer" {...props} />,
                      // @ts-ignore
                      table: ({...props}) => <div className="overflow-x-auto my-2"><table className="w-full border-collapse" {...props} /></div>,
                      // @ts-ignore
                      th: ({...props}) => <th className="border border-gray-600 px-2 py-1 bg-gray-700" {...props} />,
                      // @ts-ignore
                      td: ({...props}) => <td className="border border-gray-600 px-2 py-1" {...props} />,
                      // @ts-ignore
                      blockquote: ({...props}) => <blockquote className="border-l-4 border-blue-300 pl-4 py-1 my-3 bg-opacity-10 bg-blue-200" {...props} />,
                      // @ts-ignore
                      img: ({...props}) => <img className="max-w-full h-auto my-2 rounded" {...props} />,
                      // @ts-ignore
                      hr: ({...props}) => <hr className="border-gray-600 my-4" {...props} />,
                      // @ts-ignore
                      code: ({inline, className, children, ...props}) => {
                        const match = /language-(\w+)/.exec(className || '');
                        const language = match ? match[1] : '';
                        
                        return inline ? (
                          // Inline code
                          <code className="bg-gray-700 px-1 rounded text-xs font-mono" {...props}>
                            {children}
                          </code>
                        ) : (
                          // Code block with language label
                          <div className="code-wrapper">
                            {language && (
                              <div className="code-header">
                                {language}
                              </div>
                            )}
                            <pre className="m-0">
                              <code className={className} {...props}>
                                {children}
                              </code>
                            </pre>
                          </div>
                        );
                      }
                    }}
                  >
                    {msg.text}
                  </ReactMarkdown>
                </div>
              ) : (
                <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
              )}
            </div>
            <span className={`text-xs mt-1 ${msg.sender === 'user' ? 'mr-1 text-gray-500' : 'ml-1 text-gray-500'}`}>
              {new Date(msg.timestamp).toLocaleTimeString()} - {msg.sender}
            </span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 bg-gray-700 border-t border-gray-600">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={isSendingMessage ? "Connecting..." : "Type your message..."}
            className="flex-grow p-3 bg-gray-600 border border-gray-500 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none placeholder-gray-400 text-gray-100"
            disabled={isSendingMessage}
          />
          <Button type="submit" disabled={isSendingMessage || !inputText.trim()} className="!px-4 !py-3">
            <PaperAirplaneIcon className="w-5 h-5" />
          </Button>
        </div>
      </form>
    </div>
  );
};
