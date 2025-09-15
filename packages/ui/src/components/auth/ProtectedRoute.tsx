/**
 * Protected Route Component
 * Handles authentication checks and redirects for protected pages
 */

import React, { useEffect } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useAuth } from '../../hooks/useAuth';
import { Card } from '../atoms/card/card';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

export function ProtectedRoute({
  children,
  requireAdmin = false,
}: ProtectedRouteProps) {
  const auth = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!auth.isLoading) {
      // Not authenticated - redirect to login
      if (!auth.isAuthenticated || !auth.user) {
        // Store current path for post-login redirect
        const currentPath = window.location.pathname + window.location.search;
        navigate({
          to: '/login',
          search: { redirect: currentPath, error: '' },
        });
        return;
      }

      // Authenticated but insufficient permissions
      if (requireAdmin && !auth.user.roles.includes('admin')) {
        navigate({ to: '/' });
        return;
      }
    }
  }, [auth.isAuthenticated, auth.isLoading, auth.user, navigate, requireAdmin]);

  // Show loading state while checking auth
  if (auth.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/30">
        <Card className="max-w-md w-full p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Checking authentication...</p>
        </Card>
      </div>
    );
  }

  // Show error state if auth failed
  if (auth.error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/30">
        <Card className="max-w-md w-full p-8 text-center space-y-4">
          <h2 className="text-xl font-semibold text-destructive">
            Authentication Error
          </h2>
          <p className="text-muted-foreground">
            {auth.error.message || 'Unable to verify authentication status'}
          </p>
        </Card>
      </div>
    );
  }

  // Don't render until auth is confirmed
  if (!auth.isAuthenticated || !auth.user) {
    return null;
  }

  // Check admin requirement
  if (requireAdmin && !auth.user.roles.includes('admin')) {
    return null;
  }

  // All checks passed - render protected content
  return <>{children}</>;
}
