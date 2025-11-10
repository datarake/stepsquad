import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { trackPageView } from './analytics';

/**
 * Hook to automatically track page views on route changes
 * 
 * Usage: Add <PageTracking /> to your App component
 */
export function usePageTracking() {
  const location = useLocation();

  useEffect(() => {
    // Track page view on route change
    trackPageView(location.pathname + location.search);
  }, [location]);
}

/**
 * Component to enable automatic page tracking
 * Add this to your App component
 */
export function PageTracking() {
  usePageTracking();
  return null;
}

