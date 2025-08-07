import React from 'react';
import { Navigate } from 'react-router-dom';
import { SparklesIcon, ShieldCheckIcon, BoltIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

const LoginPage: React.FC = () => {
  const { login, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const features = [
    {
      icon: SparklesIcon,
      title: 'AI-Powered Classification',
      description: 'Automatically categorize your emails using advanced AI technology'
    },
    {
      icon: ShieldCheckIcon,
      title: 'Smart Spam Detection',
      description: 'Identify and remove spam emails with high accuracy'
    },
    {
      icon: BoltIcon,
      title: 'Bulk Operations',
      description: 'Clean up thousands of emails with just a few clicks'
    },
    {
      icon: ChatBubbleLeftRightIcon,
      title: 'Natural Language Chat',
      description: 'Manage your emails by simply talking to our AI assistant'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50">
      <div className="min-h-screen flex">
        {/* Left side - Features */}
        <div className="hidden lg:flex lg:w-1/2 flex-col justify-center px-12">
          <div className="max-w-md">
            <div className="flex items-center space-x-3 mb-8">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                <SparklesIcon className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">ScrapIt</h1>
                <p className="text-gray-600">AI-Powered Email Cleaner</p>
              </div>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Clean your inbox in minutes, not hours
            </h2>

            <div className="space-y-6">
              {features.map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <div key={index} className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Icon className="w-5 h-5 text-primary-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">{feature.title}</h3>
                      <p className="text-gray-600 text-sm">{feature.description}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right side - Login */}
        <div className="w-full lg:w-1/2 flex flex-col justify-center px-8 lg:px-12">
          <div className="max-w-md mx-auto w-full">
            {/* Mobile logo */}
            <div className="lg:hidden flex items-center justify-center space-x-3 mb-8">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <SparklesIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">ScrapIt</h1>
              </div>
            </div>

            <div className="card">
              <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Welcome to ScrapIt
                </h2>
                <p className="text-gray-600">
                  Sign in with your Google account to start cleaning your inbox
                </p>
              </div>

              <button
                onClick={login}
                className="w-full flex items-center justify-center space-x-3 px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                <span className="text-gray-700 font-medium">Continue with Google</span>
              </button>

              <div className="mt-6 text-center">
                <p className="text-xs text-gray-500">
                  By signing in, you agree to our Terms of Service and Privacy Policy.
                  We'll only access your Gmail to help you clean and organize your emails.
                </p>
              </div>
            </div>

            {/* Mobile features */}
            <div className="lg:hidden mt-8 space-y-4">
              {features.slice(0, 2).map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <div key={index} className="flex items-center space-x-3 text-sm">
                    <Icon className="w-5 h-5 text-primary-600" />
                    <span className="text-gray-600">{feature.title}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;