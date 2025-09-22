/**
 * Hook that provides authenticated fetch using our auth context
 * @deprecated Use ApiClient instead for centralized authentication
 */
import { useAuth } from './useAuth';

export function useAuthenticatedFetch() {
  const auth = useAuth();

  const authenticatedFetch = async (
    url: string,
    options: globalThis.RequestInit = {},
  ): Promise<globalThis.Response> => {
    console.warn(
      '⚠️ DEPRECATED: useAuthenticatedFetch is deprecated. Use ApiClient instead.',
    );

    if (!auth.isAuthenticated || !auth.user) {
      throw new Error(
        'AUTHENTICATION_REQUIRED: User must be authenticated to make API calls',
      );
    }

    // This hook is deprecated - redirect users to use ApiClient
    console.log('🔄 Please migrate to using ApiClient from services/apiClient.ts');
    return fetch(url, options);
  };

  return authenticatedFetch;
}
