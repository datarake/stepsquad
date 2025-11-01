import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Save, X } from 'lucide-react';
import { Competition, CompetitionCreateRequest, CompetitionUpdateRequest, Status } from './types';
import { FieldError } from './ErrorDisplay';
import { useAutoSave } from './hooks/useAutoSave';
import toast from 'react-hot-toast';

interface CompetitionFormProps {
  competition?: Competition;
  onSubmit: (data: CompetitionCreateRequest | CompetitionUpdateRequest) => Promise<void>;
}

const statusOptions: Status[] = ['DRAFT', 'REGISTRATION', 'ACTIVE', 'ENDED'];

export function CompetitionForm({ competition, onSubmit }: CompetitionFormProps) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    comp_id: '',
    name: '',
    tz: 'Europe/Bucharest',
    registration_open_date: '',
    start_date: '',
    end_date: '',
    max_teams: 10,
    max_members_per_team: 10,
    status: 'DRAFT' as Status,
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (competition) {
      setFormData({
        comp_id: competition.comp_id,
        name: competition.name,
        tz: competition.tz,
        registration_open_date: competition.registration_open_date,
        start_date: competition.start_date,
        end_date: competition.end_date,
        max_teams: competition.max_teams,
        max_members_per_team: competition.max_members_per_team,
        status: competition.status,
      });
    } else {
      // Generate a unique comp_id for new competitions
      const uniqueId = Math.random().toString(36).substring(2, 10);
      setFormData(prev => ({ ...prev, comp_id: uniqueId }));
    }
  }, [competition]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Comp ID validation (only for new competitions)
    if (!competition && !formData.comp_id.trim()) {
      newErrors.comp_id = 'Competition ID is required';
    } else if (!competition && (formData.comp_id.length < 3 || formData.comp_id.length > 20)) {
      newErrors.comp_id = 'Competition ID must be between 3 and 20 characters';
    }

    // Name validation
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.length < 3 || formData.name.length > 80) {
      newErrors.name = 'Name must be between 3 and 80 characters';
    }

    // Date validation
    if (!formData.registration_open_date) {
      newErrors.registration_open_date = 'Registration open date is required';
    }
    if (!formData.start_date) {
      newErrors.start_date = 'Start date is required';
    }
    if (!formData.end_date) {
      newErrors.end_date = 'End date is required';
    }

    // Date order validation
    if (formData.registration_open_date && formData.start_date && formData.end_date) {
      const regDate = new Date(formData.registration_open_date);
      const startDate = new Date(formData.start_date);
      const endDate = new Date(formData.end_date);

      if (regDate > startDate) {
        newErrors.registration_open_date = 'Registration open date must be before start date';
      }
      if (startDate > endDate) {
        newErrors.start_date = 'Start date must be before end date';
      }
    }

    // Number validation
    if (formData.max_teams < 1 || formData.max_teams > 500) {
      newErrors.max_teams = 'Max teams must be between 1 and 500';
    }
    if (formData.max_members_per_team < 1 || formData.max_members_per_team > 200) {
      newErrors.max_members_per_team = 'Max members per team must be between 1 and 200';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Please fix the errors below');
      return;
    }

    setLoading(true);
    try {
      await onSubmit(formData);
      toast.success(competition ? 'Competition updated successfully' : 'Competition created successfully');
      navigate('/');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/');
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-6">
            {competition ? 'Edit Competition' : 'Create New Competition'}
          </h3>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Competition ID (only for new competitions) */}
            {!competition && (
              <div>
                <label htmlFor="comp_id" className="block text-sm font-medium text-gray-700">
                  Competition ID *
                </label>
                <input
                  type="text"
                  id="comp_id"
                  value={formData.comp_id}
                  onChange={(e) => setFormData({ ...formData, comp_id: e.target.value })}
                  className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    errors.comp_id ? 'border-red-300' : ''
                  }`}
                  placeholder="Enter unique competition ID"
                />
                {errors.comp_id && <FieldError error={errors.comp_id} />}
                <p className="mt-1 text-xs text-gray-500">This will be used in URLs and must be unique</p>
              </div>
            )}

            {/* Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Competition Name *
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                  errors.name ? 'border-red-300' : ''
                }`}
                placeholder="Enter competition name"
              />
              {errors.name && <FieldError error={errors.name} />}
            </div>

            {/* Timezone */}
            <div>
              <label htmlFor="tz" className="block text-sm font-medium text-gray-700">
                Timezone
              </label>
              <select
                id="tz"
                value={formData.tz}
                onChange={(e) => setFormData({ ...formData, tz: e.target.value })}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              >
                <option value="Europe/Bucharest">Europe/Bucharest</option>
                <option value="UTC">UTC</option>
                <option value="America/New_York">America/New_York</option>
                <option value="America/Los_Angeles">America/Los_Angeles</option>
              </select>
            </div>

            {/* Dates */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
              <div>
                <label htmlFor="registration_open_date" className="block text-sm font-medium text-gray-700">
                  Registration Open Date *
                </label>
                <input
                  type="date"
                  id="registration_open_date"
                  value={formData.registration_open_date}
                  onChange={(e) => setFormData({ ...formData, registration_open_date: e.target.value })}
                  className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    errors.registration_open_date ? 'border-red-300' : ''
                  }`}
                />
                {errors.registration_open_date && <FieldError error={errors.registration_open_date} />}
              </div>

              <div>
                <label htmlFor="start_date" className="block text-sm font-medium text-gray-700">
                  Start Date *
                </label>
                <input
                  type="date"
                  id="start_date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    errors.start_date ? 'border-red-300' : ''
                  }`}
                />
                {errors.start_date && <FieldError error={errors.start_date} />}
              </div>

              <div>
                <label htmlFor="end_date" className="block text-sm font-medium text-gray-700">
                  End Date *
                </label>
                <input
                  type="date"
                  id="end_date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    errors.end_date ? 'border-red-300' : ''
                  }`}
                />
                {errors.end_date && <FieldError error={errors.end_date} />}
              </div>
            </div>

            {/* Limits */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="max_teams" className="block text-sm font-medium text-gray-700">
                  Max Teams *
                </label>
                <input
                  type="number"
                  id="max_teams"
                  min="1"
                  max="500"
                  value={formData.max_teams}
                  onChange={(e) => setFormData({ ...formData, max_teams: parseInt(e.target.value) || 0 })}
                  className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    errors.max_teams ? 'border-red-300' : ''
                  }`}
                />
                {errors.max_teams && <FieldError error={errors.max_teams} />}
              </div>

              <div>
                <label htmlFor="max_members_per_team" className="block text-sm font-medium text-gray-700">
                  Max Members per Team *
                </label>
                <input
                  type="number"
                  id="max_members_per_team"
                  min="1"
                  max="200"
                  value={formData.max_members_per_team}
                  onChange={(e) => setFormData({ ...formData, max_members_per_team: parseInt(e.target.value) || 0 })}
                  className={`mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
                    errors.max_members_per_team ? 'border-red-300' : ''
                  }`}
                />
                {errors.max_members_per_team && <FieldError error={errors.max_members_per_team} />}
              </div>
            </div>

            {/* Status (only for editing) */}
            {competition && (
              <div>
                <label htmlFor="status" className="block text-sm font-medium text-gray-700">
                  Status
                </label>
                <select
                  id="status"
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value as Status })}
                  className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                >
                  {statusOptions.map((status) => (
                    <option key={status} value={status}>
                      {status}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={handleCancel}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <X className="h-4 w-4 mr-2" />
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Save className="h-4 w-4 mr-2" />
                {loading ? 'Saving...' : (competition ? 'Update' : 'Create')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
