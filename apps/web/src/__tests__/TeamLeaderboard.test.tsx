import { describe, it, expect } from 'vitest';
import { render, screen } from '../test/utils';
import { TeamLeaderboard } from '../TeamLeaderboard';
import { LeaderboardEntry } from '../types';

describe('TeamLeaderboard', () => {
  const mockEntries: LeaderboardEntry[] = [
    { team_id: 'team1', name: 'Team Alpha', steps: 25000, rank: 1, member_count: 3 },
    { team_id: 'team2', name: 'Team Beta', steps: 22000, rank: 2, member_count: 2 },
    { team_id: 'team3', name: 'Team Gamma', steps: 18000, rank: 3, member_count: 4 },
  ];

  it('renders empty state when no entries', () => {
    render(<TeamLeaderboard entries={[]} />);

    expect(screen.getByText(/no teams yet/i)).toBeInTheDocument();
    expect(screen.getByText(/teams will appear here once they start submitting steps/i)).toBeInTheDocument();
  });

  it('shows loading state when isLoading is true', () => {
    render(<TeamLeaderboard entries={[]} isLoading={true} />);

    expect(screen.getByText(/loading leaderboard.../i)).toBeInTheDocument();
    expect(document.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('renders team leaderboard entries with ranks', () => {
    render(<TeamLeaderboard entries={mockEntries} />);

    expect(screen.getByText('Team Alpha')).toBeInTheDocument();
    expect(screen.getByText('Team Beta')).toBeInTheDocument();
    expect(screen.getByText('25,000')).toBeInTheDocument();
    expect(screen.getByText('22,000')).toBeInTheDocument();
  });

  it('displays member count for each team', () => {
    render(<TeamLeaderboard entries={mockEntries} />);

    expect(screen.getByText('3 members')).toBeInTheDocument();
    expect(screen.getByText('2 members')).toBeInTheDocument();
    expect(screen.getByText('4 members')).toBeInTheDocument();
  });

  it('highlights current user team', () => {
    render(<TeamLeaderboard entries={mockEntries} currentUserTeamId="team2" />);

    const userTeam = screen.getByText('Team Beta').closest('div');
    expect(userTeam).toHaveClass('bg-blue-50');
    expect(screen.getByText('Your Team')).toBeInTheDocument();
  });

  it('highlights first place with trophy icon', () => {
    render(<TeamLeaderboard entries={mockEntries} />);

    // First place should have trophy
    const firstPlace = screen.getByText('Team Alpha').closest('div');
    expect(firstPlace?.querySelector('.lucide-trophy')).toBeInTheDocument();
  });

  it('formats step counts with commas', () => {
    const largeSteps: LeaderboardEntry[] = [
      { team_id: 'team1', name: 'Team Alpha', steps: 123456, rank: 1, member_count: 3 },
    ];
    
    render(<TeamLeaderboard entries={largeSteps} />);

    expect(screen.getByText('123,456')).toBeInTheDocument();
  });

  it('displays rank badges for top 3', () => {
    render(<TeamLeaderboard entries={mockEntries} />);

    // Rank 1 (trophy), 2 (medal), 3 (award) should have icons
    expect(document.querySelector('.lucide-trophy')).toBeInTheDocument();
    expect(document.querySelector('.lucide-medal')).toBeInTheDocument();
    expect(document.querySelector('.lucide-award')).toBeInTheDocument();
  });

  it('shows users icon for teams', () => {
    render(<TeamLeaderboard entries={mockEntries} />);

    // Should have Users icons for teams (check for lucide-users class)
    expect(document.querySelector('.lucide-users')).toBeInTheDocument();
  });

  it('handles singular member count correctly', () => {
    const singleMemberTeam: LeaderboardEntry[] = [
      { team_id: 'team1', name: 'Team Solo', steps: 10000, rank: 1, member_count: 1 },
    ];
    
    render(<TeamLeaderboard entries={singleMemberTeam} />);

    expect(screen.getByText('1 member')).toBeInTheDocument();
  });
});

