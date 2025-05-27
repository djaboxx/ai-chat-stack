import React, { useState, useEffect } from 'react';
import type { ConfigData, Repository, RepositoryResponse, FileNode } from '../types';
import { Input } from './common/Input';
import { Button } from './common/Button';
import { Spinner } from './common/Spinner';
import { ChevronDownIcon } from './icons/ChevronDownIcon';
import { ChevronRightIcon } from './icons/ChevronRightIcon';

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
  // Repo form state
  const [isAddingRepo, setIsAddingRepo] = useState(false);
  const [editingRepoId, setEditingRepoId] = useState<string | null>(null);
  const [repoName, setRepoName] = useState(''); // Display name
  const [repoUrl, setRepoUrl] = useState(''); // Full URL (auto-generated but editable)
  const [repoHost, setRepoHost] = useState('github.com');
  const [repoOwner, setRepoOwner] = useState('');
  const [repoRepo, setRepoRepo] = useState('');
  const [repoBranch, setRepoBranch] = useState('main');
  const [repoToken, setRepoToken] = useState('');
  // Removed duplicate formError state

  // Reset repo form
  const resetRepoForm = () => {
    setRepoName('');
    setRepoUrl('');
    setRepoHost('github.com');
    setRepoOwner('');
    setRepoRepo('');
    setRepoBranch('main');
    setRepoToken('');
    setIsAddingRepo(false);
    setEditingRepoId(null);
    setFormError(null);
  };

  // Auto-generate URL when host/owner/repo changes (unless editing URL directly)
  useEffect(() => {
    if (!repoHost || !repoOwner || !repoRepo) {
      setRepoUrl('');
      return;
    }
    setRepoUrl(`https://${repoHost}/${repoOwner}/${repoRepo}`);
  }, [repoHost, repoOwner, repoRepo]);

  // Handle Gemini config submission
  const handleConfigSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!geminiToken) {
      setFormError('Gemini API Token is required.');
      return;
    }
    setFormError(null);
    onConfigure({
      geminiToken,
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
    setIsConfigured(true);
  };

  const handleRotateKey = () => {
    setGeminiToken('');
    setIsConfigured(false);
  };

  // Repo management handlers
  // Load repository data for editing
  const loadRepositoryForEdit = (repo: RepositoryResponse) => {
    setRepoName(repo.name);
    setRepoUrl(repo.url);
    setRepoHost(repo.host);
    setRepoOwner(repo.owner);
    setRepoRepo(repo.repo);
    setRepoBranch(repo.branch);
    setRepoToken(''); // Token is not returned from server for security
    setEditingRepoId(repo.id);
    setIsAddingRepo(true);
  };

  // Handle repository form submission
  const handleRepoSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoName || !repoToken || !repoOwner || !repoRepo) {
      setFormError('Repository name, token, owner, and repo are required.');
      return;
    }
    const repo: Repository = {
      name: repoName,
      url: repoUrl || `https://${repoHost}/${repoOwner}/${repoRepo}`,
      host: repoHost,
      owner: repoOwner,
      repo: repoRepo,
      branch: repoBranch || 'main',
      token: repoToken,
    };
    if (editingRepoId) {
      updateRepository(editingRepoId, repo);
    } else {
      addRepository(repo);
    }
    resetRepoForm();
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
            {formError && (
              <div className="bg-red-500 text-white p-3 rounded-md text-sm mb-4">
                {formError}
              </div>
            )}
            <form onSubmit={handleConfigSubmit} className="space-y-6 flex flex-col flex-1">
              <Input
                label="Gemini API Key"
                id="geminiToken"
                type="password"
                value={geminiToken}
                onChange={(e) => setGeminiToken(e.target.value)}
                placeholder="Your Gemini API Key"
                required
                className="bg-gray-600 border-gray-500 placeholder-gray-400"
              />
              <Button
                type="submit"
                disabled={!geminiToken || isConnecting}
                className="w-full mt-4"
              >
                Save Key
              </Button>
              {isConfigured && (
                <Button
                  type="button"
                  onClick={handleRotateKey}
                  variant="danger_ghost"
                  className="w-full mt-2"
                >
                  Rotate Key
                </Button>
              )}
            </form>
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
            {isAddingRepo && (
          <div className="bg-gray-800 p-4 rounded-lg mb-4 border border-gray-500">
            <h4 className="text-md font-medium mb-3">
              {editingRepoId ? "Edit Repository" : "Add New Repository"}
            </h4>
            <form onSubmit={handleRepoSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="Display Name" id="repoName" type="text" value={repoName} onChange={(e) => setRepoName(e.target.value)} placeholder="My Repository" required className="bg-gray-600 border-gray-500 placeholder-gray-400" />
                <Input label="GitHub Token" id="repoToken" type="password" value={repoToken} onChange={(e) => setRepoToken(e.target.value)} placeholder={editingRepoId ? "Leave blank to keep existing" : "ghp_xxxxxxxxxxxx"} required={!editingRepoId} className="bg-gray-600 border-gray-500 placeholder-gray-400" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="Host" id="repoHost" type="text" value={repoHost} onChange={(e) => setRepoHost(e.target.value)} placeholder="github.com" required className="bg-gray-600 border-gray-500 placeholder-gray-400" />
                <Input label="Owner" id="repoOwner" type="text" value={repoOwner} onChange={(e) => setRepoOwner(e.target.value)} placeholder="username or org" required className="bg-gray-600 border-gray-500 placeholder-gray-400" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input label="Repo Name" id="repoRepo" type="text" value={repoRepo} onChange={(e) => setRepoRepo(e.target.value)} placeholder="repo-name" required className="bg-gray-600 border-gray-500 placeholder-gray-400" />
                <Input label="Branch" id="repoBranch" type="text" value={repoBranch} onChange={(e) => setRepoBranch(e.target.value)} placeholder="main" className="bg-gray-600 border-gray-500 placeholder-gray-400" />
              </div>
              <Input label="Repository URL" id="repoUrl" type="text" value={repoUrl} onChange={(e) => setRepoUrl(e.target.value)} placeholder="https://github.com/owner/repo" required className="bg-gray-600 border-gray-500 placeholder-gray-400" />
              {formError && <div className="bg-red-500 text-white p-2 rounded text-xs">{formError}</div>}
              <div className="grid grid-cols-2 gap-2 mt-2">
                <Button type="button" onClick={resetRepoForm} variant="danger_ghost" className="w-full">Cancel</Button>
                <Button type="submit" variant="primary" className="w-full">{editingRepoId ? "Update Repository" : "Add Repository"}</Button>
              </div>
            </form>
          </div>
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
