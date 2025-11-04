import React, { useMemo } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from './auth';
import { LogOut, User, Activity, LayoutDashboard } from 'lucide-react';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const { user, logout, isAdmin } = useAuth();

  if (!user) return null;

  const navItems = useMemo(
    () => [
      {
        to: '/',
        label: 'Overview',
        icon: LayoutDashboard,
      },
      {
        to: '/devices',
        label: 'Devices',
        icon: Activity,
      },
    ],
    [],
  );

  const userInitials = useMemo(() => user.email?.[0]?.toUpperCase() ?? '?', [user.email]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Top Navigation */}
      <nav className="relative border-b border-white/10 bg-gradient-to-r from-indigo-600 via-purple-600 to-blue-600">
        <div className="absolute inset-0 opacity-60">
          <div className="h-full w-full bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.25),_transparent_55%)]" />
        </div>
        <div className="relative">
          <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-8">
              <Link to="/" className="group flex items-center gap-2 text-2xl font-semibold tracking-tight">
                <span className="rounded-full bg-white/20 px-3 py-1 text-sm font-medium uppercase text-white/90">Step</span>
                <span className="text-white transition group-hover:translate-x-0.5">Squad</span>
              </Link>

              <div className="hidden items-center gap-1 rounded-full bg-white/10 p-1 text-sm font-medium text-white/80 shadow-inner shadow-black/20 backdrop-blur sm:flex">
                {navItems.map(({ to, label, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    end={to === '/'}
                    className={({ isActive }) =>
                      `group flex items-center gap-2 rounded-full px-4 py-2 transition-all duration-200 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/70 ${
                        isActive
                          ? 'bg-white/95 text-indigo-600 shadow-sm shadow-black/10'
                          : 'text-white/80 hover:bg-white/10'
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <Icon
                          className={`h-4 w-4 transition ${
                            isActive ? 'text-indigo-600' : 'text-white/70 group-hover:text-white'
                          }`}
                        />
                        <span className="transition group-hover:text-white">{label}</span>
                      </>
                    )}
                  </NavLink>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3 rounded-2xl bg-white/15 px-4 py-2 shadow-lg shadow-black/20 backdrop-blur">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-white/80 to-white/40 text-lg font-semibold text-indigo-600">
                  {userInitials}
                </div>
                <div className="hidden flex-col sm:flex">
                  <span className="text-sm font-medium text-white/90">{user.email}</span>
                  <span
                    className={`mt-1 inline-flex w-max items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold uppercase tracking-wide ${
                      isAdmin ? 'bg-purple-200/90 text-purple-700' : 'bg-emerald-200/90 text-emerald-700'
                    }`}
                  >
                    <User className="h-3 w-3" />
                    {user.role}
                  </span>
                </div>
              </div>

              <button
                onClick={() => logout()}
                className="group inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-4 py-2 text-sm font-semibold text-white shadow-md shadow-black/10 transition hover:border-white/60 hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/80"
              >
                <LogOut className="h-4 w-4 transition group-hover:translate-x-0.5" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
