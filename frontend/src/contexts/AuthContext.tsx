import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthContextType } from '../types';
import { authApi } from '../services/api.ts';
import toast from 'react-hot-toast';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  const checkAuth = async () => {
    try {
      // Support OAuth redirect token directly
      const urlParams = new URLSearchParams(window.location.search);
      const tokenFromUrl = urlParams.get('token');
      if (tokenFromUrl) {
        localStorage.setItem('auth_token', tokenFromUrl);
        window.history.replaceState({}, document.title, window.location.pathname);
      }

      const token = localStorage.getItem('auth_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      const userData = await authApi.getCurrentUser();
      // Merge local profile names if saved in preferences
      try {
        const prefs = JSON.parse(localStorage.getItem('app_prefs') || '{}');
        const first = prefs?.profile?.firstName;
        const last = prefs?.profile?.lastName;
        const full = [first, last].filter(Boolean).join(' ').trim();
        setUser(full ? { ...userData, name: full } : userData);
      } catch {
        setUser(userData);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('auth_token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async () => {
    try {
      // Use the direct redirect endpoint instead of the JSON endpoint
      window.location.href = 'http://localhost:8000/auth/google-redirect';
    } catch (error) {
      console.error('Login failed:', error);
      toast.error('Failed to start login process');
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
      setUser(null);
      toast.success('Logged out successfully');
    } catch (error) {
      console.error('Logout failed:', error);
      // Still clear local state even if API call fails
      setUser(null);
      localStorage.removeItem('auth_token');
    }
  };

  useEffect(() => {
    // Handle OAuth callback first to avoid running checkAuth twice
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const error = urlParams.get('error');

    if (token) {
      localStorage.setItem('auth_token', token);
      // Clean URL quickly for faster mount and navigation
      window.history.replaceState({}, document.title, window.location.pathname);
      toast.success('Successfully logged in!');
    } else if (error) {
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
      console.error('OAuth error:', error);
      switch (error) {
        case 'access_denied':
          toast.error('Login cancelled. Please try again to access your Gmail.');
          break;
        case 'no_code':
          toast.error('Login failed. Please try again.');
          break;
        case 'auth_failed':
          toast.error('Authentication failed. Please check your internet connection and try again.');
          break;
        default:
          toast.error('Login failed. Please try again.');
      }
    }

    // Single auth check
    checkAuth();
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};