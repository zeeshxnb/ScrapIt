import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout.tsx';
import ProtectedRoute from './components/ProtectedRoute.tsx';
import { AuthProvider } from './contexts/AuthContext.tsx';
import { EmailProvider } from './contexts/EmailContext.tsx';
import Dashboard from './pages/Dashboard.tsx';
import EmailsPage from './pages/EmailsPage.tsx';
import ChatPage from './pages/ChatPage.tsx';
import AnalyticsPage from './pages/AnalyticsPage.tsx';
import SettingsPage from './pages/SettingsPage.tsx';
import Privacy from './pages/Privacy.tsx';
import Terms from './pages/Terms.tsx';
import LoginPage from './pages/LoginPage.tsx';

function App() {
  return (
    <AuthProvider>
      <EmailProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route index element={<Dashboard />} />
              <Route path="emails" element={<EmailsPage />} />
              <Route path="chat" element={<ChatPage />} />
              <Route path="analytics" element={<AnalyticsPage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="privacy" element={<Privacy />} />
              <Route path="terms" element={<Terms />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </EmailProvider>
    </AuthProvider>
  );
}

export default App;