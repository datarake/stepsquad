import React, { useState } from 'react';
import { useAuth } from './auth';
import {
  LogIn,
  Users,
  Trophy,
  Activity,
  ShieldCheck,
} from 'lucide-react';

const featureHighlights = [
  {
    Icon: Users,
    title: 'Move Together',
    description:
      'Build supportive squads, celebrate daily wins, and keep everyone accountable through collaborative step challenges.',
  },
  {
    Icon: Activity,
    title: 'Fair & Connected',
    description:
      'Sync real-time data from Garmin and Fitbit devices while AI agents keep every competition honest and engaging.',
  },
  {
    Icon: Trophy,
    title: 'Win as One',
    description:
      'Track progress, unlock insights, and climb dynamic leaderboards that update in real-time as your team moves together.',
  },
];

export function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const USE_DEV_AUTH = import.meta.env.VITE_USE_DEV_AUTH === 'true';
  const ADMIN_EMAIL = import.meta.env.VITE_ADMIN_EMAIL || 'admin@stepsquad.club';

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
    <div className="relative flex min-h-screen flex-col bg-slate-950 text-slate-100 lg:flex-row">
      <div className="relative hidden flex-1 flex-col justify-between overflow-hidden px-12 py-16 lg:flex">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.25),_transparent_55%)]" />
        <div className="absolute inset-0 opacity-40" style={{
          backgroundImage:
            'linear-gradient(120deg, rgba(56,189,248,0.25) 0%, rgba(37,99,235,0.25) 45%, rgba(148,163,184,0.15) 100%)',
        }} />
        <div className="relative z-10 max-w-xl">
          <span className="inline-flex items-center rounded-full bg-blue-500/10 px-4 py-1 text-sm font-medium text-blue-200 ring-1 ring-inset ring-blue-500/30">
            StepSquad - Move Together, Win Together
          </span>
          <h1 className="mt-6 text-4xl font-bold leading-tight text-slate-50">
            The competitive fitness platform built for squads who thrive together.
          </h1>
          <p className="mt-4 text-lg text-slate-200">
            StepSquad is a social fitness experience where teams rally around daily movement, track progress with live leaderboards, and unlock AI-powered insights to keep everyone motivated and engaged.
          </p>
          <div className="mt-12 grid gap-6">
            {featureHighlights.map(({ Icon, title, description }) => (
              <div
                key={title}
                className="flex items-start gap-4 rounded-2xl border border-white/5 bg-white/5 p-5 backdrop-blur-sm"
              >
                <span className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/20 text-blue-200">
                  <Icon className="h-6 w-6" />
                </span>
                <div>
                  <p className="text-base font-semibold text-slate-50">{title}</p>
                  <p className="mt-2 text-sm text-slate-200/90">{description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="relative z-10 mt-12 flex items-center gap-3 rounded-2xl border border-white/10 bg-slate-900/60 px-5 py-4 text-sm text-slate-300 backdrop-blur">
          <ShieldCheck className="h-5 w-5 text-blue-300" />
          <p>
            Built with secure Firebase authentication, Firestore, and AI agents orchestrated on Google Cloud Run.
          </p>
        </div>
      </div>

      <div className="relative flex flex-1 items-center justify-center px-6 py-16 sm:px-10 lg:px-16">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 opacity-70 lg:hidden" aria-hidden="true" />
        <div className="relative z-10 w-full max-w-md">
          <div className="mb-8 space-y-3 text-center lg:text-left">
            <div className="inline-flex items-center justify-center rounded-full bg-blue-500/15 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-blue-300">
              Welcome back
            </div>
            <div className="flex items-center justify-center gap-3 text-2xl font-semibold text-white lg:justify-start">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-500/20 text-blue-200">
                <LogIn className="h-6 w-6" />
              </span>
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-blue-300">StepSquad</p>
                <p>Sign in to continue</p>
              </div>
            </div>
            <p className="text-sm text-slate-300">
              Rally your team, sync your steps, and chase the leaderboard together. Log in or create an account to get moving.
            </p>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/95 p-8 text-slate-900 shadow-2xl shadow-blue-500/10 backdrop-blur">
            <form className="space-y-6" onSubmit={handleSubmit}>
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-semibold text-slate-700">
                  Email address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  className="w-full rounded-xl border border-slate-200/80 bg-slate-50 px-4 py-3 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              {!USE_DEV_AUTH && (
                <div className="space-y-2">
                  <label htmlFor="password" className="text-sm font-semibold text-slate-700">
                    Password
                  </label>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    className="w-full rounded-xl border border-slate-200/80 bg-slate-50 px-4 py-3 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <p className="text-xs text-slate-500">
                    New here? Use a fresh email and we’ll create your account instantly.
                  </p>
                </div>
              )}

              {USE_DEV_AUTH && (
                <div className="rounded-2xl border border-dashed border-blue-200 bg-blue-50/60 px-4 py-3 text-sm text-blue-800">
                  <p className="font-medium">Development Mode</p>
                  <p className="mt-1 text-xs opacity-90">
                    Quick login is enabled. Use the admin shortcut below to explore the app faster.
                  </p>
                  <button
                    type="button"
                    onClick={() => setEmail(ADMIN_EMAIL)}
                    className="mt-3 inline-flex items-center gap-2 rounded-full bg-blue-600 px-4 py-1.5 text-xs font-semibold text-white shadow-sm transition hover:bg-blue-700"
                  >
                    Use admin email ({ADMIN_EMAIL})
                  </button>
                </div>
              )}

              {error && (
                <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={
                  loading ||
                  !email.trim() ||
                  (!USE_DEV_AUTH && !password.trim())
                }
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-500 via-blue-600 to-indigo-500 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/30 transition focus:outline-none focus:ring-2 focus:ring-blue-200 focus:ring-offset-2 focus:ring-offset-white disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? 'Signing in...' : USE_DEV_AUTH ? 'Sign in' : 'Sign in / Sign up'}
              </button>
            </form>

            <p className="mt-8 text-center text-xs text-slate-500">
              Empowering every team to move, compete, and win together.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
