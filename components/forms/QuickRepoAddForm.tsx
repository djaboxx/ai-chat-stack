import React, { useState } from 'react';
import { Button } from '../common/Button';

interface QuickRepoAddFormProps {
  onAddRepo: (repoUrl: string) => void;
  onCancel?: () => void;
}

const QuickRepoAddForm: React.FC<QuickRepoAddFormProps> = ({ onAddRepo, onCancel }) => {
  const [repoInput, setRepoInput] = useState('');
  
  const handleAddRepo = () => {
    if (repoInput.trim()) {
      onAddRepo(repoInput.trim());
      setRepoInput('');
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="text-xs text-gray-400 mb-1">Add GitHub Repository URL:</div>
      <div className="flex gap-2">
        <input
          type="text"
          className="flex-1 rounded-md bg-gray-800 border border-gray-700 px-2 py-1 text-sm text-gray-200 focus:outline-none focus:ring-2 focus:ring-purple-500"
          placeholder="https://github.com/owner/repo"
          value={repoInput}
          onChange={e => setRepoInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleAddRepo(); }}
          autoFocus
        />
        <Button
          size="sm"
          onClick={handleAddRepo}
          disabled={!repoInput.trim()}
          className="rounded-md"
        >
          Add
        </Button>
        {onCancel && (
          <button
            className="rounded-md px-2 py-1 text-gray-400 hover:text-red-400 text-xs focus:outline-none"
            onClick={onCancel}
            title="Cancel"
          >
            ✕
          </button>
        )}
      </div>
      <div className="text-xs text-gray-500 mt-1">
        Note: You can configure repository details in the settings.
      </div>
    </div>
  );
};

export default QuickRepoAddForm;
