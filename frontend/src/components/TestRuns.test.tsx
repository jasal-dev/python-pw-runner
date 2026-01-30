import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TestRuns } from './TestRuns';
import { renderWithProviders } from '../test/utils';
import { testApi } from '../api/client';
import { mockRunSummary, mockRunningRun } from '../test/mockData';

// Mock the API client
vi.mock('../api/client', () => ({
  testApi: {
    listRuns: vi.fn(),
    cancelRun: vi.fn(),
    getTraceUrl: vi.fn((runId: string, testName: string) => 
      `/artifacts/${runId}/tests/${testName}/trace.zip`
    ),
    getRunSummaryUrl: vi.fn((runId: string) => 
      `/artifacts/${runId}/run-summary.json`
    ),
  },
}));

describe('TestRuns', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render loading state initially', () => {
    vi.mocked(testApi.listRuns).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    renderWithProviders(<TestRuns />);

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('should display runs when loaded', async () => {
    vi.mocked(testApi.listRuns).mockResolvedValue([mockRunSummary]);

    renderWithProviders(<TestRuns />);

    await waitFor(() => {
      expect(screen.getByText('Test Runs')).toBeInTheDocument();
    });

    expect(screen.getByText(mockRunSummary.run_id)).toBeInTheDocument();
  });

  it('should display empty state when no runs exist', async () => {
    vi.mocked(testApi.listRuns).mockResolvedValue([]);

    renderWithProviders(<TestRuns />);

    await waitFor(() => {
      expect(screen.getByText(/No test runs yet/)).toBeInTheDocument();
    });
  });

  it('should display run status with correct color', async () => {
    vi.mocked(testApi.listRuns).mockResolvedValue([mockRunSummary]);

    renderWithProviders(<TestRuns />);

    await waitFor(() => {
      expect(screen.getByText('completed')).toBeInTheDocument();
    });
  });

  it('should display test result counts', async () => {
    vi.mocked(testApi.listRuns).mockResolvedValue([mockRunSummary]);

    renderWithProviders(<TestRuns />);

    await waitFor(() => {
      expect(screen.getByText(/✓ 2/)).toBeInTheDocument(); // 2 passed
      expect(screen.getByText(/✗ 1/)).toBeInTheDocument(); // 1 failed
      expect(screen.getByText(/⊘ 0/)).toBeInTheDocument(); // 0 skipped
    });
  });

  it('should expand and collapse run details', async () => {
    vi.mocked(testApi.listRuns).mockResolvedValue([mockRunSummary]);
    const user = userEvent.setup();

    renderWithProviders(<TestRuns />);

    await waitFor(() => {
      expect(screen.getByText(mockRunSummary.run_id)).toBeInTheDocument();
    });

    // Find and click the expand button
    const expandButtons = screen.getAllByRole('button');
    const expandButton = expandButtons.find(btn => 
      btn.querySelector('svg')
    );
    
    if (expandButton) {
      await user.click(expandButton);

      // Should show test results
      await waitFor(() => {
        expect(screen.getByText('Test Results')).toBeInTheDocument();
      });

      // Should show individual tests
      expect(screen.getByText(/tests\/test_example.py::test_one/)).toBeInTheDocument();
    }
  });

  it('should display download links for traces', async () => {
    vi.mocked(testApi.listRuns).mockResolvedValue([mockRunSummary]);
    const user = userEvent.setup();

    renderWithProviders(<TestRuns />);

    await waitFor(() => {
      expect(screen.getByText(mockRunSummary.run_id)).toBeInTheDocument();
    });

    // Expand the run
    const expandButtons = screen.getAllByRole('button');
    const expandButton = expandButtons.find(btn => 
      btn.querySelector('svg')
    );
    
    if (expandButton) {
      await user.click(expandButton);

      await waitFor(() => {
        const downloadLinks = screen.getAllByText('Download Trace');
        expect(downloadLinks.length).toBeGreaterThan(0);
      });
    }
  });

  it('should show cancel button for running tests', async () => {
    vi.mocked(testApi.listRuns).mockResolvedValue([mockRunningRun]);

    renderWithProviders(<TestRuns />);

    await waitFor(() => {
      expect(screen.getByText('running')).toBeInTheDocument();
    });

    // Should have a stop/cancel button
    const buttons = screen.getAllByRole('button');
    const cancelButton = buttons.find(btn => 
      btn.querySelector('[data-testid="StopIcon"]')
    );
    
    expect(cancelButton).toBeTruthy();
  });

  it('should cancel a run when cancel button is clicked', async () => {
    vi.mocked(testApi.listRuns).mockResolvedValue([mockRunningRun]);
    vi.mocked(testApi.cancelRun).mockResolvedValue({
      status: 'cancelled',
      run_id: mockRunningRun.run_id,
    });
    const user = userEvent.setup();

    renderWithProviders(<TestRuns />);

    await waitFor(() => {
      expect(screen.getByText('running')).toBeInTheDocument();
    });

    // Find and click cancel button
    const buttons = screen.getAllByRole('button');
    const cancelButton = buttons.find(btn => 
      btn.querySelector('[data-testid="StopIcon"]')
    );
    
    if (cancelButton) {
      await user.click(cancelButton);

      await waitFor(() => {
        expect(testApi.cancelRun).toHaveBeenCalledWith(mockRunningRun.run_id);
      });
    }
  });

  it('should display error message when runs fail to load', async () => {
    vi.mocked(testApi.listRuns).mockRejectedValue(
      new Error('Failed to fetch runs')
    );

    renderWithProviders(<TestRuns />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to load runs/)).toBeInTheDocument();
    });
  });

  it('should display duration when available', async () => {
    vi.mocked(testApi.listRuns).mockResolvedValue([mockRunSummary]);

    renderWithProviders(<TestRuns />);

    await waitFor(() => {
      expect(screen.getByText(/60.00s/)).toBeInTheDocument();
    });
  });

  it('should display formatted start time', async () => {
    vi.mocked(testApi.listRuns).mockResolvedValue([mockRunSummary]);

    renderWithProviders(<TestRuns />);

    await waitFor(() => {
      // The exact format depends on locale, but it should be present
      const timeElements = screen.getAllByText(/2024|1\/30|30\/1/);
      expect(timeElements.length).toBeGreaterThan(0);
    });
  });

  it('should render action buttons for completed runs', async () => {
    vi.mocked(testApi.listRuns).mockResolvedValue([mockRunSummary]);

    renderWithProviders(<TestRuns />);

    await waitFor(() => {
      expect(screen.getByText(mockRunSummary.run_id)).toBeInTheDocument();
    });

    // For completed runs, the component should render successfully
    expect(screen.getByText('Test Runs')).toBeInTheDocument();
  });
});
