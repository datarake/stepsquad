import React, { useState } from 'react';
import { X } from 'lucide-react';
import { TeamCreateRequest } from './types';
import { FieldError } from './ErrorDisplay';

interface TeamCreateFormProps {
  compId: string;
  ownerUid: string;
  maxTeams: number;
  currentTeamCount: number;
  onSubmit: (data: TeamCreateRequest) => Promise<void>;
  onCancel: () => void;
}

export function TeamCreateForm({
  compId,
  ownerUid,
  maxTeams,
  currentTeamCount,
  onSubmit,
  onCancel,
}: TeamCreateFormProps) {
  const [formData, setFormData] = useState({
    name: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Team name is required';
    } else if (formData.name.length < 1) {
      newErrors.name = 'Team name must be at least 1 character';
    } else if (formData.name.length > 50) {
      newErrors.name = 'Team name must be at most 50 characters';
    }

    if (currentTeamCount >= maxTeams) {
      newErrors.general = `Maximum number of teams (${maxTeams}) reached for this competition`;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        name: formData.name.trim(),
        comp_id: compId,
        owner_uid: ownerUid,
      });
      // Reset form
      setFormData({ name: '' });
      setErrors({});
      onCancel();
    } catch (error) {
      console.error('Error creating team:', error);
      setErrors({
        general: error instanceof Error ? error.message : 'Failed to create team',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Create Team</h3>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-500"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {errors.general && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {errors.general}
            </div>
          )}

          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              Team Name *
            </label>
            <input
              type="text"
              id="name"
              className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${
                errors.name ? 'border-red-300' : ''
              }`}
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Enter team name"
              maxLength={50}
            />
            {errors.name && <FieldError error={errors.name} />}
          </div>

          <div className="text-sm text-gray-500">
            Teams: {currentTeamCount} / {maxTeams}
          </div>

          <div className="flex items-center justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isSubmitting || currentTeamCount >= maxTeams}
            >
              {isSubmitting ? 'Creating...' : 'Create Team'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

