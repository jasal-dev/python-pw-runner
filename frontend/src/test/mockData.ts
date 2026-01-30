import type { TestDiscoveryResponse, RunSummary, StartRunResponse } from '../types/api';

export const mockTests: TestDiscoveryResponse = {
  tests: [
    {
      nodeid: 'tests/test_example.py::test_one',
      file_path: 'tests/test_example.py',
      class_name: null,
      function_name: 'test_one',
      markers: [],
    },
    {
      nodeid: 'tests/test_example.py::test_two',
      file_path: 'tests/test_example.py',
      class_name: null,
      function_name: 'test_two',
      markers: [],
    },
    {
      nodeid: 'tests/test_login.py::TestLogin::test_valid',
      file_path: 'tests/test_login.py',
      class_name: 'TestLogin',
      function_name: 'test_valid',
      markers: [],
    },
  ],
  total: 3,
  grouped_by_file: {
    'tests/test_example.py': [
      {
        nodeid: 'tests/test_example.py::test_one',
        file_path: 'tests/test_example.py',
        class_name: null,
        function_name: 'test_one',
        markers: [],
      },
      {
        nodeid: 'tests/test_example.py::test_two',
        file_path: 'tests/test_example.py',
        class_name: null,
        function_name: 'test_two',
        markers: [],
      },
    ],
    'tests/test_login.py': [
      {
        nodeid: 'tests/test_login.py::TestLogin::test_valid',
        file_path: 'tests/test_login.py',
        class_name: 'TestLogin',
        function_name: 'test_valid',
        markers: [],
      },
    ],
  },
};

export const mockRunSummary: RunSummary = {
  run_id: 'run-20240130-120000-abc123',
  start_time: '2024-01-30T12:00:00',
  end_time: '2024-01-30T12:01:00',
  duration_seconds: 60,
  status: 'completed',
  total_tests: 3,
  passed: 2,
  failed: 1,
  skipped: 0,
  tests: [
    {
      nodeid: 'tests/test_example.py::test_one',
      outcome: 'passed',
      duration_seconds: 1.5,
      artifacts: {},
    },
    {
      nodeid: 'tests/test_example.py::test_two',
      outcome: 'passed',
      duration_seconds: 2.0,
      artifacts: {},
    },
    {
      nodeid: 'tests/test_login.py::TestLogin::test_valid',
      outcome: 'failed',
      duration_seconds: 1.2,
      artifacts: {},
    },
  ],
};

export const mockRunningRun: RunSummary = {
  run_id: 'run-20240130-130000-def456',
  start_time: '2024-01-30T13:00:00',
  end_time: null,
  duration_seconds: null,
  status: 'running',
  total_tests: 2,
  passed: 1,
  failed: 0,
  skipped: 0,
  tests: [
    {
      nodeid: 'tests/test_example.py::test_one',
      outcome: 'passed',
      duration_seconds: 1.5,
      artifacts: {},
    },
  ],
};

export const mockStartRunResponse: StartRunResponse = {
  run_id: 'run-20240130-140000-ghi789',
  status: 'running',
};
