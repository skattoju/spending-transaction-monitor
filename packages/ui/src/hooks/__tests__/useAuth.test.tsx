/**
 * @vitest-environment jsdom
 */
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useAuth } from '../useAuth';
import { AuthProvider } from '../../contexts/AuthContext';

// Mock the auth config for testing
vi.mock('../../config/auth', () => ({
  authConfig: {
    bypassAuth: true,
    environment: 'development',
    keycloak: {
      authority: 'http://localhost:8080/realms/spending-monitor',
      clientId: 'spending-monitor',
      redirectUri: 'http://localhost:3000',
      postLogoutRedirectUri: 'http://localhost:3000',
    },
  },
}));

// Mock react-oidc-context
vi.mock('react-oidc-context', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
  }),
}));

describe('useAuth', () => {
  it('should return dev user in development mode', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user?.name).toBe('John Doe');
    expect(result.current.user?.email).toBe('john.doe@example.com');
    expect(result.current.user?.isDevMode).toBe(true);
    expect(result.current.user?.roles).toEqual(['user', 'admin']);
    expect(result.current.isLoading).toBe(false);
  });

  it('should provide login and logout functions', () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <AuthProvider>{children}</AuthProvider>
    );

    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(typeof result.current.login).toBe('function');
    expect(typeof result.current.logout).toBe('function');
    expect(typeof result.current.signinRedirect).toBe('function');
    expect(result.current.error).toBe(null);
  });
});
