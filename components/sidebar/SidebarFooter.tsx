import React from 'react';

interface SidebarFooterProps {
  version?: string;
}

const SidebarFooter: React.FC<SidebarFooterProps> = ({ version = 'v1.0' }) => {
  return (
    <div className="text-xs text-gray-600 pl-2 pb-2">
      {version}
    </div>
  );
};

export default SidebarFooter;
