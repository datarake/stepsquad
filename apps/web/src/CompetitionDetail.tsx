import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Calendar, Users, Settings, Archive, ArrowLeft, Plus, Activity, Trophy } from 'lucide-react';
import { Competition, Status, Team, TeamCreateRequest, StepIngestRequest } from './types';
import { useAuth } from './auth';
import { apiClient } from './api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { TeamList } from './TeamList';
import { TeamCreateForm } from './TeamCreateForm';
import { StepEntryForm } from './StepEntryForm';
import { StepHistory } from './StepHistory';
import { IndividualLeaderboard } from './IndividualLeaderboard';
import { TeamLeaderboard } from './TeamLeaderboard';

interface CompetitionDetailProps {
  competition: Competition;
}

const statusColors: Record<Status, string> = {
  DRAFT: 'bg-gray-100 text-gray-800',
  REGISTRATION: 'bg-blue-100 text-blue-800',
  ACTIVE: 'bg-green-100 text-green-800',
  ENDED: 'bg-yellow-100 text-yellow-800',
  ARCHIVED: 'bg-red-100 text-red-800',
};

const statusLabels: Record<Status, string> = {
  DRAFT: 'Draft',
  REGISTRATION: 'Registration Open',
  ACTIVE: 'Active',
  ENDED: 'Ended',
  ARCHIVED: 'Archived',
};

export function CompetitionDetail({ competition }: CompetitionDetailProps) {
  const { isAdmin, user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showStepEntryForm, setShowStepEntryForm] = useState(false);
  const [activeTab, setActiveTab] = useState<'individual' | 'team'>('individual');
  const [leaderboardDate, setLeaderboardDate] = useState<string | undefined>(undefined);

  // Fetch teams for this competition
  const { data: teamsData, isLoading: teamsLoading } = useQuery({
    queryKey: ['competition-teams', competition.comp_id],
    queryFn: () => apiClient.getCompetitionTeams(competition.comp_id),
    enabled: !!competition.comp_id,
    retry: 1,
  });

  const teams = teamsData?.rows || [];

  // Create team mutation
  const createTeamMutation = useMutation({
    mutationFn: (data: TeamCreateRequest) => apiClient.createTeam(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competition-teams', competition.comp_id] });
      toast.success('Team created successfully');
      setShowCreateForm(false);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to create team');
    },
  });

  // Join team mutation
  const joinTeamMutation = useMutation({
    mutationFn: (teamId: string) => apiClient.joinTeam({ team_id: teamId, uid: user!.uid }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competition-teams', competition.comp_id] });
      toast.success('Joined team successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to join team');
    },
  });

  // Leave team mutation
  const leaveTeamMutation = useMutation({
    mutationFn: (teamId: string) => apiClient.leaveTeam(teamId, user!.uid),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competition-teams', competition.comp_id] });
      toast.success('Left team successfully');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to leave team');
    },
  });

  const handleArchive = async () => {
    if (!window.confirm('Are you sure you want to archive this competition? This action cannot be undone.')) {
      return;
    }

    try {
      await apiClient.deleteCompetition(competition.comp_id);
      toast.success('Competition archived successfully');
      navigate('/');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to archive competition');
    }
  };

  const canCreateOrJoinTeams = 
    (competition.status === 'REGISTRATION' || competition.status === 'ACTIVE') &&
    competition.status !== 'ARCHIVED';

  const handleCreateTeam = async (data: TeamCreateRequest) => {
    await createTeamMutation.mutateAsync(data);
  };

  const handleJoinTeam = async (teamId: string) => {
    await joinTeamMutation.mutateAsync(teamId);
  };

  const handleLeaveTeam = async (teamId: string) => {
    if (!window.confirm('Are you sure you want to leave this team?')) {
      return;
    }
    await leaveTeamMutation.mutateAsync(teamId);
  };

  // Check if user is in a team for this competition
  const isUserInTeam = user ? teams.some(team => team.members.includes(user.uid)) : false;

  // Fetch step history for current user
  const { data: stepHistoryData, isLoading: stepsLoading } = useQuery({
    queryKey: ['user-steps', user?.uid, competition.comp_id],
    queryFn: () => apiClient.getUserStepHistory(user!.uid, competition.comp_id),
    enabled: !!user && !!competition.comp_id && isUserInTeam,
    retry: 1,
  });

  const steps = stepHistoryData?.rows || [];

  // Submit steps mutation
  const submitStepsMutation = useMutation({
    mutationFn: (data: StepIngestRequest) => apiClient.submitSteps(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user-steps', user?.uid, competition.comp_id] });
      queryClient.invalidateQueries({ queryKey: ['competition-teams', competition.comp_id] });
      queryClient.invalidateQueries({ queryKey: ['individual-leaderboard', competition.comp_id] });
      queryClient.invalidateQueries({ queryKey: ['team-leaderboard', competition.comp_id] });
      toast.success('Steps submitted successfully');
      setShowStepEntryForm(false);
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to submit steps');
    },
  });

  const handleSubmitSteps = async (data: StepIngestRequest) => {
    await submitStepsMutation.mutateAsync(data);
  };

  // Find user's team ID
  const userTeam = user ? teams.find(team => team.members.includes(user.uid)) : undefined;
  const userTeamId = userTeam?.team_id;

  // Fetch leaderboards
  const { data: individualLeaderboardData, isLoading: individualLoading } = useQuery({
    queryKey: ['individual-leaderboard', competition.comp_id, leaderboardDate],
    queryFn: () => apiClient.getIndividualLeaderboard({
      comp_id: competition.comp_id,
      date: leaderboardDate,
      start_date: leaderboardDate ? undefined : competition.start_date,
      end_date: leaderboardDate ? undefined : competition.end_date,
      page_size: 50,
    }),
    enabled: !!competition.comp_id,
    retry: 1,
  });

  const { data: teamLeaderboardData, isLoading: teamLoading } = useQuery({
    queryKey: ['team-leaderboard', competition.comp_id, leaderboardDate],
    queryFn: () => apiClient.getTeamLeaderboard({
      comp_id: competition.comp_id,
      date: leaderboardDate,
      start_date: leaderboardDate ? undefined : competition.start_date,
      end_date: leaderboardDate ? undefined : competition.end_date,
      page_size: 50,
    }),
    enabled: !!competition.comp_id,
    retry: 1,
  });


  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => navigate('/')}
          className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to competitions
        </button>
      </div>

      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{competition.name}</h1>
              <div className="mt-2 flex items-center space-x-4">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[competition.status]}`}>
                  {statusLabels[competition.status]}
                </span>
                <span className="text-sm text-gray-500">
                  Created {new Date(competition.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
            
            {isAdmin && competition.status !== 'ARCHIVED' && (
              <div className="flex space-x-2">
                <Link
                  to={`/competitions/${competition.comp_id}/edit`}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Edit
                </Link>
                <button
                  onClick={handleArchive}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <Archive className="h-4 w-4 mr-2" />
                  Archive
                </button>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {/* Dates */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-gray-400" />
                <h3 className="ml-2 text-sm font-medium text-gray-900">Important Dates</h3>
              </div>
              <div className="mt-3 space-y-2">
                <div>
                  <dt className="text-xs text-gray-500">Registration Opens</dt>
                  <dd className="text-sm text-gray-900">{competition.registration_open_date}</dd>
                </div>
                <div>
                  <dt className="text-xs text-gray-500">Start Date</dt>
                  <dd className="text-sm text-gray-900">{competition.start_date}</dd>
                </div>
                <div>
                  <dt className="text-xs text-gray-500">End Date</dt>
                  <dd className="text-sm text-gray-900">{competition.end_date}</dd>
                </div>
              </div>
            </div>

            {/* Team Limits */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center">
                <Users className="h-5 w-5 text-gray-400" />
                <h3 className="ml-2 text-sm font-medium text-gray-900">Team Limits</h3>
              </div>
              <div className="mt-3 space-y-2">
                <div>
                  <dt className="text-xs text-gray-500">Maximum Teams</dt>
                  <dd className="text-sm text-gray-900">{competition.max_teams}</dd>
                </div>
                <div>
                  <dt className="text-xs text-gray-500">Max Members per Team</dt>
                  <dd className="text-sm text-gray-900">{competition.max_members_per_team}</dd>
                </div>
                <div>
                  <dt className="text-xs text-gray-500">Total Capacity</dt>
                  <dd className="text-sm text-gray-900">{competition.max_teams * competition.max_members_per_team} participants</dd>
                </div>
              </div>
            </div>

            {/* Competition Info */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-sm font-medium text-gray-900">Competition Info</h3>
              <div className="mt-3 space-y-2">
                <div>
                  <dt className="text-xs text-gray-500">Timezone</dt>
                  <dd className="text-sm text-gray-900">{competition.tz}</dd>
                </div>
                <div>
                  <dt className="text-xs text-gray-500">Created By</dt>
                  <dd className="text-sm text-gray-900">{competition.created_by}</dd>
                </div>
                <div>
                  <dt className="text-xs text-gray-500">Last Updated</dt>
                  <dd className="text-sm text-gray-900">{new Date(competition.updated_at).toLocaleDateString()}</dd>
                </div>
              </div>
            </div>
          </div>

          {/* Competition ID for admins */}
          {isAdmin && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-900">Technical Details</h3>
              <div className="mt-2">
                <dt className="text-xs text-gray-500">Competition ID</dt>
                <dd className="text-sm text-gray-900 font-mono">{competition.comp_id}</dd>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Teams Section */}
      <div className="mt-6 bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900">Teams</h2>
              <p className="mt-1 text-sm text-gray-500">
                {teams.length} {teams.length === 1 ? 'team' : 'teams'} registered
              </p>
            </div>
            {canCreateOrJoinTeams && user && (
              <button
                onClick={() => setShowCreateForm(true)}
                disabled={teams.length >= competition.max_teams}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Plus className="h-4 w-4 mr-2" />
                Create Team
              </button>
            )}
          </div>

          {teamsLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-sm text-gray-500">Loading teams...</p>
            </div>
          ) : (
            <TeamList
              teams={teams}
              competition={{
                max_members_per_team: competition.max_members_per_team,
                status: competition.status,
              }}
              currentUserUid={user?.uid || ''}
              onJoinTeam={handleJoinTeam}
              onLeaveTeam={handleLeaveTeam}
            />
          )}
        </div>
      </div>

      {/* Create Team Modal */}
      {showCreateForm && user && (
        <TeamCreateForm
          compId={competition.comp_id}
          ownerUid={user.uid}
          maxTeams={competition.max_teams}
          currentTeamCount={teams.length}
          onSubmit={handleCreateTeam}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      {/* Steps Section - Only show if user is in a team */}
      {isUserInTeam && user && (
        <>
          <div className="mt-6 bg-white shadow sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 flex items-center">
                    <Activity className="h-5 w-5 mr-2" />
                    My Steps
                  </h2>
                  <p className="mt-1 text-sm text-gray-500">
                    Track and submit your daily step count
                  </p>
                </div>
                {competition.status === 'ACTIVE' && (
                  <button
                    onClick={() => setShowStepEntryForm(true)}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Submit Steps
                  </button>
                )}
              </div>

              <StepHistory steps={steps} isLoading={stepsLoading} />
            </div>
          </div>

          {/* Step Entry Modal */}
          {showStepEntryForm && user && (
            <StepEntryForm
              compId={competition.comp_id}
              competition={{
                start_date: competition.start_date,
                end_date: competition.end_date,
                status: competition.status,
              }}
              onSubmit={handleSubmitSteps}
              onCancel={() => setShowStepEntryForm(false)}
            />
          )}
        </>
      )}

      {/* Leaderboards Section */}
      <div className="mt-6 bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900 flex items-center">
                <Trophy className="h-5 w-5 mr-2" />
                Leaderboards
              </h2>
              <p className="mt-1 text-sm text-gray-500">
                Rankings for {competition.name}
              </p>
            </div>
            
            {/* Date Filter */}
            <div className="flex items-center space-x-2">
              <label htmlFor="leaderboard-date" className="text-sm text-gray-700">
                Filter by date:
              </label>
              <input
                type="date"
                id="leaderboard-date"
                className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                value={leaderboardDate || ''}
                onChange={(e) => setLeaderboardDate(e.target.value || undefined)}
                min={competition.start_date}
                max={competition.end_date}
              />
              {leaderboardDate && (
                <button
                  onClick={() => setLeaderboardDate(undefined)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('individual')}
                className={`${
                  activeTab === 'individual'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Individual
              </button>
              <button
                onClick={() => setActiveTab('team')}
                className={`${
                  activeTab === 'team'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Teams
              </button>
            </nav>
          </div>

          {/* Leaderboard Content */}
          {activeTab === 'individual' && (
            <IndividualLeaderboard
              entries={individualLeaderboardData?.rows || []}
              isLoading={individualLoading}
              currentUserId={user?.uid}
            />
          )}

          {activeTab === 'team' && (
            <TeamLeaderboard
              entries={teamLeaderboardData?.rows || []}
              isLoading={teamLoading}
              currentUserTeamId={userTeamId}
            />
          )}
        </div>
      </div>
    </div>
  );
}
