import React from 'react';
import { Trophy, Medal, Award, Activity, Users, Crown } from 'lucide-react';
import { LeaderboardEntry } from './types';

interface TeamLeaderboardProps {
  entries: LeaderboardEntry[];
  isLoading?: boolean;
  currentUserTeamId?: string;
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

export function TeamLeaderboard({ entries, isLoading, currentUserTeamId }: TeamLeaderboardProps) {
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
        <Users className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium">No teams yet</h3>
        <p className="mt-1 text-sm">Teams will appear here once they start submitting steps.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {entries.map((entry, index) => {
        const isCurrentUserTeam = entry.team_id === currentUserTeamId;
        
        return (
          <div
            key={entry.team_id || index}
            className={`flex items-center justify-between p-4 rounded-lg border ${
              isCurrentUserTeam
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

              {/* Team Info */}
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-gray-400" />
                  <p className={`text-sm font-medium ${isCurrentUserTeam ? 'text-blue-900' : 'text-gray-900'}`}>
                    {entry.name || entry.team_id}
                  </p>
                  {isCurrentUserTeam && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-200 text-blue-800">
                      Your Team
                    </span>
                  )}
                </div>
                {entry.member_count !== undefined && (
                  <p className="text-xs text-gray-500 mt-1">
                    {entry.member_count} {entry.member_count === 1 ? 'member' : 'members'}
                  </p>
                )}
              </div>
            </div>

            {/* Steps */}
            <div className="flex items-center space-x-2">
              <Activity className="h-4 w-4 text-gray-400" />
              <span className={`text-lg font-semibold ${isCurrentUserTeam ? 'text-blue-900' : 'text-gray-900'}`}>
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

