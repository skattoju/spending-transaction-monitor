/**
 * Centralized API client with authentication
 */
class ApiClient {
  // Static method to set token from auth context
  private static currentToken: string | null = null;

  static setToken(token: string | null) {
    ApiClient.currentToken = token;
  }
  private getToken(): string | null {
    // First try static token (set from auth context)
    if (ApiClient.currentToken) {
      return ApiClient.currentToken;
    }

    // Check localStorage for OIDC tokens
    const allKeys = Object.keys(localStorage);
    const oidcKeys = allKeys.filter((k) => k.includes('oidc'));

    // Try multiple possible key patterns
    const possibleKeys = [
      'oidc.user:http://localhost:8080/realms/spending-monitor:spending-monitor',
    ];

    // First try specific keys
    for (const key of possibleKeys) {
      try {
        const stored = localStorage.getItem(key);
        if (stored) {
          const parsed = JSON.parse(stored);
          if (parsed.access_token) {
            return parsed.access_token;
          }
        }
      } catch {
        // Continue looking
      }
    }

    // Fallback: check all OIDC keys
    for (const k of oidcKeys) {
      try {
        const stored = localStorage.getItem(k);
        if (stored) {
          const parsed = JSON.parse(stored);
          if (parsed.access_token) {
            return parsed.access_token;
          }
        }
      } catch {
        // Continue looking
      }
    }

    return null;
  }

  async fetch(
    url: string,
    options: globalThis.RequestInit = {},
  ): Promise<globalThis.Response> {
    const token = this.getToken();

    if (token) {
      options.headers = {
        ...options.headers,
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      };
    } else {
      options.headers = {
        ...options.headers,
        'Content-Type': 'application/json',
      };
    }

    return fetch(url, options);
  }
}

export const apiClient = new ApiClient();
