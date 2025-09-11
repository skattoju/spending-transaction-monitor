import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock window.location for tests
Object.defineProperty(window, 'location', {
  value: {
    origin: 'http://localhost:3000',
    href: 'http://localhost:3000',
    pathname: '/',
    search: '',
    hash: '',
  },
  writable: true,
});

// Mock console methods to reduce noise in tests
globalThis.console = {
  ...console,
  // Uncomment the next line if you want to silence console.log during tests
  // log: vi.fn(),
  debug: vi.fn(),
  info: vi.fn(),
  warn: vi.fn(),
  error: vi.fn(),
};
