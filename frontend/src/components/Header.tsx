import React, { useState } from 'react';
import { 
  ArrowPathIcon,
  BellIcon,
  UserCircleIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext.tsx';
import { useEmail } from '../contexts/EmailContext.tsx';
import { onPrefsChange, t } from '../i18n.ts';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const { syncEmails, isLoading } = useEmail();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState<{ id: string; text: string; time: string }[]>([]);

  const handleSync = async () => {
    await syncEmails();
    window.dispatchEvent(new CustomEvent('app:notify', { detail: { text: 'Email sync completed' } }));
  };

  const displayName = React.useMemo(() => {
    if (user?.name) return user.name.split(' ')[0];
    if (!user?.email) return 'User';
    const local = user.email.split('@')[0];
    const parts = local.split(/[._-]/).filter(Boolean);
    if (parts.length >= 2) {
      return parts.map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(' ');
    }
    return local.charAt(0).toUpperCase() + local.slice(1);
  }, [user?.email, user?.name]);

  const [_langTick, setLangTick] = useState(0);
  const greeting = React.useMemo(() => {
    const hour = new Date().getHours();
    if (hour < 12) return t('greeting.morning');
    if (hour < 17) return t('greeting.afternoon');
    return t('greeting.evening');
  }, [_langTick]);

  React.useEffect(() => {
    const handler = (e: any) => {
      const text = e?.detail?.text || 'Action completed';
      setNotifications(prev => [{ id: String(Date.now()), text, time: new Date().toLocaleTimeString() }, ...prev].slice(0, 10));
    };
    window.addEventListener('app:notify' as any, handler as EventListener);
    const unsub = onPrefsChange(() => setLangTick(v => v + 1));
    return () => {
      window.removeEventListener('app:notify' as any, handler as EventListener);
      unsub();
    };
  }, []);

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 dark:bg-gray-900 dark:border-gray-800">
      <div className="flex items-center justify-between">
        {/* Left side - Page title will be handled by individual pages */}
        <div className="flex items-center space-x-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{greeting}, {displayName}</h2>
        </div>

        {/* Right side - Actions and user menu */}
        <div className="flex items-center space-x-4">
          {/* Sync button */}
          <button
            onClick={handleSync}
            disabled={isLoading}
            className="btn-secondary flex items-center space-x-2"
            title={t('header.sync')}
          >
            <ArrowPathIcon className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>{t('header.sync')}</span>
          </button>

          {/* Notifications */}
          <div className="relative">
            <button onClick={() => setShowNotifications(s => !s)} className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 dark:text-gray-300 dark:hover:text-gray-100 dark:hover:bg-gray-800">
              <BellIcon className="w-5 h-5" />
            </button>
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50 dark:bg-gray-900 dark:border-gray-700">
                <div className="px-4 py-2 border-b border-gray-100 flex items-center justify-between dark:border-gray-800">
                  <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">{t('header.notifications')}</span>
                  <button className="text-xs text-gray-500 dark:text-gray-400" onClick={() => setNotifications([])}>{t('header.notifications.clear')}</button>
                </div>
                <div className="max-h-80 overflow-auto">
                  {notifications.length === 0 ? (
                    <div className="px-4 py-6 text-sm text-gray-500 dark:text-gray-400">{t('header.notifications.none')}</div>
                  ) : notifications.map(n => (
                    <div key={n.id} className="px-4 py-2 text-sm">
                      <div className="text-gray-900 dark:text-gray-100">{n.text}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{n.time}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* User menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
            >
              <UserCircleIcon className="w-6 h-6 text-gray-400 dark:text-gray-300" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
                {user?.email?.split('@')[0]}
              </span>
              <ChevronDownIcon className="w-4 h-4 text-gray-400 dark:text-gray-300" />
            </button>

            {/* Dropdown menu */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50 dark:bg-gray-900 dark:border-gray-700">
                <div className="px-4 py-2 border-b border-gray-100 dark:border-gray-800">
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{user?.email}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{t('header.signedInWithGoogle')}</p>
                </div>
                
                <button
                  onClick={() => {
                    logout();
                    setShowUserMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-800"
                >
                  {t('header.signOut')}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Click outside to close menu */}
      {showUserMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowUserMenu(false)}
        />
      )}
    </header>
  );
};

export default Header;