import axios from 'axios';
import type {
  TestDiscoveryResponse,
  RunSummary,
  StartRunRequest,
  StartRunResponse,
} from '../types/api';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const testApi = {
  // Test discovery
  async discoverTests(params?: {
    path?: string;
    keyword?: string;
    marker?: string;
  }): Promise<TestDiscoveryResponse> {
    const response = await api.get<TestDiscoveryResponse>('/tests', { params });
    return response.data;
  },

  // Run management
  async startRun(request: StartRunRequest): Promise<StartRunResponse> {
    const response = await api.post<StartRunResponse>('/runs', request);
    return response.data;
  },

  async getRun(runId: string): Promise<RunSummary> {
    const response = await api.get<RunSummary>(`/runs/${runId}`);
    return response.data;
  },

  async listRuns(): Promise<RunSummary[]> {
    const response = await api.get<RunSummary[]>('/runs');
    return response.data;
  },

  async cancelRun(runId: string): Promise<{ status: string; run_id: string }> {
    const response = await api.delete(`/runs/${runId}`);
    return response.data;
  },

  // Artifact URLs
  getTraceUrl(runId: string, testName: string): string {
    return `/artifacts/${runId}/tests/${testName}/trace.zip`;
  },

  getRunSummaryUrl(runId: string): string {
    return `/artifacts/${runId}/run-summary.json`;
  },

  getEventsUrl(runId: string): string {
    return `/artifacts/${runId}/events.ndjson`;
  },
};
