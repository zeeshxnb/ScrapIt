import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  EnvelopeIcon,
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  SparklesIcon,
  ArrowPathIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import { useEmail } from './hooks';

interface SimpleLayoutProps {
  children: React.ReactNode;
}

const SimpleLayout: React.FC<SimpleLayoutProps> = ({ children }) => {
  const location = useLocation();
  const { summary } = useEmail();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Emails', href: '/emails', icon: EnvelopeIcon, badge: summary?.total || 0 },
    { name: 'AI Assistant', href: '/chat', icon: ChatBubbleLeftRightIcon },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-sm border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">ScrapIt</h1>
              <p className="text-xs text-gray-500">Email Cleaner</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className="w-5 h-5" />
                  <span>{item.name}</span>
                </div>
                
                {item.badge !== undefined && item.badge > 0 && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {item.badge > 999 ? '999+' : item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Quick Stats */}
        {summary && (
          <div className="p-4 border-t border-gray-200">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Total Emails</span>
                <span className="font-medium">{summary.total}</span>
              </div>
              {summary.spam > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-red-600">Spam</span>
                  <span className="font-medium text-red-600">{summary.spam}</span>
                </div>
              )}
              {summary.unprocessed > 0 && (
                <div className="flex justify-between text-sm">
                  <span className="text-yellow-600">Unprocessed</span>
                  <span className="font-medium text-yellow-600">{summary.unprocessed}</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h2 className="text-lg font-semibold text-gray-900">
                Welcome back, demo user
              </h2>
            </div>
            <div className="flex items-center space-x-4">
              <button className="flex items-center space-x-2 px-4 py-2 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 transition-colors">
                <ArrowPathIcon className="w-4 h-4" />
                <span>Sync</span>
              </button>
              <div className="flex items-center space-x-2">
                <UserCircleIcon className="w-6 h-6 text-gray-400" />
                <span className="text-sm font-medium text-gray-700">Demo User</span>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default SimpleLayout;