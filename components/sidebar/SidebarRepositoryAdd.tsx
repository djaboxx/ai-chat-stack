import React from 'react';

interface SidebarRepositoryAddProps {
  onAddRepo: () => void; // Just a trigger to show the form in ConfigurationScreen
}

const SidebarRepositoryAdd: React.FC<SidebarRepositoryAddProps> = ({ onAddRepo }) => {
  return (
    <button
      className="rounded-md bg-gray-700 px-2 py-1 text-xs text-gray-200 hover:bg-purple-600 hover:text-white transition-colors w-fit"
      onClick={onAddRepo}
    >
      + Add Repository
    </button>
  );
};

export default SidebarRepositoryAdd;
