// src/components/OAuthCallback.js
import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const OAuthCallback = ({ onLogin }) => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Parse query parameters (e.g., ?username=johndoe)
    const params = new URLSearchParams(location.search);
    const username = params.get('username');

    if (username) {
      console.log('OAuthCallback: Successfully received username ->', username);
      onLogin(username);
      // ✅ STEP 1: Correct the success redirect path to the dashboard
      navigate('/dashboard'); 
    } else {
      console.warn('OAuthCallback: No username found in query params. Redirecting to auth page.');
      // ✅ STEP 2: Correct the failure redirect path to the auth page
      navigate('/auth');
    }
  }, [location, navigate, onLogin]);

  return (
    <div style={{ textAlign: 'center', paddingTop: '100px' }}>
      <h2>Logging you in...</h2>
      <p>Please wait while we complete your login.</p>
    </div>
  );
};

export default OAuthCallback;