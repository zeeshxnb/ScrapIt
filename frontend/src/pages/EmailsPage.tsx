import React, { useEffect, useState } from 'react';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  TrashIcon,
  ArchiveBoxIcon,
  TagIcon,
  CheckIcon,
  ExclamationTriangleIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';
import { useEmail } from '../contexts/EmailContext';
import { Email } from '../types';
import LoadingSpinner from '../components/LoadingSpinner';

const EmailsPage: React.FC = () => {
  const { emails, fetchEmails, isLoading, deleteSpamEmails } = useEmail();
  const [selectedEmails, setSelectedEmails] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterSpam, setFilterSpam] = useState<boolean | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchEmails();
  }, []);

  const filteredEmails = emails.filter(email => {
    const matchesSearch = email.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         email.sender.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         email.snippet.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesCategory = filterCategory === 'all' || email.category === filterCategory;
    const matchesSpam = filterSpam === null || email.is_spam === filterSpam;
    
    return matchesSearch && matchesCategory && matchesSpam;
  });

  const categories = [...new Set(emails.map(email => email.category).filter(Boolean))];

  const handleSelectEmail = (emailId: string) => {
    setSelectedEmails(prev => 
      prev.includes(emailId) 
        ? prev.filter(id => id !== emailId)
        : [...prev, emailId]
    );
  };

  const handleSelectAll = () => {
    if (selectedEmails.length === filteredEmails.length) {
      setSelectedEmails([]);
    } else {
      setSelectedEmails(filteredEmails.map(email => email.id));
    }
  };

  const handleBulkDelete = async () => {
    if (selectedEmails.length === 0) return;
    
    // In a real app, this would call a bulk delete API
    console.log('Bulk deleting emails:', selectedEmails);
    setSelectedEmails([]);
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      work: 'bg-blue-100 text-blue-800',
      personal: 'bg-green-100 text-green-800',
      shopping: 'bg-purple-100 text-purple-800',
      newsletter: 'bg-yellow-100 text-yellow-800',
      social: 'bg-pink-100 text-pink-800',
      spam: 'bg-red-100 text-red-800',
    };
    return colors[category?.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  if (isLoading && emails.length === 0) {
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
          <h1 className="text-2xl font-bold text-gray-900">Emails</h1>
          <p className="text-gray-600">
            {filteredEmails.length} of {emails.length} emails
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          {selectedEmails.length > 0 && (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">
                {selectedEmails.length} selected
              </span>
              <button
                onClick={handleBulkDelete}
                className="btn-danger flex items-center space-x-2"
              >
                <TrashIcon className="w-4 h-4" />
                <span>Delete</span>
              </button>
            </div>
          )}
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary flex items-center space-x-2"
          >
            <FunnelIcon className="w-4 h-4" />
            <span>Filters</span>
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="card space-y-4">
        {/* Search */}
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search emails by subject, sender, or content..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input pl-10"
          />
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-gray-200">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category
              </label>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="input"
              >
                <option value="all">All Categories</option>
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category?.charAt(0).toUpperCase() + category?.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Spam Filter
              </label>
              <select
                value={filterSpam === null ? 'all' : filterSpam.toString()}
                onChange={(e) => {
                  const value = e.target.value;
                  setFilterSpam(value === 'all' ? null : value === 'true');
                }}
                className="input"
              >
                <option value="all">All Emails</option>
                <option value="false">Not Spam</option>
                <option value="true">Spam Only</option>
              </select>
            </div>
            
            <div className="flex items-end">
              <button
                onClick={() => {
                  setSearchQuery('');
                  setFilterCategory('all');
                  setFilterSpam(null);
                }}
                className="btn-secondary w-full"
              >
                Clear Filters
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Email List */}
      <div className="card p-0">
        {/* Header */}
        <div className="p-4 border-b border-gray-200 flex items-center space-x-4">
          <input
            type="checkbox"
            checked={selectedEmails.length === filteredEmails.length && filteredEmails.length > 0}
            onChange={handleSelectAll}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm font-medium text-gray-700">
            Select All
          </span>
        </div>

        {/* Email Items */}
        <div className="divide-y divide-gray-200">
          {filteredEmails.length === 0 ? (
            <div className="p-8 text-center">
              <MagnifyingGlassIcon className="w-12 h-12 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No emails found</h3>
              <p className="text-gray-600">
                {searchQuery || filterCategory !== 'all' || filterSpam !== null
                  ? 'Try adjusting your search or filters'
                  : 'Sync your emails to see them here'
                }
              </p>
            </div>
          ) : (
            filteredEmails.map((email) => (
              <div
                key={email.id}
                className={`p-4 hover:bg-gray-50 transition-colors ${
                  selectedEmails.includes(email.id) ? 'bg-primary-50' : ''
                }`}
              >
                <div className="flex items-start space-x-4">
                  <input
                    type="checkbox"
                    checked={selectedEmails.includes(email.id)}
                    onChange={() => handleSelectEmail(email.id)}
                    className="mt-1 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center space-x-3">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {email.sender}
                        </p>
                        {email.is_spam && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                            <ExclamationTriangleIcon className="w-3 h-3 mr-1" />
                            Spam
                          </span>
                        )}
                        {!email.is_processed && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                            <ClockIcon className="w-3 h-3 mr-1" />
                            Unprocessed
                          </span>
                        )}
                        {email.category && (
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getCategoryColor(email.category)}`}>
                            <TagIcon className="w-3 h-3 mr-1" />
                            {email.category}
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-gray-500">
                        {formatDate(email.received_date)}
                      </span>
                    </div>
                    
                    <h3 className="text-sm font-medium text-gray-900 mb-1 truncate">
                      {email.subject}
                    </h3>
                    
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {email.snippet}
                    </p>
                    
                    {email.confidence_score && (
                      <div className="mt-2 flex items-center space-x-2">
                        <span className="text-xs text-gray-500">
                          AI Confidence:
                        </span>
                        <div className="flex-1 bg-gray-200 rounded-full h-1.5 max-w-20">
                          <div
                            className="bg-primary-600 h-1.5 rounded-full"
                            style={{ width: `${email.confidence_score * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500">
                          {Math.round(email.confidence_score * 100)}%
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      className="p-1 text-gray-400 hover:text-gray-600 rounded"
                      title="Archive"
                    >
                      <ArchiveBoxIcon className="w-4 h-4" />
                    </button>
                    <button
                      className="p-1 text-gray-400 hover:text-red-600 rounded"
                      title="Delete"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Pagination */}
      {filteredEmails.length > 0 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-700">
            Showing <span className="font-medium">1</span> to{' '}
            <span className="font-medium">{Math.min(50, filteredEmails.length)}</span> of{' '}
            <span className="font-medium">{filteredEmails.length}</span> results
          </p>
          
          <div className="flex items-center space-x-2">
            <button className="btn-secondary">Previous</button>
            <button className="btn-secondary">Next</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmailsPage;