import React, { useState } from 'react';

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  onShowSection?: (section: string, show: boolean) => void;
  onAddRepo?: (repoUrl: string) => void; // Optional callback for adding repos
}

const Sidebar: React.FC<SidebarProps> = ({ activeSection, onSectionChange, onShowSection, onAddRepo }) => {
  const [repoInput, setRepoInput] = useState('');
  const [showRepoInput, setShowRepoInput] = useState(false);

  const configMenuItems = [
    { id: 'gemini', title: 'Gemini API Key', icon: '🔑' },
    { id: 'repositories', title: 'Repositories', icon: '📁' },
    { id: 'filetree', title: 'File Tree', icon: '🌲' },
  ];

  const handleItemClick = (id: string) => {
    onSectionChange(id);
    if (onShowSection) {
      if (id === 'gemini') onShowSection('gemini', true);
      else if (id === 'repositories') onShowSection('repositories', true);
      else if (id === 'filetree') onShowSection('filetree', true);
    }
  };

  const handleAddRepo = () => {
    if (repoInput.trim() && onAddRepo) {
      onAddRepo(repoInput.trim());
      setRepoInput('');
      setShowRepoInput(false);
    }
  };

  return (
    <div className="min-h-screen w-64 bg-[#181c20] flex flex-col py-6 px-3 border-r border-gray-800 shadow-lg">
      <h2 className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500 mb-8 pl-2 tracking-tight">
        AI Chat Stack
      </h2>
      <div className="mb-8">
        <h3 className="text-xs uppercase tracking-wider text-gray-400 mb-3 font-bold pl-2">
          Configuration
        </h3>
        <ul className="space-y-1">
          {configMenuItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => handleItemClick(item.id)}
                className={`flex items-center w-full px-4 py-2 rounded-lg text-base font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-gray-900 border-l-4 ${
                  activeSection === item.id
                    ? 'bg-[#23272e] text-purple-300 border-purple-500 shadow-md'
                    : 'text-gray-300 hover:bg-[#23272e] hover:text-white border-transparent'
                }`}
              >
                <span role="img" aria-label={item.title} className="mr-3 text-lg">
                  {item.icon}
                </span>
                {item.title}
              </button>
              {/* Add repo input under Repositories */}
              {item.id === 'repositories' && activeSection === 'repositories' && (
                <div className="mt-3 ml-2 flex flex-col gap-2">
                  {showRepoInput ? (
                    <div className="flex gap-2">
                      <input
                        type="text"
                        className="flex-1 rounded-md bg-gray-800 border border-gray-700 px-2 py-1 text-sm text-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="Paste repo URL..."
                        value={repoInput}
                        onChange={e => setRepoInput(e.target.value)}
                        onKeyDown={e => { if (e.key === 'Enter') handleAddRepo(); }}
                        autoFocus
                      />
                      <button
                        className="rounded-md bg-gradient-to-r from-purple-500 to-pink-500 px-3 py-1 text-white font-semibold text-xs hover:from-purple-600 hover:to-pink-600 focus:outline-none"
                        onClick={handleAddRepo}
                        title="Add Repository"
                      >Add</button>
                      <button
                        className="rounded-md px-2 py-1 text-gray-400 hover:text-red-400 text-xs focus:outline-none"
                        onClick={() => { setShowRepoInput(false); setRepoInput(''); }}
                        title="Cancel"
                      >✕</button>
                    </div>
                  ) : (
                    <button
                      className="rounded-md bg-gray-700 px-2 py-1 text-xs text-gray-200 hover:bg-purple-600 hover:text-white transition-colors w-fit"
                      onClick={() => setShowRepoInput(true)}
                    >+ Add Repository</button>
                  )}
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
      <div className="mb-8">
        <h3 className="text-xs uppercase tracking-wider text-gray-400 mb-3 font-bold pl-2">
          Interaction
        </h3>
        <ul className="space-y-1">
          <li>
            <button
              onClick={() => handleItemClick('chat')}
              className={`flex items-center w-full px-4 py-2 rounded-lg text-base font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-gray-900 border-l-4 ${
                activeSection === 'chat'
                  ? 'bg-[#23272e] text-purple-300 border-purple-500 shadow-md'
                  : 'text-gray-300 hover:bg-[#23272e] hover:text-white border-transparent'
              }`}
            >
              <span role="img" aria-label="Chat" className="mr-3 text-lg">
                💬
              </span>
              Chat
            </button>
          </li>
        </ul>
      </div>
      <div className="flex-1" />
      <div className="text-xs text-gray-600 pl-2 pb-2">v1.0</div>
    </div>
  );
};

export default Sidebar;
