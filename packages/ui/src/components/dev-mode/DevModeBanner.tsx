/**
 * Minimal Development Mode Indicator
 * Single clean banner at the top of the page
 */
import React from 'react';
import { useAuth } from '../../hooks/useAuth';

export function DevModeBanner() {
  const auth = useAuth();

  if (!auth.user?.isDevMode) {
    return null;
  }

  return (
    <div className="bg-yellow-100 border-b border-yellow-300 text-yellow-800 text-center py-1 text-sm">
      🔓 Development Mode - Auth Bypassed
    </div>
  );
}
