import React, { useState } from 'react';
import { 
  ArrowPathIcon,
  BellIcon,
  UserCircleIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext.tsx';
import { useEmail } from '../contexts/EmailContext.tsx';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const { syncEmails, isLoading } = useEmail();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleSync = async () => {
    await syncEmails();
  };

  const displayName = React.useMemo(() => {
    if (!user?.email) return 'User';
    const local = user.email.split('@')[0];
    const parts = local.split(/[._-]/).filter(Boolean);
    if (parts.length >= 2) {
      return parts.map(p => p.charAt(0).toUpperCase() + p.slice(1)).join(' ');
    }
    return local.charAt(0).toUpperCase() + local.slice(1);
  }, [user?.email]);

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side - Page title will be handled by individual pages */}
        <div className="flex items-center space-x-4">
          <h2 className="text-lg font-semibold text-gray-900">Welcome back, {displayName}</h2>
        </div>

        {/* Right side - Actions and user menu */}
        <div className="flex items-center space-x-4">
          {/* Sync button */}
          <button
            onClick={handleSync}
            disabled={isLoading}
            className="btn-secondary flex items-center space-x-2"
            title="Sync emails from Gmail"
          >
            <ArrowPathIcon className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Sync</span>
          </button>

          {/* Notifications */}
          <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100">
            <BellIcon className="w-5 h-5" />
          </button>

          {/* User menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100"
            >
              <UserCircleIcon className="w-6 h-6 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">
                {user?.email?.split('@')[0]}
              </span>
              <ChevronDownIcon className="w-4 h-4 text-gray-400" />
            </button>

            {/* Dropdown menu */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                <div className="px-4 py-2 border-b border-gray-100">
                  <p className="text-sm font-medium text-gray-900">{user?.email}</p>
                  <p className="text-xs text-gray-500">Signed in with Google</p>
                </div>
                
                <button
                  onClick={() => {
                    logout();
                    setShowUserMenu(false);
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Sign out
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