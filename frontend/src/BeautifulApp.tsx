import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Simple auth hook that works with our OAuth
function useAuth() {
  const [user, setUser] = React.useState(null);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    // Check if we have a token in the URL (from OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
      console.log('✅ Token received from OAuth callback');
      localStorage.setItem('auth_token', token);
      // Clean up URL without refreshing the page
      window.history.replaceState({}, document.title, window.location.pathname);
      fetchUserInfo(token);
    } else {
      const storedToken = localStorage.getItem('auth_token');
      if (storedToken) {
        console.log('🔑 Using stored token');
        fetchUserInfo(storedToken);
      } else {
        console.log('❌ No token found');
        setIsLoading(false);
      }
    }
  }, []);

  const fetchUserInfo = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const userData = await response.json();
        console.log('✅ User authenticated:', userData.email);
        setUser(userData);
      } else {
        console.log('❌ Token invalid, removing');
        localStorage.removeItem('auth_token');
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      localStorage.removeItem('auth_token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = () => {
    console.log('🔐 Starting OAuth flow');
    window.location.href = 'http://localhost:8000/auth/google-redirect';
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
  };

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout
  };
}

// Simple Login Page Component
function LoginPage() {
  const handleLogin = () => {
    console.log('🔐 Starting OAuth flow');
    window.location.href = 'http://localhost:8000/auth/google-redirect';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">ScrapIt</h1>
          <p className="text-gray-600 mb-8">AI-powered email cleaning and organization</p>
          
          <div className="mb-6">
            <svg className="mx-auto h-16 w-16 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          
          <button
            onClick={handleLogin}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition duration-200 flex items-center justify-center space-x-2"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            <span>Continue with Gmail</span>
          </button>
          
          <p className="text-sm text-gray-500 mt-4">
            We'll access your Gmail to help organize and clean your inbox
          </p>
        </div>
      </div>
    </div>
  );
}


// Beautiful Dashboard with Sidebar
function Dashboard() {
  const [summary, setSummary] = React.useState(null);
  const [, setIsLoading] = React.useState(false);
  const [loadingActions, setLoadingActions] = React.useState({});

  const fetchSummary = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('auth_token');
      
      // Get both Gmail stats and chat summary
      const [gmailResponse, chatResponse] = await Promise.all([
        fetch('http://localhost:8000/gmail/stats', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('http://localhost:8000/chat/summary', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);
      
      if (gmailResponse.ok && chatResponse.ok) {
        const gmailData = await gmailResponse.json();
        const chatData = await chatResponse.json();
        
        // Combine the data with Gmail stats taking priority for email counts
        setSummary({
          ...chatData,
          total_emails: gmailData.local_stats.total_emails,
          gmail_total: gmailData.gmail_stats.total_emails,
          sync_coverage: gmailData.gmail_stats.sync_coverage,
          spam_emails: gmailData.local_stats.spam_emails,
          unprocessed_emails: gmailData.local_stats.unprocessed_emails,
          folder_breakdown: gmailData.gmail_stats.folder_breakdown,
          is_connected: gmailData.sync_status.is_connected,
          needs_sync: gmailData.sync_status.needs_sync
        });
      } else if (gmailResponse.ok) {
        // Fallback to just Gmail stats
        const gmailData = await gmailResponse.json();
        setSummary({
          total_emails: gmailData.local_stats.total_emails,
          gmail_total: gmailData.gmail_stats.total_emails,
          sync_coverage: gmailData.gmail_stats.sync_coverage,
          spam_emails: gmailData.local_stats.spam_emails,
          unprocessed_emails: gmailData.local_stats.unprocessed_emails,
          folder_breakdown: gmailData.gmail_stats.folder_breakdown
        });
      }
    } catch (error) {
      console.error('Failed to fetch summary:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const syncAndRefresh = async () => {
    setLoadingActions(prev => ({ ...prev, sync: true }));
    
    // Start the API call
    const apiCall = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        
        // First sync emails - FULL SYNC to get ALL emails
        const syncResponse = await fetch('http://localhost:8000/gmail/sync', {
          method: 'POST',
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            incremental: false,  // Full sync
            max_results: null,   // No limits
            batch_size: 100,
            force_refresh: true  // Force fresh data from Gmail
          })
        });
        
        if (syncResponse.ok) {
          // Then refresh summary
          await fetchSummary();
        } else {
          console.error('Error syncing emails');
        }
      } catch (error) {
        console.error('Error syncing emails:', error);
      }
    };
    
    // Always wait at least 1 second for the animation to complete
    await Promise.all([
      apiCall(),
      new Promise(resolve => setTimeout(resolve, 1000))
    ]);
    
    setLoadingActions(prev => ({ ...prev, sync: false }));
  };

  const classifyEmails = async () => {
    setLoadingActions(prev => ({ ...prev, classify: true }));
    
    // Start the API call
    const apiCall = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch('http://localhost:8000/ai/classify', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
          await response.json(); // Get response but don't store unused data
          // No popup - just refresh data
          await fetchSummary();
        } else {
          console.error('Error classifying emails');
        }
      } catch (error) {
        console.error('Error classifying emails:', error);
      }
    };
    
    // Always wait at least 1 second for the animation to complete
    await Promise.all([
      apiCall(),
      new Promise(resolve => setTimeout(resolve, 1000))
    ]);
    
    setLoadingActions(prev => ({ ...prev, classify: false }));
  };

  const deleteSpam = async () => {
    setLoadingActions(prev => ({ ...prev, spam: true }));
    
    // Start the API call
    const apiCall = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch('http://localhost:8000/ai/spam', {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
          await response.json(); // Get response but don't store unused data
          // No popup - just refresh data
          await fetchSummary();
        } else {
          console.error('Error deleting spam emails');
        }
      } catch (error) {
        console.error('Error deleting spam:', error);
      }
    };
    
    // Always wait at least 1 second for the animation to complete
    await Promise.all([
      apiCall(),
      new Promise(resolve => setTimeout(resolve, 1000))
    ]);
    
    setLoadingActions(prev => ({ ...prev, spam: false }));
  };



  // Helper function to format sender names
  const formatSenderName = (email) => {
    // Company/Newsletter patterns
    const companyPatterns = {
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
      'updates@': 'Updates'
    };

    const emailLower = email.toLowerCase();
    
    // Check for company patterns
    for (const [pattern, name] of Object.entries(companyPatterns)) {
      if (emailLower.includes(pattern)) {
        return name;
      }
    }

    // Extract domain and make it readable
    const domain = email.split('@')[1];
    if (domain) {
      const domainName = domain.split('.')[0];
      // Capitalize first letter
      return domainName.charAt(0).toUpperCase() + domainName.slice(1);
    }

    // If it looks like a personal email (has name before @)
    const localPart = email.split('@')[0];
    if (localPart && !localPart.includes('noreply') && !localPart.includes('no-reply')) {
      // Try to extract name from email
      const nameParts = localPart.split(/[._-]/);
      if (nameParts.length >= 2) {
        return nameParts.map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(' ');
      }
    }

    // Fallback to email
    return email;
  };

  React.useEffect(() => {
    fetchSummary();
  }, []);

  const stats = [
    {
      name: 'Total Emails',
      value: summary?.total || 0,
      icon: '📧',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      name: 'Spam Emails',
      value: summary?.spam || 0,
      icon: '🚫',
      color: 'text-red-600',
      bgColor: 'bg-red-50',
    },
    {
      name: 'Unprocessed',
      value: summary?.unprocessed || 0,
      icon: '⏳',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50',
    },
    {
      name: 'Categories',
      value: Object.keys(summary?.categories || {}).length,
      icon: '📂',
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
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <span className="text-2xl">{stat.icon}</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <button 
            onClick={syncAndRefresh}
            disabled={loadingActions.sync}
            className="relative p-4 rounded-lg border-2 border-dashed border-blue-200 hover:border-blue-300 hover:bg-blue-50 transition-all disabled:opacity-50 overflow-hidden"
          >
            {loadingActions.sync && (
              <div className="absolute inset-0 rounded-lg">
                <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                  <rect 
                    x="1" y="1" width="98" height="98" 
                    fill="none" 
                    stroke="#3b82f6" 
                    strokeWidth="2" 
                    strokeDasharray="392" 
                    strokeDashoffset="392"
                    rx="8"
                    className="animate-[snake_1s_ease-in-out_infinite]"
                  />
                </svg>
              </div>
            )}
            <div className="flex items-center space-x-3 relative z-10">
              <span className="text-2xl">🔄</span>
              <div className="text-left">
                <p className="font-medium text-gray-900">Sync & Refresh</p>
                <p className="text-sm text-gray-500">Get latest emails & stats</p>
              </div>
            </div>
          </button>
          
          <button 
            onClick={classifyEmails}
            disabled={loadingActions.classify}
            className="relative p-4 rounded-lg border-2 border-dashed border-green-200 hover:border-green-300 hover:bg-green-50 transition-all disabled:opacity-50 overflow-hidden"
          >
            {loadingActions.classify && (
              <div className="absolute inset-0 rounded-lg">
                <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                  <rect 
                    x="1" y="1" width="98" height="98" 
                    fill="none" 
                    stroke="#10b981" 
                    strokeWidth="2" 
                    strokeDasharray="392" 
                    strokeDashoffset="392"
                    rx="8"
                    className="animate-[snake_1s_ease-in-out_infinite]"
                  />
                </svg>
              </div>
            )}
            <div className="flex items-center space-x-3 relative z-10">
              <span className="text-2xl">🤖</span>
              <div className="text-left">
                <p className="font-medium text-gray-900">Classify Emails</p>
                <p className="text-sm text-gray-500">AI categorization</p>
              </div>
            </div>
          </button>
          
          <button 
            onClick={deleteSpam}
            disabled={loadingActions.spam}
            className="relative p-4 rounded-lg border-2 border-dashed border-red-200 hover:border-red-300 hover:bg-red-50 transition-all disabled:opacity-50 overflow-hidden"
          >
            {loadingActions.spam && (
              <div className="absolute inset-0 rounded-lg">
                <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                  <rect 
                    x="1" y="1" width="98" height="98" 
                    fill="none" 
                    stroke="#ef4444" 
                    strokeWidth="2" 
                    strokeDasharray="392" 
                    strokeDashoffset="392"
                    rx="8"
                    className="animate-[snake_1s_ease-in-out_infinite]"
                  />
                </svg>
              </div>
            )}
            <div className="flex items-center space-x-3 relative z-10">
              <span className="text-2xl">🗑️</span>
              <div className="text-left">
                <p className="font-medium text-gray-900">Delete Spam</p>
                <p className="text-sm text-gray-500">Clean up spam</p>
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Top Senders and Email Categories - Swapped sides */}
      {(summary?.categories && Object.keys(summary.categories).length > 0) || (summary?.recent_senders && summary.recent_senders.length > 0) ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Senders - Now on the left */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Top Senders</h2>
            <div className="space-y-3">
              {summary?.recent_senders?.slice(0, 5).map((sender, index) => {
                const displayName = formatSenderName(sender.sender);
                return (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                        <span className="text-xs font-medium text-gray-600">
                          {displayName.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <span className="text-sm font-medium text-gray-900 truncate max-w-48">
                        {displayName}
                      </span>
                    </div>
                    <span className="text-sm text-gray-600">{sender.count}</span>
                  </div>
                );
              }) || (
                <p className="text-gray-500 text-sm">No sender data available</p>
              )}
            </div>
          </div>

          {/* Email Categories - Now on the right */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Email Categories</h2>
            <div className="space-y-3">
              {summary?.categories && Object.keys(summary.categories).length > 0 ? (
                Object.entries(summary.categories)
                  .filter(([category]) => category && category !== 'unknown' && category !== 'null')
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 5)
                  .map(([category, count]) => (
                    <div key={category} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                        <span className="text-sm font-medium text-gray-900 capitalize">
                          {category === 'work' ? 'Work' : 
                           category === 'personal' ? 'Personal' :
                           category === 'shopping' ? 'Shopping' :
                           category === 'newsletters' ? 'Newsletters' :
                           category === 'social' ? 'Social' :
                           category === 'promotional' ? 'Promotional' :
                           category}
                        </span>
                      </div>
                      <span className="text-sm text-gray-600">{count}</span>
                    </div>
                  ))
              ) : (
                <p className="text-gray-500 text-sm">No categories available. Try classifying your emails first!</p>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

// Simple Emails Page - Commented out for now
/*
function EmailsPage() {
  const [emails, setEmails] = React.useState([]);
  const [loading, setLoading] = React.useState(false);

  const fetchEmails = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('auth_token');
      const response = await fetch('http://localhost:8000/gmail/emails', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        const data = await response.json();
        setEmails(data.emails || []);
      }
    } catch (error) {
      console.error('Failed to fetch emails:', error);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchEmails();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Emails</h1>
          <p className="text-gray-600">Manage your email inbox</p>
        </div>
        <button 
          onClick={fetchEmails}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-2">Loading emails...</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          {emails.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {emails.slice(0, 20).map((email, index) => (
                <div key={index} className="p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="font-medium text-gray-900">{email.sender}</span>
                        {email.is_spam && (
                          <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">Spam</span>
                        )}
                        {email.category && (
                          <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full capitalize">
                            {email.category}
                          </span>
                        )}
                      </div>
                      <h3 className="font-medium text-gray-900 mb-1">{email.subject}</h3>
                      <p className="text-sm text-gray-600 line-clamp-2">{email.snippet}</p>
                    </div>
                    <div className="text-sm text-gray-500 ml-4">
                      {email.received_date ? new Date(email.received_date).toLocaleDateString() : 'No date'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📧</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No emails found</h3>
              <p className="text-gray-600">Sync your Gmail to see your emails here</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
*/

// Simple Chat Page
function ChatPage() {
  const [messages, setMessages] = React.useState([]);
  const [input, setInput] = React.useState('');
  const [loading, setLoading] = React.useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { text: input, isUser: true, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('http://localhost:8000/chat/chat', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: input })
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage = { text: data.response, isUser: false, timestamp: new Date() };
        setMessages(prev => [...prev, aiMessage]);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage = { text: 'Sorry, I encountered an error. Please try again.', isUser: false, timestamp: new Date() };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Assistant</h1>
        <p className="text-gray-600">Chat with your email management assistant</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 h-96 flex flex-col">
        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-6xl mb-4">🤖</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">AI Assistant Ready</h3>
              <p className="text-gray-600">Ask me anything about your emails!</p>
              <div className="mt-4 space-y-2 text-sm text-gray-500">
                <p>Try: "Show me my email summary"</p>
                <p>Try: "Delete my spam emails"</p>
                <p>Try: "Classify my unprocessed emails"</p>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={index} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.isUser 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  <p className="text-sm">{message.text}</p>
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 px-4 py-2 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="border-t border-gray-200 p-4">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask me about your emails..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Simple Analytics Page
function AnalyticsPage() {
  const [analytics, setAnalytics] = React.useState(null);

  React.useEffect(() => {
    // Back to working mock data - fast and reliable
    setAnalytics({
      totalEmails: 1247,
      spamBlocked: 89,
      categoriesCreated: 12,
      timesSaved: '4.2 hours',
      topCategories: [
        { name: 'Work', count: 542, percentage: 43 },
        { name: 'Personal', count: 324, percentage: 26 },
        { name: 'Shopping', count: 198, percentage: 16 },
        { name: 'Newsletters', count: 160, percentage: 13 },
        { name: 'Social', count: 23, percentage: 2 }
      ]
    });
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600">Email insights and statistics</p>
      </div>

      {analytics && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="p-3 rounded-lg bg-blue-50">
                  <span className="text-2xl">📊</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Processed</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics.totalEmails}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="p-3 rounded-lg bg-red-50">
                  <span className="text-2xl">🛡️</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Spam Blocked</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics.spamBlocked}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="p-3 rounded-lg bg-green-50">
                  <span className="text-2xl">📂</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Categories</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics.categoriesCreated}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="p-3 rounded-lg bg-purple-50">
                  <span className="text-2xl">⏰</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Time Saved</p>
                  <p className="text-2xl font-bold text-gray-900">{analytics.timesSaved}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Email Categories Distribution</h2>
            <div className="space-y-4">
              {analytics.topCategories.map((category, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
                    <span className="font-medium text-gray-900">{category.name}</span>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full" 
                        style={{ width: `${category.percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-600 w-12 text-right">{category.count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// Simple Settings Page
function SettingsPage() {
  const { user, logout } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Manage your account and preferences</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input 
              type="email" 
              value={user?.email || ''} 
              disabled 
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">User ID</label>
            <input 
              type="text" 
              value={user?.id || ''} 
              disabled 
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
            />
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Configuration</h2>
        <div className="space-y-4">
          <div className="flex justify-between items-center p-4 bg-blue-50 rounded-lg">
            <div>
              <h3 className="font-medium text-blue-900">OpenAI Model</h3>
              <p className="text-sm text-blue-700">GPT-4o-mini - Optimized for email processing</p>
            </div>
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">Active</span>
          </div>
          <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
            <div>
              <h3 className="font-medium text-gray-900">Cost per 1000 emails</h3>
              <p className="text-sm text-gray-600">Estimated processing cost</p>
            </div>
            <span className="font-medium text-gray-900">~$0.15</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Danger Zone</h2>
        <button
          onClick={logout}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Sign Out
        </button>
      </div>
    </div>
  );
}

// Layout with Sidebar
function Layout({ children }) {
  const { user, logout } = useAuth();
  const [currentPage, setCurrentPage] = React.useState('dashboard');

  const navigation = [
    { name: 'Dashboard', id: 'dashboard', icon: '🏠' },
    // { name: 'Emails', id: 'emails', icon: '📧' }, // Commented out for now
    { name: 'AI Assistant', id: 'chat', icon: '🤖' },
    { name: 'Analytics', id: 'analytics', icon: '📊' },
    { name: 'Settings', id: 'settings', icon: '⚙️' },
  ];

  // Render the correct page based on currentPage
  const renderCurrentPage = () => {
    switch (currentPage) {
      // case 'emails':
      //   return <EmailsPage />; // Commented out for now
      case 'chat':
        return <ChatPage />;
      case 'analytics':
        return <AnalyticsPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-sm border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">ScrapIt</h1>
              <p className="text-xs text-gray-500">Email Cleaner</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {navigation.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                currentPage === item.id
                  ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.name}</span>
            </button>
          ))}
        </nav>

        {/* User info */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <span className="text-xs font-medium text-gray-600">
                {user?.email?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
          >
            Sign out
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 capitalize">
                {currentPage}
              </h2>
              <p className="text-sm text-gray-600">
                {currentPage === 'dashboard' && 'Overview of your email management'}
                {currentPage === 'emails' && 'Manage your email inbox'}
                {currentPage === 'chat' && 'Chat with your AI assistant'}
                {currentPage === 'analytics' && 'Email insights and statistics'}
                {currentPage === 'settings' && 'Account and preferences'}
              </p>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-6 overflow-auto">
          {renderCurrentPage()}
        </main>
      </div>
    </div>
  );
}

// Protected Route
function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

// Main App
function BeautifulApp() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default BeautifulApp;