import React from 'react';

const Privacy: React.FC = () => (
  <div className="p-6 max-w-3xl mx-auto space-y-4">
    <h1 className="text-2xl font-bold">Privacy Policy</h1>
    <p>We store only what is needed to run the app: your account ID, email metadata, and labels. OAuth tokens are stored securely and used to sync emails. We do not sell your data. You can delete your data at any time by contacting us or using the app’s delete option when available.</p>
    <p>Email bodies may be cached locally to compute analytics and help you clean your inbox. You can choose a data retention period in Settings. After that, your cached data is deleted automatically.</p>
    <p>Third parties: We use Google APIs to access your Gmail with your consent. Data is transmitted over HTTPS. If you use AI features, snippets may be sent to OpenAI for processing.</p>
    
  </div>
);

export default Privacy;

