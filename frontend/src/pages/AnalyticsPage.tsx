import React, { useEffect, useState } from 'react';
import {
  ChartBarIcon,
  EnvelopeIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';
import { useEmail } from '../contexts/EmailContext';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart,
} from 'recharts';

const AnalyticsPage: React.FC = () => {
  const { summary, fetchSummary, isLoading } = useEmail();
  const [timeRange, setTimeRange] = useState('7d');

  useEffect(() => {
    fetchSummary();
  }, []);

  // Mock data for charts (in real app, this would come from API)
  const categoryData = summary?.categories ? 
    Object.entries(summary.categories).map(([name, value]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      value,
      percentage: Math.round((value / summary.total) * 100)
    })) : [];

  const emailVolumeData = [
    { date: '2024-01-01', emails: 45, spam: 3 },
    { date: '2024-01-02', emails: 52, spam: 5 },
    { date: '2024-01-03', emails: 38, spam: 2 },
    { date: '2024-01-04', emails: 61, spam: 8 },
    { date: '2024-01-05', emails: 43, spam: 4 },
    { date: '2024-01-06', emails: 29, spam: 1 },
    { date: '2024-01-07', emails: 67, spam: 6 },
  ];

  const senderData = summary?.recent_senders?.slice(0, 10).map(sender => ({
    name: sender.sender.length > 20 ? sender.sender.substring(0, 20) + '...' : sender.sender,
    emails: sender.count
  })) || [];

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

  const stats = [
    {
      name: 'Total Emails',
      value: summary?.total || 0,
      change: '+12%',
      changeType: 'increase',
      icon: EnvelopeIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      name: 'Spam Detected',
      value: summary?.spam || 0,
      change: '-8%',
      changeType: 'decrease',
      icon: ExclamationTriangleIcon,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      name: 'Processing Rate',
      value: summary ? `${Math.round(((summary.total - summary.unprocessed) / summary.total) * 100)}%` : '0%',
      change: '+5%',
      changeType: 'increase',
      icon: ChartBarIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      name: 'Avg Daily Emails',
      value: Math.round((summary?.total || 0) / 30),
      change: '+3%',
      changeType: 'increase',
      icon: CalendarIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600">Insights into your email patterns and management</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="input w-auto"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          const TrendIcon = stat.changeType === 'increase' ? TrendingUpIcon : TrendingDownIcon;
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  <div className="flex items-center mt-2">
                    <TrendIcon className={`w-4 h-4 ${
                      stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                    }`} />
                    <span className={`text-sm font-medium ml-1 ${
                      stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stat.change}
                    </span>
                    <span className="text-sm text-gray-500 ml-1">vs last period</span>
                  </div>
                </div>
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Email Volume Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Email Volume Over Time</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={emailVolumeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  formatter={(value, name) => [value, name === 'emails' ? 'Total Emails' : 'Spam Emails']}
                />
                <Area type="monotone" dataKey="emails" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                <Area type="monotone" dataKey="spam" stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.8} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Email Categories</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name} (${percentage}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [value, 'Emails']} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top Senders Chart */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Email Senders</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={senderData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={150} />
              <Tooltip formatter={(value) => [value, 'Emails']} />
              <Bar dataKey="emails" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Email Processing Stats */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Status</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Processed</span>
              <span className="text-sm font-medium">
                {summary ? summary.total - summary.unprocessed : 0}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-600 h-2 rounded-full" 
                style={{ 
                  width: summary ? `${((summary.total - summary.unprocessed) / summary.total) * 100}%` : '0%' 
                }}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Unprocessed</span>
              <span className="text-sm font-medium">{summary?.unprocessed || 0}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-yellow-600 h-2 rounded-full" 
                style={{ 
                  width: summary ? `${(summary.unprocessed / summary.total) * 100}%` : '0%' 
                }}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Spam Detected</span>
              <span className="text-sm font-medium">{summary?.spam || 0}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-red-600 h-2 rounded-full" 
                style={{ 
                  width: summary ? `${(summary.spam / summary.total) * 100}%` : '0%' 
                }}
              />
            </div>
          </div>
        </div>

        {/* Time-based Insights */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Time Insights</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Peak Email Hour</span>
              <span className="text-sm font-medium">9:00 AM</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Busiest Day</span>
              <span className="text-sm font-medium">Tuesday</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Avg Response Time</span>
              <span className="text-sm font-medium">2.3 hours</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Weekend Emails</span>
              <span className="text-sm font-medium">12%</span>
            </div>
          </div>
        </div>

        {/* Cleanup Efficiency */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cleanup Efficiency</h3>
          <div className="space-y-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-1">94%</div>
              <div className="text-sm text-gray-600">Spam Detection Accuracy</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-1">87%</div>
              <div className="text-sm text-gray-600">Classification Accuracy</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-1">2.5h</div>
              <div className="text-sm text-gray-600">Time Saved This Week</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-900">Classified 45 emails as "Work"</span>
            <span className="text-xs text-gray-500 ml-auto">2 hours ago</span>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <span className="text-sm text-gray-900">Deleted 12 spam emails</span>
            <span className="text-xs text-gray-500 ml-auto">4 hours ago</span>
          </div>
          <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-sm text-gray-900">Synced 67 new emails from Gmail</span>
            <span className="text-xs text-gray-500 ml-auto">6 hours ago</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;