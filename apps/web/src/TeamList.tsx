import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Team, User } from './types';
import { Users, Edit2, ChevronDown, ChevronUp } from 'lucide-react';
import { apiClient } from './api';

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
  const [expandedTeams, setExpandedTeams] = useState<Set<string>>(new Set());

  // Collect all unique member UIDs from all teams
  const allMemberUids = useMemo(() => {
    const uids = new Set<string>();
    teams.forEach(team => {
      team.members.forEach(uid => uids.add(uid));
      // Also include owner if not in members
      if (!team.members.includes(team.owner_uid)) {
        uids.add(team.owner_uid);
      }
    });
    return Array.from(uids);
  }, [teams]);

  // Fetch user data for all team members
  const { data: usersData } = useQuery({
    queryKey: ['users', allMemberUids],
    queryFn: async () => {
      // Fetch all users in parallel
      const userPromises = allMemberUids.map(uid => 
        apiClient.getUser(uid).catch(() => null)
      );
      const users = await Promise.all(userPromises);
      // Create a map of uid -> user
      const userMap = new Map<string, User>();
      users.forEach(user => {
        if (user) {
          userMap.set(user.uid, user);
        }
      });
      return userMap;
    },
    enabled: allMemberUids.length > 0,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  const userMap = usersData || new Map<string, User>();

  const toggleTeamExpansion = (teamId: string) => {
    setExpandedTeams(prev => {
      const next = new Set(prev);
      if (next.has(teamId)) {
        next.delete(teamId);
      } else {
        next.add(teamId);
      }
      return next;
    });
  };

  const isUserMember = (team: Team) => {
    return team.members.includes(currentUserUid);
  };

  const isUserOwner = (team: Team) => {
    return team.owner_uid === currentUserUid;
  };

  const getTeamMembersWithEmails = (team: Team) => {
    const members: Array<{ uid: string; email: string; isOwner: boolean }> = [];
    
    // Add owner first
    const owner = userMap.get(team.owner_uid);
    if (owner) {
      members.push({ uid: team.owner_uid, email: owner.email, isOwner: true });
    }
    
    // Add other members
    team.members.forEach(uid => {
      if (uid !== team.owner_uid) {
        const user = userMap.get(uid);
        if (user) {
          members.push({ uid, email: user.email, isOwner: false });
        } else {
          // Fallback if user not found
          members.push({ uid, email: uid.substring(0, 8) + '...', isOwner: false });
        }
      }
    });
    
    return members;
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
                <div className="mt-2 space-y-2">
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <button
                      onClick={() => toggleTeamExpansion(team.team_id)}
                      className="flex items-center gap-1 hover:text-gray-900 transition-colors"
                    >
                      <Users className="h-4 w-4" />
                      <span>
                        {team.members.length} / {competition.max_members_per_team} members
                      </span>
                      {team.members.length > 0 && (
                        expandedTeams.has(team.team_id) ? (
                          <ChevronUp className="h-3 w-3" />
                        ) : (
                          <ChevronDown className="h-3 w-3" />
                        )
                      )}
                    </button>
                    {isFull && (
                      <span className="text-orange-600 font-medium">Full</span>
                    )}
                  </div>
                  {expandedTeams.has(team.team_id) && team.members.length > 0 && (
                    <div className="ml-6 mt-1 space-y-1">
                      {getTeamMembersWithEmails(team).map((member) => (
                        <div key={member.uid} className="flex items-center gap-2 text-xs text-gray-600">
                          <span className="font-medium text-gray-700">{member.email}</span>
                          {member.isOwner && (
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                              Owner
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
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

