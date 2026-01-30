import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Collapse,
  Alert,
  CircularProgress,
  Link,
} from '@mui/material';
import {
  KeyboardArrowDown as ExpandIcon,
  KeyboardArrowUp as CollapseIcon,
  Download as DownloadIcon,
  Stop as StopIcon,
  CheckCircle as PassIcon,
  Error as FailIcon,
  RemoveCircle as SkipIcon,
} from '@mui/icons-material';
import { useRuns, useCancelRun } from '../hooks/useApi';
import type { RunSummary } from '../types/api';
import { testApi } from '../api/client';

const StatusChip: React.FC<{ status: RunSummary['status'] }> = ({ status }) => {
  const colorMap = {
    pending: 'default',
    running: 'primary',
    completed: 'success',
    failed: 'error',
    cancelled: 'warning',
  } as const;

  return <Chip label={status} color={colorMap[status]} size="small" />;
};

const TestResultIcon: React.FC<{ outcome: string }> = ({ outcome }) => {
  if (outcome === 'passed') return <PassIcon color="success" fontSize="small" />;
  if (outcome === 'failed') return <FailIcon color="error" fontSize="small" />;
  if (outcome === 'skipped') return <SkipIcon color="warning" fontSize="small" />;
  return null;
};

const RunRow: React.FC<{ run: RunSummary }> = ({ run }) => {
  const [expanded, setExpanded] = useState(false);
  const cancelMutation = useCancelRun();

  const handleCancel = async () => {
    try {
      await cancelMutation.mutateAsync(run.run_id);
    } catch (err) {
      console.error('Failed to cancel run:', err);
    }
  };

  const formatDuration = (seconds: number | null) => {
    if (seconds === null) return '-';
    return `${seconds.toFixed(2)}s`;
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  // Sanitize nodeid for artifact path
  const sanitizeNodeid = (nodeid: string): string => {
    return nodeid
      .replace(/\//g, '_')
      .replace(/::/g, '__')
      .replace(/\./g, '_')
      .replace(/[<>:"|?*\[\]]/g, '_')
      .replace(/_+/g, '_');
  };

  return (
    <>
      <TableRow>
        <TableCell>
          <IconButton size="small" onClick={() => setExpanded(!expanded)}>
            {expanded ? <CollapseIcon /> : <ExpandIcon />}
          </IconButton>
        </TableCell>
        <TableCell>
          <Typography variant="body2" fontFamily="monospace">
            {run.run_id}
          </Typography>
        </TableCell>
        <TableCell>
          <StatusChip status={run.status} />
        </TableCell>
        <TableCell>{formatTime(run.start_time)}</TableCell>
        <TableCell>{formatDuration(run.duration_seconds)}</TableCell>
        <TableCell>
          <Box display="flex" gap={1}>
            <Chip label={`✓ ${run.passed}`} color="success" size="small" />
            <Chip label={`✗ ${run.failed}`} color="error" size="small" />
            <Chip label={`⊘ ${run.skipped}`} color="warning" size="small" />
          </Box>
        </TableCell>
        <TableCell>
          <Box display="flex" gap={1}>
            {run.status === 'running' && (
              <IconButton
                size="small"
                color="error"
                onClick={handleCancel}
                disabled={cancelMutation.isPending}
              >
                <StopIcon />
              </IconButton>
            )}
            <IconButton
              size="small"
              component="a"
              href={testApi.getRunSummaryUrl(run.run_id)}
              download
            >
              <DownloadIcon />
            </IconButton>
          </Box>
        </TableCell>
      </TableRow>
      <TableRow>
        <TableCell colSpan={7} sx={{ py: 0 }}>
          <Collapse in={expanded} timeout="auto" unmountOnExit>
            <Box sx={{ m: 2 }}>
              <Typography variant="h6" gutterBottom>
                Test Results
              </Typography>
              {run.tests.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No test results yet
                </Typography>
              ) : (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Status</TableCell>
                      <TableCell>Test</TableCell>
                      <TableCell>Duration</TableCell>
                      <TableCell>Artifacts</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {run.tests.map((test) => (
                      <TableRow key={test.nodeid}>
                        <TableCell>
                          <TestResultIcon outcome={test.outcome} />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontFamily="monospace">
                            {test.nodeid}
                          </Typography>
                        </TableCell>
                        <TableCell>{formatDuration(test.duration_seconds)}</TableCell>
                        <TableCell>
                          <Link
                            href={testApi.getTraceUrl(run.run_id, sanitizeNodeid(test.nodeid))}
                            download
                            sx={{ cursor: 'pointer' }}
                          >
                            Download Trace
                          </Link>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};

export const TestRuns: React.FC = () => {
  const { data: runs, isLoading, error } = useRuns();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load runs: {error instanceof Error ? error.message : 'Unknown error'}
      </Alert>
    );
  }

  if (!runs || runs.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No test runs yet
        </Typography>
        <Typography variant="body2" color="text.secondary" mt={1}>
          Select tests and click "Run Tests" to start your first test run
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h5" mb={2}>
        Test Runs
      </Typography>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell width={50} />
              <TableCell>Run ID</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Started</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Results</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {runs.map((run) => (
              <RunRow key={run.run_id} run={run} />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
};
