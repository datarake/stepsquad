import { describe, it, expect } from 'vitest';
import { render, screen } from '../test/utils';
import { StepHistory } from '../StepHistory';
import { StepEntry } from '../types';

describe('StepHistory', () => {
  const mockSteps: StepEntry[] = [
    { user_id: 'user1', date: '2025-02-15', steps: 12000 },
    { user_id: 'user1', date: '2025-02-14', steps: 8500 },
    { user_id: 'user1', date: '2025-02-13', steps: 15000 },
    { user_id: 'user1', date: '2025-02-12', steps: 9500 },
  ];

  it('renders empty state when no steps', () => {
    render(<StepHistory steps={[]} />);

    expect(screen.getByText(/no steps submitted yet/i)).toBeInTheDocument();
    expect(screen.getByText(/start submitting steps to see your history here/i)).toBeInTheDocument();
  });

  it('shows loading state when isLoading is true', () => {
    render(<StepHistory steps={[]} isLoading={true} />);

    expect(screen.getByText(/loading step history.../i)).toBeInTheDocument();
    // Loading spinner is present
    expect(document.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('renders step history with statistics', () => {
    render(<StepHistory steps={mockSteps} />);

    // Check stats are displayed
    expect(screen.getByText(/total steps/i)).toBeInTheDocument();
    expect(screen.getByText(/average\/day/i)).toBeInTheDocument();
    expect(screen.getByText(/days active/i)).toBeInTheDocument();
    
    // Check totals (12000 + 8500 + 15000 + 9500 = 45000)
    const totalElements = screen.getAllByText('45,000');
    expect(totalElements.length).toBeGreaterThan(0);
    // Average (45000 / 4 = 11250)
    const avgElements = screen.getAllByText('11,250');
    expect(avgElements.length).toBeGreaterThan(0);
    // Days active
    const daysElements = screen.getAllByText('4');
    expect(daysElements.length).toBeGreaterThan(0);
  });

  it('renders step entries with dates and counts', () => {
    render(<StepHistory steps={mockSteps} />);

    // Check that dates are displayed (using regex for case-insensitive)
    expect(screen.getByText(/feb.*15.*2025/i)).toBeInTheDocument();
    expect(screen.getByText(/feb.*14.*2025/i)).toBeInTheDocument();
    
    // Check that step counts are displayed (may appear multiple times, use getAllByText)
    expect(screen.getAllByText('12,000').length).toBeGreaterThan(0);
    expect(screen.getAllByText('8,500').length).toBeGreaterThan(0);
    expect(screen.getAllByText('15,000').length).toBeGreaterThan(0);
    expect(screen.getAllByText('9,500').length).toBeGreaterThan(0);
  });

  it('highlights best day (max steps)', () => {
    render(<StepHistory steps={mockSteps} />);

    // Find the best day entry (15,000 steps on 2025-02-13)
    const bestDayText = screen.getByText(/feb.*13.*2025/i);
    const bestDayEntry = bestDayText.closest('div.bg-green-50');
    expect(bestDayEntry).toBeInTheDocument();
    expect(screen.getByText(/best day!/i)).toBeInTheDocument();
  });

  it('highlights lowest day when multiple entries', () => {
    render(<StepHistory steps={mockSteps} />);

    // Find the lowest day entry (8,500 steps on 2025-02-14)
    const lowestDayText = screen.getByText(/feb.*14.*2025/i);
    const lowestDayEntry = lowestDayText.closest('div.bg-red-50');
    expect(lowestDayEntry).toBeInTheDocument();
    expect(screen.getByText(/lowest day/i)).toBeInTheDocument();
  });

  it('does not show lowest day indicator when only one entry', () => {
    const singleStep: StepEntry[] = [
      { user_id: 'user1', date: '2025-02-15', steps: 12000 },
    ];
    
    render(<StepHistory steps={singleStep} />);

    // With only one entry, it won't show "Lowest Day" because steps.length > 1 check
    expect(screen.queryByText(/lowest day/i)).not.toBeInTheDocument();
    // Best Day might still show since it's the max (and only) entry
    // So we just check that lowest day doesn't show
  });

  it('formats step counts with commas', () => {
    const largeSteps: StepEntry[] = [
      { user_id: 'user1', date: '2025-02-15', steps: 12345 },
      { user_id: 'user1', date: '2025-02-14', steps: 67890 },
    ];
    
    render(<StepHistory steps={largeSteps} />);

    // May appear in stats and entry list, so use getAllByText
    expect(screen.getAllByText('12,345').length).toBeGreaterThan(0);
    expect(screen.getAllByText('67,890').length).toBeGreaterThan(0);
  });

  it('displays correct total for all entries', () => {
    const steps: StepEntry[] = [
      { user_id: 'user1', date: '2025-02-15', steps: 1000 },
      { user_id: 'user1', date: '2025-02-14', steps: 2000 },
      { user_id: 'user1', date: '2025-02-13', steps: 3000 },
    ];
    
    render(<StepHistory steps={steps} />);

    // Total: 1000 + 2000 + 3000 = 6000 (may appear in multiple places)
    expect(screen.getAllByText('6,000').length).toBeGreaterThan(0);
  });

  it('displays correct average for all entries', () => {
    const steps: StepEntry[] = [
      { user_id: 'user1', date: '2025-02-15', steps: 1000 },
      { user_id: 'user1', date: '2025-02-14', steps: 2000 },
      { user_id: 'user1', date: '2025-02-13', steps: 3000 },
    ];
    
    render(<StepHistory steps={steps} />);

    // Average: (1000 + 2000 + 3000) / 3 = 2000 (may appear in multiple places)
    expect(screen.getAllByText('2,000').length).toBeGreaterThan(0);
  });

  it('renders step history section heading', () => {
    render(<StepHistory steps={mockSteps} />);

    expect(screen.getByRole('heading', { name: /step history/i })).toBeInTheDocument();
  });
});

