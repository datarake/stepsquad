import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { CompetitionList } from './CompetitionList';
import { CompetitionFilters } from './CompetitionFilters';
import { CompetitionListSkeleton } from './Skeletons';
import { ErrorDisplay } from './ErrorDisplay';
import { apiClient } from './api';
import toast from 'react-hot-toast';
import { Status } from './types';

export function HomePage() {
  const [filters, setFilters] = useState<{
    status?: Status;
    tz?: string;
    search?: string;
  }>({});
  const [page, setPage] = useState(1);
  const pageSize = 20;

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

  return (
    <div>
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
    </div>
  );
}