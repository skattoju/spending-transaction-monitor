import { createFileRoute, useNavigate, useSearch } from '@tanstack/react-router';
import { useAuth } from '../hooks/useAuth';
import { useEffect } from 'react';
import { Button } from '../components/atoms/button/button';
import { Card } from '../components/atoms/card/card';

export const Route = createFileRoute('/login')({
  validateSearch: (search: Record<string, unknown>) => ({
    redirect: (search.redirect as string) || '/',
    error: search.error as string,
  }),
  component: LoginPage,
});

function LoginPage() {
  const auth = useAuth();
  const navigate = useNavigate();
  const { redirect, error } = useSearch({ from: '/login' });

  useEffect(() => {
    // If already authenticated, redirect to intended destination
    if (auth.isAuthenticated && !auth.isLoading) {
      navigate({ to: redirect });
    }
  }, [auth.isAuthenticated, auth.isLoading, navigate, redirect]);

  const handleLogin = () => {
    auth.signinRedirect();
  };

  if (auth.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/30">
        <Card className="max-w-md w-full p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading authentication...</p>
        </Card>
      </div>
    );
  }

  if (auth.error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/30">
        <Card className="max-w-md w-full p-8 text-center space-y-4">
          <h2 className="text-xl font-semibold text-destructive">
            Authentication Error
          </h2>
          <p className="text-muted-foreground">
            {auth.error.message || 'An error occurred during authentication'}
          </p>
          <Button
            onClick={() => window.location.reload()}
            variant="outline"
            className="w-full"
          >
            Try Again
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30">
      <Card className="max-w-md w-full p-8 space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="h-12 w-12 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-xl">SM</span>
            </div>
          </div>
          <div>
            <h2 className="text-2xl font-bold">Welcome to Spending Monitor</h2>
            <p className="text-muted-foreground mt-2">
              Sign in to access your transaction dashboard and manage alerts
            </p>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md">
            <p className="text-sm text-destructive text-center">
              {error === 'insufficient_permissions'
                ? 'You do not have sufficient permissions to access that page.'
                : 'Authentication required to access this page.'}
            </p>
          </div>
        )}

        {/* Login Section */}
        <div className="space-y-4">
          <Button onClick={handleLogin} className="w-full" size="lg">
            {auth.user?.isDevMode ? 'Continue' : 'Sign In with Keycloak'}
          </Button>

          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              {auth.user?.isDevMode
                ? 'Development mode - authentication bypassed'
                : 'Secure authentication powered by OpenID Connect'}
            </p>
          </div>
        </div>

        {/* Features Preview */}
        <div className="border-t pt-6">
          <h3 className="text-sm font-medium mb-3">What you'll get:</h3>
          <ul className="text-sm text-muted-foreground space-y-2">
            <li className="flex items-center">
              <svg
                className="w-4 h-4 text-green-500 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              Real-time transaction monitoring
            </li>
            <li className="flex items-center">
              <svg
                className="w-4 h-4 text-green-500 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              AI-powered spending alerts
            </li>
            <li className="flex items-center">
              <svg
                className="w-4 h-4 text-green-500 mr-2"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
              Secure role-based access
            </li>
          </ul>
        </div>
      </Card>
    </div>
  );
}
