import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { apiClient } from './api';
import { Device, DeviceSyncResponse, VirtualDeviceSyncRequest } from './types';
import { Activity, Trash2, RefreshCw, Link2, AlertCircle, Zap } from 'lucide-react';
import { useConfirmDialog } from './useConfirmDialog';
import { ConfirmDialog } from './ConfirmDialog';
import { InfoDialog } from './InfoDialog';
import { VirtualStepGenerator } from './VirtualStepGenerator';

export function DeviceSettingsPage() {
  const queryClient = useQueryClient();
  const [syncing, setSyncing] = useState<string | null>(null);
  const { confirm, dialogState } = useConfirmDialog();
  const [showGarminInfo, setShowGarminInfo] = useState(false);
  const [showVirtualGenerator, setShowVirtualGenerator] = useState(false);

  // Fetch devices
  const { data: devicesData, isLoading, error, refetch } = useQuery({
    queryKey: ['devices'],
    queryFn: () => apiClient.getDevices(),
  });

  // Unlink device mutation
  const unlinkMutation = useMutation({
    mutationFn: (provider: "garmin" | "fitbit" | "virtual") => apiClient.unlinkDevice(provider),
    onSuccess: (data, provider) => {
      toast.success(`${provider.charAt(0).toUpperCase() + provider.slice(1)} device unlinked successfully`);
      queryClient.invalidateQueries({ queryKey: ['devices'] });
    },
    onError: (error: Error) => {
      toast.error(`Failed to unlink device: ${error.message}`);
    },
  });

  // Sync device mutation
  const syncMutation = useMutation({
    mutationFn: ({ provider, date }: { provider: "garmin" | "fitbit"; date?: string }) =>
      apiClient.syncDevice(provider, date),
    onSuccess: (data: DeviceSyncResponse, variables) => {
      const { provider, steps, submitted_count, message } = data;
      toast.success(
        `Synced ${steps} steps from ${provider.charAt(0).toUpperCase() + provider.slice(1)}. ${message}`
      );
      queryClient.invalidateQueries({ queryKey: ['devices'] });
      setSyncing(null);
    },
    onError: (error: Error) => {
      toast.error(`Failed to sync device: ${error.message}`);
      setSyncing(null);
    },
  });

  // Connect virtual device mutation
  const connectVirtualMutation = useMutation({
    mutationFn: () => apiClient.connectVirtualDevice(),
    onSuccess: () => {
      toast.success('Virtual step generator connected successfully');
      queryClient.invalidateQueries({ queryKey: ['devices'] });
    },
    onError: (error: Error) => {
      toast.error(`Failed to connect virtual device: ${error.message}`);
    },
  });

  // Sync virtual device mutation
  const syncVirtualMutation = useMutation({
    mutationFn: (data: VirtualDeviceSyncRequest) => apiClient.syncVirtualDevice(data),
    onSuccess: (data: DeviceSyncResponse) => {
      const { steps, submitted_count, message, status } = data;
      if (status === 'warning' || submitted_count === 0) {
        toast.error(message || 'No active competitions found where you are a team member. Make sure you\'re in a team and the competition is ACTIVE.');
      } else {
        toast.success(`Generated and synced ${steps} steps. ${message}`);
        queryClient.invalidateQueries({ queryKey: ['devices'] });
        queryClient.invalidateQueries({ queryKey: ['user-steps'] });
        queryClient.invalidateQueries({ queryKey: ['individual-leaderboard'] });
        queryClient.invalidateQueries({ queryKey: ['team-leaderboard'] });
      }
      setShowVirtualGenerator(false);
    },
    onError: (error: Error) => {
      toast.error(`Failed to sync virtual device: ${error.message}`);
    },
  });

  // Connect device handlers
  const handleConnectGarmin = () => {
    // Show info dialog instead of connecting
    // Garmin Connect integration is pending developer program approval
    setShowGarminInfo(true);
  };

  const handleConnectFitbit = async () => {
    try {
      const { authorization_url } = await apiClient.getFitbitAuthUrl();
      // Store state in localStorage for callback verification
      window.localStorage.setItem('oauth_state', 'fitbit');
      // Redirect to Fitbit OAuth
      window.location.href = authorization_url;
    } catch (error: any) {
      toast.error(`Failed to connect Fitbit: ${error.message}`);
    }
  };

  const handleConnectVirtual = async () => {
    connectVirtualMutation.mutate();
  };

  const handleSync = async (provider: "garmin" | "fitbit" | "virtual") => {
    if (provider === "virtual") {
      setShowVirtualGenerator(true);
    } else {
      setSyncing(provider);
      syncMutation.mutate({ provider });
    }
  };

  const handleGenerateSteps = async (data: VirtualDeviceSyncRequest) => {
    await syncVirtualMutation.mutateAsync(data);
  };

  const handleUnlink = async (provider: "garmin" | "fitbit" | "virtual") => {
    const confirmed = await confirm({
      title: 'Unlink Device',
      message: `Are you sure you want to unlink your ${provider.charAt(0).toUpperCase() + provider.slice(1)} device? You will need to reconnect it to sync steps again.`,
      confirmText: 'Unlink',
      cancelText: 'Cancel',
      variant: 'warning',
    });

    if (!confirmed) {
      return;
    }

    unlinkMutation.mutate(provider);
  };

  const devices = devicesData?.devices || [];
  const linkedProviders = devices.map(d => d.provider);
  const hasGarmin = linkedProviders.includes('garmin');
  const hasFitbit = linkedProviders.includes('fitbit');
  const hasVirtual = linkedProviders.includes('virtual');

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-red-600" />
          <p className="text-red-800">Failed to load devices: {(error as Error).message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Device Settings</h1>
        <p className="text-gray-600">
          Connect your Garmin or Fitbit device to automatically sync step data to competitions.
        </p>
      </div>

      {/* Linked Devices */}
      {devices.length > 0 && (
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Connected Devices</h2>
          <div className="space-y-4">
            {devices.map((device: Device) => (
              <div
                key={device.provider}
                className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <div className={`flex items-center justify-center w-12 h-12 rounded-lg ${
                      device.provider === 'virtual' ? 'bg-purple-100' :
                      device.provider === 'garmin' ? 'bg-orange-100' :
                      'bg-blue-100'
                    }`}>
                      {device.provider === 'virtual' ? (
                        <Zap className="h-6 w-6 text-purple-600" />
                      ) : (
                        <Activity className={`h-6 w-6 ${
                          device.provider === 'garmin' ? 'text-orange-600' : 'text-blue-600'
                        }`} />
                      )}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 capitalize">
                        {device.provider === 'virtual' ? 'Virtual Step Generator' : device.provider}
                      </h3>
                      <div className="text-sm text-gray-600">
                        <p>Linked: {new Date(device.linked_at).toLocaleDateString()}</p>
                        {device.last_sync && (
                          <p>Last sync: {new Date(device.last_sync).toLocaleString()}</p>
                        )}
                        {!device.last_sync && <p className="text-gray-400">Never synced</p>}
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col md:flex-row items-stretch md:items-center gap-2">
                    <button
                      onClick={() => handleSync(device.provider)}
                      disabled={
                        (device.provider !== 'virtual' && (syncing === device.provider || syncMutation.isPending)) ||
                        (device.provider === 'virtual' && syncVirtualMutation.isPending)
                      }
                      className={`px-4 py-2 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 ${
                        device.provider === 'virtual' 
                          ? 'bg-purple-600 hover:bg-purple-700' 
                          : 'bg-blue-600 hover:bg-blue-700'
                      }`}
                    >
                      {(device.provider !== 'virtual' && syncing === device.provider) || 
                       (device.provider === 'virtual' && syncVirtualMutation.isPending) ? (
                        <>
                          <RefreshCw className="h-4 w-4 animate-spin" />
                          {device.provider === 'virtual' ? 'Generating...' : 'Syncing...'}
                        </>
                      ) : (
                        <>
                          {device.provider === 'virtual' ? (
                            <>
                              <Zap className="h-4 w-4" />
                              Generate Steps
                            </>
                          ) : (
                            <>
                              <RefreshCw className="h-4 w-4" />
                              Sync Now
                            </>
                          )}
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => handleUnlink(device.provider)}
                      disabled={unlinkMutation.isPending}
                      className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      <Trash2 className="h-4 w-4" />
                      Unlink
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Connect New Devices */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Connect a Device</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Garmin */}
          <div className={`bg-white border rounded-lg p-6 shadow-sm ${hasFitbit && !hasGarmin ? 'border-amber-300 bg-amber-50' : 'border-gray-200'}`}>
            <div className="flex items-center gap-4 mb-4">
              <div className="flex items-center justify-center w-12 h-12 bg-orange-100 rounded-lg">
                <Activity className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Garmin</h3>
                <p className="text-sm text-gray-600">Connect your Garmin device</p>
              </div>
            </div>
            {hasGarmin ? (
              <div className="text-sm text-green-600 font-medium flex items-center gap-2">
                <Link2 className="h-4 w-4" />
                Connected
              </div>
            ) : (hasFitbit || hasVirtual) ? (
              <div className="space-y-2">
                <button
                  disabled
                  className="w-full px-4 py-2 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <Link2 className="h-4 w-4" />
                  Connect Garmin
                </button>
                <div className="text-xs text-amber-700 bg-amber-100 border border-amber-200 rounded p-2 flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>Only one device can be connected at a time. Please unlink your {hasFitbit ? 'Fitbit' : 'Virtual'} device first to connect Garmin.</span>
                </div>
              </div>
            ) : (
              <button
                onClick={handleConnectGarmin}
                className="w-full px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 flex items-center justify-center gap-2"
              >
                <Link2 className="h-4 w-4" />
                Connect Garmin
              </button>
            )}
          </div>

          {/* Fitbit */}
          <div className={`bg-white border rounded-lg p-6 shadow-sm ${hasGarmin && !hasFitbit ? 'border-amber-300 bg-amber-50' : 'border-gray-200'}`}>
            <div className="flex items-center gap-4 mb-4">
              <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg">
                <Activity className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Fitbit</h3>
                <p className="text-sm text-gray-600">Connect your Fitbit device</p>
              </div>
            </div>
            {hasFitbit ? (
              <div className="text-sm text-green-600 font-medium flex items-center gap-2">
                <Link2 className="h-4 w-4" />
                Connected
              </div>
            ) : (hasGarmin || hasVirtual) ? (
              <div className="space-y-2">
                <button
                  disabled
                  className="w-full px-4 py-2 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <Link2 className="h-4 w-4" />
                  Connect Fitbit
                </button>
                <div className="text-xs text-amber-700 bg-amber-100 border border-amber-200 rounded p-2 flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>Only one device can be connected at a time. Please unlink your {hasGarmin ? 'Garmin' : 'Virtual'} device first to connect Fitbit.</span>
                </div>
              </div>
            ) : (
              <button
                onClick={handleConnectFitbit}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
              >
                <Link2 className="h-4 w-4" />
                Connect Fitbit
              </button>
            )}
          </div>

          {/* Virtual Step Generator */}
          <div className={`bg-white border rounded-lg p-6 shadow-sm ${(hasGarmin || hasFitbit) && !hasVirtual ? 'border-amber-300 bg-amber-50' : 'border-gray-200'}`}>
            <div className="flex items-center gap-4 mb-4">
              <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg">
                <Zap className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Virtual Step Generator</h3>
                <p className="text-sm text-gray-600">Demo device for hackathon</p>
              </div>
            </div>
            {hasVirtual ? (
              <div className="text-sm text-green-600 font-medium flex items-center gap-2">
                <Link2 className="h-4 w-4" />
                Connected
              </div>
            ) : (hasGarmin || hasFitbit) ? (
              <div className="space-y-2">
                <button
                  disabled
                  className="w-full px-4 py-2 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed flex items-center justify-center gap-2"
                >
                  <Link2 className="h-4 w-4" />
                  Connect Virtual
                </button>
                <div className="text-xs text-amber-700 bg-amber-100 border border-amber-200 rounded p-2 flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                  <span>Only one device can be connected at a time. Please unlink your {hasGarmin ? 'Garmin' : 'Fitbit'} device first to connect Virtual Step Generator.</span>
                </div>
              </div>
            ) : (
              <button
                onClick={handleConnectVirtual}
                disabled={connectVirtualMutation.isPending}
                className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Link2 className="h-4 w-4" />
                {connectVirtualMutation.isPending ? 'Connecting...' : 'Connect Virtual'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-semibold mb-1">How it works:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Connect your device to authorize StepSquad to access your step data</li>
              <li>Steps are automatically synced daily via background jobs</li>
              <li>You can manually sync steps at any time using the "Sync Now" button</li>
              <li>Synced steps are automatically submitted to your active competitions</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Confirmation Dialog */}
      {dialogState && (
        <ConfirmDialog
          isOpen={dialogState.isOpen}
          title={dialogState.title}
          message={dialogState.message}
          confirmText={dialogState.confirmText}
          cancelText={dialogState.cancelText}
          variant={dialogState.variant}
          onConfirm={dialogState.onConfirm}
          onCancel={dialogState.onCancel}
        />
      )}

      {/* Garmin Info Dialog */}
      <InfoDialog
        isOpen={showGarminInfo}
        title="Garmin Connect Coming Soon"
        message={`Garmin Connect integration is currently not available as we are awaiting approval from the Garmin Connect Developer Program.

We're working on bringing Garmin device support to StepSquad and will enable this feature as soon as we receive approval.

In the meantime, you can connect your Fitbit device or use the Virtual Step Generator to sync your step data.`}
        onClose={() => setShowGarminInfo(false)}
        closeText="Got it"
      />

      {/* Virtual Step Generator Dialog */}
      <VirtualStepGenerator
        isOpen={showVirtualGenerator}
        onClose={() => setShowVirtualGenerator(false)}
        onGenerate={handleGenerateSteps}
        isGenerating={syncVirtualMutation.isPending}
      />
    </div>
  );
}

