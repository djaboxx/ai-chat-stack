
import React, { useState } from 'react';
import type { FileNode } from '../types';
import { FolderIcon } from './icons/FolderIcon';
import { FileIcon } from './icons/FileIcon';
import { ChevronRightIcon } from './icons/ChevronRightIcon';
import { ChevronDownIcon } from './icons/ChevronDownIcon';

interface FileTreeProps {
  nodes: FileNode[];
  selectedPaths: string[];
  onSelectionChange: (selectedPaths: string[]) => void;
  initiallyOpen?: boolean; // To control if top-level directories are open by default
}

interface TreeNodeProps {
  node: FileNode;
  selectedPaths: string[];
  onToggleSelect: (path: string, type: 'file' | 'directory', children?: FileNode[]) => void;
  level?: number;
  initiallyOpen?: boolean;
}

const TreeNode: React.FC<TreeNodeProps> = ({ node, selectedPaths, onToggleSelect, level = 0, initiallyOpen = false }) => {
  const [isOpen, setIsOpen] = useState(initiallyOpen || level === 0); // Open root level by default
  const isSelected = selectedPaths.includes(node.path);

  const handleToggleOpen = () => {
    if (node.type === 'directory') {
      setIsOpen(!isOpen);
    }
  };

  const handleSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    onToggleSelect(node.path, node.type, node.children);
  };

  const paddingLeft = `${level * 1.5}rem`; // 24px per level

  return (
    <div className="text-gray-300">
      <div
        className={`flex items-center py-1.5 px-2 rounded-md hover:bg-gray-500 transition-colors duration-150 ${isSelected ? 'bg-blue-600 bg-opacity-30' : ''}`}
        style={{ paddingLeft }}
      >
        {node.type === 'directory' && (
          <button onClick={handleToggleOpen} className="mr-2 focus:outline-none">
            {isOpen ? <ChevronDownIcon className="w-4 h-4 text-gray-400" /> : <ChevronRightIcon className="w-4 h-4 text-gray-400" />}
          </button>
        )}
        <input
          type="checkbox"
          id={`file-${node.id.replace(/[^a-zA-Z0-9]/g, '-')}`} // Sanitize ID
          checked={isSelected}
          onChange={handleSelect}
          className="mr-2 h-4 w-4 text-blue-500 bg-gray-700 border-gray-500 rounded focus:ring-blue-400 focus:ring-offset-gray-600"
        />
        {node.type === 'directory' ? <FolderIcon className="w-5 h-5 mr-2 text-yellow-400" /> : <FileIcon className="w-5 h-5 mr-2 text-blue-400" />}
        <label htmlFor={`file-${node.id.replace(/[^a-zA-Z0-9]/g, '-')}`} className="cursor-pointer select-none text-sm truncate">
          {node.name}
        </label>
      </div>
      {isOpen && node.type === 'directory' && node.children && node.children.length > 0 && (
        <div className="pl-0"> {/* No extra padding here, handled by level in TreeNode */}
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              selectedPaths={selectedPaths}
              onToggleSelect={onToggleSelect}
              level={level + 1}
              initiallyOpen={false} // Children are closed by default unless explicitly opened
            />
          ))}
        </div>
      )}
       {isOpen && node.type === 'directory' && (!node.children || node.children.length === 0) && (
         <div style={{ paddingLeft: `${(level + 1) * 1.5}rem` }} className="py-1.5 px-2 text-xs text-gray-500 italic">
            (empty directory)
          </div>
       )}
    </div>
  );
};

export const FileTree: React.FC<FileTreeProps> = ({ nodes, selectedPaths, onSelectionChange, initiallyOpen = true }) => {
  const getAllChildPaths = (node: FileNode): string[] => {
    let paths: string[] = [];
    if (node.type === 'file') {
      paths.push(node.path);
    } else if (node.type === 'directory') {
      paths.push(node.path); // Select the directory itself
      if (node.children) {
        node.children.forEach(child => {
          paths = paths.concat(getAllChildPaths(child));
        });
      }
    }
    return paths;
  };

  const handleToggleSelect = (path: string, type: 'file' | 'directory', children?: FileNode[]) => {
    let newSelectedPaths = [...selectedPaths];
    const isCurrentlySelected = selectedPaths.includes(path);
    
    let pathsToToggle: string[] = [path];
    if (type === 'directory') {
      const node = findNode(nodes, path);
      if (node) {
        pathsToToggle = getAllChildPaths(node);
      }
    }

    if (isCurrentlySelected) {
      // Deselect the item and all its children if it's a directory
      newSelectedPaths = newSelectedPaths.filter(p => !pathsToToggle.includes(p));
    } else {
      // Select the item and all its children if it's a directory
      pathsToToggle.forEach(p => {
        if (!newSelectedPaths.includes(p)) {
          newSelectedPaths.push(p);
        }
      });
    }
    onSelectionChange(newSelectedPaths);
  };

  const findNode = (nodesToSearch: FileNode[], path: string): FileNode | null => {
    for (const node of nodesToSearch) {
      if (node.path === path) return node;
      if (node.children) {
        const found = findNode(node.children, path);
        if (found) return found;
      }
    }
    return null;
  };
  
  if (!nodes || nodes.length === 0) {
    return <p className="text-gray-400 italic p-2">No files or folders to display. Try fetching them.</p>;
  }

  return (
    <div className="space-y-1">
      {nodes.map((node) => (
        <TreeNode
          key={node.id}
          node={node}
          selectedPaths={selectedPaths}
          onToggleSelect={handleToggleSelect}
          initiallyOpen={initiallyOpen}
        />
      ))}
    </div>
  );
};
