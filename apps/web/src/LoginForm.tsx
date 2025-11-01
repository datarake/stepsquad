import React, { useState } from 'react';
import { useAuth } from './auth';
import { LogIn } from 'lucide-react';

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const USE_DEV_AUTH = import.meta.env.VITE_USE_DEV_AUTH === 'true';
  const ADMIN_EMAIL = import.meta.env.VITE_ADMIN_EMAIL || 'admin@stepsquad.com';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;
    if (!USE_DEV_AUTH && !password.trim()) {
      setError('Password is required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await login(email.trim(), USE_DEV_AUTH ? undefined : password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100">
            <LogIn className="h-6 w-6 text-blue-600" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to StepSquad
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {USE_DEV_AUTH ? 'Development Mode' : 'Enter your credentials'}
          </p>
        </div>
        
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {!USE_DEV_AUTH && (
              <div>
                <label htmlFor="password" className="sr-only">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <p className="mt-2 text-xs text-gray-500">
                  New users: Entering a new email will automatically create an account
                </p>
              </div>
            )}

            {USE_DEV_AUTH && (
              <div className="text-sm text-gray-600">
                <p>Quick login:</p>
                <button
                  type="button"
                  onClick={() => setEmail(ADMIN_EMAIL)}
                  className="text-blue-600 hover:text-blue-500"
                >
                  Use admin email ({ADMIN_EMAIL})
                </button>
              </div>
            )}

          {error && (
            <div className="text-red-600 text-sm text-center">
              {error}
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading || !email.trim() || (!USE_DEV_AUTH && !password.trim())}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (USE_DEV_AUTH ? 'Signing in...' : 'Signing in...') : (USE_DEV_AUTH ? 'Sign in' : 'Sign in / Sign up')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
