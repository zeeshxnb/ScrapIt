import React, { useEffect, useState } from 'react';
import { EnvelopeIcon, ExclamationTriangleIcon, SparklesIcon, ChartBarIcon, ClockIcon } from '@heroicons/react/24/outline';
import { useEmail } from '../contexts/EmailContext.tsx';
import { chatApi } from '../services/api.ts';
import LoadingSpinner from '../components/LoadingSpinner.tsx';
import { QuickAction } from '../types';
import { t, onPrefsChange } from '../i18n.ts';

// Format sender names: map companies and derive person names
const formatSenderName = (email: string): string => {
  if (!email) return '';
  const lower = email.toLowerCase();
  const companyPatterns: Record<string, string> = {
    'morning-brew': 'Morning Brew',
    'morningbrew': 'Morning Brew',
    'newsletter@': 'Newsletter',
    'noreply@': 'System',
    'no-reply@': 'System',
    'support@': 'Support',
    'hello@': 'Team',
    'team@': 'Team',
    'info@': 'Info',
    'news@': 'News',
    'updates@': 'Updates',
  };
  for (const [pattern, name] of Object.entries(companyPatterns)) {
    if (lower.includes(pattern)) return name;
  }
  const atIndex = email.indexOf('@');
  const localPart = atIndex > 0 ? email.slice(0, atIndex) : email;
  // If local part has separators, treat as person name
  const parts = localPart.split(/[._-]/).filter(Boolean);
  const looksLikePerson = parts.length >= 2 && !/^(info|hello|contact|support|team|admin|sales|billing|no-?reply|newsletter)$/i.test(parts[0]);
  if (looksLikePerson) {
    return parts.map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(' ');
  }
  // Fallback to domain name title case
  const domain = atIndex > 0 ? email.slice(atIndex + 1) : '';
  const domainParts = domain.split('.');
  const domainName = domainParts.length > 1 ? domainParts[domainParts.length - 2] : domainParts[0] || localPart;
  return domainName.charAt(0).toUpperCase() + domainName.slice(1);
};

const Dashboard: React.FC = () => {
  const { summary, fetchSummary, classifyEmails, deleteSpamEmails, isLoading } = useEmail();
  const [quickActions, setQuickActions] = useState<QuickAction[]>([]);
  const [loadingActions, setLoadingActions] = useState(false);
  const [progressByAction, setProgressByAction] = useState<Record<string, number>>({});

  useEffect(() => {
    fetchSummary();
    loadQuickActions();
    const unsub = onPrefsChange(() => setLangTick((v) => v + 1));
    return unsub;
  }, [fetchSummary]);

  // Trigger re-render on language changes without keeping the tick
  useEffect(() => {
    const unsub = onPrefsChange(() => setRerenderKey((k) => k + 1));
    return unsub;
  }, []);
  const [rerenderKey, setRerenderKey] = useState(0);

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
    // Start progress at 0 and update via simple intervals; finalize on completion
    setProgressByAction(prev => ({ ...prev, [actionId]: 5 }));
    const interval = setInterval(() => {
      setProgressByAction(prev => ({ ...prev, [actionId]: Math.min((prev[actionId] || 0) + 8, 90) }));
    }, 300);
    switch (actionId) {
      case 'delete_spam':
        await deleteSpamEmails();
        window.dispatchEvent(new CustomEvent('app:notify', { detail: { text: 'Deleted spam emails' } }));
        break;
      case 'classify_emails':
        await classifyEmails();
        window.dispatchEvent(new CustomEvent('app:notify', { detail: { text: 'Classified emails' } }));
        break;
      case 'sync_emails':
        window.dispatchEvent(new CustomEvent('app:notify', { detail: { text: 'Starting email sync…' } }));
        // Call the actual sync; kept minimal UI log elsewhere
        await fetchSummary();
        break;
      case 'go_to_ai':
        window.location.href = '/chat';
        break;
      default:
        console.log('Unknown action:', actionId);
    }
    
    // Refresh data after action
    await Promise.all([fetchSummary(), loadQuickActions()]);
    clearInterval(interval);
    setProgressByAction(prev => ({ ...prev, [actionId]: 100 }));
    setTimeout(() => setProgressByAction(prev => ({ ...prev, [actionId]: 0 })), 800);
  };

  const stats = [
    {
      name: 'Total Emails',
      value: summary?.total || 0,
      icon: EnvelopeIcon,
      color: 'text-primary-600',
      darkColor: 'dark:text-blue-300',
      bgColor: 'bg-primary-50',
    },
    {
      name: 'Spam Emails',
      value: summary?.spam || 0,
      icon: ExclamationTriangleIcon,
      color: 'text-red-600',
      darkColor: 'dark:text-red-300',
      bgColor: 'bg-red-50',
    },
    {
      name: 'Unprocessed',
      value: summary?.unprocessed || 0,
      icon: ClockIcon,
      color: 'text-yellow-600',
      darkColor: 'dark:text-yellow-300',
      bgColor: 'bg-yellow-50',
    },
    {
      name: 'Categories',
      value: Object.keys(summary?.categories || {}).length,
      icon: ChartBarIcon,
      color: 'text-green-600',
      darkColor: 'dark:text-green-300',
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
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{t('dashboard.title')}</h1>
        <p className="text-gray-600 dark:text-gray-300">{t('dashboard.subtitle')}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.bgColor} dark:bg-gray-800 dark:border dark:border-gray-700`}>
                  <Icon className={`w-6 h-6 ${stat.color} ${stat.darkColor || ''}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-300">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stat.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{t('dashboard.quickActions')}</h2>
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
                  ? 'border-red-200 hover:border-red-300 hover:bg-red-50 dark:border-red-700 dark:hover:border-red-600 dark:hover:bg-red-900/30'
                  : action.type === 'primary'
                  ? 'border-primary-200 hover:border-primary-300 hover:bg-primary-50 dark:border-blue-700 dark:hover:border-blue-600 dark:hover:bg-blue-900/30'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50 dark:border-gray-700 dark:hover:border-gray-600 dark:hover:bg-gray-800'
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{action.icon}</span>
                <div className="text-left">
                  <p className="font-medium text-gray-900 dark:text-gray-100">{action.label}</p>
                  {action.count && (
                    <p className="text-sm text-gray-500 dark:text-gray-400">{action.count} items</p>
                  )}
                </div>
              </div>
              {/* Show progress bar only for actions that support it (not for go_to_ai) */}
              {action.id !== 'go_to_ai' && (progressByAction[action.id] || 0) > 0 && (
                <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden dark:bg-gray-700">
                  <div
                    className="h-2 bg-primary-600 transition-all dark:bg-blue-400"
                    style={{ width: `${progressByAction[action.id] || 0}%` }}
                  />
                </div>
              )}
            </button>
          ))}
          
          {quickActions.length === 0 && !loadingActions && (
            <div className="col-span-full text-center py-8 text-gray-500 dark:text-gray-400">
              <SparklesIcon className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>{t('dashboard.noActions')}</p>
              <p className="text-sm">{t('dashboard.noActionsHint')}</p>
            </div>
          )}
        </div>
      </div>

      {/* Top Senders and Email Categories (swapped order) */}
      {summary?.categories && Object.keys(summary.categories).length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Senders (left) */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Senders</h2>
            <div className="space-y-3">
              {summary.recent_senders?.slice(0, 5).map((sender, index) => {
                const displayName = formatSenderName(sender.sender);
                return (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center dark:bg-gray-700">
                        <span className="text-xs font-medium text-gray-600 dark:text-gray-200">
                          {displayName.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate max-w-48">
                        {displayName}
                      </span>
                    </div>
                    <span className="text-sm text-gray-600 dark:text-gray-300">{sender.count}</span>
                  </div>
                );
              }) || (
                <p className="text-gray-500 text-sm">No sender data available</p>
              )}
            </div>
          </div>

          {/* Email Categories (right) */}
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
        </div>
      )}

      {/* Oldest Unread removed */}
    </div>
  );
};

export default Dashboard;