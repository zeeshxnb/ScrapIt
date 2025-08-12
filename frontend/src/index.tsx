import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// Apply theme class BEFORE React mounts, based on saved preferences
(() => {
  try {
    const raw = localStorage.getItem('app_prefs');
    const prefs = raw ? JSON.parse(raw) : {};
    const theme = prefs?.preferences?.theme ?? 'dark';
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldDark = theme === 'dark' || (theme === 'auto' && prefersDark);
    document.documentElement.classList.toggle('dark', !!shouldDark);
  } catch (_) {
    // ignore
  }
})();

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);