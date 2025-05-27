import React from 'react';
// @ts-ignore
import SidebarMenu from 'react-sidebar-menu';
import 'react-sidebar-menu/dist/sidebar-menu.css';

const menuItems = [
  {
    header: true,
    title: 'Menu',
    hiddenOnCollapse: true
  },
  {
    title: 'Configuration',
    icon: <span role="img" aria-label="config">⚙️</span>,
    children: [
      { title: 'Gemini Key', icon: <span role="img" aria-label="key">🔑</span> },
      { title: 'Repositories', icon: <span role="img" aria-label="repo">📁</span> },
      { title: 'File Tree', icon: <span role="img" aria-label="tree">🌲</span> },
    ]
  },
  {
    title: 'Chat',
    icon: <span role="img" aria-label="chat">💬</span>
  }
];

export const SidebarMenuWrapper: React.FC = () => (
  <SidebarMenu
    menu={menuItems}
    theme="light"
    collapse={false}
    onMenuItemClick={(item) => {
      // Optionally handle menu navigation here
    }}
  />
);
