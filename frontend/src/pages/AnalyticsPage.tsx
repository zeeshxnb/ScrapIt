import React, { useEffect, useState } from 'react';
import {
  ChartBarIcon,
  EnvelopeIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CalendarIcon,
} from '@heroicons/react/24/outline';
import { useEmail } from '../contexts/EmailContext.tsx';
import { analyticsApi } from '../services/api.ts';
import LoadingSpinner from '../components/LoadingSpinner.tsx';
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
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);

  useEffect(() => {
    console.log('🚀 AnalyticsPage mounted');
    fetchSummary();
    loadAnalyticsData();
  }, []);

  // Keep analytics in sync when global summary changes (e.g., after Dashboard actions)
  useEffect(() => {
    if (summary) {
      loadAnalyticsData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [summary]);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange]);

  const loadAnalyticsData = async () => {
    try {
      setLoadingAnalytics(true);
      console.log('🔄 Loading analytics data...');
      const days = timeRange === 'lifetime' ? 0 : timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : timeRange === '90d' ? 90 : 365;
      
      console.log(`📊 Fetching analytics for ${days} days`);
      const [overview, activity] = await Promise.all([
        analyticsApi.getOverview(days),
        analyticsApi.getActivity(10)
      ]);
      
      console.log('✅ Analytics data loaded:', { overview, activity });
      setAnalyticsData(overview);
      setRecentActivity(activity.activities || []);
    } catch (error) {
      console.error('❌ Failed to load analytics data:', error);
      console.error('Error details:', error.response?.data || error.message);
    } finally {
      setLoadingAnalytics(false);
    }
  };

  // Use real analytics data
  const categoryData = analyticsData?.categories || [];
  const displayCategories = React.useMemo(() => {
    const data = Array.isArray(categoryData) ? categoryData : [];
    const other = data.find((d: any) => d.name === 'Other');
    const top = data.filter((d: any) => d.name !== 'Other').slice(0, 8);
    if (other) top.push(other);
    return top;
  }, [categoryData]);
  const emailVolumeData = analyticsData?.time_series?.daily_volume || [];
  const senderData = analyticsData?.top_senders || [];

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

  const stats = [
    {
      name: 'Emails Received',
      value: analyticsData?.summary?.period_emails || 0,
      change: '',
      changeType: 'increase',
      icon: EnvelopeIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      name: 'Processed',
      value: analyticsData?.summary?.processed_emails || 0,
      change: '',
      changeType: 'increase',
      icon: ChartBarIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      name: 'Unprocessed',
      value: analyticsData?.summary?.unprocessed_emails || 0,
      change: '',
      changeType: 'decrease',
      icon: ClockIcon,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      name: 'Label Coverage',
      value: `${analyticsData?.summary?.label_coverage || 0}%`,
      change: '',
      changeType: 'increase',
      icon: CalendarIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
  ];

  if ((isLoading && !summary) || (loadingAnalytics && !analyticsData)) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Debug Info */}
      {loadingAnalytics && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-blue-800 text-sm">🔄 Loading analytics data...</p>
        </div>
      )}
      
      {!analyticsData && !loadingAnalytics && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <p className="text-yellow-800 text-sm">⚠️ No analytics data loaded. Check console for errors.</p>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600">Insights into your email patterns and management</p>
          <p className="text-xs text-gray-400">Last updated: {new Date().toLocaleTimeString()}</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={loadAnalyticsData}
            disabled={loadingAnalytics}
            className="btn btn-secondary"
          >
            {loadingAnalytics ? 'Loading...' : 'Refresh Analytics'}
          </button>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="input w-auto"
          >
             <option value="7d">Last 7 days</option>
             <option value="30d">Last 30 days</option>
             <option value="90d">Last 90 days</option>
             <option value="1y">Last year</option>
             <option value="lifetime">Lifetime</option>
          </select>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          const TrendIcon = stat.changeType === 'increase' ? ArrowTrendingUpIcon : ArrowTrendingDownIcon;
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

        {/* Category Distribution (readable horizontal bars) */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Email Categories</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={displayCategories} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={180} tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value) => [value as number, 'Emails']} />
                <Bar dataKey="value" fill="#3b82f6">
                  {displayCategories.map((entry: any, index: number) => (
                    <Cell key={`bar-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

        {/* Removed Top Senders */}

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Email Processing Stats */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Status</h3>
            <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Processed</span>
              <span className="text-sm font-medium">
                {analyticsData?.summary?.processed_emails || 0}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-600 h-2 rounded-full" 
                style={{ 
                  width: `${analyticsData?.summary?.processing_rate || 0}%`
                }}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Unprocessed</span>
              <span className="text-sm font-medium">{analyticsData?.summary?.unprocessed_emails || 0}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-yellow-600 h-2 rounded-full" 
                style={{ 
                  width: `${100 - (analyticsData?.summary?.processing_rate || 0)}%`
                }}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Spam Detected</span>
              <span className="text-sm font-medium">{analyticsData?.summary?.spam_emails || 0}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-red-600 h-2 rounded-full" 
                style={{ 
                  width: `${analyticsData?.summary?.spam_detection_rate || 0}%`
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
              <span className="text-sm font-medium">{analyticsData?.insights?.peak_email_hour || '9:00 AM'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Busiest Day</span>
              <span className="text-sm font-medium">{analyticsData?.insights?.busiest_day || 'Tuesday'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Avg Response Time</span>
              <span className="text-sm font-medium">{analyticsData?.insights?.avg_response_time || '2.3 hours'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Weekend Emails</span>
              <span className="text-sm font-medium">{analyticsData?.insights?.weekend_percentage || 12}%</span>
            </div>
          </div>
        </div>

        {/* Cleanup Efficiency */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cleanup Efficiency</h3>
          <div className="space-y-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-1">{analyticsData?.summary?.label_coverage || 0}%</div>
              <div className="text-sm text-gray-600">Label Coverage</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-1">{analyticsData?.summary?.processing_rate || 0}%</div>
              <div className="text-sm text-gray-600">Processed Rate</div>
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
          {recentActivity.length > 0 ? recentActivity.map((activity, index) => (
            <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className={`w-2 h-2 rounded-full ${
                activity.type === 'spam_deleted' ? 'bg-red-500' : 
                activity.type === 'classified' ? 'bg-green-500' : 'bg-blue-500'
              }`}></div>
              <span className="text-sm text-gray-900">{activity.description}</span>
              <span className="text-xs text-gray-500 ml-auto">{activity.time_ago}</span>
            </div>
          )) : (
            <div className="text-center py-8 text-gray-500">
              <p>No recent activity</p>
              <p className="text-sm">Process some emails to see activity here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;