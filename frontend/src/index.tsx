import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import {
  HomeIcon,
  EnvelopeIcon,
  ChatBubbleLeftRightIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  SparklesIcon,
  ArrowPathIcon,
  UserCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import './index.css';

// Mock data
const mockSummary = {
  total: 1247,
  spam: 23,
  unprocessed: 156,
  categories: { 
    work: 542, 
    personal: 324, 
    shopping: 198, 
    newsletters: 160,
    social: 23 
  },
  recent_senders: [
    { sender: 'john@company.com', count: 45 },
    { sender: 'newsletter@example.com', count: 32 },
    { sender: 'support@service.com', count: 28 }
  ],
  oldest_unread: {
    subject: 'Project Update - Q4 Progress',
    sender: 'john@company.com',
    received_date: '2024-01-15T10:30:00Z'
  }
};

// Simple Layout Component
function SimpleLayout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Emails', href: '/emails', icon: EnvelopeIcon, badge: mockSummary.total },
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
        <div className="p-4 border-t border-gray-200">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Total Emails</span>
              <span className="font-medium">{mockSummary.total}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-red-600">Spam</span>
              <span className="font-medium text-red-600">{mockSummary.spam}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-yellow-600">Unprocessed</span>
              <span className="font-medium text-yellow-600">{mockSummary.unprocessed}</span>
            </div>
          </div>
        </div>
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
}

// Dashboard Component
function Dashboard() {
  const stats = [
    {
      name: 'Total Emails',
      value: mockSummary.total,
      icon: EnvelopeIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      name: 'Spam Emails',
      value: mockSummary.spam,
      icon: ExclamationTriangleIcon,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      name: 'Unprocessed',
      value: mockSummary.unprocessed,
      icon: ClockIcon,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      name: 'Categories',
      value: Object.keys(mockSummary.categories).length,
      icon: ChartBarIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of your email management</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
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
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <button className="p-4 rounded-lg border-2 border-dashed border-red-200 hover:border-red-300 hover:bg-red-50 transition-all">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🗑️</span>
              <div className="text-left">
                <p className="font-medium text-gray-900">Delete {mockSummary.spam} Spam Emails</p>
                <p className="text-sm text-gray-500">Clean up spam</p>
              </div>
            </div>
          </button>
          <button className="p-4 rounded-lg border-2 border-dashed border-blue-200 hover:border-blue-300 hover:bg-blue-50 transition-all">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🤖</span>
              <div className="text-left">
                <p className="font-medium text-gray-900">Classify {mockSummary.unprocessed} Emails</p>
                <p className="text-sm text-gray-500">AI categorization</p>
              </div>
            </div>
          </button>
          <button className="p-4 rounded-lg border-2 border-dashed border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">🔄</span>
              <div className="text-left">
                <p className="font-medium text-gray-900">Sync Latest Emails</p>
                <p className="text-sm text-gray-500">Get new emails</p>
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Email Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Email Categories</h2>
          <div className="space-y-3">
            {Object.entries(mockSummary.categories).map(([category, count]) => (
              <div key={category} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="text-sm font-medium text-gray-900 capitalize">{category}</span>
                </div>
                <span className="text-sm text-gray-600">{count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Senders</h2>
          <div className="space-y-3">
            {mockSummary.recent_senders.map((sender, index) => (
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
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Simple placeholder components for other pages
function EmailsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Emails</h1>
        <p className="text-gray-600">Manage your email inbox</p>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <EnvelopeIcon className="w-12 h-12 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Email Management</h3>
        <p className="text-gray-600">Full email list with search, filters, and bulk actions would be here.</p>
      </div>
    </div>
  );
}

function ChatPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Assistant</h1>
        <p className="text-gray-600">Chat with your email management assistant</p>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <ChatBubbleLeftRightIcon className="w-12 h-12 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">AI Chat Interface</h3>
        <p className="text-gray-600">Natural language email management would be here.</p>
      </div>
    </div>
  );
}

function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600">Email insights and statistics</p>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <ChartBarIcon className="w-12 h-12 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Email Analytics</h3>
        <p className="text-gray-600">Charts, graphs, and insights would be here.</p>
      </div>
    </div>
  );
}

function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Manage your account and preferences</p>
      </div>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <Cog6ToothIcon className="w-12 h-12 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Account Settings</h3>
        <p className="text-gray-600">User preferences and configuration would be here.</p>
      </div>
    </div>
  );
}

function LoginPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 max-w-md w-full mx-4">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <SparklesIcon className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Welcome to ScrapIt</h1>
          <p className="text-gray-600">Sign in to start cleaning your inbox</p>
        </div>
        <Link
          to="/"
          className="w-full flex items-center justify-center space-x-3 px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <span className="text-gray-700 font-medium">Continue to Dashboard (Demo)</span>
        </Link>
      </div>
    </div>
  );
}

// Main App Component
function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<SimpleLayout><Dashboard /></SimpleLayout>} />
          <Route path="/emails" element={<SimpleLayout><EmailsPage /></SimpleLayout>} />
          <Route path="/chat" element={<SimpleLayout><ChatPage /></SimpleLayout>} />
          <Route path="/analytics" element={<SimpleLayout><AnalyticsPage /></SimpleLayout>} />
          <Route path="/settings" element={<SimpleLayout><SettingsPage /></SimpleLayout>} />
        </Routes>
      </div>
    </Router>
  );
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);