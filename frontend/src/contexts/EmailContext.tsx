import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Email, EmailSummary, EmailContextType, EmailFetchParams, EmailFilters } from '../types';
import { gmailApi, aiApi, chatApi } from '../services/api';
import toast from 'react-hot-toast';

const EmailContext = createContext<EmailContextType | undefined>(undefined);

export const useEmail = () => {
  const context = useContext(EmailContext);
  if (context === undefined) {
    throw new Error('useEmail must be used within an EmailProvider');
  }
  return context;
};

interface EmailProviderProps {
  children: ReactNode;
}

export const EmailProvider: React.FC<EmailProviderProps> = ({ children }) => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [summary, setSummary] = useState<EmailSummary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEmails = async (params: EmailFetchParams = {}) => {
    try {
      setIsLoading(true);
      setError(null);
      const emailData = await gmailApi.getEmails(params);
      setEmails(emailData);
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to fetch emails';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const summaryData = await chatApi.getSummary();
      setSummary(summaryData);
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to fetch email summary';
      setError(errorMessage);
      console.error('Failed to fetch summary:', err);
    }
  };

  const syncEmails = async () => {
    try {
      setIsLoading(true);
      toast.loading('Syncing emails from Gmail...', { id: 'sync' });
      
      await gmailApi.syncEmails();
      
      // Refresh data after sync
      await Promise.all([
        fetchEmails(),
        fetchSummary()
      ]);
      
      toast.success('Emails synced successfully!', { id: 'sync' });
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to sync emails';
      toast.error(errorMessage, { id: 'sync' });
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const classifyEmails = async () => {
    try {
      setIsLoading(true);
      toast.loading('Classifying emails with AI...', { id: 'classify' });
      
      await aiApi.classifyEmails();
      
      // Refresh data after classification
      await Promise.all([
        fetchEmails(),
        fetchSummary()
      ]);
      
      toast.success('Emails classified successfully!', { id: 'classify' });
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to classify emails';
      toast.error(errorMessage, { id: 'classify' });
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteSpamEmails = async () => {
    try {
      setIsLoading(true);
      toast.loading('Deleting spam emails...', { id: 'delete-spam' });
      
      const result = await aiApi.deleteSpamEmails();
      
      // Refresh data after deletion
      await Promise.all([
        fetchEmails(),
        fetchSummary()
      ]);
      
      const deletedCount = result.deleted_count || 0;
      toast.success(`Deleted ${deletedCount} spam emails!`, { id: 'delete-spam' });
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to delete spam emails';
      toast.error(errorMessage, { id: 'delete-spam' });
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const searchEmails = async (query: string, filters: EmailFilters = {}): Promise<Email[]> => {
    try {
      const results = await chatApi.searchEmails(query, filters);
      return results;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to search emails';
      toast.error(errorMessage);
      throw err;
    }
  };

  const value: EmailContextType = {
    emails,
    summary,
    isLoading,
    error,
    fetchEmails,
    fetchSummary,
    syncEmails,
    classifyEmails,
    deleteSpamEmails,
    searchEmails,
  };

  return (
    <EmailContext.Provider value={value}>
      {children}
    </EmailContext.Provider>
  );
};