import React from 'react';
import { Team } from './types';
import { Users, Edit2 } from 'lucide-react';

interface TeamListProps {
  teams: Team[];
  competition: {
    max_members_per_team: number;
    status: string;
  };
  currentUserUid: string;
  onJoinTeam: (teamId: string) => void;
  onLeaveTeam: (teamId: string) => void;
  onRenameTeam?: (teamId: string, currentName: string) => void;
}

export function TeamList({ teams, competition, currentUserUid, onJoinTeam, onLeaveTeam, onRenameTeam }: TeamListProps) {
  const canJoinOrLeave = competition.status === 'REGISTRATION' || competition.status === 'ACTIVE';

  const isUserMember = (team: Team) => {
    return team.members.includes(currentUserUid);
  };

  const isUserOwner = (team: Team) => {
    return team.owner_uid === currentUserUid;
  };

  if (teams.length === 0) {
    return (
      <div className="text-center py-12">
        <Users className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">No teams yet</h3>
        <p className="mt-1 text-sm text-gray-500">
          Be the first to create a team for this competition!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {teams.map((team) => {
        const isMember = isUserMember(team);
        const isOwner = isUserOwner(team);
        const isFull = team.members.length >= competition.max_members_per_team;

        return (
          <div
            key={team.team_id}
            className="bg-white rounded-lg border border-gray-200 p-4 hover:border-gray-300 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-semibold text-gray-900">{team.name}</h3>
                  {isOwner && onRenameTeam && (
                    <button
                      onClick={() => onRenameTeam(team.team_id, team.name)}
                      className="text-gray-400 hover:text-blue-600 transition-colors"
                      title="Rename team"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                  )}
                  {isOwner && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                      Owner
                    </span>
                  )}
                  {isMember && !isOwner && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                      Member
                    </span>
                  )}
                </div>
                <div className="mt-2 flex items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    <span>
                      {team.members.length} / {competition.max_members_per_team} members
                    </span>
                  </div>
                  {isFull && (
                    <span className="text-orange-600 font-medium">Full</span>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                {canJoinOrLeave && !isMember && !isFull && (
                  <button
                    onClick={() => onJoinTeam(team.team_id)}
                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Join Team
                  </button>
                )}
                {canJoinOrLeave && isMember && !isOwner && (
                  <button
                    onClick={() => onLeaveTeam(team.team_id)}
                    className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Leave Team
                  </button>
                )}
                {isFull && !isMember && (
                  <span className="text-sm text-gray-500">Team is full</span>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

