import { useEffect, useState, useCallback } from 'react';
import {
  getCurrentLocation,
  watchLocation,
  clearWatch,
  checkLocationPermission,
  type Location,
} from '../services/geolocation';

interface LocationState {
  location: Location | null;
  error: string | null;
  loading: boolean;
  permissionState: 'granted' | 'denied' | 'prompt' | null;
}

/**
 * React hook for accessing the user's location with proper permission handling
 * @param watch - if true, continuously watches location changes
 * @param sendToBackend - if true, sends location to backend when captured
 */
export function useUserLocation(
  watch: boolean = false,
  sendToBackend: boolean = true,
): LocationState & {
  requestLocation: () => Promise<void>;
  clearLocation: () => void;
} {
  const [location, setLocation] = useState<Location | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [permissionState, setPermissionState] = useState<
    'granted' | 'denied' | 'prompt' | null
  >(null);

  // Check permission state on mount
  useEffect(() => {
    checkLocationPermission().then(setPermissionState);
  }, []);

  // Send location to backend
  const sendLocationToBackend = useCallback(
    async (loc: Location) => {
      if (!sendToBackend) return;

      try {
        console.log('📤 Sending location to backend:', loc);

        // Use apiClient to automatically include Authorization header
        const { apiClient } = await import('../services/apiClient');

        // Update user location consent and coordinates
        await apiClient.post(
          '/users/location',
          {
            location_consent_given: true,
            last_app_location_latitude: loc.latitude,
            last_app_location_longitude: loc.longitude,
            last_app_location_accuracy: loc.accuracy,
          },
          {
            headers: {
              'X-User-Latitude': loc.latitude.toString(),
              'X-User-Longitude': loc.longitude.toString(),
              'X-User-Location-Accuracy': loc.accuracy.toString(),
            },
          },
        );

        console.log('✅ Location sent to backend successfully');
      } catch (err) {
        console.error('❌ Error sending location to backend:', err);
      }
    },
    [sendToBackend],
  );

  // Request location once
  const requestLocation = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('🗺️ Requesting user location...');
      const loc = await getCurrentLocation();

      setLocation(loc);
      setError(null);

      // Send to backend
      await sendLocationToBackend(loc);

      console.log('🎉 Location captured successfully:', {
        lat: loc.latitude.toFixed(6),
        lng: loc.longitude.toFixed(6),
        accuracy: `±${Math.round(loc.accuracy)}m`,
      });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Unknown location error';
      setError(errorMessage);
      console.error('❌ Location request failed:', errorMessage);
    } finally {
      setLoading(false);
    }
  }, [sendLocationToBackend]);

  // Clear location
  const clearLocation = useCallback(() => {
    setLocation(null);
    setError(null);
  }, []);

  // Watch location continuously
  useEffect(() => {
    if (!watch) return;

    const id = watchLocation(
      async (loc) => {
        setLocation(loc);
        setError(null);
        setLoading(false);
        await sendLocationToBackend(loc);
      },
      (err) => {
        setError(err.message);
        setLoading(false);
      },
    );

    return () => clearWatch(id);
  }, [watch, sendLocationToBackend]);

  return {
    location,
    error,
    loading,
    permissionState,
    requestLocation,
    clearLocation,
  };
}
