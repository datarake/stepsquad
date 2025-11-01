import React, { useState } from 'react';
import { Search, Filter, X } from 'lucide-react';
import { Status } from './types';

interface CompetitionFiltersProps {
  filters: {
    status?: Status;
    tz?: string;
    search?: string;
  };
  onFilterChange: (filters: CompetitionFiltersProps['filters']) => void;
}

const timezones = [
  'Europe/Bucharest',
  'UTC',
  'America/New_York',
  'America/Los_Angeles',
  'Europe/London',
  'Asia/Tokyo',
];

const statusOptions: Status[] = ['DRAFT', 'REGISTRATION', 'ACTIVE', 'ENDED', 'ARCHIVED'];

export function CompetitionFilters({ filters, onFilterChange }: CompetitionFiltersProps) {
  const [searchValue, setSearchValue] = useState(filters.search || '');

  const handleSearch = (value: string) => {
    setSearchValue(value);
    onFilterChange({ ...filters, search: value || undefined });
  };

  const handleStatusChange = (status: Status | '') => {
    onFilterChange({ ...filters, status: status || undefined });
  };

  const handleTimezoneChange = (tz: string | '') => {
    onFilterChange({ ...filters, tz: tz || undefined });
  };

  const clearFilters = () => {
    setSearchValue('');
    onFilterChange({});
  };

  const hasActiveFilters = filters.status || filters.tz || filters.search;

  return (
    <div className="bg-white shadow rounded-lg p-4 mb-6">
      <div className="flex flex-wrap gap-4 items-end">
        {/* Search */}
        <div className="flex-1 min-w-[200px]">
          <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
            Search
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-gray-400" />
            </div>
            <input
              id="search"
              type="text"
              value={searchValue}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search by name or ID... (Ctrl+K)"
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>
        </div>

        {/* Status Filter */}
        <div className="min-w-[150px]">
          <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            id="status"
            value={filters.status || ''}
            onChange={(e) => handleStatusChange(e.target.value as Status | '')}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="">All Statuses</option>
            {statusOptions.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        {/* Timezone Filter */}
        <div className="min-w-[180px]">
          <label htmlFor="tz" className="block text-sm font-medium text-gray-700 mb-1">
            Timezone
          </label>
          <select
            id="tz"
            value={filters.tz || ''}
            onChange={(e) => handleTimezoneChange(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="">All Timezones</option>
            {timezones.map((tz) => (
              <option key={tz} value={tz}>
                {tz}
              </option>
            ))}
          </select>
        </div>

        {/* Clear Filters */}
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <X className="h-4 w-4 mr-1" />
            Clear
          </button>
        )}
      </div>

      {/* Active Filters Display */}
      {hasActiveFilters && (
        <div className="mt-3 flex flex-wrap gap-2">
          <span className="text-xs text-gray-500">Active filters:</span>
          {filters.status && (
            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
              Status: {filters.status}
            </span>
          )}
          {filters.tz && (
            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-green-100 text-green-800">
              TZ: {filters.tz}
            </span>
          )}
          {filters.search && (
            <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-purple-100 text-purple-800">
              Search: {filters.search}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
