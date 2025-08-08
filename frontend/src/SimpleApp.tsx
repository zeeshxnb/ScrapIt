import React from 'react';

function SimpleApp() {
  const handleGoogleLogin = () => {
    console.log('Button clicked!');
    // Direct redirect to backend endpoint that will redirect to Google
    window.location.href = 'http://localhost:8000/auth/google-redirect';
  };

  return (
    <div style={{ padding: '50px', textAlign: 'center', fontFamily: 'Arial' }}>
      <h1>ScrapIt - Simple Test</h1>
      <p>If you see this, React is working!</p>
      <button 
        onClick={handleGoogleLogin}
        style={{
          padding: '10px 20px',
          fontSize: '16px',
          backgroundColor: '#4285f4',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer'
        }}
      >
        Continue with Google
      </button>
      
      <div style={{ marginTop: '20px' }}>
        <p>Or try direct link:</p>
        <a 
          href="http://localhost:8000/auth/google-redirect"
          style={{ color: '#4285f4', textDecoration: 'underline' }}
        >
          Direct Google Login Link
        </a>
      </div>
    </div>
  );
}

export default SimpleApp;