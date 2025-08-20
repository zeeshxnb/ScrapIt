import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Email, EmailSummary, EmailContextType, EmailFetchParams, EmailFilters } from '../types';
import { gmailApi, aiApi, chatApi } from '../services/api.ts';
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
      window.dispatchEvent(new CustomEvent('app:notify', { detail: { text: 'Emails loaded' } }));
    } catch (err: any) {
      setError(err.message || 'Failed to fetch emails');
      toast.error('Failed to fetch emails');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const summaryData = await chatApi.getSummary();
      setSummary(summaryData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch summary');
      toast.error('Failed to fetch email summary');
    } finally {
      setIsLoading(false);
    }
  };

  const syncEmails = async () => {
    try {
      setIsLoading(true);
      setError(null);
      await gmailApi.syncEmails();
      toast.success('Emails synced successfully');
      window.dispatchEvent(new CustomEvent('app:notify', { detail: { text: 'Email sync completed' } }));
      // Refresh data after sync
      await Promise.all([fetchEmails(), fetchSummary()]);
    } catch (err: any) {
      setError(err.message || 'Failed to sync emails');
      toast.error('Failed to sync emails');
    } finally {
      setIsLoading(false);
    }
  };

  const classifyEmails = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await aiApi.classifyEmails();
      toast.success(`Classified ${result.processed || 0} emails`);
      window.dispatchEvent(new CustomEvent('app:notify', { detail: { text: `Classified ${result.processed || 0} emails` } }));
      // Refresh data after classification
      await Promise.all([fetchEmails(), fetchSummary()]);
    } catch (err: any) {
      setError(err.message || 'Failed to classify emails');
      toast.error('Failed to classify emails');
    } finally {
      setIsLoading(false);
    }
  };

  const deleteSpamEmails = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await aiApi.deleteSpamEmails();
      toast.success(`Deleted ${result.deleted_count || 0} spam emails`);
      window.dispatchEvent(new CustomEvent('app:notify', { detail: { text: `Deleted ${result.deleted_count || 0} spam emails` } }));
      // Refresh data after deletion
      await Promise.all([fetchEmails(), fetchSummary()]);
    } catch (err: any) {
      setError(err.message || 'Failed to delete spam emails');
      toast.error('Failed to delete spam emails');
    } finally {
      setIsLoading(false);
    }
  };

  const searchEmails = async (query: string, filters: EmailFilters = {}): Promise<Email[]> => {
    try {
      setError(null);
      const results = await chatApi.searchEmails(query, filters);
      return results;
    } catch (err: any) {
      setError(err.message || 'Failed to search emails');
      toast.error('Failed to search emails');
      return [];
    }
  };

  const bulkDeleteEmails = async (emailIds: string[], permanent: boolean = false) => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await aiApi.bulkDeleteEmails(emailIds, permanent);
      toast.success(`Deleted ${result.count || 0} emails`);
      window.dispatchEvent(new CustomEvent('app:notify', { detail: { text: `Deleted ${result.count || 0} emails` } }));
      await Promise.all([fetchEmails(), fetchSummary()]);
    } catch (err: any) {
      setError(err.message || 'Failed to delete emails');
      toast.error('Failed to delete emails');
    } finally {
      setIsLoading(false);
    }
  };

  const deleteEmail = async (emailId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await aiApi.deleteEmail(emailId);
      toast.success('Email moved to trash');
      window.dispatchEvent(new CustomEvent('app:notify', { detail: { text: 'Email moved to trash' } }));
      // Refresh data after deletion
      await Promise.all([fetchEmails(), fetchSummary()]);
    } catch (err: any) {
      setError(err.message || 'Failed to delete email');
      toast.error('Failed to delete email');
    } finally {
      setIsLoading(false);
    }
  };

  const archiveEmail = async (emailId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await aiApi.archiveEmail(emailId);
      toast.success('Email archived');
      window.dispatchEvent(new CustomEvent('app:notify', { detail: { text: 'Email archived' } }));
      // Refresh data after archiving
      await Promise.all([fetchEmails(), fetchSummary()]);
    } catch (err: any) {
      setError(err.message || 'Failed to archive email');
      toast.error('Failed to archive email');
    } finally {
      setIsLoading(false);
    }
  };

  const bulkArchiveEmails = async (emailIds: string[]) => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await aiApi.bulkArchiveEmails(emailIds);
      toast.success(`Archived ${result.count || 0} emails`);
      window.dispatchEvent(new CustomEvent('app:notify', { detail: { text: `Archived ${result.count || 0} emails` } }));
      await Promise.all([fetchEmails(), fetchSummary()]);
    } catch (err: any) {
      setError(err.message || 'Failed to archive emails');
      toast.error('Failed to archive emails');
    } finally {
      setIsLoading(false);
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
    bulkDeleteEmails,
    bulkArchiveEmails,
    deleteEmail,
    archiveEmail,
  };

  return (
    <EmailContext.Provider value={value}>
      {children}
    </EmailContext.Provider>
  );
};