/**
 * Google Analytics 4 (GA4) integration
 * 
 * Usage:
 * 1. Set VITE_GA_MEASUREMENT_ID in your .env file
 * 2. Import and call initGA() in your App component
 * 3. Use trackPageView() on route changes
 * 4. Use trackEvent() for custom events
 */

declare global {
  interface Window {
    gtag: (
      command: 'config' | 'event' | 'js' | 'set',
      targetId: string | Date,
      config?: Record<string, any>
    ) => void;
    dataLayer: any[];
  }
}

const GA_MEASUREMENT_ID = import.meta.env.VITE_GA_MEASUREMENT_ID;

/**
 * Initialize Google Analytics
 */
export function initGA() {
  if (!GA_MEASUREMENT_ID) {
    console.warn('Google Analytics: VITE_GA_MEASUREMENT_ID not set');
    return;
  }

  // Initialize dataLayer
  window.dataLayer = window.dataLayer || [];
  window.gtag = function() {
    window.dataLayer.push(arguments);
  };
  window.gtag('js', new Date());
  window.gtag('config', GA_MEASUREMENT_ID, {
    page_path: window.location.pathname,
  });

  // Load GA script
  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
  document.head.appendChild(script);
}

/**
 * Track page view
 */
export function trackPageView(path: string, title?: string) {
  if (!GA_MEASUREMENT_ID || !window.gtag) return;

  window.gtag('config', GA_MEASUREMENT_ID, {
    page_path: path,
    page_title: title || document.title,
  });
}

/**
 * Track custom event
 */
export function trackEvent(
  eventName: string,
  eventParams?: {
    category?: string;
    label?: string;
    value?: number;
    [key: string]: any;
  }
) {
  if (!GA_MEASUREMENT_ID || !window.gtag) return;

  window.gtag('event', eventName, eventParams);
}

/**
 * Track user login
 */
export function trackLogin(method: string = 'email') {
  trackEvent('login', { method });
}

/**
 * Track user signup
 */
export function trackSignup(method: string = 'email') {
  trackEvent('sign_up', { method });
}

/**
 * Track competition actions
 */
export function trackCompetitionAction(
  action: 'create' | 'join' | 'leave' | 'view',
  competitionId: string
) {
  trackEvent('competition_action', {
    action,
    competition_id: competitionId,
  });
}

/**
 * Track team actions
 */
export function trackTeamAction(
  action: 'create' | 'join' | 'leave',
  teamId: string,
  competitionId: string
) {
  trackEvent('team_action', {
    action,
    team_id: teamId,
    competition_id: competitionId,
  });
}

/**
 * Track device connection
 */
export function trackDeviceConnection(provider: 'garmin' | 'fitbit' | 'virtual') {
  trackEvent('device_connect', { provider });
}

/**
 * Track step submission
 */
export function trackStepSubmission(
  steps: number,
  competitionId?: string,
  provider?: string
) {
  trackEvent('step_submit', {
    steps,
    competition_id: competitionId,
    provider: provider || 'manual',
  });
}

