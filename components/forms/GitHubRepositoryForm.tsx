import React, { useState } from 'react';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import type { Repository, RepositoryResponse } from '../../types';

interface GitHubRepositoryFormProps {
  onSubmit: (repository: Repository) => void;
  onCancel: () => void;
  initialRepository?: RepositoryResponse;
  isEditing?: boolean;
}

const GitHubRepositoryForm: React.FC<GitHubRepositoryFormProps> = ({
  onSubmit,
  onCancel,
  initialRepository,
  isEditing = false,
}) => {
  const [repoName, setRepoName] = useState(initialRepository?.name || '');
  // URL is now auto-generated internally when needed
  const [repoHost, setRepoHost] = useState(initialRepository?.host || 'github.com');
  const [repoOwner, setRepoOwner] = useState(initialRepository?.owner || '');
  const [repoRepo, setRepoRepo] = useState(initialRepository?.repo || '');
  const [repoBranch, setRepoBranch] = useState(initialRepository?.branch || 'main');
  const [repoToken, setRepoToken] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoName || !repoOwner || !repoRepo || !repoHost) {
      setFormError('Repository name, owner, and repo are required.');
      return;
    }
    
    if (!isEditing && !repoToken) {
      setFormError('GitHub token is required for new repositories.');
      return;
    }
    
    // Auto-generate URL from host, owner, repo
    const url = `https://${repoHost}/${repoOwner}/${repoRepo}`;
    
    const repository: Repository = {
      name: repoName,
      url: url,
      host: repoHost,
      owner: repoOwner,
      repo: repoRepo,
      branch: repoBranch || 'main',
      token: repoToken,
      id: initialRepository?.id
    };
    
    setFormError(null);
    onSubmit(repository);
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg border border-gray-500">
      <h4 className="text-md font-medium mb-3">
        {isEditing ? "Edit Repository" : "Add New Repository"}
      </h4>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input 
            label="Display Name" 
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
            placeholder={isEditing ? "Leave blank to keep existing" : "ghp_xxxxxxxxxxxx"} 
            required={!isEditing} 
            className="bg-gray-600 border-gray-500 placeholder-gray-400" 
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input 
            label="Host" 
            id="repoHost" 
            type="text" 
            value={repoHost} 
            onChange={(e) => setRepoHost(e.target.value)} 
            placeholder="github.com" 
            required 
            className="bg-gray-600 border-gray-500 placeholder-gray-400" 
          />
          <Input 
            label="Owner" 
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
            label="Repo Name" 
            id="repoRepo" 
            type="text" 
            value={repoRepo} 
            onChange={(e) => setRepoRepo(e.target.value)} 
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
        
        {/* URL field removed as it won't be used - URL is auto-generated */}
        
        {formError && (
          <div className="bg-red-500 text-white p-2 rounded text-xs">
            {formError}
          </div>
        )}
        
        <div className="grid grid-cols-2 gap-2 mt-2">
          <Button type="button" onClick={onCancel} variant="danger_ghost" className="w-full">
            Cancel
          </Button>
          <Button type="submit" variant="primary" className="w-full">
            {isEditing ? "Update Repository" : "Add Repository"}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default GitHubRepositoryForm;
