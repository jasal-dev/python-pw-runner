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
- **Vitest** - Unit testing
- **Playwright** - E2E testing

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

## Testing

### Unit Tests

Run unit tests with Vitest:

```bash
# Run tests once
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

**Test Coverage:**
- Component tests (TestSelection, TestRuns)
- Hook tests (useApi)
- 32 total unit tests

### E2E Tests

Run end-to-end tests with Playwright:

```bash
# Run E2E tests (starts backend and frontend automatically)
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui
```

**Note:** E2E tests will automatically start both the backend server and frontend dev server.

### Writing Tests

**Unit Tests:**
- Place unit tests next to the file being tested with `.test.tsx` extension
- Use `renderWithProviders` helper from `src/test/utils.tsx`
- Mock API calls using Vitest's `vi.mock()`

Example:
```typescript
import { describe, it, expect, vi } from 'vitest';
import { renderWithProviders } from '../test/utils';

describe('MyComponent', () => {
  it('should render', () => {
    const { getByText } = renderWithProviders(<MyComponent />);
    expect(getByText('Hello')).toBeInTheDocument();
  });
});
```

**E2E Tests:**
- Place E2E tests in the `e2e/` directory with `.spec.ts` extension
- Use Playwright's testing API
- Tests run against the actual application

Example:
```typescript
import { test, expect } from '@playwright/test';

test('should load application', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('Test Selection')).toBeVisible();
});
```

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
│   ├── components/    # React components with tests
│   ├── hooks/         # Custom React hooks with tests
│   ├── test/          # Test utilities and mock data
│   ├── types/         # TypeScript type definitions
│   ├── App.tsx        # Main application component
│   └── main.tsx       # Application entry point
├── e2e/               # Playwright E2E tests
├── playwright.config.ts  # Playwright configuration
├── vite.config.ts     # Vite configuration
└── package.json       # Dependencies and scripts
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm test` - Run unit tests
- `npm run test:ui` - Run unit tests with UI
- `npm run test:coverage` - Run unit tests with coverage report
- `npm run test:e2e` - Run E2E tests
- `npm run test:e2e:ui` - Run E2E tests with UI

