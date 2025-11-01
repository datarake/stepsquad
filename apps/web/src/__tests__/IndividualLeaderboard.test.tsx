import { describe, it, expect } from 'vitest';
import { render, screen } from '../test/utils';
import { IndividualLeaderboard } from '../IndividualLeaderboard';
import { LeaderboardEntry } from '../types';

describe('IndividualLeaderboard', () => {
  const mockEntries: LeaderboardEntry[] = [
    { user_id: 'user1', email: 'user1@example.com', steps: 15000, rank: 1 },
    { user_id: 'user2', email: 'user2@example.com', steps: 12000, rank: 2 },
    { user_id: 'user3', email: 'user3@example.com', steps: 10000, rank: 3 },
    { user_id: 'user4', email: 'user4@example.com', steps: 8500, rank: 4 },
  ];

  it('renders empty state when no entries', () => {
    render(<IndividualLeaderboard entries={[]} />);

    expect(screen.getByText(/no entries yet/i)).toBeInTheDocument();
    expect(screen.getByText(/start submitting steps to see rankings/i)).toBeInTheDocument();
  });

  it('shows loading state when isLoading is true', () => {
    render(<IndividualLeaderboard entries={[]} isLoading={true} />);

    expect(screen.getByText(/loading leaderboard.../i)).toBeInTheDocument();
    expect(document.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('renders leaderboard entries with ranks', () => {
    render(<IndividualLeaderboard entries={mockEntries} />);

    expect(screen.getByText('user1@example.com')).toBeInTheDocument();
    expect(screen.getByText('user2@example.com')).toBeInTheDocument();
    expect(screen.getByText('15,000')).toBeInTheDocument();
    expect(screen.getByText('12,000')).toBeInTheDocument();
  });

  it('highlights first place with trophy icon', () => {
    render(<IndividualLeaderboard entries={mockEntries} />);

    // First place should have trophy - check for trophy icon in the rank badge
    expect(document.querySelector('.lucide-trophy')).toBeInTheDocument();
  });

  it('highlights current user entry', () => {
    render(<IndividualLeaderboard entries={mockEntries} currentUserId="user2" />);

    const userEntry = screen.getByText('user2@example.com').closest('div');
    expect(userEntry).toHaveClass('bg-blue-50');
    expect(screen.getByText('You')).toBeInTheDocument();
  });

  it('formats step counts with commas', () => {
    const largeSteps: LeaderboardEntry[] = [
      { user_id: 'user1', email: 'user1@example.com', steps: 12345, rank: 1 },
    ];
    
    render(<IndividualLeaderboard entries={largeSteps} />);

    expect(screen.getByText('12,345')).toBeInTheDocument();
  });

  it('displays rank badges for top 3', () => {
    render(<IndividualLeaderboard entries={mockEntries} />);

    // Rank 1 (trophy), 2 (medal), 3 (award) should have icons
    expect(document.querySelector('.lucide-trophy')).toBeInTheDocument();
    expect(document.querySelector('.lucide-medal')).toBeInTheDocument();
    expect(document.querySelector('.lucide-award')).toBeInTheDocument();
  });

  it('displays numeric rank for entries beyond top 3', () => {
    render(<IndividualLeaderboard entries={mockEntries} />);

    // Rank 4 should show numeric rank (check that rank 4 is displayed)
    expect(screen.getByText('4')).toBeInTheDocument();
  });

  it('shows steps label for each entry', () => {
    render(<IndividualLeaderboard entries={mockEntries} />);

    const stepsLabels = screen.getAllByText(/steps/i);
    expect(stepsLabels.length).toBeGreaterThan(0);
  });
});

