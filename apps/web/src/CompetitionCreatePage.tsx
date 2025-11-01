import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { CompetitionForm } from './CompetitionForm';
import { CompetitionCreateRequest } from './types';
import { apiClient } from './api';
import toast from 'react-hot-toast';

export function CompetitionCreatePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const createMutation = useMutation({
    mutationFn: (data: CompetitionCreateRequest) => apiClient.createCompetition(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitions'] });
    },
  });

  return (
    <CompetitionForm
      onSubmit={createMutation.mutateAsync}
    />
  );
}
