import React, { useState } from 'react';
import { X, Save, Calendar, Activity } from 'lucide-react';
import { StepIngestRequest } from './types';
import { FieldError } from './ErrorDisplay';

interface StepEntryFormProps {
  compId: string;
  competition: {
    start_date: string;
    end_date: string;
    status: string;
  };
  onSubmit: (data: StepIngestRequest) => Promise<void>;
  onCancel: () => void;
}

export function StepEntryForm({
  compId,
  competition,
  onSubmit,
  onCancel,
}: StepEntryFormProps) {
  const today = new Date().toISOString().split('T')[0];
  const [formData, setFormData] = useState({
    date: today,
    steps: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors: Record<string, string> = {};

    // Date validation
    if (!formData.date) {
      newErrors.date = 'Date is required';
    } else {
      const stepDate = new Date(formData.date);
      const startDate = new Date(competition.start_date);
      const endDate = new Date(competition.end_date);
      const graceEndDate = new Date(endDate);
      graceEndDate.setDate(graceEndDate.getDate() + 2); // 2 day grace period

      if (stepDate < startDate) {
        newErrors.date = `Date must be on or after competition start date (${competition.start_date})`;
      }
      if (stepDate > graceEndDate) {
        newErrors.date = `Date must be within competition end date + grace period (${graceEndDate.toISOString().split('T')[0]})`;
      }
    }

    // Steps validation
    const stepsNum = parseInt(formData.steps, 10);
    if (!formData.steps || isNaN(stepsNum)) {
      newErrors.steps = 'Step count is required';
    } else if (stepsNum < 0) {
      newErrors.steps = 'Step count cannot be negative';
    } else if (stepsNum > 100000) {
      newErrors.steps = 'Step count cannot exceed 100,000 steps per day';
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
        comp_id: compId,
        date: formData.date,
        steps: parseInt(formData.steps, 10),
        provider: 'manual',
      });
      // Reset form
      setFormData({ date: today, steps: '' });
      setErrors({});
      onCancel();
    } catch (error) {
      console.error('Error submitting steps:', error);
      setErrors({
        general: error instanceof Error ? error.message : 'Failed to submit steps',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const canSubmit = competition.status === 'ACTIVE';

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Activity className="h-5 w-5 mr-2" />
            Submit Steps
          </h3>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-500"
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {!canSubmit && (
          <div className="mb-4 bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded">
            Step submission is only available for ACTIVE competitions. Current status: {competition.status}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {errors.general && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {errors.general}
            </div>
          )}

          <div>
            <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-1">
              <Calendar className="inline h-4 w-4 mr-1" />
              Date *
            </label>
            <input
              type="date"
              id="date"
              className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${
                errors.date ? 'border-red-300' : ''
              }`}
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              min={competition.start_date}
              max={new Date(new Date(competition.end_date).getTime() + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}
              disabled={isSubmitting || !canSubmit}
            />
            {errors.date && <FieldError error={errors.date} />}
            <p className="mt-1 text-xs text-gray-500">
              Competition: {competition.start_date} to {competition.end_date}
            </p>
          </div>

          <div>
            <label htmlFor="steps" className="block text-sm font-medium text-gray-700 mb-1">
              <Activity className="inline h-4 w-4 mr-1" />
              Steps *
            </label>
            <input
              type="number"
              id="steps"
              className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${
                errors.steps ? 'border-red-300' : ''
              }`}
              value={formData.steps}
              onChange={(e) => setFormData({ ...formData, steps: e.target.value })}
              placeholder="Enter step count"
              min="0"
              max="100000"
              step="1"
              disabled={isSubmitting || !canSubmit}
            />
            {errors.steps && <FieldError error={errors.steps} />}
            <p className="mt-1 text-xs text-gray-500">
              Maximum: 100,000 steps per day
            </p>
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
              className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isSubmitting || !canSubmit}
            >
              {isSubmitting ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Submitting...
                </span>
              ) : (
                <span className="flex items-center">
                  <Save className="h-4 w-4 mr-2" />
                  Submit Steps
                </span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

