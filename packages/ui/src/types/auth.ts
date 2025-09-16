/**
 * Authentication types
 */

export interface User {
  id: string;
  email: string;
  username?: string;
  name?: string;
  roles: string[];
  isDevMode: boolean;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => void;
  logout: () => void;
  // OIDC compatibility props
  signinRedirect: () => void;
  error: Error | null;
}
