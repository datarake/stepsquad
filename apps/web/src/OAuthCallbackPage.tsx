import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { apiClient } from './api';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';

export function OAuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState<string>('');
  const [provider, setProvider] = useState<'garmin' | 'fitbit' | null>(null);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Determine provider from URL path
        const path = window.location.pathname;
        let currentProvider: 'garmin' | 'fitbit' | null = null;
        
        if (path.includes('/oauth/garmin/callback')) {
          currentProvider = 'garmin';
        } else if (path.includes('/oauth/fitbit/callback')) {
          currentProvider = 'fitbit';
        } else {
          // Try to get from localStorage (set by DeviceSettingsPage)
          const storedProvider = localStorage.getItem('oauth_state');
          if (storedProvider === 'garmin' || storedProvider === 'fitbit') {
            currentProvider = storedProvider;
          }
        }

        if (!currentProvider) {
          throw new Error('Unable to determine OAuth provider');
        }

        setProvider(currentProvider);

        // Get OAuth parameters from URL
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const error = searchParams.get('error');
        const oauth_token = searchParams.get('oauth_token'); // For Garmin OAuth 1.0a
        const oauth_verifier = searchParams.get('oauth_verifier'); // For Garmin OAuth 1.0a

        // Check for OAuth errors
        if (error) {
          throw new Error(`OAuth error: ${error}`);
        }

        // Handle callback based on provider
        if (currentProvider === 'garmin') {
          if (!state && !oauth_token) {
            throw new Error('Missing OAuth parameters for Garmin');
          }

          const response = await apiClient.handleGarminCallback(
            code || undefined,
            state || undefined,
            oauth_token || undefined,
            oauth_verifier || undefined
          );

          if (response.status === 'success') {
            setStatus('success');
            setMessage(response.message || 'Garmin device connected successfully');
            toast.success('Garmin device connected successfully');
          } else {
            throw new Error(response.message || 'Failed to connect Garmin device');
          }
        } else if (currentProvider === 'fitbit') {
          if (!code || !state) {
            throw new Error('Missing OAuth parameters for Fitbit');
          }

          const response = await apiClient.handleFitbitCallback(code, state, error || undefined);

          if (response.status === 'success') {
            setStatus('success');
            setMessage(response.message || 'Fitbit device connected successfully');
            toast.success('Fitbit device connected successfully');
          } else {
            throw new Error(response.message || 'Failed to connect Fitbit device');
          }
        }

        // Clear stored OAuth state
        localStorage.removeItem('oauth_state');

        // Redirect to device settings after 2 seconds
        setTimeout(() => {
          navigate('/devices');
        }, 2000);
      } catch (error: any) {
        console.error('OAuth callback error:', error);
        setStatus('error');
        setMessage(error.message || 'Failed to complete OAuth flow');
        toast.error(`Failed to connect device: ${error.message}`);
        
        // Redirect to device settings after 3 seconds on error
        setTimeout(() => {
          navigate('/devices');
        }, 3000);
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          {status === 'loading' && (
            <>
              <Loader2 className="h-12 w-12 text-blue-600 animate-spin mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Connecting your {provider || 'device'}...
              </h2>
              <p className="text-gray-600">Please wait while we complete the connection.</p>
            </>
          )}

          {status === 'success' && (
            <>
              <CheckCircle2 className="h-12 w-12 text-green-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Connection Successful!</h2>
              <p className="text-gray-600 mb-4">{message}</p>
              <p className="text-sm text-gray-500">Redirecting to device settings...</p>
            </>
          )}

          {status === 'error' && (
            <>
              <XCircle className="h-12 w-12 text-red-600 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Connection Failed</h2>
              <p className="text-gray-600 mb-4">{message}</p>
              <p className="text-sm text-gray-500">Redirecting to device settings...</p>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

