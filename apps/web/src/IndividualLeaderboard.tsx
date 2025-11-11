import React from 'react';
import { Trophy, Medal, Award, Activity, User } from 'lucide-react';
import { LeaderboardEntry } from './types';

interface IndividualLeaderboardProps {
  entries: LeaderboardEntry[];
  isLoading?: boolean;
  currentUserId?: string;
}

const getRankIcon = (rank: number) => {
  if (rank === 1) return <Trophy className="h-5 w-5 text-yellow-500" />;
  if (rank === 2) return <Medal className="h-5 w-5 text-gray-400" />;
  if (rank === 3) return <Award className="h-5 w-5 text-amber-600" />;
  return <span className="text-sm font-semibold text-gray-500 w-5">{rank}</span>;
};

const getRankBadgeColor = (rank: number) => {
  if (rank === 1) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
  if (rank === 2) return 'bg-gray-100 text-gray-800 border-gray-300';
  if (rank === 3) return 'bg-amber-100 text-amber-800 border-amber-300';
  return 'bg-blue-50 text-blue-800 border-blue-200';
};

export function IndividualLeaderboard({ entries, isLoading, currentUserId }: IndividualLeaderboardProps) {
  if (isLoading) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-2 text-sm text-gray-500">Loading leaderboard...</p>
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <User className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium">No entries yet</h3>
        <p className="mt-1 text-sm">Start submitting steps to see rankings.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {entries.map((entry, index) => {
        const isCurrentUser = entry.user_id === currentUserId;
        
        return (
          <div
            key={entry.user_id || index}
            className={`flex items-center justify-between p-4 rounded-lg border ${
              isCurrentUser
                ? 'bg-blue-50 border-blue-300 shadow-sm'
                : 'bg-white border-gray-200'
            } ${
              entry.rank <= 3 ? 'border-2' : ''
            }`}
          >
            <div className="flex items-center space-x-4 flex-1">
              {/* Rank */}
              <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${getRankBadgeColor(entry.rank)}`}>
                {getRankIcon(entry.rank)}
              </div>

              {/* User Info */}
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <p className={`text-sm font-medium ${isCurrentUser ? 'text-blue-900' : 'text-gray-900'}`}>
                    {entry.email || entry.user_id}
                  </p>
                  {isCurrentUser && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-200 text-blue-800">
                      You
                    </span>
                  )}
                </div>
                {entry.team_name && (
                  <p className="text-xs text-gray-500 mt-1">
                    {entry.team_name}
                  </p>
                )}
              </div>
            </div>

            {/* Steps */}
            <div className="flex items-center space-x-2">
              <Activity className="h-4 w-4 text-gray-400" />
              <span className={`text-lg font-semibold ${isCurrentUser ? 'text-blue-900' : 'text-gray-900'}`}>
                {entry.steps.toLocaleString()}
              </span>
              <span className="text-sm text-gray-500">steps</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

