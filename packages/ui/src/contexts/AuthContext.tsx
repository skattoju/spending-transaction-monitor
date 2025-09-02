/**
 * Authentication Context
 * Provides auth functionality with development bypass support
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  AuthProvider as OIDCProvider,
  useAuth as useOIDCAuth,
} from 'react-oidc-context';
import { authConfig } from '../config/auth';

export interface User {
  id: string;
  email: string;
  username?: string;
  name?: string;
  roles: string[];
  isDevMode: boolean;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => void;
  logout: () => void;
  // OIDC compatibility props
  signinRedirect: () => void;
  error: Error | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mock development user
const DEV_USER: User = {
  id: 'dev-user-123',
  email: 'developer@example.com',
  username: 'developer',
  name: 'Development User',
  roles: ['user', 'admin'],
  isDevMode: true,
};

/**
 * Development Auth Provider - bypasses OIDC
 */
function DevAuthProvider({ children }: { children: React.ReactNode }) {
  const [user] = useState<User>(DEV_USER);

  const contextValue: AuthContextType = {
    user,
    isAuthenticated: true,
    isLoading: false,
    login: () => console.log('🔓 Dev mode: login() called - already authenticated'),
    logout: () => console.log('🔓 Dev mode: logout() called - staying authenticated'),
    signinRedirect: () =>
      console.log('🔓 Dev mode: signinRedirect() called - already authenticated'),
    error: null,
  };

  useEffect(() => {
    console.log('🔓 Development auth provider initialized');
  }, []);

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
}

/**
 * Production OIDC Auth Provider
 */
function ProductionAuthProvider({ children }: { children: React.ReactNode }) {
  const oidcConfig = {
    authority: authConfig.keycloak.authority,
    client_id: authConfig.keycloak.clientId,
    redirect_uri: authConfig.keycloak.redirectUri,
    post_logout_redirect_uri: authConfig.keycloak.postLogoutRedirectUri,
    response_type: 'code',
    scope: 'openid profile email',
    automaticSilentRenew: true,
    includeIdTokenInSilentRenew: true,
  };

  console.log('🔒 Production OIDC config:', {
    authority: oidcConfig.authority,
    client_id: oidcConfig.client_id,
    redirect_uri: oidcConfig.redirect_uri,
  });

  return (
    <OIDCProvider {...oidcConfig}>
      <OIDCAuthWrapper>{children}</OIDCAuthWrapper>
    </OIDCProvider>
  );
}

/**
 * Wrapper for OIDC provider to adapt to our auth context
 */
function OIDCAuthWrapper({ children }: { children: React.ReactNode }) {
  const oidcAuth = useOIDCAuth();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    if (oidcAuth.user) {
      setUser({
        id: oidcAuth.user.profile.sub!,
        email: oidcAuth.user.profile.email!,
        username: oidcAuth.user.profile.preferred_username,
        name: oidcAuth.user.profile.name,
        roles: (oidcAuth.user.profile as { realm_access?: { roles?: string[] } })
          .realm_access?.roles || ['user'],
        isDevMode: false,
      });
      console.log('🔒 User authenticated via OIDC:', {
        id: oidcAuth.user.profile.sub,
        email: oidcAuth.user.profile.email,
      });
    } else {
      setUser(null);
    }
  }, [oidcAuth.user]);

  const contextValue: AuthContextType = {
    user,
    isAuthenticated: !!oidcAuth.user,
    isLoading: oidcAuth.isLoading,
    login: () => oidcAuth.signinRedirect(),
    logout: () => oidcAuth.signoutRedirect(),
    signinRedirect: () => oidcAuth.signinRedirect(),
    error: oidcAuth.error ? new Error(oidcAuth.error.message) : null,
  };

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
}

/**
 * Main Auth Provider - chooses development or production mode
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  if (authConfig.bypassAuth) {
    return <DevAuthProvider>{children}</DevAuthProvider>;
  }

  return <ProductionAuthProvider>{children}</ProductionAuthProvider>;
}

/**
 * Hook to use auth context
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
