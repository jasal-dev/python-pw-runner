import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Checkbox,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useTests, useStartRun } from '../hooks/useApi';

export const TestSelection: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTests, setSelectedTests] = useState<Set<string>>(new Set());
  const { data: testsData, isLoading, error, refetch } = useTests();
  const startRunMutation = useStartRun();

  // Filter tests based on search term
  const filteredTests = useMemo(() => {
    if (!testsData) return null;
    
    if (!searchTerm) return testsData;

    const filtered = testsData.tests.filter(
      (test) =>
        test.nodeid.toLowerCase().includes(searchTerm.toLowerCase()) ||
        test.function_name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Rebuild grouped_by_file
    const grouped: Record<string, typeof filtered> = {};
    filtered.forEach((test) => {
      if (!grouped[test.file_path]) {
        grouped[test.file_path] = [];
      }
      grouped[test.file_path].push(test);
    });

    return {
      ...testsData,
      tests: filtered,
      total: filtered.length,
      grouped_by_file: grouped,
    };
  }, [testsData, searchTerm]);

  const toggleTest = (nodeid: string) => {
    const newSelected = new Set(selectedTests);
    if (newSelected.has(nodeid)) {
      newSelected.delete(nodeid);
    } else {
      newSelected.add(nodeid);
    }
    setSelectedTests(newSelected);
  };

  const toggleFile = (filePath: string) => {
    if (!filteredTests) return;
    
    const fileTests = filteredTests.grouped_by_file[filePath] || [];
    const allSelected = fileTests.every((test) => selectedTests.has(test.nodeid));
    
    const newSelected = new Set(selectedTests);
    fileTests.forEach((test) => {
      if (allSelected) {
        newSelected.delete(test.nodeid);
      } else {
        newSelected.add(test.nodeid);
      }
    });
    setSelectedTests(newSelected);
  };

  const selectAll = () => {
    if (!filteredTests) return;
    setSelectedTests(new Set(filteredTests.tests.map((t) => t.nodeid)));
  };

  const clearSelection = () => {
    setSelectedTests(new Set());
  };

  const handleRunTests = async () => {
    if (selectedTests.size === 0) return;

    try {
      await startRunMutation.mutateAsync({
        test_nodeids: Array.from(selectedTests),
      });
      // Clear selection after starting run
      clearSelection();
    } catch (err) {
      console.error('Failed to start run:', err);
    }
  };

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
        Failed to load tests: {error instanceof Error ? error.message : 'Unknown error'}
      </Alert>
    );
  }

  if (!filteredTests || filteredTests.total === 0) {
    return (
      <Alert severity="info">
        No tests found. Make sure you have test files in your project.
      </Alert>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Test Selection</Typography>
        <Button
          startIcon={<RefreshIcon />}
          onClick={() => refetch()}
          size="small"
        >
          Refresh
        </Button>
      </Box>

      <TextField
        fullWidth
        size="small"
        placeholder="Search tests..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        sx={{ mb: 2 }}
      />

      <Box display="flex" gap={1} mb={2}>
        <Button size="small" onClick={selectAll}>
          Select All ({filteredTests.total})
        </Button>
        <Button size="small" onClick={clearSelection}>
          Clear Selection
        </Button>
        <Typography variant="body2" sx={{ ml: 'auto', alignSelf: 'center' }}>
          {selectedTests.size} selected
        </Typography>
      </Box>

      <Box sx={{ maxHeight: 500, overflowY: 'auto', mb: 2 }}>
        {Object.entries(filteredTests.grouped_by_file).map(([filePath, tests]) => {
          const allSelected = tests.every((test) => selectedTests.has(test.nodeid));
          const someSelected = tests.some((test) => selectedTests.has(test.nodeid));

          return (
            <Accordion key={filePath} defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Checkbox
                  checked={allSelected}
                  indeterminate={someSelected && !allSelected}
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleFile(filePath);
                  }}
                />
                <Typography>
                  {filePath} ({tests.length})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List dense>
                  {tests.map((test) => (
                    <ListItem key={test.nodeid} disablePadding>
                      <ListItemButton onClick={() => toggleTest(test.nodeid)}>
                        <ListItemIcon>
                          <Checkbox
                            edge="start"
                            checked={selectedTests.has(test.nodeid)}
                            tabIndex={-1}
                            disableRipple
                          />
                        </ListItemIcon>
                        <ListItemText
                          primary={test.function_name}
                          secondary={test.class_name}
                        />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          );
        })}
      </Box>

      <Button
        fullWidth
        variant="contained"
        size="large"
        startIcon={<PlayIcon />}
        onClick={handleRunTests}
        disabled={selectedTests.size === 0 || startRunMutation.isPending}
      >
        {startRunMutation.isPending
          ? 'Starting...'
          : `Run ${selectedTests.size} Test${selectedTests.size !== 1 ? 's' : ''}`}
      </Button>

      {startRunMutation.error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          Failed to start run:{' '}
          {startRunMutation.error instanceof Error
            ? startRunMutation.error.message
            : 'Unknown error'}
        </Alert>
      )}
    </Paper>
  );
};
