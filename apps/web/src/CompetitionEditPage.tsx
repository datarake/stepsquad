import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CompetitionForm } from './CompetitionForm';
import { CompetitionDetailSkeleton } from './Skeletons';
import { CompetitionCreateRequest, CompetitionUpdateRequest } from './types';
import { apiClient } from './api';
import toast from 'react-hot-toast';

export function CompetitionEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: competition, isLoading, error } = useQuery({
    queryKey: ['competition', id],
    queryFn: () => apiClient.getCompetition(id!),
    enabled: !!id,
    retry: 1,
  });

  const updateMutation = useMutation({
    mutationFn: (data: CompetitionUpdateRequest) => apiClient.updateCompetition(id!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competition', id] });
      queryClient.invalidateQueries({ queryKey: ['competitions'] });
    },
  });

  if (error) {
    toast.error('Failed to load competition');
    navigate('/');
    return null;
  }

  if (isLoading) {
    return <CompetitionDetailSkeleton />;
  }

  if (!competition) {
    return (
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Competition not found</h3>
        <p className="mt-1 text-sm text-gray-500">The competition you're looking for doesn't exist.</p>
      </div>
    );
  }

  return (
    <CompetitionForm
      competition={competition}
      onSubmit={updateMutation.mutateAsync}
    />
  );
}
