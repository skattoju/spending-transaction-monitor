/**
 * Runtime environment configuration
 * These values are injected at container startup via env-config.js
 */
export interface RuntimeEnv {
  BYPASS_AUTH: boolean;
  API_BASE_URL: string;
  ENVIRONMENT: 'development' | 'staging' | 'production';
  KEYCLOAK_URL: string;
  KEYCLOAK_CLIENT_ID: string;
  KEYCLOAK_REALM: string;
  DEV?: boolean; // Debug logging flag
}

declare global {
  interface Window {
    ENV?: RuntimeEnv;
  }
}

export {};
