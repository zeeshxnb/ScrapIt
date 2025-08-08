import React, { useEffect, useState } from 'react';

interface User {
  email: string;
  id: string;
}

function SimpleDashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [emailSummary, setEmailSummary] = useState<any>(null);

  useEffect(() => {
    // Check if we have a token in the URL (from OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
      // Store the token
      localStorage.setItem('auth_token', token);
      // Remove token from URL
      window.history.replaceState({}, document.title, window.location.pathname);
      fetchUserInfo(token);
    } else {
      // Check if we already have a token stored
      const storedToken = localStorage.getItem('auth_token');
      if (storedToken) {
        fetchUserInfo(storedToken);
      } else {
        setLoading(false);
      }
    }
  }, []);

  const fetchUserInfo = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        localStorage.removeItem('auth_token');
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
      localStorage.removeItem('auth_token');
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = () => {
    window.location.href = 'http://localhost:8000/auth/google-redirect';
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
  };

  const syncEmails = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('http://localhost:8000/gmail/sync', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        alert('Emails synced successfully!');
        fetchEmailSummary();
      } else {
        alert('Failed to sync emails');
      }
    } catch (error) {
      alert('Error syncing emails: ' + error.message);
    }
  };

  const fetchEmailSummary = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('http://localhost:8000/chat/summary', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setEmailSummary(data);
      }
    } catch (error) {
      console.error('Failed to fetch email summary:', error);
    }
  };

  const classifyEmails = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('http://localhost:8000/ai/classify', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`Classified ${data.processed} emails!`);
        fetchEmailSummary();
      } else {
        alert('Failed to classify emails');
      }
    } catch (error) {
      alert('Error classifying emails: ' + error.message);
    }
  };

  const deleteSpam = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch('http://localhost:8000/ai/spam', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        alert(`Deleted ${data.deleted_count} spam emails!`);
        fetchEmailSummary();
      } else {
        alert('Failed to delete spam emails');
      }
    } catch (error) {
      alert('Error deleting spam: ' + error.message);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '50px', textAlign: 'center', fontFamily: 'Arial' }}>
        <h1>Loading...</h1>
      </div>
    );
  }

  if (!user) {
    return (
      <div style={{ padding: '50px', textAlign: 'center', fontFamily: 'Arial', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
        <div style={{ maxWidth: '600px', margin: '0 auto', backgroundColor: 'white', padding: '40px', borderRadius: '10px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
          <h1 style={{ color: '#1f2937', marginBottom: '10px' }}>🤖 ScrapIt</h1>
          <h2 style={{ color: '#6b7280', marginBottom: '30px' }}>AI-Powered Email Cleaner</h2>
          <p style={{ color: '#374151', marginBottom: '30px' }}>
            Clean your Gmail inbox in minutes with AI-powered spam detection, 
            email categorization, and bulk operations.
          </p>
          
          <button 
            onClick={handleLogin}
            style={{
              padding: '15px 30px',
              fontSize: '18px',
              backgroundColor: '#4285f4',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              marginBottom: '30px'
            }}
          >
            🚀 Sign in with Google
          </button>
          
          <div style={{ backgroundColor: '#f9fafb', padding: '20px', borderRadius: '8px', textAlign: 'left' }}>
            <h3 style={{ color: '#1f2937', marginBottom: '15px' }}>✨ Features:</h3>
            <ul style={{ color: '#374151', lineHeight: '1.6' }}>
              <li>🎯 Smart spam detection with GPT-4o-mini</li>
              <li>📂 Automatic email categorization</li>
              <li>🗑️ Bulk delete spam and unwanted emails</li>
              <li>💬 Natural language chat interface</li>
              <li>📊 Email analytics and insights</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '10px', marginBottom: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h1 style={{ color: '#1f2937', margin: '0' }}>🤖 ScrapIt Dashboard</h1>
              <p style={{ color: '#6b7280', margin: '5px 0 0 0' }}>Welcome, {user.email}</p>
            </div>
            <button 
              onClick={handleLogout}
              style={{
                padding: '10px 20px',
                backgroundColor: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer'
              }}
            >
              Logout
            </button>
          </div>
        </div>

        {/* Quick Actions */}
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '10px', marginBottom: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h2 style={{ color: '#1f2937', marginBottom: '20px' }}>🚀 Quick Actions</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
            <button 
              onClick={syncEmails}
              style={{
                padding: '15px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              📥 Sync Gmail
            </button>
            <button 
              onClick={fetchEmailSummary}
              style={{
                padding: '15px',
                backgroundColor: '#10b981',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              📊 Get Summary
            </button>
            <button 
              onClick={classifyEmails}
              style={{
                padding: '15px',
                backgroundColor: '#f59e0b',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              🤖 Classify Emails
            </button>
            <button 
              onClick={deleteSpam}
              style={{
                padding: '15px',
                backgroundColor: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              🗑️ Delete Spam
            </button>
          </div>
        </div>

        {/* Email Summary */}
        {emailSummary && (
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '10px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <h2 style={{ color: '#1f2937', marginBottom: '20px' }}>📈 Email Summary</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px', marginBottom: '20px' }}>
              <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#f3f4f6', borderRadius: '8px' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1f2937' }}>{emailSummary.total}</div>
                <div style={{ color: '#6b7280' }}>Total Emails</div>
              </div>
              <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#fef2f2', borderRadius: '8px' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc2626' }}>{emailSummary.spam}</div>
                <div style={{ color: '#6b7280' }}>Spam</div>
              </div>
              <div style={{ textAlign: 'center', padding: '15px', backgroundColor: '#fffbeb', borderRadius: '8px' }}>
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#d97706' }}>{emailSummary.unprocessed}</div>
                <div style={{ color: '#6b7280' }}>Unprocessed</div>
              </div>
            </div>
            
            {emailSummary.categories && Object.keys(emailSummary.categories).length > 0 && (
              <div>
                <h3 style={{ color: '#1f2937', marginBottom: '15px' }}>📂 Categories</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '10px' }}>
                  {Object.entries(emailSummary.categories).map(([category, count]) => (
                    <div key={category} style={{ padding: '10px', backgroundColor: '#f9fafb', borderRadius: '6px', textAlign: 'center' }}>
                      <div style={{ fontWeight: 'bold', color: '#1f2937', textTransform: 'capitalize' }}>{category}</div>
                      <div style={{ color: '#6b7280' }}>{count}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* AI Model Info */}
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '10px', marginTop: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          <h2 style={{ color: '#1f2937', marginBottom: '15px' }}>🧠 AI Configuration</h2>
          <div style={{ backgroundColor: '#f0f9ff', padding: '15px', borderRadius: '8px' }}>
            <p style={{ color: '#0369a1', margin: '0' }}>
              <strong>Model:</strong> GPT-4o-mini<br/>
              <strong>Cost:</strong> ~$0.15 per 1000 emails<br/>
              <strong>Features:</strong> Smart spam detection, email categorization, natural language processing
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SimpleDashboard;