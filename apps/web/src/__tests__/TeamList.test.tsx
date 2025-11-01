import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '../test/utils';
import { TeamList } from '../TeamList';
import { Team } from '../types';

const mockCompetition = {
  max_members_per_team: 5,
  status: 'REGISTRATION',
};

const mockTeams: Team[] = [
  {
    team_id: 'team1',
    name: 'Team Alpha',
    comp_id: 'comp1',
    owner_uid: 'user1',
    members: ['user1'],
  },
  {
    team_id: 'team2',
    name: 'Team Beta',
    comp_id: 'comp1',
    owner_uid: 'user2',
    members: ['user2', 'user3'],
  },
];

describe('TeamList', () => {
  it('renders empty state when no teams', () => {
    const onJoinTeam = vi.fn();
    const onLeaveTeam = vi.fn();
    
    render(
      <TeamList
        teams={[]}
        competition={mockCompetition}
        currentUserUid="user1"
        onJoinTeam={onJoinTeam}
        onLeaveTeam={onLeaveTeam}
      />
    );

    expect(screen.getByText(/no teams yet/i)).toBeInTheDocument();
    expect(screen.getByText(/be the first to create a team/i)).toBeInTheDocument();
  });

  it('renders list of teams', () => {
    const onJoinTeam = vi.fn();
    const onLeaveTeam = vi.fn();
    
    render(
      <TeamList
        teams={mockTeams}
        competition={mockCompetition}
        currentUserUid="user1"
        onJoinTeam={onJoinTeam}
        onLeaveTeam={onLeaveTeam}
      />
    );

    expect(screen.getByText('Team Alpha')).toBeInTheDocument();
    expect(screen.getByText('Team Beta')).toBeInTheDocument();
  });

  it('shows owner badge for team owner', () => {
    const onJoinTeam = vi.fn();
    const onLeaveTeam = vi.fn();
    
    render(
      <TeamList
        teams={mockTeams}
        competition={mockCompetition}
        currentUserUid="user1"
        onJoinTeam={onJoinTeam}
        onLeaveTeam={onLeaveTeam}
      />
    );

    expect(screen.getByText('Owner')).toBeInTheDocument();
  });

  it('shows member count', () => {
    const onJoinTeam = vi.fn();
    const onLeaveTeam = vi.fn();
    
    render(
      <TeamList
        teams={mockTeams}
        competition={mockCompetition}
        currentUserUid="user4"
        onJoinTeam={onJoinTeam}
        onLeaveTeam={onLeaveTeam}
      />
    );

    expect(screen.getByText(/1 \/ 5 members/i)).toBeInTheDocument();
    expect(screen.getByText(/2 \/ 5 members/i)).toBeInTheDocument();
  });

  it('shows join button when user is not a member and team is not full', () => {
    const onJoinTeam = vi.fn();
    const onLeaveTeam = vi.fn();
    
    render(
      <TeamList
        teams={mockTeams}
        competition={mockCompetition}
        currentUserUid="user4"
        onJoinTeam={onJoinTeam}
        onLeaveTeam={onLeaveTeam}
      />
    );

    const joinButtons = screen.getAllByText(/join team/i);
    expect(joinButtons.length).toBeGreaterThan(0);
  });

  it('shows leave button when user is a member', () => {
    const onJoinTeam = vi.fn();
    const onLeaveTeam = vi.fn();
    
    render(
      <TeamList
        teams={mockTeams}
        competition={mockCompetition}
        currentUserUid="user3"
        onJoinTeam={onJoinTeam}
        onLeaveTeam={onLeaveTeam}
      />
    );

    expect(screen.getByText(/leave team/i)).toBeInTheDocument();
  });

  it('shows full indicator when team is full', () => {
    const fullTeam: Team[] = [
      {
        team_id: 'team3',
        name: 'Test Team',
        comp_id: 'comp1',
        owner_uid: 'user1',
        members: ['user1', 'user2', 'user3', 'user4', 'user5'],
      },
    ];

    const onJoinTeam = vi.fn();
    const onLeaveTeam = vi.fn();
    
    render(
      <TeamList
        teams={fullTeam}
        competition={mockCompetition}
        currentUserUid="user6"
        onJoinTeam={onJoinTeam}
        onLeaveTeam={onLeaveTeam}
      />
    );

    expect(screen.getByText(/team is full/i)).toBeInTheDocument();
  });

  it('calls onJoinTeam when join button is clicked', () => {
    const onJoinTeam = vi.fn();
    const onLeaveTeam = vi.fn();
    
    render(
      <TeamList
        teams={mockTeams}
        competition={mockCompetition}
        currentUserUid="user4"
        onJoinTeam={onJoinTeam}
        onLeaveTeam={onLeaveTeam}
      />
    );

    const joinButtons = screen.getAllByText(/join team/i);
    joinButtons[0].click();
    
    expect(onJoinTeam).toHaveBeenCalledWith('team1');
  });

  it('calls onLeaveTeam when leave button is clicked', () => {
    const onJoinTeam = vi.fn();
    const onLeaveTeam = vi.fn();
    
    render(
      <TeamList
        teams={mockTeams}
        competition={mockCompetition}
        currentUserUid="user3"
        onJoinTeam={onJoinTeam}
        onLeaveTeam={onLeaveTeam}
      />
    );

    const leaveButton = screen.getByText(/leave team/i);
    leaveButton.click();
    
    expect(onLeaveTeam).toHaveBeenCalledWith('team2');
  });

  it('does not show join/leave buttons when competition status is not REGISTRATION or ACTIVE', () => {
    const onJoinTeam = vi.fn();
    const onLeaveTeam = vi.fn();
    
    render(
      <TeamList
        teams={mockTeams}
        competition={{ ...mockCompetition, status: 'ENDED' }}
        currentUserUid="user4"
        onJoinTeam={onJoinTeam}
        onLeaveTeam={onLeaveTeam}
      />
    );

    expect(screen.queryByText(/join team/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/leave team/i)).not.toBeInTheDocument();
  });
});

