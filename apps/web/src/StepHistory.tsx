import React from 'react';
import { Activity, Calendar, TrendingUp } from 'lucide-react';
import { StepEntry } from './types';

interface StepHistoryProps {
  steps: StepEntry[];
  isLoading?: boolean;
}

export function StepHistory({ steps, isLoading }: StepHistoryProps) {
  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-2 text-sm text-gray-500">Loading step history...</p>
      </div>
    );
  }

  if (steps.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Activity className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium">No steps submitted yet</h3>
        <p className="mt-1 text-sm">Start submitting steps to see your history here.</p>
      </div>
    );
  }

  // Calculate total and average
  const totalSteps = steps.reduce((sum, entry) => sum + entry.steps, 0);
  const avgSteps = Math.round(totalSteps / steps.length);

  // Find max and min days
  const maxEntry = steps.reduce((max, entry) => entry.steps > max.steps ? entry : max, steps[0]);
  const minEntry = steps.reduce((min, entry) => entry.steps < min.steps ? entry : min, steps[0]);

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-blue-600 mr-2" />
            <div>
              <p className="text-xs text-gray-600">Total Steps</p>
              <p className="text-lg font-semibold text-gray-900">{totalSteps.toLocaleString()}</p>
            </div>
          </div>
        </div>
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center">
            <Activity className="h-5 w-5 text-green-600 mr-2" />
            <div>
              <p className="text-xs text-gray-600">Average/Day</p>
              <p className="text-lg font-semibold text-gray-900">{avgSteps.toLocaleString()}</p>
            </div>
          </div>
        </div>
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center">
            <Calendar className="h-5 w-5 text-purple-600 mr-2" />
            <div>
              <p className="text-xs text-gray-600">Days Active</p>
              <p className="text-lg font-semibold text-gray-900">{steps.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Step History List */}
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Step History</h3>
          <div className="space-y-3">
            {steps.map((entry, index) => {
              const date = new Date(entry.date + 'T00:00:00');
              const isMax = entry.date === maxEntry.date;
              const isMin = entry.date === minEntry.date;

              return (
                <div
                  key={`${entry.date}-${index}`}
                  className={`flex items-center justify-between p-3 rounded-lg border ${
                    isMax
                      ? 'bg-green-50 border-green-200'
                      : isMin && steps.length > 1
                      ? 'bg-red-50 border-red-200'
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-center">
                    <Calendar className="h-4 w-4 text-gray-400 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {date.toLocaleDateString('en-US', {
                          weekday: 'short',
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                        })}
                      </p>
                      {isMax && (
                        <p className="text-xs text-green-600 font-medium">Best Day!</p>
                      )}
                      {isMin && steps.length > 1 && (
                        <p className="text-xs text-red-600 font-medium">Lowest Day</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center">
                    <Activity className="h-4 w-4 text-blue-500 mr-2" />
                    <span className="text-lg font-semibold text-gray-900">
                      {entry.steps.toLocaleString()}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

