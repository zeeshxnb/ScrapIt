import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  HomeIcon,
  EnvelopeIcon,
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { useEmail } from '../contexts/EmailContext.tsx';
import { t, onPrefsChange } from '../i18n.ts';

const Sidebar: React.FC = () => {
  const { summary } = useEmail();

  const [_langVersion, setLangVersion] = React.useState(0);

  React.useEffect(() => {
    return onPrefsChange(() => setLangVersion((v) => v + 1));
  }, []);

  const navigation = [
    {
      name: t('nav.dashboard'),
      href: '/',
      icon: HomeIcon,
      current: false,
    },
    {
      name: t('nav.emails'),
      href: '/emails',
      icon: EnvelopeIcon,
      current: false,
      badge: summary?.total || 0,
    },
    {
      name: t('nav.chat'),
      href: '/chat',
      icon: ChatBubbleLeftRightIcon,
      current: false,
    },
    {
      name: t('nav.analytics'),
      href: '/analytics',
      icon: ChartBarIcon,
      current: false,
    },
    {
      name: t('nav.settings'),
      href: '/settings',
      icon: Cog6ToothIcon,
      current: false,
    },
  ];

  return (
    <div className="w-64 bg-white shadow-sm border-r border-gray-200 flex flex-col dark:bg-gray-900 dark:border-gray-800">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
            <SparklesIcon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-gray-100">ScrapIt</h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">Email Cleaner</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600 dark:bg-blue-900/30 dark:text-blue-300'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-gray-100'
                }`
              }
            >
              <div className="flex items-center space-x-3">
                <Icon className="w-5 h-5" />
                <span>{item.name}</span>
              </div>
              
              {item.badge !== undefined && item.badge > 0 && (
                <span className="badge-primary">
                  {item.badge > 999 ? '999+' : item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Quick Stats */}
      {summary && (
        <div className="p-4 border-t border-gray-200 dark:border-gray-800">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500 dark:text-gray-400">Total Emails</span>
              <span className="font-medium dark:text-gray-100">{summary.total}</span>
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
  );
};

export default Sidebar;