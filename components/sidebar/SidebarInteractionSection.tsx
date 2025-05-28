import React from 'react';

interface SidebarInteractionSectionProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

const SidebarInteractionSection: React.FC<SidebarInteractionSectionProps> = ({ 
  activeSection, 
  onSectionChange 
}) => {
  return (
    <div className="mb-8">
      <h3 className="text-xs uppercase tracking-wider text-gray-400 mb-3 font-bold pl-2">
        Interaction
      </h3>
      <ul className="space-y-1">
        <li>
          <button
            onClick={() => onSectionChange('chat')}
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
  );
};

export default SidebarInteractionSection;
