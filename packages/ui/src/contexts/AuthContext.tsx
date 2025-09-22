/**
 * Authentication Context
 * Provides auth functionality with development bypass support
 */
/* eslint-disable react-refresh/only-export-components */

import React, { createContext, useState, useEffect, useCallback, useMemo } from 'react';
import {
  AuthProvider as OIDCProvider,
  useAuth as useOIDCAuth,
} from 'react-oidc-context';
import { authConfig } from '../config/auth';
import type { User, AuthContextType } from '../types/auth';
import { DEV_USER } from '../constants/auth';
import { apiClient } from '../services/apiClient';

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Development Auth Provider - bypasses OIDC
 */
const DevAuthProvider = React.memo(({ children }: { children: React.ReactNode }) => {
  const [user] = useState<User>(DEV_USER);

  const login = useCallback(() => {
    if (import.meta.env.DEV) {
      console.log('🔓 Dev mode: login() called - already authenticated');
    }
  }, []);

  const logout = useCallback(() => {
    if (import.meta.env.DEV) {
      console.log('🔓 Dev mode: logout() called - staying authenticated');
    }
  }, []);

  const signinRedirect = useCallback(() => {
    if (import.meta.env.DEV) {
      console.log('🔓 Dev mode: signinRedirect() called - already authenticated');
    }
  }, []);

  const contextValue: AuthContextType = useMemo(
    () => ({
      user,
      isAuthenticated: true,
      isLoading: false,
      login,
      logout,
      signinRedirect,
      error: null,
    }),
    [user, login, logout, signinRedirect],
  );

  useEffect(() => {
    if (import.meta.env.DEV) {
      console.log('🔓 Development auth provider initialized');
    }
  }, []);

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
});
DevAuthProvider.displayName = 'DevAuthProvider';

/**
 * Production OIDC Auth Provider
 */
const ProductionAuthProvider = React.memo(
  ({ children }: { children: React.ReactNode }) => {
    const oidcConfig = useMemo(
      () => ({
        authority: authConfig.keycloak.authority,
        client_id: authConfig.keycloak.clientId,
        redirect_uri: authConfig.keycloak.redirectUri,
        post_logout_redirect_uri: authConfig.keycloak.postLogoutRedirectUri,
        response_type: 'code',
        scope: 'openid profile email',
        automaticSilentRenew: false, // Disable for debugging
        includeIdTokenInSilentRenew: false, // Disable for debugging
        // Ensure localStorage persistence
        storeUser: true, // Explicitly enable user storage
        userStore: undefined, // Use default WebStorageStateStore (localStorage)
        // Remove problematic config
        loadUserInfo: false,
        monitorSession: false,
      }),
      [],
    );

    useEffect(() => {
      if (import.meta.env.DEV) {
        console.log('🔒 Production OIDC config:', {
          authority: oidcConfig.authority,
          client_id: oidcConfig.client_id,
          redirect_uri: oidcConfig.redirect_uri,
        });
      }
    }, [oidcConfig]);

    return (
      <OIDCProvider {...oidcConfig}>
        <OIDCAuthWrapper>{children}</OIDCAuthWrapper>
      </OIDCProvider>
    );
  },
);
ProductionAuthProvider.displayName = 'ProductionAuthProvider';

/**
 * Wrapper for OIDC provider to adapt to our auth context
 */
const OIDCAuthWrapper = React.memo(({ children }: { children: React.ReactNode }) => {
  const oidcAuth = useOIDCAuth();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Debug OIDC state changes
    console.log('🔒 OIDC State Update:', {
      isLoading: oidcAuth.isLoading,
      hasUser: !!oidcAuth.user,
      hasError: !!oidcAuth.error,
      errorMessage: oidcAuth.error?.message,
      activeNavigator: oidcAuth.activeNavigator,
      isAuthenticated: oidcAuth.isAuthenticated,
    });

    if (oidcAuth.error) {
      console.error('🚫 OIDC Error:', oidcAuth.error);
    }

    if (oidcAuth.user) {
      const newUser: User = {
        id: oidcAuth.user.profile.sub!,
        email: oidcAuth.user.profile.email!,
        username: oidcAuth.user.profile.preferred_username,
        name: oidcAuth.user.profile.name,
        roles: (oidcAuth.user.profile as { realm_access?: { roles?: string[] } })
          .realm_access?.roles || ['user'],
        isDevMode: false,
      };
      setUser(newUser);

      console.log('✅ User authenticated via OIDC:', {
        id: oidcAuth.user.profile.sub,
        email: oidcAuth.user.profile.email,
        accessToken: oidcAuth.user.access_token ? 'Present' : 'Missing',
      });

      // Pass token to ApiClient
      if (oidcAuth.user.access_token) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (apiClient as any).constructor.setToken(oidcAuth.user.access_token);
      }
    } else {
      setUser(null);
      // Clear token from ApiClient
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (apiClient as any).constructor.setToken(null);
    }
  }, [
    oidcAuth.user,
    oidcAuth.isLoading,
    oidcAuth.error,
    oidcAuth.activeNavigator,
    oidcAuth.isAuthenticated,
  ]);

  const login = useCallback(() => oidcAuth.signinRedirect(), [oidcAuth]);
  const logout = useCallback(() => oidcAuth.signoutRedirect(), [oidcAuth]);
  const signinRedirect = useCallback(() => oidcAuth.signinRedirect(), [oidcAuth]);

  const contextValue: AuthContextType = useMemo(() => {
    const authState = {
      user,
      isAuthenticated: !!oidcAuth.user,
      isLoading: oidcAuth.isLoading,
      login,
      logout,
      signinRedirect,
      error: oidcAuth.error ? new Error(oidcAuth.error.message) : null,
    };

    console.log('🔒 AuthContext: OIDC state update', {
      isLoading: oidcAuth.isLoading,
      hasOidcUser: !!oidcAuth.user,
      isAuthenticated: !!oidcAuth.user,
      hasError: !!oidcAuth.error,
      errorMessage: oidcAuth.error?.message,
      userEmail: user?.email,
    });

    return authState;
  }, [
    user,
    oidcAuth.user,
    oidcAuth.isLoading,
    oidcAuth.error,
    login,
    logout,
    signinRedirect,
  ]);

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
});
OIDCAuthWrapper.displayName = 'OIDCAuthWrapper';

/**
 * Main Auth Provider - chooses development or production mode
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  if (authConfig.bypassAuth) {
    return <DevAuthProvider>{children}</DevAuthProvider>;
  }

  return <ProductionAuthProvider>{children}</ProductionAuthProvider>;
}
