import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './auth';
import { AppShell } from './AppShell';
import { LoginForm } from './LoginForm';
import { ProtectedRoute } from './ProtectedRoute';
import { HomePage } from './HomePage';
import { CompetitionDetailPage } from './CompetitionDetailPage';
import { CompetitionCreatePage } from './CompetitionCreatePage';
import { CompetitionEditPage } from './CompetitionEditPage';
import { KeyboardShortcuts } from './KeyboardShortcuts';
import { ErrorBoundary } from './ErrorBoundary';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function AppRoutes() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-sm text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <KeyboardShortcuts />
      <Routes>
        <Route
          path="/login"
          element={
            user ? <Navigate to="/" replace /> : <LoginForm />
          }
        />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppShell>
                <HomePage />
              </AppShell>
            </ProtectedRoute>
          }
        />
        <Route
          path="/competitions/:id"
          element={
            <ProtectedRoute>
              <AppShell>
                <CompetitionDetailPage />
              </AppShell>
            </ProtectedRoute>
          }
        />
        <Route
          path="/competitions/new"
          element={
            <ProtectedRoute adminOnly>
              <AppShell>
                <CompetitionCreatePage />
              </AppShell>
            </ProtectedRoute>
          }
        />
        <Route
          path="/competitions/:id/edit"
          element={
            <ProtectedRoute adminOnly>
              <AppShell>
                <CompetitionEditPage />
              </AppShell>
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <AppRoutes />
          <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
            },
            error: {
              duration: 5000,
            },
          }}
        />
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
