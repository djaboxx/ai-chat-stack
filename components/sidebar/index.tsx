import React from 'react';
import SidebarHeader from './SidebarHeader';
import SidebarConfigSection from './SidebarConfigSection';
import SidebarInteractionSection from './SidebarInteractionSection';
import SidebarFooter from './SidebarFooter';

interface SidebarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  onShowSection?: (section: string, show: boolean) => void;
  showAddRepoForm?: () => void; // replaces onAddRepo
  version?: string;
}

const Sidebar: React.FC<SidebarProps> = ({
  activeSection,
  onSectionChange,
  onShowSection,
  showAddRepoForm,
  version
}) => {
  return (
    <div className="min-h-screen w-64 bg-[#181c20] flex flex-col py-6 px-3 border-r border-gray-800 shadow-lg">
      <SidebarHeader />
      
      <SidebarConfigSection
        activeSection={activeSection}
        onSectionChange={onSectionChange}
        onShowSection={onShowSection}
        showAddRepoForm={showAddRepoForm}
      />
      
      <SidebarInteractionSection
        activeSection={activeSection}
        onSectionChange={onSectionChange}
      />
      
      <div className="flex-1" />
      
      <SidebarFooter version={version} />
    </div>
  );
};

export default Sidebar;
