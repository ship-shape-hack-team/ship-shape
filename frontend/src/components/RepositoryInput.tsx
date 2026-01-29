/**
 * Repository input component for adding new repositories
 */

import React, { useState } from 'react';
import {
  Form,
  FormGroup,
  TextInput,
  Button,
  Alert,
  AlertVariant,
} from '@patternfly/react-core';
import { PlusCircleIcon } from '@patternfly/react-icons';

interface RepositoryInputProps {
  onSubmit: (repoUrl: string) => Promise<void>;
}

export const RepositoryInput: React.FC<RepositoryInputProps> = ({ onSubmit }) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!repoUrl.trim()) {
      setError('Please enter a repository URL');
      return;
    }

    setIsLoading(true);

    try {
      await onSubmit(repoUrl);
      setSuccess(true);
      setRepoUrl('');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add repository');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ marginBottom: '2rem' }}>
      {error && (
        <Alert variant={AlertVariant.danger} title="Error" isInline style={{ marginBottom: '1rem' }}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert variant={AlertVariant.success} title="Success" isInline style={{ marginBottom: '1rem' }}>
          Repository added and assessment started!
        </Alert>
      )}

      <Form onSubmit={handleSubmit}>
        <FormGroup label="Repository URL" isRequired fieldId="repo-url">
          <div style={{ display: 'flex', gap: '1rem' }}>
            <TextInput
              id="repo-url"
              type="text"
              value={repoUrl}
              onChange={(_event, value) => setRepoUrl(value)}
              placeholder="https://github.com/owner/repo or /path/to/local/repo"
              isRequired
              style={{ flex: 1 }}
              isDisabled={isLoading}
            />
            <Button
              type="submit"
              variant="primary"
              icon={<PlusCircleIcon />}
              isLoading={isLoading}
              isDisabled={isLoading}
            >
              Add Repository
            </Button>
          </div>
        </FormGroup>
      </Form>
    </div>
  );
};
