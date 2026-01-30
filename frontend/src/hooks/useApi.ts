import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { testApi } from '../api/client';
import type { StartRunRequest } from '../types/api';

// Test discovery hook
export function useTests(filters?: {
  path?: string;
  keyword?: string;
  marker?: string;
}) {
  return useQuery({
    queryKey: ['tests', filters],
    queryFn: () => testApi.discoverTests(filters),
    staleTime: 30000, // 30 seconds
  });
}

// Run hooks
export function useRun(runId: string | null, enabled = true) {
  return useQuery({
    queryKey: ['run', runId],
    queryFn: () => testApi.getRun(runId!),
    enabled: enabled && !!runId,
    refetchInterval: (query) => {
      const data = query.state.data;
      // Poll every 2 seconds if running, otherwise stop polling
      return data?.status === 'running' ? 2000 : false;
    },
  });
}

export function useRuns() {
  return useQuery({
    queryKey: ['runs'],
    queryFn: () => testApi.listRuns(),
    refetchInterval: 5000, // Refresh every 5 seconds
  });
}

// Mutations
export function useStartRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: StartRunRequest) => testApi.startRun(request),
    onSuccess: () => {
      // Invalidate runs list to refetch
      queryClient.invalidateQueries({ queryKey: ['runs'] });
    },
  });
}

export function useCancelRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (runId: string) => testApi.cancelRun(runId),
    onSuccess: (_, runId) => {
      // Invalidate the specific run and runs list
      queryClient.invalidateQueries({ queryKey: ['run', runId] });
      queryClient.invalidateQueries({ queryKey: ['runs'] });
    },
  });
}
