/**
 * Login Component
 * 
 * React component for user authentication with Google OAuth
 */
import React, { useState, useCallback } from 'react';
import {
  Button,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Typography,
  Box,
  Container
} from '@mui/material';
import { Google as GoogleIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

// Props interface
interface LoginProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
  redirectTo?: string;
}

// Login state interface
interface LoginState {
  loading: boolean;
  error: string | null;
}

const Login: React.FC<LoginProps> = ({ 
  onSuccess, 
  onError, 
  redirectTo = '/dashboard' 
}) => {
  // State management
  const [state, setState] = useState<LoginState>({
    loading: false,
    error: null
  });

  // Hooks
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();

  /**
   * Handle Google OAuth login initiation
   */
  const handleGoogleLogin = useCallback(async (): Promise<void> => {
    // TODO: Implement Google login
    // Set loading state
    // Clear previous errors
    // Initiate OAuth flow
    // Handle success/error
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      // Call auth service to start OAuth flow
      // const result = await login();
      
      // Handle success
      // handleLoginSuccess(result);
      
    } catch (error) {
      handleLoginError(error as Error);
    }
  }, [login]);

  /**
   * Handle successful login
   */
  const handleLoginSuccess = useCallback((response: any): void => {
    // TODO: Implement success handling
    // Update loading state
    // Call onSuccess callback
    // Navigate to dashboard
    setState(prev => ({ ...prev, loading: false }));
    
    if (onSuccess) {
      onSuccess();
    }
    
    navigate(redirectTo);
  }, [onSuccess, navigate, redirectTo]);

  /**
   * Handle login error
   */
  const handleLoginError = useCallback((error: Error): void => {
    // TODO: Implement error handling
    // Update error state
    // Log error for debugging
    // Call onError callback
    const errorMessage = error.message || 'Login failed. Please try again.';
    
    setState(prev => ({ 
      ...prev, 
      loading: false, 
      error: errorMessage 
    }));
    
    if (onError) {
      onError(errorMessage);
    }
    
    console.error('Login error:', error);
  }, [onError]);

  /**
   * Clear error state
   */
  const clearError = useCallback((): void => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate(redirectTo);
    }
  }, [isAuthenticated, navigate, redirectTo]);

  return (
    <Container maxWidth="sm">
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
      >
        <Card elevation={3} sx={{ width: '100%', maxWidth: 400 }}>
          <CardContent sx={{ p: 4 }}>
            {/* Header */}
            <Box textAlign="center" mb={3}>
              <Typography variant="h4" component="h1" gutterBottom>
                Welcome to ScrapIt
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Sign in with your Google account to get started
              </Typography>
            </Box>

            {/* Error Alert */}
            {state.error && (
              <Alert 
                severity="error" 
                onClose={clearError}
                sx={{ mb: 2 }}
              >
                {state.error}
              </Alert>
            )}

            {/* Login Button */}
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={state.loading ? <CircularProgress size={20} /> : <GoogleIcon />}
              onClick={handleGoogleLogin}
              disabled={state.loading}
              sx={{ 
                py: 1.5,
                backgroundColor: '#4285f4',
                '&:hover': {
                  backgroundColor: '#3367d6'
                }
              }}
            >
              {state.loading ? 'Signing in...' : 'Sign in with Google'}
            </Button>

            {/* Terms and Privacy */}
            <Typography 
              variant="caption" 
              color="text.secondary" 
              textAlign="center"
              display="block"
              mt={2}
            >
              By signing in, you agree to our Terms of Service and Privacy Policy
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};

export default Login;