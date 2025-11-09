import React, { useState } from 'react';
import { X, Activity, RefreshCw } from 'lucide-react';
import { VirtualDeviceSyncRequest } from './types';

interface VirtualStepGeneratorProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (data: VirtualDeviceSyncRequest) => Promise<void>;
  isGenerating: boolean;
}

export function VirtualStepGenerator({
  isOpen,
  onClose,
  onGenerate,
  isGenerating,
}: VirtualStepGeneratorProps) {
  const [steps, setSteps] = useState<number>(10000);
  const [date, setDate] = useState<string>(() => {
    // Default to today in YYYY-MM-DD format
    return new Date().toISOString().split('T')[0];
  });
  const [useRandom, setUseRandom] = useState<boolean>(true);

  const generateRandomSteps = () => {
    // Generate random steps between 5,000 and 15,000
    return Math.floor(Math.random() * 10000) + 5000;
  };

  const handleRandomize = () => {
    setSteps(generateRandomSteps());
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const stepsToUse = useRandom ? generateRandomSteps() : steps;
    
    await onGenerate({
      steps: stepsToUse,
      date: date || undefined,
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-75 transition-opacity">
      <div
        className="relative bg-white rounded-lg shadow-xl transform transition-all sm:max-w-lg sm:w-full mx-4"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 bg-purple-100 rounded-lg">
                <Activity className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900" id="modal-title">
                Generate Steps
              </h3>
            </div>
            <button
              onClick={onClose}
              className="rounded-md p-1 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              aria-label="Close"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Random vs Manual Toggle */}
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="stepMode"
                  checked={useRandom}
                  onChange={() => setUseRandom(true)}
                  className="w-4 h-4 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm font-medium text-gray-700">Random (5,000 - 15,000)</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="stepMode"
                  checked={!useRandom}
                  onChange={() => setUseRandom(false)}
                  className="w-4 h-4 text-purple-600 focus:ring-purple-500"
                />
                <span className="text-sm font-medium text-gray-700">Manual</span>
              </label>
            </div>

            {/* Steps Input */}
            {!useRandom && (
              <div>
                <label htmlFor="steps" className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Steps
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    id="steps"
                    min="0"
                    max="100000"
                    value={steps}
                    onChange={(e) => setSteps(parseInt(e.target.value) || 0)}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
                    required
                  />
                  <button
                    type="button"
                    onClick={handleRandomize}
                    className="px-3 py-2 text-sm font-medium text-purple-600 hover:text-purple-700 border border-purple-300 rounded-md hover:bg-purple-50"
                  >
                    <RefreshCw className="h-4 w-4" />
                  </button>
                </div>
                <p className="mt-1 text-xs text-gray-500">Enter steps between 0 and 100,000</p>
              </div>
            )}

            {/* Date Input */}
            <div>
              <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-2">
                Date (optional)
              </label>
              <input
                type="date"
                id="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
              />
              <p className="mt-1 text-xs text-gray-500">Leave empty to use today's date</p>
            </div>

            {/* Preview */}
            {useRandom && (
              <div className="bg-purple-50 border border-purple-200 rounded-md p-3">
                <p className="text-sm text-purple-800">
                  <span className="font-medium">Random steps will be generated</span> between 5,000 and 15,000 when you click "Generate & Sync".
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200">
              <button
                type="button"
                onClick={onClose}
                disabled={isGenerating}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isGenerating || (!useRandom && (steps < 0 || steps > 100000))}
                className="px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isGenerating ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Activity className="h-4 w-4" />
                    Generate & Sync
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

