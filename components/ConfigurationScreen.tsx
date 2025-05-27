import React, { useState, useEffect } from 'react';
import type { ConfigData, Repository, RepositoryResponse, FileNode } from '../types';
import { Input } from './common/Input';
import { Button } from './common/Button';
import { Spinner } from './common/Spinner';
import { FileTree } from './FileTree';

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
}) => {
  const [geminiToken, setGeminiToken] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [formError, setFormError] = useState<string | null>(null);
  const [isConfigured, setIsConfigured] = useState(false);
  
  // Repository form
  const [isAddingRepo, setIsAddingRepo] = useState(false);
  const [editingRepoId, setEditingRepoId] = useState<string | null>(null);
  const [repoName, setRepoName] = useState('');
  const [repoUrl, setRepoUrl] = useState('');
  const [repoHost, setRepoHost] = useState('github.com');
  const [repoOwner, setRepoOwner] = useState('');
  const [repoName2, setRepoName2] = useState('');
  const [repoBranch, setRepoBranch] = useState('main');
  const [repoToken, setRepoToken] = useState('');

  // Reset repo form
  const resetRepoForm = () => {
    setRepoName('');
    setRepoUrl('');
    setRepoHost('github.com');
    setRepoOwner('');
    setRepoName2('');
    setRepoBranch('main');
    setRepoToken('');
    setIsAddingRepo(false);
    setEditingRepoId(null);
  };

  // Load repository data for editing
  const loadRepositoryForEdit = (repo: RepositoryResponse) => {
    setRepoName(repo.name);
    setRepoUrl(repo.url);
    setRepoHost(repo.host);
    setRepoOwner(repo.owner);
    setRepoName2(repo.repo);
    setRepoBranch(repo.branch);
    setRepoToken(''); // Token is not returned from server for security
    setEditingRepoId(repo.id);
    setIsAddingRepo(true);
  };

  // Handle repository form submission
  const handleRepoSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!repoName || !repoToken || !repoOwner || !repoName2) {
      setFormError('Repository name, token, owner, and name are required.');
      return;
    }

    const repo: Repository = {
      name: repoName,
      url: repoUrl || `https://${repoHost}/${repoOwner}/${repoName2}`,
      host: repoHost,
      owner: repoOwner,
      repo: repoName2,
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

  // Handle configuration submission
  const handleConfigSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!geminiToken) {
      setFormError('Gemini API Token is required.');
      return;
    }
    if (repositories.length === 0) {
      setFormError('Please add at least one repository.');
      return;
    }
    setFormError(null);
    
    // Create config data with current repositories
    const config: ConfigData = {
      geminiToken,
      repositories: repositories.map(repo => ({
        id: repo.id,
        name: repo.name,
        url: repo.url,
        host: repo.host,
        owner: repo.owner,
        repo: repo.repo,
        branch: repo.branch,
        token: '', // We don't have the token anymore
      })),
    };
    
    onConfigure(config);
    setIsConfigured(true);
  };

  // Clear selected files when file tree data changes
  useEffect(() => {
    setSelectedFiles([]);
  }, [fileTreeData]);

  return (
    <div className="flex-grow flex flex-col items-center justify-center p-4 sm:p-6 md:p-8 bg-gray-800 overflow-y-auto">
      <div className="w-full max-w-3xl bg-gray-700 shadow-2xl rounded-xl p-6 sm:p-8 space-y-6">
        <h1 className="text-3xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500 mb-6">
          Configure Your AI Agent
        </h1>

        {isConnecting && (
          <div className="flex items-center justify-center p-3 bg-yellow-500 text-yellow-900 rounded-md">
            <Spinner size="sm" />
            <span className="ml-2">Connecting to server... Please wait.</span>
          </div>
        )}

        {formError && (
          <div className="bg-red-500 text-white p-3 rounded-md text-sm">
            {formError}
          </div>
        )}

        {/* Main Configuration Form */}
        <form onSubmit={handleConfigSubmit} className="space-y-6">
          <div className="grid grid-cols-1 gap-6">
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
          </div>

          {/* Repository Management */}
          <div className="mt-6 bg-gray-600 p-4 rounded-lg border border-gray-500">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-200">Repositories</h3>
              {!isAddingRepo && (
                <Button
                  type="button"
                  onClick={() => setIsAddingRepo(true)}
                  variant="primary"
                  size="sm"
                >
                  Add Repository
                </Button>
              )}
            </div>

            {/* Repository Form */}
            {isAddingRepo && (
              <div className="bg-gray-700 p-4 rounded-lg mb-4 border border-gray-500">
                <h4 className="text-md font-medium mb-3">
                  {editingRepoId ? "Edit Repository" : "Add New Repository"}
                </h4>
                <form onSubmit={handleRepoSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label="Repository Name (Display Name)"
                      id="repoName"
                      type="text"
                      value={repoName}
                      onChange={(e) => setRepoName(e.target.value)}
                      placeholder="My Repository"
                      required
                      className="bg-gray-600 border-gray-500 placeholder-gray-400"
                    />
                    <Input
                      label="GitHub Token"
                      id="repoToken"
                      type="password"
                      value={repoToken}
                      onChange={(e) => setRepoToken(e.target.value)}
                      placeholder={editingRepoId ? "Leave blank to keep existing" : "ghp_xxxxxxxxxxxx"}
                      required={!editingRepoId}
                      className="bg-gray-600 border-gray-500 placeholder-gray-400"
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label="GitHub Host"
                      id="repoHost"
                      type="text"
                      value={repoHost}
                      onChange={(e) => setRepoHost(e.target.value)}
                      placeholder="github.com"
                      className="bg-gray-600 border-gray-500 placeholder-gray-400"
                      helpText="Use github.com or your Enterprise instance"
                    />
                    <Input
                      label="Repository Owner"
                      id="repoOwner"
                      type="text"
                      value={repoOwner}
                      onChange={(e) => setRepoOwner(e.target.value)}
                      placeholder="username or org"
                      required
                      className="bg-gray-600 border-gray-500 placeholder-gray-400"
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label="Repository Name"
                      id="repoName2"
                      type="text"
                      value={repoName2}
                      onChange={(e) => setRepoName2(e.target.value)}
                      placeholder="repo-name"
                      required
                      className="bg-gray-600 border-gray-500 placeholder-gray-400"
                    />
                    <Input
                      label="Branch"
                      id="repoBranch"
                      type="text"
                      value={repoBranch}
                      onChange={(e) => setRepoBranch(e.target.value)}
                      placeholder="main"
                      className="bg-gray-600 border-gray-500 placeholder-gray-400"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2 mt-2">
                    <Button
                      type="button"
                      onClick={resetRepoForm}
                      variant="danger_ghost"
                      className="w-full"
                    >
                      Cancel
                    </Button>
                    <Button type="submit" variant="primary" className="w-full">
                      {editingRepoId ? "Update Repository" : "Add Repository"}
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* Repository List */}
            {repositories.length === 0 ? (
              <div className="text-gray-400 text-center py-6">
                No repositories configured. Add a repository to get started.
              </div>
            ) : (
              <div className="space-y-3">
                {repositories.map((repo) => (
                  <div
                    key={repo.id}
                    className={`flex flex-col sm:flex-row sm:items-center justify-between p-3 rounded-lg ${
                      selectedRepositoryId === repo.id
                        ? "bg-blue-700 bg-opacity-40"
                        : "bg-gray-700"
                    }`}
                  >
                    <div className="mb-2 sm:mb-0">
                      <h4 className="font-medium">{repo.name}</h4>
                      <p className="text-xs text-gray-400">
                        {repo.host}/{repo.owner}/{repo.repo}:{repo.branch}
                      </p>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        type="button"
                        onClick={() => selectRepository(repo.id)}
                        variant="ghost"
                        size="sm"
                        className={
                          selectedRepositoryId === repo.id
                            ? "bg-blue-600"
                            : ""
                        }
                      >
                        {selectedRepositoryId === repo.id ? "Selected" : "Select"}
                      </Button>
                      <Button
                        type="button"
                        onClick={() => loadRepositoryForEdit(repo)}
                        variant="ghost"
                        size="sm"
                      >
                        Edit
                      </Button>
                      <Button
                        type="button"
                        onClick={() => deleteRepository(repo.id)}
                        variant="danger_ghost"
                        size="sm"
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* File Tree */}
          {selectedRepositoryId && (
            <div>
              <div className="flex justify-between items-center mb-2">
                <h3 className="text-md font-semibold text-gray-200">
                  File Tree
                </h3>
                <Button
                  type="button"
                  onClick={() => {
                    if (selectedRepositoryId) {
                      fetchFileTree({ repository_id: selectedRepositoryId });
                    }
                  }}
                  disabled={isFileTreeLoading || !selectedRepositoryId || isConnecting}
                  variant="secondary"
                  size="sm"
                >
                  {isFileTreeLoading ? <Spinner size="sm" /> : "Refresh Files"}
                </Button>
              </div>

              {fileTreeError && (
                <div className="bg-red-500 text-white p-3 rounded-md text-sm mt-2">
                  Error fetching file tree: {fileTreeError}
                </div>
              )}

              {fileTreeData && !isFileTreeLoading && !fileTreeError && (
                <div className="mt-2 bg-gray-600 p-4 rounded-lg max-h-72 overflow-y-auto border border-gray-500">
                  <FileTree
                    nodes={fileTreeData}
                    selectedPaths={selectedFiles}
                    onSelectionChange={setSelectedFiles}
                  />
                </div>
              )}
              
              {isFileTreeLoading && (
                <div className="mt-2 flex flex-col items-center justify-center text-gray-400 p-4 bg-gray-600 rounded-lg border border-gray-500">
                  <Spinner />
                  <p className="mt-2">Loading file tree...</p>
                </div>
              )}
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={
              !geminiToken ||
              repositories.length === 0 ||
              isConnecting ||
              isConfigured
            }
            className="w-full !mt-8"
          >
            {isConfigured ? "Configuration Applied" : "Apply Configuration"}
          </Button>
        </form>
      </div>
    </div>
  );
};
