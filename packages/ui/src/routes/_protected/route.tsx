import { createFileRoute, Outlet } from '@tanstack/react-router';
import { ProtectedRoute } from '../../components/auth/ProtectedRoute';

export const Route = createFileRoute('/_protected')({
  component: ProtectedPages,
});

function ProtectedPages() {
  return (
    <ProtectedRoute>
      <Outlet />
    </ProtectedRoute>
  );
}
