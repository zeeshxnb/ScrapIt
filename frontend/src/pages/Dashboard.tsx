import React, { useEffect, useState } from 'react';
import {
  EnvelopeIcon,
  ExclamationTriangleIcon,
  SparklesIcon,
  TrashIcon,
  ChartBarIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import { useEmail } from '../contexts/EmailContext.tsx';
import { chatApi } from '../services/api.ts';
import LoadingSpinner from '../components/LoadingSpinner.tsx';
import { QuickAction } from '../types';

const Dashboard: React.FC = () => {
  const { summary, fetchSummary, classifyEmails, deleteSpamEmails, isLoading } = useEmail();
  const [quickActions, setQuickActions] = useState<QuickAction[]>([]);
  const [loadingActions, setLoadingActions] = useState(false);

  useEffect(() => {
    fetchSummary();
    loadQuickActions();
  }, []);

  const loadQuickActions = async () => {
    try {
      setLoadingActions(true);
      const response = await chatApi.getQuickActions();
      setQuickActions(response.actions || []);
    } catch (error) {
      console.error('Failed to load quick actions:', error);
    } finally {
      setLoadingActions(false);
    }
  };

  const handleQuickAction = async (actionId: string) => {
    switch (actionId) {
      case 'delete_spam':
        await deleteSpamEmails();
        break;
      case 'classify_emails':
        await classifyEmails();
        break;
      case 'sync_emails':
        // This is handled by the header sync button
        break;
      default:
        console.log('Unknown action:', actionId);
    }
    
    // Refresh data after action
    await Promise.all([fetchSummary(), loadQuickActions()]);
  };

  const stats = [
    {
      name: 'Total Emails',
      value: summary?.total || 0,
      icon: EnvelopeIcon,
      color: 'text-primary-600',
      bgColor: 'bg-primary-50',
    },
    {
      name: 'Spam Emails',
      value: summary?.spam || 0,
      icon: ExclamationTriangleIcon,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      name: 'Unprocessed',
      value: summary?.unprocessed || 0,
      icon: ClockIcon,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      name: 'Categories',
      value: Object.keys(summary?.categories || {}).length,
      icon: ChartBarIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
  ];

  if (isLoading && !summary) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of your email management</p>
        <p className="text-xs text-red-500">TEST: {new Date().toLocaleTimeString()}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
          {loadingActions && <LoadingSpinner size="small" />}
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickActions.map((action) => (
            <button
              key={action.id}
              onClick={() => handleQuickAction(action.id)}
              disabled={isLoading}
              className={`p-4 rounded-lg border-2 border-dashed transition-all hover:border-solid hover:shadow-md ${
                action.type === 'destructive'
                  ? 'border-red-200 hover:border-red-300 hover:bg-red-50'
                  : action.type === 'primary'
                  ? 'border-primary-200 hover:border-primary-300 hover:bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{action.icon}</span>
                <div className="text-left">
                  <p className="font-medium text-gray-900">{action.label}</p>
                  {action.count && (
                    <p className="text-sm text-gray-500">{action.count} items</p>
                  )}
                </div>
              </div>
            </button>
          ))}
          
          {quickActions.length === 0 && !loadingActions && (
            <div className="col-span-full text-center py-8 text-gray-500">
              <SparklesIcon className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>No quick actions available</p>
              <p className="text-sm">Sync your emails to see available actions</p>
            </div>
          )}
        </div>
      </div>

      {/* Email Categories */}
      {summary?.categories && Object.keys(summary.categories).length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Email Categories</h2>
            <div className="space-y-3">
              {Object.entries(summary.categories)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 5)
                .map(([category, count]) => (
                  <div key={category} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
                      <span className="text-sm font-medium text-gray-900 capitalize">
                        {category}
                      </span>
                    </div>
                    <span className="text-sm text-gray-600">{count}</span>
                  </div>
                ))}
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Senders</h2>
            <div className="space-y-3">
              {summary.recent_senders?.slice(0, 5).map((sender, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                      <span className="text-xs font-medium text-gray-600">
                        {sender.sender.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <span className="text-sm font-medium text-gray-900 truncate max-w-48">
                      {sender.sender}
                    </span>
                  </div>
                  <span className="text-sm text-gray-600">{sender.count}</span>
                </div>
              )) || (
                <p className="text-gray-500 text-sm">No sender data available</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Oldest Unread */}
      {summary?.oldest_unread && (
        <div className="card bg-yellow-50 border-yellow-200">
          <div className="flex items-start space-x-3">
            <ClockIcon className="w-5 h-5 text-yellow-600 mt-0.5" />
            <div>
              <h3 className="font-medium text-yellow-900">Oldest Unread Email</h3>
              <p className="text-sm text-yellow-800 mt-1">
                <strong>{summary.oldest_unread.subject}</strong> from {summary.oldest_unread.sender}
              </p>
              <p className="text-xs text-yellow-700 mt-1">
                Received: {new Date(summary.oldest_unread.received_date).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;