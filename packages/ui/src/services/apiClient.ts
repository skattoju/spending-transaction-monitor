import { authConfig } from '../config/auth';

/**
 * Centralized API client with authentication
 */
class ApiClient {
  // Static method to set token from auth context
  private static currentToken: string | null = null;
  
  static setToken(token: string | null) {
    ApiClient.currentToken = token;
    console.log('🔧 ApiClient token updated:', token ? 'Present' : 'None');
  }
  private getToken(): string | null {
    // First try static token (set from auth context)
    if (ApiClient.currentToken) {
      console.log('✅ Using token from auth context');
      return ApiClient.currentToken;
    }
    // Debug: Check all localStorage keys
    const allKeys = Object.keys(localStorage);
    const oidcKeys = allKeys.filter(k => k.includes('oidc'));
    console.log('🔍 OIDC keys in localStorage:', oidcKeys);
    
    // Try multiple possible key patterns
    const possibleKeys = [
      'oidc.user:http://localhost:8080/realms/spending-monitor:spending-monitor',
      // Add more possible variations
    ];
    
    // First try specific keys
    for (const key of possibleKeys) {
      try {
        const stored = localStorage.getItem(key);
        if (stored) {
          const parsed = JSON.parse(stored);
          if (parsed.access_token) {
            console.log(`✅ FOUND JWT TOKEN with key: ${key}`);
            return parsed.access_token;
          }
        }
      } catch (error) {
        console.warn(`Failed to parse OIDC token for key ${key}:`, error);
      }
    }
    
    // Fallback: check all OIDC keys
    for (const k of oidcKeys) {
      try {
        const stored = localStorage.getItem(k);
        if (stored) {
          const parsed = JSON.parse(stored);
          if (parsed.access_token) {
            console.log(`✅ FOUND JWT TOKEN in fallback key: ${k}`);
            return parsed.access_token;
          }
        }
      } catch (error) {
        // Continue looking
      }
    }
    
    console.warn('❌ NO JWT TOKEN FOUND ANYWHERE');
    console.log('🔍 Available localStorage keys:', allKeys);
    return null;
  }

  async fetch(url: string, options: globalThis.RequestInit = {}): Promise<globalThis.Response> {
    console.log(`🌐 DEBUG: ApiClient.fetch() called for: ${url}`);
    
    const token = this.getToken();
    
    if (token) {
      console.log(`🔒 DEBUG: Adding Authorization header for: ${url}`);
      console.log(`🔒 DEBUG: Token preview: ${token.substring(0, 50)}...`);
      options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      };
      console.log(`🔒 DEBUG: Final headers:`, options.headers);
    } else {
      console.warn(`⚠️  DEBUG: Making unauthenticated request to: ${url}`);
      console.log('🔄 ProtectedRoute should handle redirect to login');
      options.headers = {
        ...options.headers,
        'Content-Type': 'application/json',
      };
    }
    
    console.log(`🌐 DEBUG: About to call fetch() with:`, { url, headers: options.headers });
    return fetch(url, options);
  }
}

export const apiClient = new ApiClient();
