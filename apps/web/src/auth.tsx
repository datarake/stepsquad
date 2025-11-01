import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from './types';
import { apiClient } from './api';
import { 
  initFirebase, 
  firebaseSignIn, 
  firebaseSignUp, 
  firebaseSignOut,
  firebaseGetCurrentUser,
  firebaseGetIdToken
} from './firebase';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password?: string) => Promise<void>;
  logout: () => Promise<void>;
  isAdmin: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const USE_DEV_AUTH = import.meta.env.VITE_USE_DEV_AUTH === 'true';

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      console.log('Auth check started, USE_DEV_AUTH:', USE_DEV_AUTH);
      if (USE_DEV_AUTH) {
        const devEmail = localStorage.getItem('devEmail');
        console.log('Dev auth - devEmail:', devEmail);
        if (!devEmail) {
          setLoading(false);
          return;
        }
      } else {
        // Firebase: check if user is authenticated and refresh token
        const firebase = initFirebase();
        if (firebase) {
          const firebaseUser = await firebaseGetCurrentUser();
          if (firebaseUser) {
            // Refresh token
            const token = await firebaseGetIdToken();
            if (token) {
              localStorage.setItem('firebaseToken', token);
            }
          } else {
            // No Firebase user, clear token
            localStorage.removeItem('firebaseToken');
            setLoading(false);
            return;
          }
        } else {
          setLoading(false);
          return;
        }
      }

      console.log('Calling apiClient.getMe()...');
      const userData = await apiClient.getMe();
      console.log('User data received:', userData);
      setUser(userData);
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
    } finally {
      console.log('Auth check complete, setting loading to false');
      setLoading(false);
    }
  };

  const login = async (email: string, password?: string) => {
    if (USE_DEV_AUTH) {
      // Dev mode: just store email
      localStorage.setItem('devEmail', email);
      await checkAuth();
    } else {
      // Firebase authentication
      const firebase = initFirebase();
      if (!firebase) {
        throw new Error('Firebase not configured. Please set Firebase environment variables.');
      }

      if (!password) {
        throw new Error('Password is required for Firebase authentication');
      }

      try {
        // Sign in with Firebase
        const token = await firebaseSignIn(email, password);
        localStorage.setItem('firebaseToken', token);
        await checkAuth();
      } catch (error) {
        // If sign in fails, try to create account
        try {
          const token = await firebaseSignUp(email, password);
          localStorage.setItem('firebaseToken', token);
          await checkAuth();
        } catch (signUpError) {
          throw signUpError;
        }
      }
    }
  };

  const logout = async () => {
    if (!USE_DEV_AUTH) {
      // Firebase: sign out from Firebase
      await firebaseSignOut();
    }
    localStorage.removeItem('devEmail');
    localStorage.removeItem('firebaseToken');
    setUser(null);
  };

  const isAdmin = user?.role === 'ADMIN';

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, isAdmin }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
