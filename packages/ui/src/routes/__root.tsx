import { createRootRoute, Outlet } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/router-devtools';
import { ModeToggle } from '../components/mode-toggle/mode-toggle';
import { useAuth } from 'react-oidc-context';
import { Button } from '../components/atoms/button/button';
import { Footer } from '../components/footer/footer';

function RootComponent() {
  const auth = useAuth()

  return (
    <>
      <header className="sticky top-0 z-20 border-b bg-background/80 backdrop-blur">
        <div className="container mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <a href="/" className="flex items-center gap-2">
            <span className="font-bold text-lg">💳 spending-monitor</span>
          </a>
          <div className="flex items-center gap-4">
            {auth.isAuthenticated ? (
              <>
                <span className="text-sm text-gray-600">
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
              <Button 
                onClick={() => auth.signinRedirect()}
                size="sm"
              >
                Login
              </Button>
            )}
            <a href="/auth-demo" className="text-sm text-blue-600 hover:text-blue-800">
              Auth Demo
            </a>
            <ModeToggle />
          </div>
        </div>
      </header>
      <main>
        <Outlet />
      </main>
      <Footer />
      <TanStackRouterDevtools />
    </>
  )
}

export const Route = createRootRoute({
  component: RootComponent,
});
