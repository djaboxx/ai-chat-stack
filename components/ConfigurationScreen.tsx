
import React, { useState, useEffect } from 'react';
import type { ConfigData, FileNode } from '../types';
import { Input } from './common/Input';
import { Button } from './common/Button';
import { Spinner } from './common/Spinner';
import { FileTree } from './FileTree';

interface ConfigurationScreenProps {
  onConfigure: (config: ConfigData) => void;
  fetchFileTree: (details: { repo: string; branch: string; githubToken: string }) => void;
  fileTreeData: FileNode[] | null;
  isFileTreeLoading: boolean;
  fileTreeError: string | null;
  isConnecting: boolean;
}

export const ConfigurationScreen: React.FC<ConfigurationScreenProps> = ({
  onConfigure,
  fetchFileTree,
  fileTreeData,
  isFileTreeLoading,
  fileTreeError,
  isConnecting,
}) => {
  const [githubToken, setGithubToken] = useState('');
  const [geminiToken, setGeminiToken] = useState('');
  const [githubRepo, setGithubRepo] = useState(''); // e.g., "owner/repo"
  const [githubBranch, setGithubBranch] = useState('main');
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [formError, setFormError] = useState<string | null>(null);

  const handleFetchFiles = () => {
    if (!githubToken || !githubRepo || !githubBranch) {
      setFormError('GitHub Token, Repository, and Branch are required to fetch files.');
      return;
    }
    setFormError(null);
    fetchFileTree({ repo: githubRepo, branch: githubBranch, githubToken: githubToken });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!githubToken || !geminiToken || !githubRepo || !githubBranch) {
      setFormError('All fields (GitHub Token, Gemini Token, GitHub Repo, GitHub Branch) are required.');
      return;
    }
    if (!fileTreeData || selectedFiles.length === 0) {
      setFormError('Please fetch and select at least one file or folder from the repository.');
      return;
    }
    setFormError(null);
    onConfigure({
      githubToken,
      geminiToken,
      githubRepo,
      githubBranch,
      selectedFiles,
    });
  };

  useEffect(() => {
    // Clear selected files if file tree data changes (e.g., new fetch)
    setSelectedFiles([]);
  }, [fileTreeData]);

  return (
    <div className="flex-grow flex flex-col items-center justify-center p-4 sm:p-6 md:p-8 bg-gray-800 overflow-y-auto">
      <div className="w-full max-w-2xl bg-gray-700 shadow-2xl rounded-xl p-6 sm:p-8 space-y-6">
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

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input
              label="GitHub Personal Access Token"
              id="githubToken"
              type="password"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              placeholder="ghp_xxxxxxxxxxxx"
              required
              className="bg-gray-600 border-gray-500 placeholder-gray-400"
            />
            <Input
              label="Gemini API Key"
              id="geminiToken"
              type="password"
              value={geminiToken}
              onChange={(e) => setGeminiToken(e.target.value)}
              placeholder="Your Gemini API Key"
              required
              className="bg-gray-600 border-gray-500 placeholder-gray-400"
              helpText="Note: For Gemini API, it's best if the backend uses an environment variable (process.env.API_KEY)."
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input
              label="GitHub Repository"
              id="githubRepo"
              type="text"
              value={githubRepo}
              onChange={(e) => setGithubRepo(e.target.value)}
              placeholder="owner/repository-name"
              required
              className="bg-gray-600 border-gray-500 placeholder-gray-400"
            />
            <Input
              label="GitHub Branch"
              id="githubBranch"
              type="text"
              value={githubBranch}
              onChange={(e) => setGithubBranch(e.target.value)}
              placeholder="main"
              required
              className="bg-gray-600 border-gray-500 placeholder-gray-400"
            />
          </div>

          <div className="pt-2">
            <Button type="button" onClick={handleFetchFiles} disabled={isFileTreeLoading || !githubToken || !githubRepo || !githubBranch || isConnecting} variant="secondary" className="w-full">
              {isFileTreeLoading ? <Spinner size="sm" /> : 'Fetch Repository Files'}
            </Button>
          </div>

          {fileTreeError && (
            <div className="bg-red-500 text-white p-3 rounded-md text-sm mt-4">
              Error fetching file tree: {fileTreeError}
            </div>
          )}

          {fileTreeData && !isFileTreeLoading && !fileTreeError && (
            <div className="mt-6 bg-gray-600 p-4 rounded-lg max-h-72 overflow-y-auto border border-gray-500">
              <h3 className="text-lg font-semibold mb-2 text-gray-200">Select Files/Folders for Context:</h3>
              <FileTree
                nodes={fileTreeData}
                selectedPaths={selectedFiles}
                onSelectionChange={setSelectedFiles}
              />
            </div>
          )}
          
          {isFileTreeLoading && !fileTreeData && (
            <div className="mt-6 flex flex-col items-center justify-center text-gray-400 p-4">
              <Spinner />
              <p className="mt-2">Loading file tree...</p>
            </div>
          )}


          <Button type="submit" disabled={isFileTreeLoading || !fileTreeData || selectedFiles.length === 0 || isConnecting} className="w-full !mt-8">
            Configure & Start Chat
          </Button>
        </form>
      </div>
    </div>
  );
};
