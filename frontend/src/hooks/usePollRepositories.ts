/**
 * Custom hook for polling repositories with in-progress assessments
 *
 * This hook automatically polls the repositories endpoint every 3 seconds
 * when there are repositories with 'pending' or 'running' status.
 * It stops polling when all repositories are completed or failed.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import apiClient from '../services/api';
import { RepositorySummary } from '../types';

interface UsePollRepositoriesOptions {
  pollingInterval?: number; // milliseconds, default 3000 (3 seconds)
  enabled?: boolean; // whether polling is enabled, default true
}

interface UsePollRepositoriesReturn {
  repositories: RepositorySummary[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  hasInProgressAssessments: boolean;
}

export const usePollRepositories = (
  options: UsePollRepositoriesOptions = {}
): UsePollRepositoriesReturn => {
  const { pollingInterval = 3000, enabled = true } = options;

  const [repositories, setRepositories] = useState<RepositorySummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasInProgressAssessments, setHasInProgressAssessments] = useState(false);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const loadRepositories = useCallback(async () => {
    try {
      console.log('[usePollRepositories] Fetching repositories...');
      const data = await apiClient.listRepositories({
        limit: 100,
        sort_by: 'last_assessed',
        order: 'desc',
      });

      const repos = data.repositories || [];
      console.log('[usePollRepositories] Received repositories:', repos.length, repos);
      setRepositories(repos);

      // Check if any repositories have in-progress assessments
      // Include null/undefined status for repos that were just added and haven't been assessed yet
      const hasInProgress = repos.some(
        (repo: RepositorySummary) =>
          repo.assessment_status === 'pending' ||
          repo.assessment_status === 'running' ||
          (repo.assessment_status === null && repo.latest_assessment_id === null)
      );
      console.log('[usePollRepositories] Has in-progress assessments:', hasInProgress);
      setHasInProgressAssessments(hasInProgress);

      setError(null);
    } catch (err) {
      console.error('[usePollRepositories] Failed to load repositories:', err);
      setError('Failed to load repositories');
      setRepositories([]);
      setHasInProgressAssessments(false);
    } finally {
      setIsLoading(false);
    }
  }, []); // Empty deps - this function is stable

  // Initial load
  useEffect(() => {
    if (enabled) {
      console.log('[usePollRepositories] Initial load triggered');
      loadRepositories();
    }
  }, [enabled, loadRepositories]);

  // Polling effect
  useEffect(() => {
    if (!enabled) {
      console.log('[usePollRepositories] Polling disabled');
      return;
    }

    // Clear existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // Only poll if there are in-progress assessments
    if (hasInProgressAssessments) {
      console.log('[usePollRepositories] Starting polling (interval:', pollingInterval, 'ms)');
      intervalRef.current = setInterval(() => {
        console.log('[usePollRepositories] Polling tick...');
        loadRepositories();
      }, pollingInterval);
    } else {
      console.log('[usePollRepositories] No in-progress assessments, stopping polling');
    }

    // Cleanup on unmount or when dependencies change
    return () => {
      if (intervalRef.current) {
        console.log('[usePollRepositories] Cleaning up polling interval');
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [hasInProgressAssessments, pollingInterval, enabled, loadRepositories]);

  return {
    repositories,
    isLoading,
    error,
    refresh: loadRepositories,
    hasInProgressAssessments,
  };
};
