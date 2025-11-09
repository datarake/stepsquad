import React, { useMemo, useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from './auth';
import { LogOut, User, Activity, LayoutDashboard, Menu, X } from 'lucide-react';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const { user, logout, isAdmin } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

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
    <div className="min-h-screen bg-white">
      {/* Top Navigation */}
      <nav className="relative border-b border-blue-400/20 bg-gradient-to-r from-blue-500 via-blue-600 to-indigo-500">
        <div className="absolute inset-0 opacity-60">
          <div className="h-full w-full bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.25),_transparent_55%)]" />
        </div>
        <div className="relative">
          <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-4 sm:gap-8">
              {/* Mobile Menu Button - on the left, before logo */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="flex items-center justify-center rounded-lg p-2 text-white transition hover:bg-white/10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/70 sm:hidden"
                aria-label="Toggle menu"
              >
                {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>

              <Link to="/" className="group flex items-center text-2xl font-bold tracking-tight text-white transition hover:opacity-90">
                <span>StepSquad</span>
              </Link>

              {/* Desktop Navigation */}
              <div className="hidden items-center gap-1 rounded-full bg-white/10 p-1 text-sm font-medium text-white/80 shadow-inner shadow-black/20 backdrop-blur sm:flex">
                {navItems.map(({ to, label, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    end={to === '/'}
                    className={({ isActive }) =>
                      `group flex items-center gap-2 rounded-full px-4 py-2 transition-all duration-200 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/70 ${
                        isActive
                          ? 'bg-white/95 text-blue-600 shadow-sm shadow-black/10'
                          : 'text-white/80 hover:bg-white/10'
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <Icon
                          className={`h-4 w-4 transition ${
                            isActive ? 'text-blue-600' : 'text-white/70 group-hover:text-white'
                          }`}
                        />
                        <span className="transition group-hover:text-white">{label}</span>
                      </>
                    )}
                  </NavLink>
                ))}
              </div>
            </div>

            {/* Right side: User info and logout - hide logout on mobile */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3 rounded-2xl bg-white/15 px-4 py-2 shadow-lg shadow-black/20 backdrop-blur">
                {/* User avatar with tooltip on mobile */}
                <div className="relative group">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-white/80 to-white/40 text-lg font-semibold text-blue-600">
                    {userInitials}
                  </div>
                  {/* Tooltip - visible on mobile (sm:hidden) */}
                  <div className="absolute right-0 top-full mt-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none z-50 whitespace-nowrap sm:hidden">
                    {user.email}
                    <div className="absolute bottom-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                  </div>
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

              {/* Logout button - hidden on mobile, only visible in hamburger menu */}
              <button
                onClick={() => logout()}
                className="hidden sm:inline-flex items-center gap-2 rounded-full border border-white/30 bg-white/10 px-4 py-2 text-sm font-semibold text-white shadow-md shadow-black/10 transition hover:border-white/60 hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/80 group"
              >
                <LogOut className="h-4 w-4 transition group-hover:translate-x-0.5" />
                <span>Logout</span>
              </button>
            </div>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="border-t border-blue-400/20 bg-blue-600/95 backdrop-blur sm:hidden">
              <div className="mx-auto max-w-7xl px-4 py-4">
                <div className="flex flex-col gap-2">
                  {navItems.map(({ to, label, icon: Icon }) => (
                    <NavLink
                      key={to}
                      to={to}
                      end={to === '/'}
                      onClick={() => setMobileMenuOpen(false)}
                      className={({ isActive }) =>
                        `group flex items-center gap-3 rounded-lg px-4 py-3 text-base font-medium transition-all duration-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/70 ${
                          isActive
                            ? 'bg-white/95 text-blue-600 shadow-sm shadow-black/10'
                            : 'text-white/80 hover:bg-white/10 hover:text-white'
                        }`
                      }
                    >
                      {({ isActive }) => (
                        <>
                          <Icon
                            className={`h-5 w-5 transition ${
                              isActive ? 'text-blue-600' : 'text-white/70 group-hover:text-white'
                            }`}
                          />
                          <span>{label}</span>
                        </>
                      )}
                    </NavLink>
                  ))}
                  
                  {/* Separator */}
                  <div className="my-2 border-t border-blue-400/20"></div>
                  
                  {/* Logout Button */}
                  <button
                    onClick={() => {
                      setMobileMenuOpen(false);
                      logout();
                    }}
                    className="group flex items-center gap-3 rounded-lg px-4 py-3 text-base font-medium text-white/80 transition-all duration-200 hover:bg-white/10 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/70"
                  >
                    <LogOut className="h-5 w-5 text-white/70 transition group-hover:text-white" />
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
