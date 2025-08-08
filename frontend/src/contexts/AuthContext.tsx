import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthContextType } from '../types';
import { authApi } from '../services/api';
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
      const token = localStorage.getItem('auth_token');
      if (!token) {
        setIsLoading(false);
        return;
      }

      const userData = await authApi.getCurrentUser();
      setUser(userData);
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
    checkAuth();

    // Handle OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
      localStorage.setItem('auth_token', token);
      // Remove token from URL
      window.history.replaceState({}, document.title, window.location.pathname);
      checkAuth();
    }
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