import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider, createRouter } from '@tanstack/react-router';
import { routeTree } from './routeTree.gen';
import './styles/globals.css';
import { ThemeProvider } from './components/theme-provider/theme-provider';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TooltipProvider } from './components/atoms/tooltip/tooltip.tsx';
import { AuthProvider } from 'react-oidc-context';

const queryClient = new QueryClient();
const router = createRouter({ routeTree });

// OIDC configuration for Keycloak
const oidcConfig = {
  authority: 'http://localhost:8080/realms/spending-monitor',
  client_id: 'spending-monitor',
  redirect_uri: 'http://localhost:5173',
  response_type: 'code',
  scope: 'openid profile email',
  automaticSilentRenew: true,
  includeIdTokenInSilentRenew: true,
  post_logout_redirect_uri: 'http://localhost:5173',
};

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider {...oidcConfig}>
      <ThemeProvider>
        <TooltipProvider>
          <QueryClientProvider client={queryClient}>
            <RouterProvider router={router} />
          </QueryClientProvider>
        </TooltipProvider>
      </ThemeProvider>
    </AuthProvider>
  </React.StrictMode>,
);
