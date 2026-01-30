import {
  Container,
  Box,
  AppBar,
  Toolbar,
  Typography,
  CssBaseline,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TestSelection } from './components/TestSelection';
import { TestRuns } from './components/TestRuns';

// Create a theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Python Playwright Test Runner
              </Typography>
            </Toolbar>
          </AppBar>
          <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
            <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', md: 'row' } }}>
              <Box sx={{ flex: { xs: 1, md: '0 0 40%' } }}>
                <TestSelection />
              </Box>
              <Box sx={{ flex: { xs: 1, md: '0 0 60%' } }}>
                <TestRuns />
              </Box>
            </Box>
          </Container>
        </Box>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;

