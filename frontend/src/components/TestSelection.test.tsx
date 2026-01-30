import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TestSelection } from './TestSelection';
import { renderWithProviders } from '../test/utils';
import { testApi } from '../api/client';
import { mockTests } from '../test/mockData';

// Mock the API client
vi.mock('../api/client', () => ({
  testApi: {
    discoverTests: vi.fn(),
    startRun: vi.fn(),
  },
}));

describe('TestSelection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render loading state initially', () => {
    vi.mocked(testApi.discoverTests).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    renderWithProviders(<TestSelection />);

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('should display tests when loaded', async () => {
    vi.mocked(testApi.discoverTests).mockResolvedValue(mockTests);

    renderWithProviders(<TestSelection />);

    await waitFor(() => {
      expect(screen.getByText('Test Selection')).toBeInTheDocument();
    });

    // Check that test files are displayed
    expect(screen.getByText(/tests\/test_example.py/)).toBeInTheDocument();
    expect(screen.getByText(/tests\/test_login.py/)).toBeInTheDocument();
  });

  it('should filter tests by search term', async () => {
    vi.mocked(testApi.discoverTests).mockResolvedValue(mockTests);
    const user = userEvent.setup();

    renderWithProviders(<TestSelection />);

    await waitFor(() => {
      expect(screen.getByText('Test Selection')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search tests...');
    await user.type(searchInput, 'login');

    // Should show login test but not example tests
    await waitFor(() => {
      expect(screen.getByText(/test_login.py/)).toBeInTheDocument();
      expect(screen.queryByText(/test_example.py/)).not.toBeInTheDocument();
    });
  });

  it('should select individual tests', async () => {
    vi.mocked(testApi.discoverTests).mockResolvedValue(mockTests);
    const user = userEvent.setup();

    renderWithProviders(<TestSelection />);

    await waitFor(() => {
      expect(screen.getByText('Test Selection')).toBeInTheDocument();
    });

    // The accordions are expanded by default, so we should see the tests
    // Find a test by its name and click it
    const testOneButton = screen.getByRole('button', { name: /test_one/ });
    await user.click(testOneButton);

    // Check that the selection count updates
    await waitFor(() => {
      expect(screen.getByText(/1 selected/)).toBeInTheDocument();
    });
  });

  it('should select all tests in a file', async () => {
    vi.mocked(testApi.discoverTests).mockResolvedValue(mockTests);
    const user = userEvent.setup();

    renderWithProviders(<TestSelection />);

    await waitFor(() => {
      expect(screen.getByText('Test Selection')).toBeInTheDocument();
    });

    // Find and click the file-level checkbox
    const checkboxes = screen.getAllByRole('checkbox');
    const fileCheckbox = checkboxes[0]; // First checkbox is the file-level one
    
    await user.click(fileCheckbox);

    // Should show 2 selected (the two tests in that file)
    await waitFor(() => {
      expect(screen.getByText(/2 selected/)).toBeInTheDocument();
    });
  });

  it('should handle select all action', async () => {
    vi.mocked(testApi.discoverTests).mockResolvedValue(mockTests);
    const user = userEvent.setup();

    renderWithProviders(<TestSelection />);

    await waitFor(() => {
      expect(screen.getByText('Test Selection')).toBeInTheDocument();
    });

    const selectAllButton = screen.getByRole('button', { name: /Select All/ });
    await user.click(selectAllButton);

    expect(screen.getByText(/3 selected/)).toBeInTheDocument();
  });

  it('should handle clear selection action', async () => {
    vi.mocked(testApi.discoverTests).mockResolvedValue(mockTests);
    const user = userEvent.setup();

    renderWithProviders(<TestSelection />);

    await waitFor(() => {
      expect(screen.getByText('Test Selection')).toBeInTheDocument();
    });

    // First select all
    const selectAllButton = screen.getByRole('button', { name: /Select All/ });
    await user.click(selectAllButton);

    // Then clear
    const clearButton = screen.getByRole('button', { name: /Clear Selection/ });
    await user.click(clearButton);

    expect(screen.getByText(/0 selected/)).toBeInTheDocument();
  });

  it('should start a run when run button is clicked', async () => {
    vi.mocked(testApi.discoverTests).mockResolvedValue(mockTests);
    vi.mocked(testApi.startRun).mockResolvedValue({
      run_id: 'run-123',
      status: 'running',
    });
    const user = userEvent.setup();

    renderWithProviders(<TestSelection />);

    await waitFor(() => {
      expect(screen.getByText('Test Selection')).toBeInTheDocument();
    });

    // Select all tests
    const selectAllButton = screen.getByRole('button', { name: /Select All/ });
    await user.click(selectAllButton);

    // Click run button
    const runButton = screen.getByRole('button', { name: /Run 3 Tests/ });
    await user.click(runButton);

    await waitFor(() => {
      expect(testApi.startRun).toHaveBeenCalledWith({
        test_nodeids: expect.arrayContaining([
          'tests/test_example.py::test_one',
          'tests/test_example.py::test_two',
          'tests/test_login.py::TestLogin::test_valid',
        ]),
      });
    });
  });

  it('should display error message when tests fail to load', async () => {
    vi.mocked(testApi.discoverTests).mockRejectedValue(
      new Error('Failed to fetch tests')
    );

    renderWithProviders(<TestSelection />);

    await waitFor(() => {
      expect(screen.getByText(/Failed to load tests/)).toBeInTheDocument();
    });
  });

  it('should display info message when no tests found', async () => {
    vi.mocked(testApi.discoverTests).mockResolvedValue({
      tests: [],
      total: 0,
      grouped_by_file: {},
    });

    renderWithProviders(<TestSelection />);

    await waitFor(() => {
      expect(screen.getByText(/No tests found/)).toBeInTheDocument();
    });
  });

  it('should disable run button when no tests selected', async () => {
    vi.mocked(testApi.discoverTests).mockResolvedValue(mockTests);

    renderWithProviders(<TestSelection />);

    await waitFor(() => {
      expect(screen.getByText('Test Selection')).toBeInTheDocument();
    });

    const runButton = screen.getByRole('button', { name: /Run 0 Test/ });
    expect(runButton).toBeDisabled();
  });

  it('should refresh tests when refresh button is clicked', async () => {
    vi.mocked(testApi.discoverTests).mockResolvedValue(mockTests);
    const user = userEvent.setup();

    renderWithProviders(<TestSelection />);

    await waitFor(() => {
      expect(screen.getByText('Test Selection')).toBeInTheDocument();
    });

    const refreshButton = screen.getByRole('button', { name: /Refresh/ });
    await user.click(refreshButton);

    // Should call discover tests again
    await waitFor(() => {
      expect(testApi.discoverTests).toHaveBeenCalledTimes(2);
    });
  });
});
