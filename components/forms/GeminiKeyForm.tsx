import React, { useState } from 'react';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { Spinner } from '../common/Spinner';

interface GeminiKeyFormProps {
  onSubmit: (apiKey: string) => void;
  isConfigured?: boolean;
  isConnecting?: boolean;
  apiKey?: string; // Optional prop to pre-fill the key
  onRotateKey?: () => void; // Optional callback for rotating key
  formError?: string; // Optional prop to display form error
}

const GeminiKeyForm: React.FC<GeminiKeyFormProps> = ({
  onSubmit,
  isConfigured = false,
  isConnecting = false,
}) => {
  const [geminiToken, setGeminiToken] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!geminiToken) {
      setFormError('Gemini API Token is required.');
      return;
    }
    setFormError(null);
    onSubmit(geminiToken);
  };

  const handleRotateKey = () => {
    setGeminiToken('');
  };

  return (
    <div className="w-full">
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
      
      <form onSubmit={handleSubmit} className="space-y-6 flex flex-col">
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
  );
};

export default GeminiKeyForm;
