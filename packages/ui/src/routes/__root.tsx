import { createRootRoute, Outlet } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/router-devtools';
import { DashboardHeader } from '../components/dashboard-header/dashboard-header';
import { Footer } from '../components/footer/footer';

export const Route = createRootRoute({
  component: () => (
    <div className="min-h-screen flex flex-col">
      <DashboardHeader />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
      <TanStackRouterDevtools />
    </div>
  ),
});
