import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTests, useStartRun, useRuns, useCancelRun } from '../hooks/useApi';
import { testApi } from '../api/client';
import { mockTests, mockRunSummary, mockStartRunResponse } from '../test/mockData';

// Mock the API client
vi.mock('../api/client', () => ({
  testApi: {
    discoverTests: vi.fn(),
    startRun: vi.fn(),
    listRuns: vi.fn(),
    getRun: vi.fn(),
    cancelRun: vi.fn(),
  },
}));

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

describe('useTests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch tests successfully', async () => {
    vi.mocked(testApi.discoverTests).mockResolvedValue(mockTests);

    const { result } = renderHook(() => useTests(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockTests);
    expect(testApi.discoverTests).toHaveBeenCalledTimes(1);
  });

  it('should handle filters', async () => {
    vi.mocked(testApi.discoverTests).mockResolvedValue(mockTests);

    const filters = { path: 'tests/', keyword: 'test' };
    const { result } = renderHook(() => useTests(filters), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(testApi.discoverTests).toHaveBeenCalledWith(filters);
  });

  it('should handle errors', async () => {
    const error = new Error('Failed to fetch tests');
    vi.mocked(testApi.discoverTests).mockRejectedValue(error);

    const { result } = renderHook(() => useTests(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBe(error);
  });
});

describe('useStartRun', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should start a run successfully', async () => {
    vi.mocked(testApi.startRun).mockResolvedValue(mockStartRunResponse);

    const { result } = renderHook(() => useStartRun(), { wrapper: createWrapper() });

    const request = { test_nodeids: ['test1', 'test2'] };
    result.current.mutate(request);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockStartRunResponse);
    expect(testApi.startRun).toHaveBeenCalledWith(request);
  });

  it('should handle errors when starting a run', async () => {
    const error = new Error('Failed to start run');
    vi.mocked(testApi.startRun).mockRejectedValue(error);

    const { result } = renderHook(() => useStartRun(), { wrapper: createWrapper() });

    result.current.mutate({ test_nodeids: ['test1'] });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBe(error);
  });
});

describe('useRuns', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch runs successfully', async () => {
    const mockRuns = [mockRunSummary];
    vi.mocked(testApi.listRuns).mockResolvedValue(mockRuns);

    const { result } = renderHook(() => useRuns(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockRuns);
    expect(testApi.listRuns).toHaveBeenCalledTimes(1);
  });
});

describe('useCancelRun', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should cancel a run successfully', async () => {
    const cancelResponse = { status: 'cancelled', run_id: 'run-123' };
    vi.mocked(testApi.cancelRun).mockResolvedValue(cancelResponse);

    const { result } = renderHook(() => useCancelRun(), { wrapper: createWrapper() });

    result.current.mutate('run-123');

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(cancelResponse);
    expect(testApi.cancelRun).toHaveBeenCalledWith('run-123');
  });
});
