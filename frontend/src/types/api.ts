// Type definitions for the Python Playwright Test Runner API

export interface TestInfo {
  nodeid: string;
  file_path: string;
  class_name: string | null;
  function_name: string;
  markers: string[];
}

export interface TestDiscoveryResponse {
  tests: TestInfo[];
  total: number;
  grouped_by_file: Record<string, TestInfo[]>;
}

export interface TestResult {
  nodeid: string;
  outcome: string;
  duration_seconds: number;
  artifacts: Record<string, string>;
}

export interface RunSummary {
  run_id: string;
  start_time: string;
  end_time: string | null;
  duration_seconds: number | null;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  total_tests: number;
  passed: number;
  failed: number;
  skipped: number;
  tests: TestResult[];
}

export interface StartRunRequest {
  test_nodeids: string[];
  pytest_args?: string[];
}

export interface StartRunResponse {
  run_id: string;
  status: string;
}
