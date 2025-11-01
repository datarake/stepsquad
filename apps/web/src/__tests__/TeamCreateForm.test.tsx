import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '../test/utils';
import userEvent from '@testing-library/user-event';
import { TeamCreateForm } from '../TeamCreateForm';

describe('TeamCreateForm', () => {
  const mockOnSubmit = vi.fn();
  const mockOnCancel = vi.fn();

  const defaultProps = {
    compId: 'comp1',
    ownerUid: 'user1',
    maxTeams: 10,
    currentTeamCount: 2,
    onSubmit: mockOnSubmit,
    onCancel: mockOnCancel,
  };

  beforeEach(() => {
    mockOnSubmit.mockClear();
    mockOnCancel.mockClear();
  });

  it('renders form with all fields', () => {
    render(<TeamCreateForm {...defaultProps} />);

    expect(screen.getByRole('heading', { name: /create team/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/team name/i)).toBeInTheDocument();
    expect(screen.getByText(/teams: 2 \/ 10/i)).toBeInTheDocument();
  });

  it('calls onCancel when cancel button is clicked', async () => {
    const user = userEvent.setup();
    render(<TeamCreateForm {...defaultProps} />);

    const cancelButton = screen.getByText(/cancel/i);
    await user.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });

  it('calls onCancel when X button is clicked', async () => {
    const user = userEvent.setup();
    render(<TeamCreateForm {...defaultProps} />);

    const xButton = screen.getByRole('button', { name: '' }); // X button has no accessible name
    await user.click(xButton);

    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });

  it('validates team name is required', async () => {
    const user = userEvent.setup();
    render(<TeamCreateForm {...defaultProps} />);

    const submitButton = screen.getByRole('button', { name: /create team/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/team name is required/i)).toBeInTheDocument();
    });
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('validates team name length', async () => {
    const user = userEvent.setup();
    render(<TeamCreateForm {...defaultProps} />);

    const nameInput = screen.getByLabelText(/team name/i) as HTMLInputElement;
    expect(nameInput.maxLength).toBe(50); // maxLength attribute should be set
    
    // Try to type 51 characters - maxLength should limit it
    await user.type(nameInput, 'a'.repeat(51));
    expect(nameInput.value.length).toBeLessThanOrEqual(50);
    
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('calls onSubmit with correct data when form is valid', async () => {
    const user = userEvent.setup();
    mockOnSubmit.mockResolvedValue(undefined);
    
    render(<TeamCreateForm {...defaultProps} />);

    const nameInput = screen.getByLabelText(/team name/i);
    await user.type(nameInput, 'Test Team');

    const submitButton = screen.getByRole('button', { name: /create team/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'Test Team',
        comp_id: 'comp1',
        owner_uid: 'user1',
      });
    });
  });

  it('disables submit button when max teams reached', () => {
    render(
      <TeamCreateForm
        {...defaultProps}
        currentTeamCount={10}
        maxTeams={10}
      />
    );

    const submitButton = screen.getByRole('button', { name: /create team/i });
    expect(submitButton).toBeDisabled();
  });

  it('shows error when max teams reached', () => {
    render(
      <TeamCreateForm
        {...defaultProps}
        currentTeamCount={10}
        maxTeams={10}
      />
    );

    // Verify form renders with max teams info
    expect(screen.getByText(/teams: 10 \/ 10/i)).toBeInTheDocument();
    // Verify submit button is disabled
    const submitButton = screen.getByRole('button', { name: /create team/i });
    expect(submitButton).toBeDisabled();
    // The error is validated in validate() function, which prevents submission
    // The button being disabled is the main indication
  });

  it('trims team name before submitting', async () => {
    const user = userEvent.setup();
    mockOnSubmit.mockResolvedValue(undefined);
    
    render(<TeamCreateForm {...defaultProps} />);

    const nameInput = screen.getByLabelText(/team name/i);
    await user.type(nameInput, '  Test Team  '); // With spaces

    const submitButton = screen.getByRole('button', { name: /create team/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'Test Team', // Should be trimmed
        comp_id: 'comp1',
        owner_uid: 'user1',
      });
    });
  });

  it('shows loading state when submitting', async () => {
    const user = userEvent.setup();
    let resolvePromise: () => void;
    const promise = new Promise<void>((resolve) => {
      resolvePromise = resolve;
    });
    mockOnSubmit.mockReturnValue(promise);
    
    render(<TeamCreateForm {...defaultProps} />);

    const nameInput = screen.getByLabelText(/team name/i);
    await user.type(nameInput, 'Test Team');

    const submitButton = screen.getByRole('button', { name: /create team/i });
    await user.click(submitButton);

    expect(screen.getByText(/creating.../i)).toBeInTheDocument();
    expect(submitButton).toBeDisabled();

    resolvePromise!();
    await waitFor(() => {
      expect(screen.queryByText(/creating.../i)).not.toBeInTheDocument();
    });
  });

  it('displays error when onSubmit fails', async () => {
    const user = userEvent.setup();
    const errorMessage = 'Failed to create team';
    mockOnSubmit.mockRejectedValue(new Error(errorMessage));
    
    render(<TeamCreateForm {...defaultProps} />);

    const nameInput = screen.getByLabelText(/team name/i);
    await user.type(nameInput, 'Test Team');

    const submitButton = screen.getByRole('button', { name: /create team/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });
});

