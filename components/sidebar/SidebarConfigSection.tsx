import React from 'react';
import SidebarRepositoryAdd from './SidebarRepositoryAdd';

interface MenuItemProps {
  id: string;
  title: string;
  icon: string;
  isActive: boolean;
  onClick: (id: string) => void;
}

const MenuItem: React.FC<MenuItemProps> = ({ id, title, icon, isActive, onClick }) => (
  <button
    onClick={() => onClick(id)}
    className={`flex items-center w-full px-4 py-2 rounded-lg text-base font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-gray-900 border-l-4 ${
      isActive
        ? 'bg-[#23272e] text-purple-300 border-purple-500 shadow-md'
        : 'text-gray-300 hover:bg-[#23272e] hover:text-white border-transparent'
    }`}
  >
    <span role="img" aria-label={title} className="mr-3 text-lg">
      {icon}
    </span>
    {title}
  </button>
);

interface SidebarConfigSectionProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  onShowSection?: (section: string, show: boolean) => void;
  showAddRepoForm?: () => void; // replaces onAddRepo
}

const SidebarConfigSection: React.FC<SidebarConfigSectionProps> = ({
  activeSection,
  onSectionChange,
  onShowSection,
  showAddRepoForm
}) => {
  const configMenuItems = [
    { id: 'gemini', title: 'Gemini API Key', icon: '🔑' },
    { id: 'repositories', title: 'Repositories', icon: '📁' },
    { id: 'filetree', title: 'File Tree', icon: '🌲' },
  ];

  const handleItemClick = (id: string) => {
    onSectionChange(id);
    if (onShowSection) {
      onShowSection(id, true);
    }
  };

  return (
    <div className="mb-8">
      <h3 className="text-xs uppercase tracking-wider text-gray-400 mb-3 font-bold pl-2">
        Configuration
      </h3>
      <ul className="space-y-1">
        {configMenuItems.map((item) => (
          <li key={item.id}>
            <MenuItem
              id={item.id}
              title={item.title}
              icon={item.icon}
              isActive={activeSection === item.id}
              onClick={handleItemClick}
            />
            {/* Add repo button under Repositories */}
            {item.id === 'repositories' && activeSection === 'repositories' && showAddRepoForm && (
              <div className="mt-3 ml-2 flex flex-col gap-2">
                <SidebarRepositoryAdd onAddRepo={showAddRepoForm} />
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SidebarConfigSection;
