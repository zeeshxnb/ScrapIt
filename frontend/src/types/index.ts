export interface User {
  id: string;
  email: string;
  google_id: string;
  created_at: string;
  name?: string;
}

export interface Email {
  id: string;
  user_id: string;
  gmail_id: string;
  subject: string;
  sender: string;
  recipient: string;
  content?: string;
  snippet: string;
  received_date: string;
  labels: string[];
  category?: string;
  confidence_score?: number;
  is_spam: boolean;
  is_processed: boolean;
  is_deleted: boolean;
  is_archived: boolean;
  created_at: string;
}

export interface EmailSummary {
  total: number;
  spam: number;
  unprocessed: number;
  categories: Record<string, number>;
  recent_senders: Array<{
    sender: string;
    count: number;
  }>;
  oldest_unread?: {
    subject: string;
    sender: string;
    received_date: string;
  };
}

export interface ChatMessage {
  id: string;
  message: string;
  response: string;
  action?: string;
  data?: any;
  suggestions: string[];
  quick_actions: Array<{
    label: string;
    action: string;
  }>;
  timestamp: string;
  isUser: boolean;
}

export interface QuickAction {
  id: string;
  label: string;
  icon: string;
  type: 'primary' | 'secondary' | 'destructive';
  count?: number;
}

export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: () => void;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export interface EmailContextType {
  emails: Email[];
  summary: EmailSummary | null;
  isLoading: boolean;
  error: string | null;
  fetchEmails: (params?: EmailFetchParams) => Promise<void>;
  fetchSummary: () => Promise<void>;
  syncEmails: () => Promise<void>;
  classifyEmails: () => Promise<void>;
  deleteSpamEmails: () => Promise<void>;
  searchEmails: (query: string, filters?: EmailFilters) => Promise<Email[]>;
}

export interface EmailFetchParams {
  limit?: number;
  offset?: number;
  category?: string;
  is_spam?: boolean;
}

export interface EmailFilters {
  sender?: string;
  category?: string;
  is_spam?: boolean;
  date_from?: string;
  date_to?: string;
}