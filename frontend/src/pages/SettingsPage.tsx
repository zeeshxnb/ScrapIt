import React, { useState } from 'react';
import { UserCircleIcon, ShieldCheckIcon, Cog6ToothIcon, TrashIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext.tsx';
import { useEmail } from '../contexts/EmailContext.tsx';
import toast from 'react-hot-toast';
import { setPrefs, t, onPrefsChange } from '../i18n.ts';

const SettingsPage: React.FC = () => {
  const { user, logout, checkAuth } = useAuth();
  useEmail();
  
  // Profile & Settings state
  const [profile, setProfile] = useState({ firstName: '', lastName: '' });
  const [privacy, setPrivacy] = useState({
    dataRetention: '1year',
    shareAnalytics: false,
    emailPreview: true,
  });
  
  const [preferences, setPreferences] = useState({
    theme: 'light',
    language: 'en',
    timezone: 'auto',
    emailsPerPage: 50,
  });

  React.useEffect(() => {
    try {
      const raw = localStorage.getItem('app_prefs');
      if (raw) {
        const data = JSON.parse(raw);
        if (data.profile) setProfile(data.profile);
        if (data.privacy) setPrivacy(data.privacy);
        if (data.preferences) setPreferences(data.preferences);
      }
    } catch {}
    const unsub = onPrefsChange(() => setRerenderKey(v => v + 1));
    return unsub;
  }, []);

  React.useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('dark');
    if (
      preferences.theme === 'dark' ||
      (preferences.theme === 'auto' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches)
    ) {
      root.classList.add('dark');
    }
  }, [preferences.theme]);

  const handleSaveSettings = () => {
    // Persist complete object for backward compatibility
    localStorage.setItem('app_prefs', JSON.stringify({ profile, privacy, preferences }));
    // Also emit granular preferences change for live updates
    setPrefs(preferences);
    window.dispatchEvent(new CustomEvent('app:notify', { detail: { text: 'Settings saved' } }));
    toast.success('Settings saved successfully!');
    checkAuth();
  };

  const [rerenderKey, setRerenderKey] = useState(0);

  const handleDeleteAccount = () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      // In a real app, this would call the delete account API
      toast.error('Account deletion is not implemented in this demo');
    }
  };

  return (
    <div className="space-y-6 text-gray-900 dark:text-gray-100">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{t('settings.title')}</h1>
        <p className="text-gray-600 dark:text-gray-300">{t('settings.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Account Information */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <UserCircleIcon className="w-6 h-6 text-gray-600 dark:text-gray-300" />
              <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{t('settings.accountInfo')}</h2>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
                  <span className="text-xl font-semibold text-primary-600">
                    {user?.email?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900">{user?.email}</h3>
                  <p className="text-sm text-gray-600">
                    Member since {new Date(user?.created_at || '').toLocaleDateString()}
                  </p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-gray-200">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.firstName')}</label>
                  <input type="text" value={profile.firstName} onChange={(e) => setProfile(p => ({ ...p, firstName: e.target.value }))} className="input" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.lastName')}</label>
                  <input type="text" value={profile.lastName} onChange={(e) => setProfile(p => ({ ...p, lastName: e.target.value }))} className="input" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.emailAddress')}</label>
                  <input
                    type="email"
                    value={user?.email || ''}
                    disabled
                    className="input bg-gray-50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.accountId')}</label>
                  <input
                    type="text"
                    value={user?.id || ''}
                    disabled
                    className="input bg-gray-50 font-mono text-sm"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Notifications removed */}

          {/* Privacy Settings */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <ShieldCheckIcon className="w-6 h-6 text-gray-600" />
              <h2 className="text-lg font-semibold text-gray-900">{t('settings.privacy')}</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">{t('settings.dataRetention')}</label>
                <select
                  value={privacy.dataRetention}
                  onChange={(e) => setPrivacy(prev => ({ ...prev, dataRetention: e.target.value }))}
                  className="input"
                >
                  <option value="3months">3 months</option>
                  <option value="6months">6 months</option>
                  <option value="1year">1 year</option>
                  <option value="2years">2 years</option>
                  <option value="forever">Keep forever</option>
                </select>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">{t('settings.shareAnalytics')}</h4>
                  <p className="text-sm text-gray-600">Help improve ScrapIt by sharing usage data</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={privacy.shareAnalytics}
                    onChange={(e) => setPrivacy(prev => ({ ...prev, shareAnalytics: e.target.checked }))}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">{t('settings.emailPreview')}</h4>
                  <p className="text-sm text-gray-600">Show email snippets in the interface</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={privacy.emailPreview}
                    onChange={(e) => setPrivacy(prev => ({ ...prev, emailPreview: e.target.checked }))}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
            </div>
          </div>

          {/* Application Preferences */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <Cog6ToothIcon className="w-6 h-6 text-gray-600" />
              <h2 className="text-lg font-semibold text-gray-900">{t('settings.appPrefs')}</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">{t('settings.theme')}</label>
                <select
                  value={preferences.theme}
                  onChange={(e) => setPreferences(prev => ({ ...prev, theme: e.target.value }))}
                  className="input"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                  <option value="auto">Auto (System)</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">{t('settings.language')}</label>
                <select
                  value={preferences.language}
                  onChange={(e) => setPreferences(prev => ({ ...prev, language: e.target.value }))}
                  className="input"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>
              
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">{t('settings.timezone')}</label>
                <select
                  value={preferences.timezone}
                  onChange={(e) => setPreferences(prev => ({ ...prev, timezone: e.target.value }))}
                  className="input"
                >
                    <option value="auto">Auto-detect</option>
                    <option value="utc">UTC</option>
                    <option value="est">US/Eastern</option>
                    <option value="pst">US/Pacific</option>
                  </select>
                </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">{t('settings.emailsPerPage')}</label>
                <select
                  value={preferences.emailsPerPage}
                  onChange={(e) => setPreferences(prev => ({ ...prev, emailsPerPage: parseInt(e.target.value) }))}
                  className="input"
                >
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                  <option value={100}>100</option>
                  <option value={200}>200</option>
                </select>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <button onClick={handleSaveSettings} className="btn-primary">{t('settings.save')}</button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Account Stats removed */}

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('settings.quickActions')}</h3>
            <div className="space-y-3">
              {/* Removed Export Data and Change Password */}
              
              <button
                onClick={logout}
                className="w-full btn-secondary flex items-center justify-center space-x-2"
              >
                <span>{t('settings.signOut')}</span>
              </button>
            </div>
          </div>

          {/* Danger Zone */}
          <div className="card border-red-200 bg-red-50">
            <h3 className="text-lg font-semibold text-red-900 mb-4">{t('settings.danger')}</h3>
            <div className="space-y-3">
              <p className="text-sm text-red-700">
                Once you delete your account, there is no going back. Please be certain.
              </p>
              <button
                onClick={handleDeleteAccount}
                className="w-full btn-danger flex items-center justify-center space-x-2"
              >
                <TrashIcon className="w-4 h-4" />
                <span>{t('settings.deleteAccount')}</span>
              </button>
            </div>
          </div>

          {/* Support */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('settings.support')}</h3>
            <div className="space-y-3">
              <a href="/privacy" className="block text-sm text-primary-600 hover:text-primary-700">{t('settings.privacyPolicy')}</a>
              <a href="/terms" className="block text-sm text-primary-600 hover:text-primary-700">{t('settings.terms')}</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;