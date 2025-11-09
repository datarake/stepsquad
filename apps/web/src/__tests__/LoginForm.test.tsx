import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '../test/utils'
import { LoginForm } from '../LoginForm'
import * as authModule from '../auth'

describe('LoginForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('renders login form with email input', () => {
    render(<LoginForm />)
    
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('shows password field in Firebase mode', () => {
    // Mock environment to use Firebase mode
    vi.stubEnv('VITE_USE_DEV_AUTH', 'false')
    
    render(<LoginForm />)
    
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
  })

  it('hides password field in dev mode', () => {
    vi.stubEnv('VITE_USE_DEV_AUTH', 'true')
    
    render(<LoginForm />)
    
    expect(screen.queryByLabelText(/password/i)).not.toBeInTheDocument()
  })

  it('renders admin email quick login in dev mode', () => {
    vi.stubEnv('VITE_USE_DEV_AUTH', 'true')
    vi.stubEnv('VITE_ADMIN_EMAIL', 'admin@stepsquad.club')
    
    render(<LoginForm />)
    
    expect(screen.getByText(/admin@stepsquad.club/i)).toBeInTheDocument()
  })
})
