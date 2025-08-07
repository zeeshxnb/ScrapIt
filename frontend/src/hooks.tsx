import React from 'react';

// Mock hooks for demo
export const useAuth = () => {
  return {
    user: { email: 'demo@example.com', id: '1', created_at: '2024-01-01' },
    isAuthenticated: true,
    isLoading: false,
    login: () => console.log('Login clicked'),
    logout: () => console.log('Logout clicked'),
    checkAuth: () => Promise.resolve()
  };
};

export const useEmail = () => {
  return {
    emails: [
      {
        id: '1',
        subject: 'Welcome to ScrapIt!',
        sender: 'welcome@scrapit.com',
        snippet: 'Thank you for trying ScrapIt - your AI-powered email cleaner...',
        received_date: '2024-01-15T10:30:00Z',
        category: 'personal',
        is_spam: false,
        is_processed: true,
        confidence_score: 0.95
      },
      {
        id: '2', 
        subject: 'Special Offer - 50% Off!',
        sender: 'spam@example.com',
        snippet: 'Limited time offer! Click now to save big...',
        received_date: '2024-01-14T09:15:00Z',
        category: 'spam',
        is_spam: true,
        is_processed: true,
        confidence_score: 0.98
      }
    ],
    summary: {
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
    },
    fetchEmails: () => Promise.resolve(),
    fetchSummary: () => Promise.resolve(),
    syncEmails: () => Promise.resolve(),
    classifyEmails: () => Promise.resolve(),
    deleteSpamEmails: () => Promise.resolve(),
    searchEmails: () => Promise.resolve([]),
    isLoading: false,
    error: null
  };
};