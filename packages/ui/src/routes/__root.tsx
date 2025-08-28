import { createRootRoute, Outlet } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/router-devtools';
import { DashboardHeader } from '../components/dashboard-header/dashboard-header';
import { Footer } from '../components/footer/footer';
import { useAuth } from 'react-oidc-context';
import { Button } from '../components/atoms/button/button';

function RootComponent() {
  const auth = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      {/* Enhanced header with optional auth */}
      <header className="sticky top-0 z-20 border-b bg-background/80 backdrop-blur">
        <div className="container mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center">
            <DashboardHeader />
          </div>
          <div className="flex items-center gap-4">
            {auth.isAuthenticated ? (
              <>
                <span className="text-sm text-muted-foreground">
                  {auth.user?.profile?.preferred_username || auth.user?.profile?.email}
                </span>
                <Button
                  onClick={() => auth.signoutRedirect()}
                  variant="outline"
                  size="sm"
                >
                  Logout
                </Button>
              </>
            ) : (
              <Button onClick={() => auth.signinRedirect()} variant="outline" size="sm">
                Login
              </Button>
            )}
          </div>
        </div>
      </header>
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
      <TanStackRouterDevtools />
    </div>
  );
}

export const Route = createRootRoute({
  component: RootComponent,
});
