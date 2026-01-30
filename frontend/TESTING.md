# Frontend Testing Guide

This guide explains the testing strategy and best practices for the Python Playwright Test Runner frontend.

## Testing Stack

### Unit Tests
- **Vitest** - Fast, Vite-native test runner
- **React Testing Library** - Component testing utilities
- **@testing-library/user-event** - User interaction simulation
- **@testing-library/jest-dom** - Custom matchers for DOM assertions

### E2E Tests
- **Playwright** - End-to-end browser testing
- **Auto-start servers** - Automatically starts backend and frontend

## Running Tests

### Unit Tests

```bash
# Run all unit tests once
npm test

# Run tests in watch mode (re-runs on file changes)
npm test -- --watch

# Run tests with UI (interactive browser interface)
npm run test:ui

# Run tests with coverage report
npm run test:coverage

# Run specific test file
npm test src/components/TestSelection.test.tsx
```

### E2E Tests

```bash
# Run all E2E tests (headless mode)
npm run test:e2e

# Run E2E tests with UI (interactive mode)
npm run test:e2e:ui

# Run specific E2E test file
npx playwright test e2e/app.spec.ts

# Run with headed browser
npx playwright test --headed

# Run with debug mode
npx playwright test --debug
```

## Test Structure

### Unit Test Organization

```
src/
├── components/
│   ├── TestSelection.tsx
│   └── TestSelection.test.tsx      # Component test
├── hooks/
│   ├── useApi.ts
│   └── useApi.test.tsx             # Hook test
└── test/
    ├── setup.ts                     # Test configuration
    ├── utils.tsx                    # Test utilities
    └── mockData.ts                  # Mock data
```

### E2E Test Organization

```
e2e/
├── app.spec.ts                      # Main application tests
└── [feature].spec.ts                # Feature-specific tests
```

## Writing Unit Tests

### Component Tests

Use `renderWithProviders` to render components with React Query provider:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../test/utils';
import { MyComponent } from './MyComponent';

describe('MyComponent', () => {
  it('should render and handle user interaction', async () => {
    const user = userEvent.setup();
    
    renderWithProviders(<MyComponent />);
    
    // Assert initial state
    expect(screen.getByText('Click me')).toBeInTheDocument();
    
    // Simulate user interaction
    await user.click(screen.getByRole('button'));
    
    // Assert updated state
    await waitFor(() => {
      expect(screen.getByText('Clicked!')).toBeInTheDocument();
    });
  });
});
```

### Hook Tests

Use `renderHook` from React Testing Library:

```typescript
import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useMyHook } from './useMyHook';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

describe('useMyHook', () => {
  it('should fetch data', async () => {
    const { result } = renderHook(() => useMyHook(), {
      wrapper: createWrapper(),
    });
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toBeDefined();
  });
});
```

### Mocking API Calls

Use Vitest's `vi.mock()`:

```typescript
import { vi } from 'vitest';
import { testApi } from '../api/client';

// Mock the entire module
vi.mock('../api/client', () => ({
  testApi: {
    discoverTests: vi.fn(),
    startRun: vi.fn(),
  },
}));

// In your test
vi.mocked(testApi.discoverTests).mockResolvedValue(mockData);
```

## Writing E2E Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test('should do something', async ({ page }) => {
    // Navigate to page
    await page.goto('/');
    
    // Interact with elements
    await page.getByRole('button', { name: 'Submit' }).click();
    
    // Assert outcomes
    await expect(page.getByText('Success')).toBeVisible();
  });
});
```

### Best Practices for E2E Tests

1. **Use semantic selectors**:
   ```typescript
   // Good
   await page.getByRole('button', { name: 'Submit' });
   await page.getByLabel('Username');
   
   // Avoid
   await page.locator('.submit-btn');
   ```

2. **Wait for conditions**:
   ```typescript
   // Wait for element to be visible
   await expect(page.getByText('Loading')).toBeVisible();
   
   // Wait for element to disappear
   await expect(page.getByText('Loading')).not.toBeVisible();
   ```

3. **Use page object pattern for complex tests**:
   ```typescript
   class TestSelectionPage {
     constructor(private page: Page) {}
     
     async selectTest(testName: string) {
       await this.page.getByRole('button', { name: testName }).click();
     }
   }
   ```

## Test Coverage

### Current Coverage

- **Components**: TestSelection, TestRuns
- **Hooks**: useApi (useTests, useStartRun, useRuns, useCancelRun)
- **Total Unit Tests**: 32
- **Total E2E Tests**: 16

### Coverage Goals

- Minimum 80% line coverage for critical components
- All user-facing features covered by E2E tests
- All API hooks tested

### Viewing Coverage

```bash
npm run test:coverage
```

This generates a coverage report in the `coverage/` directory. Open `coverage/index.html` in a browser to view detailed coverage.

## Debugging Tests

### Unit Tests

1. **Use `screen.debug()`**:
   ```typescript
   import { screen } from '@testing-library/react';
   
   screen.debug(); // Prints entire DOM
   screen.debug(screen.getByRole('button')); // Prints specific element
   ```

2. **Use Vitest UI**:
   ```bash
   npm run test:ui
   ```

3. **Use `console.log()`**:
   ```typescript
   console.log(result.current.data);
   ```

### E2E Tests

1. **Run with headed browser**:
   ```bash
   npx playwright test --headed
   ```

2. **Run with debug mode**:
   ```bash
   npx playwright test --debug
   ```

3. **Use `page.pause()`**:
   ```typescript
   await page.goto('/');
   await page.pause(); // Pauses execution for manual inspection
   ```

4. **Take screenshots**:
   ```typescript
   await page.screenshot({ path: 'screenshot.png' });
   ```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm ci
      - run: cd frontend && npm test

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e .
      - run: playwright install --with-deps chromium
      - run: cd frontend && npm ci
      - run: cd frontend && npm run test:e2e
```

## Common Issues

### Issue: Tests timeout

**Solution**: Increase timeout or ensure API mocks are properly set up
```typescript
test('slow test', async ({ page }) => {
  test.setTimeout(60000); // 60 seconds
  // ...
});
```

### Issue: Tests flaky in CI

**Solution**: Add proper wait conditions
```typescript
// Bad
await page.click('button');
expect(page.getByText('Success')).toBeVisible();

// Good
await page.click('button');
await expect(page.getByText('Success')).toBeVisible();
```

### Issue: Mock not working

**Solution**: Ensure mock is set up before import
```typescript
// Mock must be at top of file
vi.mock('../api/client');

import { MyComponent } from './MyComponent';
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Best Practices](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
