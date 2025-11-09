import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CompetitionList } from './CompetitionList';
import { CompetitionFilters } from './CompetitionFilters';
import { CompetitionListSkeleton } from './Skeletons';
import { ErrorDisplay } from './ErrorDisplay';
import { apiClient } from './api';
import { useAuth } from './auth';
import { useConfirmDialog } from './useConfirmDialog';
import { ConfirmDialog } from './ConfirmDialog';
import toast from 'react-hot-toast';
import { Status } from './types';
import { RefreshCw, Database } from 'lucide-react';

export function HomePage() {
  const { user } = useAuth();
  const { confirm, dialogState } = useConfirmDialog();
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<{
    status?: Status;
    tz?: string;
    search?: string;
  }>({});
  const [page, setPage] = useState(1);
  const pageSize = 20;
  
  // Check if user is admin@stepsquad.club (hackathon demo admin)
  const isHackathonAdmin = user?.email?.toLowerCase() === 'admin@stepsquad.club';

  const { data, isLoading, error } = useQuery({
    queryKey: ['competitions', filters, page],
    queryFn: () => apiClient.getCompetitions({
      ...filters,
      page,
      page_size: pageSize,
    }),
    retry: 1,
  });

  const [errorDismissed, setErrorDismissed] = React.useState(false);

  const handleFilterChange = (newFilters: typeof filters) => {
    setFilters(newFilters);
    setPage(1); // Reset to first page when filters change
  };

  // Reset and seed demo data mutation
  const resetAndSeedMutation = useMutation({
    mutationFn: () => apiClient.resetAndSeedDemoData(),
    onSuccess: (data) => {
      toast.success(`Demo data reset! Created ${data.teams_created} teams, ${data.steps_created} steps. ${data.note}`);
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['competitions'] });
      queryClient.invalidateQueries({ queryKey: ['teams'] });
      queryClient.invalidateQueries({ queryKey: ['leaderboard'] });
    },
    onError: (error: any) => {
      toast.error(error?.message || 'Failed to reset and seed demo data');
    },
  });

  const handleResetAndSeed = async () => {
    const confirmed = await confirm({
      title: 'Reset & Seed Demo Data',
      message: 'This will reset all teams and steps, then seed the database with demo data for the hackathon. This action cannot be undone. Continue?',
      confirmText: 'Reset & Seed',
      cancelText: 'Cancel',
      variant: 'warning',
    });

    if (confirmed) {
      resetAndSeedMutation.mutate();
    }
  };

  return (
    <div>
      {/* Hackathon Demo Admin Button */}
      {isHackathonAdmin && (
        <div className="mb-6 rounded-lg border-2 border-amber-200 bg-amber-50 p-4">
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <Database className="h-5 w-5 text-amber-600" />
              <div>
                <h3 className="text-sm font-semibold text-amber-900">Hackathon Demo Tools</h3>
                <p className="text-xs text-amber-700">Reset and seed demo data for hackathon organizers</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleResetAndSeed}
                disabled={resetAndSeedMutation.isPending}
                className="inline-flex items-center gap-2 rounded-md bg-amber-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-amber-700 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {resetAndSeedMutation.isPending ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    Resetting...
                  </>
                ) : (
                  <>
                    <RefreshCw className="h-4 w-4" />
                    Reset & Seed Demo Data
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {error && !errorDismissed && (
        <div className="mb-6">
          <ErrorDisplay
            error={error instanceof Error ? error : new Error('Failed to load competitions')}
            onDismiss={() => setErrorDismissed(true)}
          />
        </div>
      )}

      <CompetitionFilters
        filters={filters}
        onFilterChange={handleFilterChange}
      />
      
      {isLoading ? (
        <CompetitionListSkeleton />
      ) : (
        <>
          <CompetitionList 
            competitions={data?.rows || []} 
            pagination={{
              total: data?.total || 0,
              page: data?.page || 1,
              pageSize: data?.page_size || pageSize,
              totalPages: data?.total_pages || 0,
              onPageChange: setPage,
            }}
          />
        </>
      )}

      {/* Confirm Dialog */}
      {dialogState && (
        <ConfirmDialog
          isOpen={dialogState.isOpen}
          title={dialogState.title}
          message={dialogState.message}
          onConfirm={dialogState.onConfirm}
          onCancel={dialogState.onCancel}
          confirmText={dialogState.confirmText}
          cancelText={dialogState.cancelText}
          variant={dialogState.variant}
        />
      )}
    </div>
  );
}