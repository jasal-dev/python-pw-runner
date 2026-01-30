# Frontend UI Guide

The Python Playwright Test Runner now includes a modern React-based frontend!

## Features

### Test Selection Panel
- Browse all available tests grouped by file
- Search tests by name or function
- Select individual tests or entire files with checkboxes
- "Select All" and "Clear Selection" bulk actions
- Real-time test count display
- One-click refresh to reload tests

### Test Runs Panel  
- View all test runs with real-time status updates
- Expandable rows to see detailed test results
- Live progress indicators (passed/failed/skipped counts)
- Download traces and run summaries
- Cancel running tests
- Auto-refreshing every 2-5 seconds

### UI Components
- **Material-UI Design** - Clean, professional interface
- **Responsive Layout** - Works on desktop and mobile
- **Real-time Updates** - Auto-polling for live progress
- **Error Handling** - Clear error messages
- **Loading States** - Spinners during data fetching

## Quick Start

```bash
# 1. Start the backend
pw-runner

# 2. In a new terminal, start the frontend
cd frontend
npm install
npm run dev

# 3. Open http://localhost:3000 in your browser
```

## How It Works

The frontend is a single-page React application that communicates with the backend API:

1. **Test Discovery** - `GET /api/tests` fetches available tests
2. **Start Run** - `POST /api/runs` with selected test nodeids
3. **Monitor Progress** - `GET /api/runs/{id}` polls for updates (every 2s)
4. **View Results** - Expand runs to see per-test outcomes
5. **Download Artifacts** - Click links to download trace files

## Technology Stack

- **React 18** + TypeScript
- **Vite** - Fast development server and build tool
- **Material-UI** - Component library for UI
- **TanStack Query** - Smart data fetching with caching
- **Axios** - HTTP client for API calls

## Development

### Project Structure
```
frontend/
├── src/
│   ├── api/client.ts           # API service layer
│   ├── components/
│   │   ├── TestSelection.tsx  # Test browser
│   │   └── TestRuns.tsx       # Results viewer
│   ├── hooks/useApi.ts        # React Query hooks
│   ├── types/api.ts           # TypeScript types
│   └── App.tsx                # Main app
└── vite.config.ts             # Vite config
```

### Building for Production

```bash
cd frontend
npm run build
# Output in frontend/dist/
```

### Configuration

The Vite dev server proxies API requests:
- `/api/*` → `http://localhost:8000`
- `/artifacts/*` → `http://localhost:8000`

For production, configure your web server to proxy these paths to the backend.

## Troubleshooting

**"No tests found"**
- Make sure you have test files in your project
- Check backend is discovering tests: `curl http://localhost:8000/api/tests`

**Connection errors**
- Ensure backend is running on port 8000
- Check CORS settings in backend allow localhost:3000

**Build errors**
- Delete `node_modules` and run `npm install` again
- Clear Vite cache: `rm -rf node_modules/.vite`

## Screenshots

See the PR description for screenshots of the UI in action!
