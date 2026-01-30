# Python Playwright Test Runner - Frontend

A React-based frontend for the Python Playwright Test Runner.

## Features

- **Test Discovery**: Browse and search available tests
- **Test Selection**: Select individual tests or entire files
- **Run Management**: Start, monitor, and cancel test runs
- **Live Progress**: Real-time updates of test execution status
- **Artifact Access**: Download traces and run summaries
- **Responsive UI**: Built with Material-UI for a modern look

## Technology Stack

- **React 18** with TypeScript
- **Vite** - Fast build tool
- **Material-UI** - Component library
- **TanStack Query** - Data fetching and caching
- **Axios** - HTTP client

## Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`

## Development Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Start Development Server

```bash
npm run dev
```

The frontend will start on `http://localhost:3000` and proxy API requests to the backend at `http://localhost:8000`.

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Usage

1. **Start the backend server**:
   ```bash
   pw-runner
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open your browser** to `http://localhost:3000`

4. **Select tests** from the left panel, click "Run Tests" to execute, and monitor progress in the right panel

## Project Structure

```
frontend/
├── src/
│   ├── api/           # API client and service layer
│   ├── components/    # React components
│   ├── hooks/         # Custom React hooks
│   ├── types/         # TypeScript type definitions
│   ├── App.tsx        # Main application component
│   └── main.tsx       # Application entry point
├── vite.config.ts     # Vite configuration
└── package.json       # Dependencies and scripts
```
