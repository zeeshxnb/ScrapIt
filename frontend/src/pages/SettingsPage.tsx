import React, { useState } from 'react';
import {
  UserCircleIcon,
  BellIcon,
  ShieldCheckIcon,
  Cog6ToothIcon,
  TrashIcon,
  KeyIcon,
  GlobeAltIcon,
  MoonIcon,
  SunIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext.tsx';
import { useEmail } from '../contexts/EmailContext.tsx';
import toast from 'react-hot-toast';

const SettingsPage: React.FC = () => {
  const { user, logout } = useAuth();
  const { summary } = useEmail();
  
  // Settings state
  const [notifications, setNotifications] = useState({
    emailSync: true,
    spamDetection: true,
    weeklyReport: false,
    systemUpdates: true,
  });
  
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

  const handleSaveSettings = () => {
    // In a real app, this would save to the backend
    toast.success('Settings saved successfully!');
  };

  const handleDeleteAccount = () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      // In a real app, this would call the delete account API
      toast.error('Account deletion is not implemented in this demo');
    }
  };

  const handleExportData = () => {
    // In a real app, this would trigger a data export
    toast.success('Data export started. You\'ll receive an email when it\'s ready.');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Manage your account and application preferences</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Account Information */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <UserCircleIcon className="w-6 h-6 text-gray-600" />
              <h2 className="text-lg font-semibold text-gray-900">Account Information</h2>
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
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={user?.email || ''}
                    disabled
                    className="input bg-gray-50"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Account ID
                  </label>
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

          {/* Notification Settings */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <BellIcon className="w-6 h-6 text-gray-600" />
              <h2 className="text-lg font-semibold text-gray-900">Notifications</h2>
            </div>
            
            <div className="space-y-4">
              {Object.entries(notifications).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">
                      {key === 'emailSync' && 'Email Sync Notifications'}
                      {key === 'spamDetection' && 'Spam Detection Alerts'}
                      {key === 'weeklyReport' && 'Weekly Summary Report'}
                      {key === 'systemUpdates' && 'System Updates'}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {key === 'emailSync' && 'Get notified when emails are synced'}
                      {key === 'spamDetection' && 'Alerts when spam is detected'}
                      {key === 'weeklyReport' && 'Weekly email management summary'}
                      {key === 'systemUpdates' && 'Important system announcements'}
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={(e) => setNotifications(prev => ({
                        ...prev,
                        [key]: e.target.checked
                      }))}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Privacy Settings */}
          <div className="card">
            <div className="flex items-center space-x-3 mb-6">
              <ShieldCheckIcon className="w-6 h-6 text-gray-600" />
              <h2 className="text-lg font-semibold text-gray-900">Privacy & Security</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data Retention Period
                </label>
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
                  <h4 className="text-sm font-medium text-gray-900">Share Anonymous Analytics</h4>
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
                  <h4 className="text-sm font-medium text-gray-900">Email Content Preview</h4>
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
              <h2 className="text-lg font-semibold text-gray-900">Application Preferences</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Theme
                </label>
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
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Language
                </label>
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
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Timezone
                </label>
                <select
                  value={preferences.timezone}
                  onChange={(e) => setPreferences(prev => ({ ...prev, timezone: e.target.value }))}
                  className="input"
                >
                  <option value="auto">Auto-detect</option>
                  <option value="utc">UTC</option>
                  <option value="est">Eastern Time</option>
                  <option value="pst">Pacific Time</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Emails per page
                </label>
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
            <button onClick={handleSaveSettings} className="btn-primary">
              Save Settings
            </button>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Account Stats */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total Emails</span>
                <span className="text-sm font-medium">{summary?.total || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Spam Blocked</span>
                <span className="text-sm font-medium">{summary?.spam || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Categories</span>
                <span className="text-sm font-medium">{Object.keys(summary?.categories || {}).length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Time Saved</span>
                <span className="text-sm font-medium">12.5 hours</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <button
                onClick={handleExportData}
                className="w-full btn-secondary flex items-center justify-center space-x-2"
              >
                <GlobeAltIcon className="w-4 h-4" />
                <span>Export Data</span>
              </button>
              
              <button
                onClick={() => toast.info('Password change not implemented in demo')}
                className="w-full btn-secondary flex items-center justify-center space-x-2"
              >
                <KeyIcon className="w-4 h-4" />
                <span>Change Password</span>
              </button>
              
              <button
                onClick={logout}
                className="w-full btn-secondary flex items-center justify-center space-x-2"
              >
                <span>Sign Out</span>
              </button>
            </div>
          </div>

          {/* Danger Zone */}
          <div className="card border-red-200 bg-red-50">
            <h3 className="text-lg font-semibold text-red-900 mb-4">Danger Zone</h3>
            <div className="space-y-3">
              <p className="text-sm text-red-700">
                Once you delete your account, there is no going back. Please be certain.
              </p>
              <button
                onClick={handleDeleteAccount}
                className="w-full btn-danger flex items-center justify-center space-x-2"
              >
                <TrashIcon className="w-4 h-4" />
                <span>Delete Account</span>
              </button>
            </div>
          </div>

          {/* Support */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Support</h3>
            <div className="space-y-3">
              <a href="#" className="block text-sm text-primary-600 hover:text-primary-700">
                Help Center
              </a>
              <a href="#" className="block text-sm text-primary-600 hover:text-primary-700">
                Contact Support
              </a>
              <a href="#" className="block text-sm text-primary-600 hover:text-primary-700">
                Privacy Policy
              </a>
              <a href="#" className="block text-sm text-primary-600 hover:text-primary-700">
                Terms of Service
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;