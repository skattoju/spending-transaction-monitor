import { createRootRoute, Outlet } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/router-devtools';
import { DashboardHeader } from '../components/dashboard-header/dashboard-header';
import { Footer } from '../components/footer/footer';
import { DevModeBanner } from '../components/dev-mode/DevModeBanner';

function RootComponent() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Development Mode Banner */}
      <DevModeBanner />

      {/* Use existing header pattern */}
      <DashboardHeader />
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
