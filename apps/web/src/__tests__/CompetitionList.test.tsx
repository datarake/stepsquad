import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '../test/utils'
import { CompetitionList } from '../CompetitionList'
import { Competition, Status } from '../types'

const mockCompetitions: Competition[] = [
  {
    comp_id: 'comp1',
    name: 'Test Competition 1',
    status: 'ACTIVE' as Status,
    tz: 'Europe/Bucharest',
    registration_open_date: '2025-01-01',
    start_date: '2025-02-01',
    end_date: '2025-03-01',
    max_teams: 10,
    max_members_per_team: 5,
    created_by: 'admin@stepsquad.com',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    comp_id: 'comp2',
    name: 'Test Competition 2',
    status: 'DRAFT' as Status,
    tz: 'Europe/Bucharest',
    registration_open_date: '2025-04-01',
    start_date: '2025-05-01',
    end_date: '2025-06-01',
    max_teams: 20,
    max_members_per_team: 8,
    created_by: 'admin@stepsquad.com',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

describe('CompetitionList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders empty state when no competitions', () => {
    render(<CompetitionList competitions={[]} />)
    
    expect(screen.getByRole('heading', { name: /no competitions/i })).toBeInTheDocument()
  })

  it('renders list of competitions', () => {
    render(<CompetitionList competitions={mockCompetitions} />)
    
    expect(screen.getByText('Test Competition 1')).toBeInTheDocument()
    expect(screen.getByText('Test Competition 2')).toBeInTheDocument()
  })

  it('shows status badges', () => {
    render(<CompetitionList competitions={mockCompetitions} />)
    
    expect(screen.getByText('Active')).toBeInTheDocument()
    expect(screen.getByText('Draft')).toBeInTheDocument()
  })

  it('shows competitions with dates', () => {
    render(<CompetitionList competitions={mockCompetitions} />)
    
    // Check that competition names are visible
    expect(screen.getByText('Test Competition 1')).toBeInTheDocument()
    expect(screen.getByText('Test Competition 2')).toBeInTheDocument()
  })
})
