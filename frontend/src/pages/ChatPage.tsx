import React, { useState, useRef, useEffect } from 'react';
import {
  PaperAirplaneIcon,
  SparklesIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  ChartBarIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';
import { chatApi } from '../services/api.ts';
import { useEmail } from '../contexts/EmailContext.tsx';
import LoadingSpinner from '../components/LoadingSpinner.tsx';

interface ChatMessage {
  id: string;
  message: string;
  response: string;
  isUser: boolean;
  timestamp: string;
  suggestions?: string[];
  quickActions?: Array<{ label: string; action: string }>;
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { summary, syncEmails, classifyEmails, deleteSpamEmails } = useEmail();

  useEffect(() => {
    // Load initial suggestions
    loadSuggestions();
    
    // Add welcome message
    const welcomeMessage: ChatMessage = {
      id: '1',
      message: '',
      response: "Hi! I'm your ScrapIt AI assistant. I can help you manage your emails with natural language commands. Try asking me to 'delete spam emails' or 'show my email stats'!",
      isUser: false,
      timestamp: new Date().toISOString(),
      suggestions: [
        "Show me my email statistics",
        "Delete my spam emails",
        "Classify my unprocessed emails",
        "Find emails from my boss"
      ]
    };
    setMessages([welcomeMessage]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSuggestions = async () => {
    try {
      const response = await chatApi.getSuggestions();
      setSuggestions(response.suggestions || []);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    }
  };

  const sendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      message,
      response: '',
      isUser: true,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage(message);
      
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: '',
        response: response.response,
        isUser: false,
        timestamp: new Date().toISOString(),
        suggestions: response.suggestions,
        quickActions: response.quick_actions,
      };

      setMessages(prev => [...prev, botMessage]);
      
      // Handle actions
      if (response.action) {
        await handleAction(response.action, response.data);
      }
      
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: '',
        response: "I'm having trouble processing that right now. Could you try rephrasing your request?",
        isUser: false,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAction = async (action: string, data?: any) => {
    switch (action) {
      case 'delete_spam':
        await deleteSpamEmails();
        break;
      case 'classify_emails':
        await classifyEmails();
        break;
      case 'sync_emails':
        await syncEmails();
        break;
      default:
        console.log('Unknown action:', action);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion);
  };

  const handleQuickAction = (action: string) => {
    const actionMessages: Record<string, string> = {
      'confirm_delete_spam': 'Yes, delete all spam emails',
      'show_spam': 'Show me the spam emails first',
      'confirm_classify': 'Start classifying my emails',
      'confirm_sync': 'Sync my emails now',
    };
    
    const message = actionMessages[action] || action;
    sendMessage(message);
  };

  const quickActions = [
    {
      icon: TrashIcon,
      label: `Delete ${summary?.spam || 0} Spam Emails`,
      action: () => sendMessage('Delete my spam emails'),
      color: 'text-red-600 bg-red-50 hover:bg-red-100',
      disabled: !summary?.spam,
    },
    {
      icon: SparklesIcon,
      label: `Classify ${summary?.unprocessed || 0} Emails`,
      action: () => sendMessage('Classify my emails'),
      color: 'text-blue-600 bg-blue-50 hover:bg-blue-100',
      disabled: !summary?.unprocessed,
    },
    {
      icon: ChartBarIcon,
      label: 'Show Email Stats',
      action: () => sendMessage('Show me my email statistics'),
      color: 'text-green-600 bg-green-50 hover:bg-green-100',
      disabled: false,
    },
    {
      icon: ArrowPathIcon,
      label: 'Sync Latest Emails',
      action: () => sendMessage('Sync my latest emails'),
      color: 'text-purple-600 bg-purple-50 hover:bg-purple-100',
      disabled: false,
    },
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Assistant</h1>
            <p className="text-gray-600">Chat with your email management assistant</p>
          </div>
          
          <div className="flex items-center space-x-2">
            <SparklesIcon className="w-6 h-6 text-primary-600" />
            <span className="text-sm font-medium text-primary-600">AI Powered</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Quick Actions</h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <button
                key={index}
                onClick={action.action}
                disabled={action.disabled}
                className={`p-3 rounded-lg border border-gray-200 transition-colors ${
                  action.disabled 
                    ? 'opacity-50 cursor-not-allowed' 
                    : `${action.color} hover:border-gray-300`
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Icon className="w-4 h-4" />
                  <span className="text-sm font-medium truncate">{action.label}</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((message) => (
            <div key={message.id} className="space-y-4">
              {/* User Message */}
              {message.isUser && (
                <div className="flex justify-end">
                  <div className="max-w-xs lg:max-w-md">
                    <div className="bg-primary-600 text-white rounded-lg px-4 py-2">
                      <p className="text-sm">{message.message}</p>
                    </div>
                    <p className="text-xs text-gray-500 mt-1 text-right">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              )}

              {/* Bot Message */}
              {!message.isUser && (
                <div className="flex justify-start">
                  <div className="max-w-xs lg:max-w-2xl">
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <SparklesIcon className="w-4 h-4 text-primary-600" />
                      </div>
                      <div className="bg-white rounded-lg px-4 py-2 shadow-sm border border-gray-200">
                        <p className="text-sm text-gray-900 whitespace-pre-wrap">{message.response}</p>
                      </div>
                    </div>
                    
                    {/* Quick Actions */}
                    {message.quickActions && message.quickActions.length > 0 && (
                      <div className="mt-3 ml-11 flex flex-wrap gap-2">
                        {message.quickActions.map((action, index) => (
                          <button
                            key={index}
                            onClick={() => handleQuickAction(action.action)}
                            className="px-3 py-1 text-xs bg-primary-100 text-primary-700 rounded-full hover:bg-primary-200 transition-colors"
                          >
                            {action.label}
                          </button>
                        ))}
                      </div>
                    )}
                    
                    {/* Suggestions */}
                    {message.suggestions && message.suggestions.length > 0 && (
                      <div className="mt-3 ml-11">
                        <p className="text-xs text-gray-500 mb-2">Try these:</p>
                        <div className="flex flex-wrap gap-2">
                          {message.suggestions.map((suggestion, index) => (
                            <button
                              key={index}
                              onClick={() => handleSuggestionClick(suggestion)}
                              className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <p className="text-xs text-gray-500 mt-1 ml-11">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <SparklesIcon className="w-4 h-4 text-primary-600" />
                </div>
                <div className="bg-white rounded-lg px-4 py-2 shadow-sm border border-gray-200">
                  <div className="flex items-center space-x-2">
                    <LoadingSpinner size="small" />
                    <span className="text-sm text-gray-500">Thinking...</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto">
          {/* Suggestions */}
          {suggestions.length > 0 && messages.length <= 1 && (
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">💡 Suggestions:</p>
              <div className="flex flex-wrap gap-2">
                {suggestions.slice(0, 4).map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input */}
          <div className="flex items-center space-x-3">
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage(inputMessage)}
                placeholder="Ask me anything about your emails..."
                disabled={isLoading}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50"
              />
            </div>
            <button
              onClick={() => sendMessage(inputMessage)}
              disabled={!inputMessage.trim() || isLoading}
              className="btn-primary p-3 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <PaperAirplaneIcon className="w-5 h-5" />
            </button>
          </div>

          <p className="text-xs text-gray-500 mt-2 text-center">
            I can help you delete spam, classify emails, search your inbox, and more!
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;