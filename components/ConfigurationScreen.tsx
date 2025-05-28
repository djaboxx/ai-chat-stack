import React, { useState, useEffect } from 'react';
import type { ConfigData, Repository, RepositoryResponse, FileNode } from '../types';
import { Button } from './common/Button';
import { Spinner } from './common/Spinner';
import { ChevronDownIcon } from './icons/ChevronDownIcon';
import { ChevronRightIcon } from './icons/ChevronRightIcon';
import GitHubRepositoryForm from './forms/GitHubRepositoryForm';
import GeminiKeyForm from './forms/GeminiKeyForm';

interface ConfigurationScreenProps {
  onConfigure: (config: ConfigData) => void;
  fetchFileTree: (details: { repository_id: string }) => void;
  addRepository: (repo: Repository) => void;
  updateRepository: (id: string, repo: Repository) => void;
  deleteRepository: (id: string) => void;
  selectRepository: (id: string) => void;
  repositories: RepositoryResponse[];
  selectedRepositoryId: string | null;
  fileTreeData: FileNode[] | null;
  isFileTreeLoading: boolean;
  fileTreeError: string | null;
  isConnecting: boolean;
  activeSection?: string; // Added activeSection prop
  isAddingRepo?: boolean;
  setIsAddingRepo?: (v: boolean) => void;
}

export const ConfigurationScreen: React.FC<ConfigurationScreenProps> = ({
  onConfigure,
  fetchFileTree,
  addRepository,
  updateRepository,
  deleteRepository,
  selectRepository,
  repositories,
  selectedRepositoryId,
  fileTreeData,
  isFileTreeLoading,
  fileTreeError,
  isConnecting,
  activeSection,
  isAddingRepo: isAddingRepoProp,
  setIsAddingRepo: setIsAddingRepoProp,
}) => {
  // Collapsible section state (now influenced by activeSection)
  const [showGemini, setShowGemini] = useState(activeSection === 'gemini' || activeSection === undefined);
  const [showRepos, setShowRepos] = useState(activeSection === 'repositories' || activeSection === undefined);
  const [showFileTree, setShowFileTree] = useState(activeSection === 'filetree' || activeSection === undefined);
  
  // Update section visibility when activeSection changes
  useEffect(() => {
    if (activeSection === 'gemini') {
      setShowGemini(true);
    } else if (activeSection === 'repositories') {
      setShowRepos(true);
    } else if (activeSection === 'filetree') {
      setShowFileTree(true);
    }
  }, [activeSection]);

  // Gemini Key state
  const [geminiToken, setGeminiToken] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [isConfigured, setIsConfigured] = useState(false);

  // Repo management state
  const [selectedRepoId, setSelectedRepoId] = useState<string | null>(null);
  // Simplified repo form state
  const [isAddingRepoState, setIsAddingRepoState] = useState(false);
  const [editingRepoId, setEditingRepoId] = useState<string | null>(null);
  const isAddingRepo = typeof isAddingRepoProp === 'boolean' ? isAddingRepoProp : isAddingRepoState;
  const setIsAddingRepo = setIsAddingRepoProp || setIsAddingRepoState;

  // Reset repo form
  const resetRepoForm = () => {
    setIsAddingRepo(false);
    setEditingRepoId(null);
    setFormError(null);
  };

  // Handle Gemini config submission
  const handleConfigSubmit = (apiKey: string) => {
    if (!apiKey) {
      setFormError('Gemini API Token is required.');
      return;
    }
    setFormError(null);
    onConfigure({
      geminiToken: apiKey,
      repositories: repositories.map((repo: RepositoryResponse) => ({
        id: repo.id,
        name: repo.name,
        url: repo.url,
        host: repo.host,
        owner: repo.owner,
        repo: repo.repo,
        branch: repo.branch,
        token: '', // Not returned from server for security
      }))
    });
    setGeminiToken(apiKey);
    setIsConfigured(true);
  };

  const handleRotateKey = () => {
    setGeminiToken('');
    setIsConfigured(false);
  };

  // Repo management handlers
  // Load repository data for editing - simplified to just set the ID and show form
  const loadRepositoryForEdit = (repo: RepositoryResponse) => {
    setEditingRepoId(repo.id);
    setIsAddingRepo(true);
  };

  const handleRemoveRepo = (id: string) => {
    if (selectedRepoId === id) setSelectedRepoId(null);
    if (editingRepoId === id) setEditingRepoId(null);
  };

  const handleSelectRepo = (id: string) => {
    setSelectedRepoId(id);
    setShowFileTree(true);
  };

  return (
    <div className="flex flex-col h-full p-6 bg-gray-900 overflow-y-auto">
      {/* Gemini Key Section */}
      <div className="mb-4">
        <button
          className="flex items-center w-full text-left focus:outline-none"
          onClick={() => setShowGemini(v => !v)}
          aria-expanded={showGemini}
          aria-controls="gemini-section"
        >
          {showGemini ? <ChevronDownIcon className="w-5 h-5 mr-2" /> : <ChevronRightIcon className="w-5 h-5 mr-2" />}
          <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">
            Gemini API Key
          </h1>
        </button>
        {showGemini && (
          <div id="gemini-section" className="mt-4">
            {isConnecting && (
              <div className="flex items-center justify-center p-3 bg-yellow-500 text-yellow-900 rounded-md mb-4">
                <Spinner size="sm" />
                <span className="ml-2">Connecting to server... Please wait.</span>
              </div>
            )}
            <GeminiKeyForm
              onSubmit={handleConfigSubmit}
              isConfigured={isConfigured}
              isConnecting={isConnecting}
              apiKey={geminiToken}
              formError={formError == null ? undefined : formError}
            />
          </div>
        )}
      </div>

      {/* Git Repositories Section */}
      <div className="mb-4">
        <button
          className="flex items-center w-full text-left focus:outline-none"
          onClick={() => setShowRepos(v => !v)}
          aria-expanded={showRepos}
          aria-controls="repos-section"
        >
          {showRepos ? <ChevronDownIcon className="w-5 h-5 mr-2" /> : <ChevronRightIcon className="w-5 h-5 mr-2" />}
          <h2 className="text-xl font-bold text-purple-300">Git Repositories</h2>
        </button>
        {showRepos && (
          <div id="repos-section" className="mt-4">
            {/* Add New Repository button */}
            {!isAddingRepo && !editingRepoId && (
              <Button
                variant="primary"
                className="mb-4 w-full"
                onClick={() => setIsAddingRepo(true)}
              >
                + Add New Repository
              </Button>
            )}
            {isAddingRepo && (
              <GitHubRepositoryForm
                onSubmit={(repo: Repository) => {
                  if (editingRepoId) {
                    updateRepository(editingRepoId, repo);
                  } else {
                    addRepository(repo);
                  }
                  resetRepoForm();
                }}
                onCancel={resetRepoForm}
                initialRepository={editingRepoId ? repositories.find(r => r.id === editingRepoId) : undefined}
                isEditing={!!editingRepoId}
              />
            )}
            <ul className="divide-y divide-gray-700">
              {repositories.length === 0 && <li className="text-gray-400 text-sm py-2">No repositories added.</li>}
              {repositories.map(repo => (
                <li key={repo.id} className={`flex items-center justify-between py-2 px-1 rounded ${selectedRepoId === repo.id ? 'bg-gray-800' : ''}`}>
                  <button
                    className={`flex-1 text-left focus:outline-none ${selectedRepoId === repo.id ? 'text-pink-400 font-bold' : 'text-white'}`}
                    onClick={() => handleSelectRepo(repo.id)}
                    aria-current={selectedRepoId === repo.id}
                  >
                    {repo.name} <span className="text-xs text-gray-400 ml-2">{repo.url}</span>
                  </button>
                  <div className="flex gap-2 ml-2">
                    <Button
                      type="button"
                      size="sm"
                      variant="secondary"
                      onClick={() => loadRepositoryForEdit(repo)}
                      aria-label={`Edit ${repo.name}`}
                    >Edit</Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="danger_ghost"
                      onClick={() => handleRemoveRepo(repo.id)}
                      aria-label={`Remove ${repo.name}`}
                    >Remove</Button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* File Tree Section (only if repo selected) */}
      {selectedRepoId && (
        <div className="mb-4">
          <button
            className="flex items-center w-full text-left focus:outline-none"
            onClick={() => setShowFileTree(v => !v)}
            aria-expanded={showFileTree}
            aria-controls="filetree-section"
          >
            {showFileTree ? <ChevronDownIcon className="w-5 h-5 mr-2" /> : <ChevronRightIcon className="w-5 h-5 mr-2" />}
            <h2 className="text-xl font-bold text-purple-300">File Tree Configuration</h2>
          </button>
          {showFileTree && (
            <div id="filetree-section" className="mt-4">
              {/* Placeholder for file tree config UI */}
              <div className="text-gray-400 text-sm">File tree configuration for <span className="text-pink-400 font-bold">{repositories.find(r => r.id === selectedRepoId)?.name}</span> will appear here.</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
