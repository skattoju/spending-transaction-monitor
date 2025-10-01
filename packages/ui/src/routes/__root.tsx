import { createRootRoute, Outlet, useRouter } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/router-devtools';
import { DashboardHeader } from '../components/dashboard-header/dashboard-header';
import { Footer } from '../components/footer/footer';
import { DevModeBanner } from '../components/dev-mode/DevModeBanner';
import { useAuth } from '../hooks/useAuth';

function RootComponent() {
  const router = useRouter();
  const auth = useAuth();

  // Hide header and banner on login page or when user is not authenticated (and not loading)
  const shouldHideHeader =
    router.state.location.pathname === '/login' ||
    (!auth.isAuthenticated && !auth.isLoading);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Development Mode Banner - hidden on login page */}
      {!shouldHideHeader && <DevModeBanner />}

      {/* Dashboard Header - hidden on login page */}
      {!shouldHideHeader && <DashboardHeader />}

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
