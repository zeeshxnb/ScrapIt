import React, { useEffect, useMemo, useState } from 'react';
import { ChartBarIcon, EnvelopeIcon, ClockIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, CalendarIcon } from '@heroicons/react/24/outline';
import { useEmail } from '../contexts/EmailContext.tsx';
import { analyticsApi } from '../services/api.ts';
import LoadingSpinner from '../components/LoadingSpinner.tsx';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Area, AreaChart } from 'recharts';
import { onPrefsChange, t } from '../i18n.ts';

const AnalyticsPage: React.FC = () => {
  const { summary, fetchSummary, isLoading } = useEmail();
  const [timeRange, setTimeRange] = useState('7d');
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);

  useEffect(() => {
    console.log('🚀 AnalyticsPage mounted');
    fetchSummary();
    loadAnalyticsData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // React to preference changes (language/timezone)
  useEffect(() => {
    const unsub = onPrefsChange(() => loadAnalyticsData());
    return unsub;
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timeRange]);

  const loadAnalyticsData = async () => {
    try {
      setLoadingAnalytics(true);
      console.log('🔄 Loading analytics data...');
      const days = timeRange === 'lifetime' ? 0 : timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : timeRange === '90d' ? 90 : 365;
      
      console.log(`📊 Fetching analytics for ${days} days`);
      const prefs = JSON.parse(localStorage.getItem('app_prefs') || '{}');
      const tzPref = prefs?.preferences?.timezone;
      const tzOffsetOverride = tzPref && tzPref !== 'auto' ? (
        tzPref === 'utc' ? 0 : tzPref === 'pst' ? 480 : tzPref === 'est' ? 300 : undefined
      ) : undefined;
      const overview = await analyticsApi.getOverview(days, tzOffsetOverride);
      
      console.log('✅ Analytics data loaded:', { overview });
      setAnalyticsData(overview);
    } catch (error) {
      console.error('❌ Failed to load analytics data:', error);
      console.error('Error details:', error.response?.data || error.message);
    } finally {
      setLoadingAnalytics(false);
    }
  };

  // Use real analytics data
  const displayCategories = useMemo(() => {
    const raw = analyticsData?.categories || [];
    const data = Array.isArray(raw) ? raw : [];
    const other = data.find((d: any) => d.name === 'Other');
    const top = data.filter((d: any) => d.name !== 'Other').slice(0, 8);
    if (other) top.push(other);
    return top;
  }, [analyticsData?.categories]);
  const emailVolumeData = analyticsData?.time_series?.daily_volume || [];
  // removed unused senderData

  const COLORS = ['#60a5fa', '#34d399', '#fbbf24', '#f87171', '#a78bfa', '#22d3ee'];

  const stats = [
    {
      name: t('analytics.emailsReceived') || 'Emails Received',
      value: analyticsData?.summary?.period_emails || 0,
      change: `${analyticsData?.summary?.period_change ?? 0}%`,
      changeType: (analyticsData?.summary?.period_change || 0) >= 0 ? 'increase' : 'decrease',
      icon: EnvelopeIcon,
      color: 'text-blue-600',
      darkColor: 'dark:text-blue-300',
      bgColor: 'bg-blue-50',
    },
    {
      name: t('analytics.processed'),
      value: analyticsData?.summary?.processed_emails || 0,
      change: `${analyticsData?.summary?.processed_change ?? 0}%`,
      changeType: (analyticsData?.summary?.processed_change || 0) >= 0 ? 'increase' : 'decrease',
      icon: ChartBarIcon,
      color: 'text-green-600',
      darkColor: 'dark:text-green-300',
      bgColor: 'bg-green-50',
    },
    {
      name: t('analytics.unprocessed'),
      value: analyticsData?.summary?.unprocessed_emails || 0,
      change: `${analyticsData?.summary?.unprocessed_change ?? 0}%`,
      changeType: (analyticsData?.summary?.unprocessed_change || 0) <= 0 ? 'decrease' : 'increase',
      icon: ClockIcon,
      color: 'text-yellow-600',
      darkColor: 'dark:text-yellow-300',
      bgColor: 'bg-yellow-50',
    },
    {
      name: t('analytics.labelCoverage'),
      value: `${analyticsData?.summary?.label_coverage || 0}%`,
      change: `${analyticsData?.summary?.label_coverage_change ?? 0}%`,
      changeType: (analyticsData?.summary?.label_coverage_change || 0) >= 0 ? 'increase' : 'decrease',
      icon: CalendarIcon,
      color: 'text-purple-600',
      darkColor: 'dark:text-purple-300',
      bgColor: 'bg-purple-50',
    },
  ];

  if (loadingAnalytics && !analyticsData) {
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
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 dark:bg-gray-800 dark:border-gray-700">
          <p className="text-blue-800 text-sm dark:text-gray-100">🔄 {t('analytics.loading')}</p>
        </div>
      )}
      
      {!analyticsData && !loadingAnalytics && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <p className="text-yellow-800 text-sm">⚠️ {t('analytics.noData')}</p>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{t('analytics.title')}</h1>
          <p className="text-gray-600 dark:text-gray-300">{t('analytics.subtitle')}</p>
          <p className="text-xs text-gray-400">{t('analytics.lastUpdated')}: {new Date().toLocaleTimeString()}</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={loadAnalyticsData}
            disabled={loadingAnalytics}
            className="btn btn-secondary"
          >
            {loadingAnalytics ? t('analytics.loading') : t('analytics.refresh')}
          </button>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="input w-auto"
          >
             <option value="7d">{t('analytics.range.7d')}</option>
             <option value="30d">{t('analytics.range.30d')}</option>
             <option value="90d">{t('analytics.range.90d')}</option>
             <option value="1y">{t('analytics.range.1y')}</option>
             <option value="lifetime">{t('analytics.range.lifetime')}</option>
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
                    <span className="text-sm text-gray-500 ml-1">{t('analytics.vsLastPeriod')}</span>
                  </div>
                </div>
                <div className={`p-3 rounded-lg ${stat.bgColor} dark:bg-gray-800 dark:border dark:border-gray-700`}>
                  <Icon className={`w-6 h-6 ${stat.color} ${stat.darkColor || ''}`} />
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
          <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('analytics.chart.volume')}</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={emailVolumeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={(value) => {
                    const prefs = JSON.parse(localStorage.getItem('app_prefs') || '{}');
                    const lang = prefs?.preferences?.language || 'en';
                    return new Date(value).toLocaleDateString(lang, { month: 'short', day: 'numeric' });
                  }}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  formatter={(value, name) => [value, name === 'emails' ? t('analytics.tooltip.emails') : t('analytics.tooltip.spam')]}
                  contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', color: '#F3F4F6' }}
                  itemStyle={{ color: '#93C5FD' }}
                  labelStyle={{ color: '#D1D5DB' }}
                  wrapperStyle={{ outline: 'none' }}
                />
                 <Area type="monotone" dataKey="emails" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Distribution (readable horizontal bars) */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('analytics.chart.categories')}</h3>
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
          <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('analytics.processing')}</h3>
            <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">{t('analytics.processed')}</span>
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
              <span className="text-sm text-gray-600">{t('analytics.unprocessed')}</span>
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
              <span className="text-sm text-gray-600">{t('analytics.spamDetected')}</span>
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
          <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('analytics.timeInsights')}</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">{t('analytics.peakHour')}</span>
              <span className="text-sm font-medium">{analyticsData?.insights?.peak_email_hour || '9:00 AM'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">{t('analytics.busiestDay')}</span>
              <span className="text-sm font-medium">{
                analyticsData?.insights?.busiest_day
                  ? t(`day.${String(analyticsData.insights.busiest_day).toLowerCase()}`)
                  : t('day.tuesday')
              }</span>
            </div>
            {/* Avg Response Time removed (not reliable without thread analysis) */}
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">{t('analytics.weekendEmails')}</span>
              <span className="text-sm font-medium">{analyticsData?.insights?.weekend_percentage || 12}%</span>
            </div>
          </div>
        </div>

        {/* Cleanup Efficiency */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('analytics.cleanup')}</h3>
          <div className="space-y-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-1">{analyticsData?.summary?.label_coverage || 0}%</div>
              <div className="text-sm text-gray-600">{t('analytics.labelCoverage')}</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-1">{analyticsData?.summary?.processing_rate || 0}%</div>
              <div className="text-sm text-gray-600">{t('analytics.processedRate')}</div>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-1">
                {Math.floor((analyticsData?.summary?.time_saved_seconds || 0) / 3600)}h {Math.floor(((analyticsData?.summary?.time_saved_seconds || 0) % 3600) / 60)}m
              </div>
              <div className="text-sm text-gray-600">{t('analytics.timeSaved')}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      {/* Recent Activity removed by request */}
    </div>
  );
};

export default AnalyticsPage;